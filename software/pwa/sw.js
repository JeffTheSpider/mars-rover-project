// Mars Rover PWA — Service Worker v2
// Network-first strategy (proven pattern from Hub project)
// Bump CACHE_VERSION when changing index.html

const CACHE_VERSION = 'rover-v3';
const CACHE_FILES = [
    '/',
    '/index.html',
    '/manifest.json',
];

// Install — pre-cache core assets
self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open(CACHE_VERSION)
            .then(cache => cache.addAll(CACHE_FILES))
            .then(() => self.skipWaiting())
    );
});

// Activate — clean old caches
self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys.filter(k => k !== CACHE_VERSION)
                    .map(k => caches.delete(k))
            )
        ).then(() => self.clients.claim())
    );
});

// Fetch — network-first, fall back to cache
self.addEventListener('fetch', (e) => {
    // Skip WebSocket and non-GET requests
    if (e.request.url.startsWith('ws') || e.request.method !== 'GET') return;

    // Skip CDN resources (Leaflet, Google Fonts) from caching
    const url = new URL(e.request.url);
    if (url.hostname !== location.hostname) {
        e.respondWith(
            fetch(e.request).catch(() => caches.match(e.request))
        );
        return;
    }

    e.respondWith(
        fetch(e.request)
            .then(response => {
                // Cache successful responses
                if (response.ok) {
                    const clone = response.clone();
                    caches.open(CACHE_VERSION).then(c => c.put(e.request, clone));
                }
                return response;
            })
            .catch(() => caches.match(e.request))
    );
});
