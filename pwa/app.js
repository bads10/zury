import {
  fetchGarment, compressImage, requestTryOn, pollResult,
  shareViaWhatsApp, registerSW, API_BASE,
} from './api.js';

// ── DOM helpers ───────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

// ── Shared state ──────────────────────────────────────────────────────────────
const state = {
  sellerSlug:   null,
  garmentId:    null,
  garment:      null,
  selfieFile:   null,      // File original
  selfieDataUrl: null,     // dataUrl compressé (AVIF/WebP)
  jobId:        null,
  resultUrl:    null,
  pollAbort:    null,      // AbortController
};

// ── Screen switching ──────────────────────────────────────────────────────────
const SCREEN_IDS = ['landing', 'capture', 'processing', 'result', 'error'];

function show(name) {
  SCREEN_IDS.forEach(id => {
    $(`screen-${id}`).hidden = id !== name;
  });
  window.scrollTo({ top: 0, behavior: 'instant' });
}

function showError(title, msg) {
  $('error-title').textContent   = title;
  $('error-message').textContent = msg;
  show('error');
}

// ── URL helper ────────────────────────────────────────────────────────────────
function resolveUrl(url) {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  return `${API_BASE}${url}`;
}

// ── Boot ──────────────────────────────────────────────────────────────────────
async function init() {
  registerSW();

  const p = new URLSearchParams(location.search);
  state.sellerSlug = p.get('seller');
  state.garmentId  = p.get('garment');

  if (!state.sellerSlug || !state.garmentId) {
    return showError(
      'Paramètres manquants',
      'Ce lien est incomplet. Demandez un nouveau lien au vendeur.'
    );
  }

  show('landing');
  $('screen-landing').classList.add('is-loading');

  try {
    state.garment = await fetchGarment(state.sellerSlug, state.garmentId);
    populateLanding(state.garment);
    $('screen-landing').classList.remove('is-loading');
  } catch (e) {
    if (e.code === 'NOT_FOUND') {
      showError('Vêtement introuvable', 'Ce vêtement n\'est plus disponible.');
    } else {
      showError('Connexion impossible', 'Vérifiez votre réseau et réessayez.');
    }
  }
}

// ── Landing ───────────────────────────────────────────────────────────────────
function populateLanding(g) {
  const img = $('garment-img');
  if (g.image_url) {
    img.src = resolveUrl(g.image_url);
    img.alt = g.name;
  }
  $('garment-name').textContent     = g.name;
  $('garment-seller').textContent   = `par ${g.seller_slug || g.seller_id}`;
  $('garment-category').textContent = g.category ?? '';
}

$('btn-tryon').addEventListener('click', () => show('capture'));

// ── Capture — file selection ──────────────────────────────────────────────────
$('btn-back-capture').addEventListener('click', () => show('landing'));

function setPreview(file) {
  if (!file) return;
  state.selfieFile = file;

  const imgEl = $('selfie-preview');
  if (imgEl._blob) URL.revokeObjectURL(imgEl._blob);
  imgEl._blob = URL.createObjectURL(file);
  imgEl.src   = imgEl._blob;

  $('upload-zone').hidden  = true;
  $('preview-wrap').hidden = false;
  $('skin-select').hidden  = false;
  $('submit-wrap').hidden  = false;
}

function clearCapture() {
  const imgEl = $('selfie-preview');
  if (imgEl._blob) { URL.revokeObjectURL(imgEl._blob); imgEl._blob = null; }
  imgEl.src = '';
  state.selfieFile    = null;
  state.selfieDataUrl = null;

  $('input-selfie').value  = '';
  $('input-gallery').value = '';
  $('upload-zone').hidden  = false;
  $('preview-wrap').hidden = true;
  $('skin-select').hidden  = true;
  $('submit-wrap').hidden  = true;
}

$('input-selfie').addEventListener('change',  e => setPreview(e.target.files[0]));
$('input-gallery').addEventListener('change', e => setPreview(e.target.files[0]));
$('btn-retake').addEventListener('click', clearCapture);

// ── Capture — skin tone (Fitzpatrick manuel) ──────────────────────────────────
// Note : la détection auto ITA est faite dans api.js au moment du submit.
// Le swatch sélectionné ici sert de fallback si la détection échoue.
document.querySelectorAll('.swatch').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.swatch').forEach(b => {
      b.classList.remove('active');
      b.removeAttribute('aria-checked');
    });
    btn.classList.add('active');
    btn.setAttribute('aria-checked', 'true');
  });
});

// ── Capture — submit ──────────────────────────────────────────────────────────
$('btn-submit').addEventListener('click', async () => {
  if (!state.selfieFile) return;

  const btn = $('btn-submit');
  btn.disabled    = true;
  btn.textContent = 'Compression…';

  try {
    // Compress → dataUrl (AVIF ou WebP selon device)
    state.selfieDataUrl = await compressImage(state.selfieFile);
    await startTryOn();
  } catch (e) {
    btn.disabled  = false;
    btn.innerHTML = 'Générer l\'essayage <span aria-hidden="true">✨</span>';
    showError('Erreur d\'image', e.message);
  }
});

// ── Processing ────────────────────────────────────────────────────────────────
async function startTryOn() {
  show('processing');
  setProgress(0);

  try {
    // Fitzpatrick détecté automatiquement dans api.js via ITA
    const { job_id } = await requestTryOn({
      selfieDataUrl: state.selfieDataUrl,
      garmentId:     state.garmentId,
      sellerId:      state.garment.seller_id,
    });

    state.jobId     = job_id;
    state.pollAbort = new AbortController();

    const data = await pollResult(job_id, {
      onProgress: pct => setProgress(pct),
      signal:     state.pollAbort.signal,
    });

    state.resultUrl = data.result_url;
    renderResult();
  } catch (e) {
    if (e.name === 'AbortError') return;
    if (e.message === 'offline_queued') {
      showError(
        'Connexion perdue',
        'Votre photo a été sauvegardée. Reconnectez-vous pour continuer.'
      );
      return;
    }
    showError('Traitement échoué', e.message);
  }
}

function setProgress(pct) {
  $('progress-fill').style.width = `${pct}%`;
  $('progress-pct').textContent  = `${Math.round(pct)}%`;
  $('progress-track').setAttribute('aria-valuenow', pct);
}

// ── Result ────────────────────────────────────────────────────────────────────
function renderResult() {
  const resultAbsUrl = resolveUrl(state.resultUrl);
  $('result-img').src              = resultAbsUrl;
  $('result-garment-name').textContent = state.garment?.name ?? '';

  // Reset submit button pour un prochain essayage
  const btn = $('btn-submit');
  btn.disabled  = false;
  btn.innerHTML = 'Générer l\'essayage <span aria-hidden="true">✨</span>';

  show('result');
}

$('btn-share').addEventListener('click', () => {
  const tryOnUrl = `${location.origin}${location.pathname}${location.search}`;
  shareViaWhatsApp({
    resultImageUrl: resolveUrl(state.resultUrl),
    sellerName:     state.garment?.seller_slug ?? 'le vendeur',
    garmentName:    state.garment?.name ?? '',
    tryOnUrl,
  });
});

$('btn-order').addEventListener('click', () =>
  window.open(state.garment?.meta?.order_url ?? '#', '_blank')
);

$('btn-retry').addEventListener('click', () => {
  state.pollAbort?.abort();
  clearCapture();
  show('capture');
});

// ── Error retry ───────────────────────────────────────────────────────────────
$('btn-error-retry').addEventListener('click', () => init());

// ── Start ─────────────────────────────────────────────────────────────────────
init();
