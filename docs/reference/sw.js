/**
 * Service Worker for p4lottery Frontier Synthesis Lab (PWA Offline Cockpit)
 * Provides cache-first offline capability for all local visualizers and simulators.
 */

const CACHE_NAME = 'p4lottery-lab-v1';
const ASSETS_TO_CACHE = [
  './frontier-synthesis-lab.html',
  './manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  // Offline-first strategy
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request).catch(() => {
        // Fallback to main page if navigation request fails
        if (event.request.mode === 'navigate') {
          return caches.match('./frontier-synthesis-lab.html');
        }
      });
    })
  );
});
