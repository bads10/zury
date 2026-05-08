// ─── Service Worker — Try-On PWA ─────────────────────────────────
// Stratégie Africa-first :
//   - Cache agressif des assets statiques (garment images, fonts)
//   - Background sync pour les uploads en cas de déconnexion
//   - Fallback offline avec page de retry

const CACHE_VERSION = 'tryon-v2';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const IMAGE_CACHE  = `${CACHE_VERSION}-images`;

// Assets mis en cache à l'installation
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/app.js',
  '/api.js',
  '/manifest.json',
  '/icon.svg',
  '/styles/main.css',
  // Fonts depuis CDN (pré-cachées)
  'https://cdn.jsdelivr.net/npm/@fontsource/playfair-display@5/500.css',
  'https://cdn.jsdelivr.net/npm/@fontsource/dm-sans@5/400.css',
];

// ─── Installation : pré-cache statique ───────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// ─── Activation : purge des anciens caches ────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(k => k.startsWith('tryon-') && k !== STATIC_CACHE && k !== IMAGE_CACHE)
          .map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

// ─── Fetch : stratégie par type de ressource ─────────────────────
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // API calls → network only, pas de cache
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkOnly(request));
    return;
  }

  // Garment images + résultats try-on → Cache-First (changent rarement)
  if (
    url.pathname.startsWith('/api/v1/media/') ||
    url.pathname.endsWith('.avif') ||
    url.pathname.endsWith('.webp')
  ) {
    event.respondWith(cacheFirst(request, IMAGE_CACHE));
    return;
  }

  // Fonts CDN → Stale-While-Revalidate
  if (url.hostname.includes('jsdelivr.net')) {
    event.respondWith(staleWhileRevalidate(request, STATIC_CACHE));
    return;
  }

  // App shell → Network-First avec fallback cache
  event.respondWith(networkFirst(request, STATIC_CACHE));
});

// ─── Stratégies de cache ─────────────────────────────────────────

async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (response.ok) {
    const cache = await caches.open(cacheName);
    cache.put(request, response.clone());
  }
  return response;
}

async function networkFirst(request, cacheName) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    return cached || offlineFallback();
  }
}

async function staleWhileRevalidate(request, cacheName) {
  const cached = await caches.match(request);
  const fetchPromise = fetch(request).then(response => {
    if (response.ok) {
      caches.open(cacheName).then(c => c.put(request, response.clone()));
    }
    return response;
  }).catch(() => cached);
  return cached || fetchPromise;
}

async function networkOnly(request) {
  try {
    return await fetch(request);
  } catch {
    return new Response(
      JSON.stringify({ error: 'offline', message: 'Connexion indisponible. Réessayez.' }),
      { status: 503, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

function offlineFallback() {
  return new Response(`
    <!DOCTYPE html>
    <html lang="fr">
    <head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Hors ligne</title>
    <style>body{background:#150A03;color:#F0E6D3;font-family:sans-serif;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;padding:24px;text-align:center}button{background:#D4A843;color:#150A03;border:none;border-radius:12px;padding:14px 28px;font-size:15px;cursor:pointer;margin-top:24px}</style></head>
    <body>
      <div style="font-size:48px">📶</div>
      <h2 style="font-size:20px;margin:16px 0 8px">Connexion perdue</h2>
      <p style="color:#8A7560;font-size:14px">Vérifiez votre réseau et réessayez.</p>
      <button onclick="location.reload()">Réessayer</button>
    </body></html>
  `, { headers: { 'Content-Type': 'text/html' } });
}

// ─── Background Sync : upload différé si déconnexion ─────────────
self.addEventListener('sync', event => {
  if (event.tag === 'tryon-upload-retry') {
    event.waitUntil(retrySyncedUploads());
  }
});

async function retrySyncedUploads() {
  const clients = await self.clients.matchAll();
  clients.forEach(client => {
    client.postMessage({ type: 'SYNC_COMPLETE', tag: 'tryon-upload-retry' });
  });
}

// ─── Push notifications (phase 2) ────────────────────────────────
self.addEventListener('push', event => {
  if (!event.data) return;
  const data = event.data.json();
  event.waitUntil(
    self.registration.showNotification(data.title || 'Votre essayage est prêt !', {
      body: data.body || 'Cliquez pour voir le résultat',
      icon: '/icons/icon-192.png',
      badge: '/icons/badge-72.png',
      data: { url: data.url || '/' },
      actions: [
        { action: 'view', title: 'Voir mon look' },
        { action: 'share', title: 'Partager' },
      ],
    })
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  const url = event.notification.data?.url || '/';
  event.waitUntil(
    self.clients.matchAll({ type: 'window' }).then(clients => {
      const existing = clients.find(c => c.url === url);
      if (existing) return existing.focus();
      return self.clients.openWindow(url);
    })
  );
});
