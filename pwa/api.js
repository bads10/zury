// ─── api.js — Client API Try-On ────────────────────────────────────
// Conçu pour les contraintes réseau africaines :
//   - Timeout 30s (réseau 3G Lagos peut être lent)
//   - Retry automatique 2x sur erreur réseau
//   - Background Sync si ServiceWorker disponible
//   - Compression AVIF→WebP→JPEG côté client avant upload

export const API_BASE =
  (window.ZURY_CONFIG && window.ZURY_CONFIG.API_BASE) || 'https://api.zury.africa';

const MAX_UPLOAD_KB = 800;

// ─── Info vêtement ─────────────────────────────────────────────────
export async function fetchGarment(sellerSlug, garmentId) {
  const res = await fetch(
    `${API_BASE}/api/v1/sellers/${encodeURIComponent(sellerSlug)}/garment/${encodeURIComponent(garmentId)}`
  );
  if (res.status === 404)
    throw Object.assign(new Error('Vêtement introuvable'), { code: 'NOT_FOUND' });
  if (!res.ok)
    throw new Error(`Erreur serveur (${res.status})`);
  return res.json();
}

// ─── Compression image avant upload ────────────────────────────────
// Cascade AVIF → WebP → JPEG jusqu'à atteindre < MAX_UPLOAD_KB
export async function compressImage(file, maxPx = 768) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const url = URL.createObjectURL(file);
    img.onload = () => {
      // Ratio pour respecter max 768×1024 (portrait)
      const ratio = Math.min(maxPx / img.width, (maxPx * 1.33) / img.height, 1);
      const canvas = document.createElement('canvas');
      canvas.width  = Math.round(img.width  * ratio);
      canvas.height = Math.round(img.height * ratio);
      canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(url);

      // Détecte le meilleur format supporté
      const avifTest = canvas.toDataURL('image/avif');
      const format = avifTest.startsWith('data:image/avif') ? 'image/avif' : 'image/webp';
      let quality = 0.80;

      const tryCompress = () => {
        const dataUrl = canvas.toDataURL(format, quality);
        const bytes = Math.round((dataUrl.length * 3) / 4);
        if (bytes <= MAX_UPLOAD_KB * 1024 || quality < 0.35) {
          resolve(dataUrl);
        } else {
          quality -= 0.10;
          tryCompress();
        }
      };
      tryCompress();
    };
    img.onerror = reject;
    img.src = url;
  });
}

// ─── Détection Fitzpatrick (ITA simplifié) ──────────────────────────
// Échantillonne la zone visage (top 30%) pour estimer le ton de peau
export function detectFitzpatrick(imageDataUrl) {
  return new Promise(resolve => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = canvas.height = 64;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 12, 64, 40, 0, 0, 64, 64); // zone visage centrale
      const data = ctx.getImageData(0, 0, 64, 64).data;

      let rSum = 0, gSum = 0, bSum = 0, count = 0;
      for (let i = 0; i < data.length; i += 4) {
        if (data[i + 3] < 128) continue; // skip pixels transparents
        rSum += data[i]; gSum += data[i + 1]; bSum += data[i + 2];
        count++;
      }
      if (count === 0) { resolve(4); return; } // défaut : Fitzpatrick IV

      const r = rSum / count, g = gSum / count, b = bSum / count;
      const L = 0.299 * r + 0.587 * g + 0.114 * b;
      const ita = Math.atan2(L - 127, b - 128) * (180 / Math.PI);

      let zone;
      if      (ita > 55)  zone = 1;
      else if (ita > 41)  zone = 2;
      else if (ita > 28)  zone = 3;
      else if (ita > 10)  zone = 4;
      else if (ita > -30) zone = 5;
      else                zone = 6;
      resolve(zone);
    };
    img.src = imageDataUrl;
  });
}

// ─── Upload + lancement try-on ─────────────────────────────────────
export async function requestTryOn({ selfieDataUrl, garmentId, sellerId }) {
  const fitzpatrick = await detectFitzpatrick(selfieDataUrl);

  const blob = dataUrlToBlob(selfieDataUrl);
  const form = new FormData();
  form.append('selfie',      blob, 'selfie.jpg');
  form.append('garment_id',  garmentId);
  form.append('seller_id',   sellerId);
  form.append('fitzpatrick', fitzpatrick);
  form.append('client_ts',   Date.now());

  const data = await fetchWithRetry(`${API_BASE}/api/v1/tryon`, { method: 'POST', body: form });
  return data; // { job_id, estimated_seconds }
}

