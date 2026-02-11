const CACHE_NAME = 'seat-dict-v1';
const ASSETS = [
    './',
    './index.html',
    './data.js',
    './manifest.json',
    './icon.svg',
    'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700&family=Noto+Sans+JP:wght@400;500;700&display=swap'
];

// Install event: Cache assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                return cache.addAll(ASSETS);
            })
    );
});

// Activate event: Clean up old caches
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
        })
    );
});

// Fetch event: Serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Cache hit
                if (response) {
                    return response;
                }
                // Network request
                return fetch(event.request).then((networkResponse) => {
                    // Cache new requests dynamically (optional, but good for fonts/images not pre-cached)
                    // Check if valid response
                    if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
                        return networkResponse;
                    }

                    // Clone response for cache
                    const responseToCache = networkResponse.clone();

                    caches.open(CACHE_NAME)
                        .then((cache) => {
                            cache.put(event.request, responseToCache);
                        });

                    return networkResponse;
                });
            })
    );
});
