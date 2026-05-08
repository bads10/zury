import {
  fetchGarment, compressImage, requestTryOn, pollResult, shareViaWhatsApp, API_BASE
} from './api.js';

// ── DOM helpers ───────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

// ── Shared state ──────────────────────────────────────────────────────────────
const state = {
  sellerSlug:  null,
  garmentId:   null,
  garment:     null,
  selfie:      null,   // File (original, before compression)
  fitzpatrick: 3,
  jobId:       null,
  resultUrl:   null,
  pollAbort:   null,   // AbortController
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

// ── Theme toggle ──────────────────────────────────────────────────────────────
(function initTheme() {
  const root  = document.documentElement;
  const saved = localStorage.getItem('zury-theme');
  if (saved) root.setAttribute('data-theme', saved);

  $('btn-theme').addEventListener('click', () => {
    const current = root.getAttribute('data-theme');
    const isDark  = current === 'dark' ||
                    (!current && window.matchMedia('(prefers-color-scheme: dark)').matches);
    const next    = isDark ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('zury-theme', next);
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = next === 'light' ? '#FBF5EC' : '#D4A843';
  });
})();

// ── Boot ──────────────────────────────────────────────────────────────────────
async function init() {
  const p = new URLSearchParams(location.search);
  state.sellerSlug = p.get('seller');
  state.garmentId  = p.get('garment');

  if (!state.sellerSlug || !state.garmentId) {
    return showError(
      'Paramètres manquants',
      'Ajoutez ?seller=<slug>&garment=<id> à l’URL pour charger un vêtement.'
    );
  }

  // Show landing immediately with loading skeleton
  show('landing');
  $('screen-landing').classList.add('is-loading');

  try {
    state.garment = await fetchGarment(state.sellerSlug, state.garmentId);
    populateLanding(state.garment);
    $('screen-landing').classList.remove('is-loading');
  } catch (e) {
    showError('Vêtement introuvable', e.message);
  }
}

// ── URL helper ────────────────────────────────────────────────────────────────
function resolveUrl(url) {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  return `${API_BASE}${url}`;
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
  state.selfie = file;

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
  state.selfie = null;

  $('input-selfie').value  = '';
  $('input-gallery').value = '';
  $('upload-zone').hidden  = false;
  $('preview-wrap').hidden = true;
  $('skin-select').hidden  = true;
  $('submit-wrap').hidden  = true;
}

$('btn-camera').addEventListener('click',  () => $('input-selfie').click());
$('btn-gallery').addEventListener('click', () => $('input-gallery').click());
$('input-selfie').addEventListener('change',  e => setPreview(e.target.files[0]));
$('input-gallery').addEventListener('change', e => setPreview(e.target.files[0]));
$('btn-retake').addEventListener('click', clearCapture);

// ── Capture — skin tone ───────────────────────────────────────────────────────
document.querySelectorAll('.swatch').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.swatch').forEach(b => {
      b.classList.remove('active');
      b.removeAttribute('aria-checked');
    });
    btn.classList.add('active');
    btn.setAttribute('aria-checked', 'true');
    state.fitzpatrick = Number(btn.dataset.fitz);
  });
});

// ── Capture — submit ──────────────────────────────────────────────────────────
$('btn-submit').addEventListener('click', async () => {
  if (!state.selfie) return;
  $('btn-submit').disabled    = true;
  $('btn-submit').textContent = 'Compression…';
  try {
    const compressed = await compressImage(state.selfie);
    await startTryOn(compressed);
  } catch (e) {
    $('btn-submit').disabled    = false;
    $('btn-submit').innerHTML   = 'Générer l’essayage <span aria-hidden="true">✨</span>';
    showError('Erreur d’image', e.message);
  }
});

// ── Processing ────────────────────────────────────────────────────────────────
async function startTryOn(selfieDataUrl) {
  show('processing');
  setProgress(0);

  try {
    const { job_id } = await requestTryOn({
      selfieDataUrl,
      garmentId:   state.garmentId,
      sellerId:    state.garment.seller_id,
      fitzpatrick: state.fitzpatrick,
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
    showError('Traitement échoué', e.message);
  }
}

function setProgress(pct) {
  $('progress-fill').style.width = `${pct}%`;
  $('progress-pct').textContent  = `${pct}%`;
  $('progress-track').setAttribute('aria-valuenow', pct);
}

// ── Result ────────────────────────────────────────────────────────────────────
function renderResult() {
  $('result-img').src              = resolveUrl(state.resultUrl);
  $('result-garment-name').textContent = state.garment?.name ?? '';

  // Reset submit button for next run
  $('btn-submit').disabled  = false;
  $('btn-submit').innerHTML = 'Générer l’essayage <span aria-hidden="true">✨</span>';

  show('result');
}

$('btn-share').addEventListener('click', () =>
  shareViaWhatsApp(state.resultUrl, state.garment?.name ?? '')
);

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

// ── Service worker ────────────────────────────────────────────────────────────
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('./sw.js').catch(() => {});
}

init();