// ─── Polling jusqu'au résultat ─────────────────────────────────────
export async function pollResult(jobId, { onProgress, signal } = {}, maxWait = 30000) {
  const start = Date.now();
  let delay = 1000;
  const FACTOR = 1.3;
  const MAX_DELAY = 3000;

  const sleep = ms => new Promise((res, rej) => {
    const t = setTimeout(res, ms);
    signal?.addEventListener(
      'abort',
      () => { clearTimeout(t); rej(new DOMException('Polling annulé', 'AbortError')); },
      { once: true }
    );
  });

  for (;;) {
    if (signal?.aborted) throw new DOMException('Polling annulé', 'AbortError');
    if (Date.now() - start > maxWait) throw new Error('timeout');

    const result = await fetchWithRetry(
      `${API_BASE}/api/v1/tryon/${encodeURIComponent(jobId)}`,
      { signal }
    );

    onProgress?.(result.progress ?? 0, result.status);

    if (result.status === 'done')   return result;
    if (result.status === 'failed') throw new Error(result.error || 'Inférence échouée');

    await sleep(delay);
    delay = Math.min(delay * FACTOR, MAX_DELAY);
  }
}

// ─── Helpers réseau ────────────────────────────────────────────────

async function fetchWithRetry(url, options = {}, retries = 2) {
  const controller = new AbortController();
  // Fusionne l'AbortSignal externe avec le timeout interne
  const timeout = setTimeout(() => controller.abort(), 30000);
  const signal = options.signal
    ? anySignal([options.signal, controller.signal])
    : controller.signal;

  try {
    const res = await fetch(url, { ...options, signal });
    clearTimeout(timeout);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch (err) {
    clearTimeout(timeout);
    if (retries > 0 && err.name !== 'AbortError') {
      await new Promise(r => setTimeout(r, 800));
      return fetchWithRetry(url, options, retries - 1);
    }
    // Background Sync si upload POST échoue hors ligne
    if (
      'serviceWorker' in navigator &&
      'SyncManager' in window &&
      options.method === 'POST'
    ) {
      const reg = await navigator.serviceWorker.ready;
      await reg.sync.register('tryon-upload-retry');
      throw new Error('offline_queued');
    }
    throw err;
  }
}

// Combine plusieurs AbortSignals (polyfill léger)
function anySignal(signals) {
  const controller = new AbortController();
  for (const s of signals) {
    if (s.aborted) { controller.abort(); break; }
    s.addEventListener('abort', () => controller.abort(), { once: true });
  }
  return controller.signal;
}

function dataUrlToBlob(dataUrl) {
  const [header, data] = dataUrl.split(',');
  const mime = header.match(/:(.*?);/)[1];
  const binary = atob(data);
  const arr = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) arr[i] = binary.charCodeAt(i);
  return new Blob([arr], { type: mime });
}

// ─── Enregistrement Service Worker ─────────────────────────────────
export async function registerSW() {
  if (!('serviceWorker' in navigator)) return;
  try {
    const reg = await navigator.serviceWorker.register('/sw.js', { scope: '/' });
    reg.addEventListener('updatefound', () => {
      const newSW = reg.installing;
      newSW.addEventListener('statechange', () => {
        if (newSW.state === 'installed' && navigator.serviceWorker.controller) {
          window.dispatchEvent(new CustomEvent('sw-update-available'));
        }
      });
    });
  } catch (err) {
    console.warn('SW registration failed:', err);
  }
}

// ─── Partage WhatsApp ───────────────────────────────────────────────
export async function shareViaWhatsApp({ resultImageUrl, sellerName, garmentName, tryOnUrl }) {
  const text = `J'ai essayé "${garmentName}" chez ${sellerName} ✨\nEssaie toi aussi : ${tryOnUrl}`;

  if (navigator.share) {
    try {
      if (resultImageUrl) {
        const blob = await fetch(resultImageUrl).then(r => r.blob()).catch(() => null);
        if (blob) {
          const file = new File([blob], 'mon-look.jpg', { type: 'image/jpeg' });
          if (navigator.canShare?.({ files: [file] })) {
            await navigator.share({ files: [file], text, title: garmentName });
            return { method: 'native-share-with-image' };
          }
        }
      }
      await navigator.share({ text, title: garmentName });
      return { method: 'native-share' };
    } catch (e) {
      if (e.name !== 'AbortError') console.warn('Share failed:', e);
    }
  }

  // Fallback wa.me
  window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
  return { method: 'whatsapp-link' };
}
