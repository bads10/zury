export const API_BASE =
  (window.ZURY_CONFIG && window.ZURY_CONFIG.API_BASE) || 'http://localhost:8000';

// ── Garment info ──────────────────────────────────────────────────────────────

export async function fetchGarment(sellerSlug, garmentId) {
  const res = await fetch(
    `${API_BASE}/api/v1/sellers/${encodeURIComponent(sellerSlug)}/garment/${encodeURIComponent(garmentId)}`
  );
  if (res.status === 404)
    throw Object.assign(new Error('Garment not found'), { code: 'NOT_FOUND' });
  if (!res.ok)
    throw new Error(`Server error (${res.status})`);
  return res.json();
}

// ── Image compression ─────────────────────────────────────────────────────────

export function compressImage(file, maxDim = 768, quality = 0.75) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const blobUrl = URL.createObjectURL(file);

    img.onload = () => {
      URL.revokeObjectURL(blobUrl);
      let { width, height } = img;
      if (width > maxDim || height > maxDim) {
        const r = maxDim / Math.max(width, height);
        width  = Math.round(width  * r);
        height = Math.round(height * r);
      }
      const canvas = document.createElement('canvas');
      canvas.width  = width;
      canvas.height = height;
      canvas.getContext('2d').drawImage(img, 0, 0, width, height);
      canvas.toBlob(
        blob => resolve(new File([blob], 'selfie.jpg', { type: 'image/jpeg' })),
        'image/jpeg',
        quality
      );
    };

    img.onerror = () => {
      URL.revokeObjectURL(blobUrl);
      reject(new Error('Could not read image'));
    };
    img.src = blobUrl;
  });
}

// ── Try-on API ────────────────────────────────────────────────────────────────

export async function requestTryOn({ selfie, garmentId, sellerId, fitzpatrick }) {
  const form = new FormData();
  form.append('selfie',      selfie, 'selfie.jpg');
  form.append('garment_id',  garmentId);
  form.append('seller_id',   sellerId);
  form.append('fitzpatrick', String(fitzpatrick));

  const res = await fetch(`${API_BASE}/api/v1/tryon`, { method: 'POST', body: form });
  if (!res.ok) throw new Error('Upload failed — please try again');
  return res.json(); // { job_id, estimated_seconds }
}

// ── Polling with exponential backoff ──────────────────────────────────────────

export async function pollResult(jobId, { onProgress, signal } = {}) {
  let delay = 1300;
  const MAX    = 3000;
  const FACTOR = 1.3;

  const sleep = ms => new Promise((res, rej) => {
    const t = setTimeout(res, ms);
    signal?.addEventListener(
      'abort',
      () => { clearTimeout(t); rej(new DOMException('Aborted', 'AbortError')); },
      { once: true }
    );
  });

  for (;;) {
    if (signal?.aborted) throw new DOMException('Polling aborted', 'AbortError');

    const r    = await fetch(`${API_BASE}/api/v1/tryon/${encodeURIComponent(jobId)}`, { signal });
    const data = await r.json();

    onProgress?.(data.progress ?? 0, data.status);

    if (data.status === 'done')   return data;
    if (data.status === 'failed') throw new Error('Processing failed — please try again');

    await sleep(delay);
    delay = Math.min(delay * FACTOR, MAX);
  }
}

// ── Share ─────────────────────────────────────────────────────────────────────

export async function shareViaWhatsApp(resultUrl, garmentName) {
  const fullUrl = `${API_BASE}${resultUrl}`;

  try {
    const res  = await fetch(fullUrl);
    const blob = await res.blob();
    const file = new File([blob], 'zury-tryon.png', { type: 'image/png' });

    if (navigator.share && navigator.canShare?.({ files: [file] })) {
      await navigator.share({
        title: 'Mon essayage Zury',
        text:  `✨ Regardez comment je porte "${garmentName}" avec Zury !`,
        files: [file],
      });
      return;
    }
  } catch (e) {
    if (e.name === 'AbortError') return;
  }

  const appUrl = (window.ZURY_CONFIG?.baseUrl || 'https://zury.africa') + window.location.search;
  const msg = encodeURIComponent(
    `✨ Regardez mon essayage virtuel avec Zury !\n${appUrl}`
  );
  window.open(`https://wa.me/?text=${msg}`, '_blank');
}
