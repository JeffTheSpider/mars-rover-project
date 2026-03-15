// Mars Rover PWA — Service Worker v1
// Network-first strategy (proven pattern from Hub project)

const CACHE_VERSION = 'rover-v1';
const CACHE_FILES = [
    '/',
    '/index.html',
    '/manifest.json',
    '/css/styles.css',
    '/js/app.js',
    '/js/connection.js',
    '/js/controls.js',
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
