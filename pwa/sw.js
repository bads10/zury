const CACHE = 'zury-v1';
const STATIC = [
  '/index.html',
  '/app.js',
  '/api.js',
  '/styles/main.css',
  '/manifest.json',
  '/icon.svg',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c =>
      Promise.allSettled(STATIC.map(url => c.add(url)))
    )
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE).map(k => caches.delete(k))
      ))
      .then(() => clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const { origin, pathname } = new URL(e.request.url);
  const own = origin === self.location.origin;

  if (own && pathname.startsWith('/api/v1/media/')) {
    e.respondWith(cacheFirst(e.request));
  } else if (own && pathname.startsWith('/api/')) {
    e.respondWith(networkFirst(e.request));
  } else if (own) {
    e.respondWith(cacheFirst(e.request));
  }
  // cross-origin API calls (dev: different port) → browser handles natively
});

async function cacheFirst(req) {
  const hit = await caches.match(req);
  if (hit) return hit;
  const res = await fetch(req);
  if (res.ok) (await caches.open(CACHE)).put(req, res.clone());
  return res;
}

async function networkFirst(req) {
  try {
    const res = await fetch(req);
    if (res.ok) (await caches.open(CACHE)).put(req, res.clone());
    return res;
  } catch {
    return caches.match(req);
  }
}
