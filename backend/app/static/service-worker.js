const CACHE_NAME = 'shlaiman-cache-v2';
const urlsToCache = [
  '/',
  '/profile/',
  '/profile',
  '/show',
  '/show/',
  '/show/my-shows',
  '/show/my-shows/',
  '/map',
  '/map/',
  '/join_group',
  '/join_group/',
  '/friends',
  '/friends/',
  '/location/test-location',
  '/superuser/',
  '/superuser',
  '/static/fallback.html',
  '/static/styles.css',
  '/static/dark-mode.css',
  '/static/images/favicon.ico',
  '/static/images/logo1.png',
  '/static/images/background.png',
  '/static/images/background2.png',
  '/static/images/background3.png',
  '/static/images/background4.png',
  '/static/images/eagle_logo.png',
  '/static/images/hawk_logo.png',
  '/static/images/buzzard_logo.png',
  '/static/images/vulture_logo.png',
  '/static/shows.js',
  '/static/my_shows.js',
  '/static/map.js',
  '/templates/base.html',
  '/templates/profile.html',
  '/templates/index.html',
  '/templates/shows.html',
  '/templates/my_shows.html',
  '/templates/map.html',
  '/templates/maps.html',
  '/templates/index.html',
  '/templates/friends.html',
  '/templates/auth.html',
  '/templates/join_group.html'
];

// Install event - cache specified URLs and skip waiting to activate the new service worker immediately
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('Opened cache');
      return cache.addAll(urlsToCache);
    })
  );
  self.skipWaiting(); // Forces the waiting service worker to become the active service worker
});

// Fetch event - serve cached content when offline and cache new requests dynamically
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      // Cache hit - return response
      if (response) {
        return response;
      }

      // Not in cache - fetch from network
      return fetch(event.request).then(
        response => {
          // Check if we received a valid response
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Important: Clone the response. A response is a stream
          // and because we want the browser to consume the response
          // as well as the cache consuming the response, we need
          // to clone it so we have two streams.
          const responseToCache = response.clone();

          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });

          return response;
        }
      );
    }).catch(() => {
      return caches.match('/static/fallback.html'); // Serve the fallback page when offline
    })
  );
});

// Activate event - cleanup old caches
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];

  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (!cacheWhitelist.includes(cacheName)) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim(); // Ensures that the service worker takes control of all clients as soon as it activates
});