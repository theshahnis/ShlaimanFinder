const CACHE_NAME = 'shlaiman-cache-v3';
const urlsToCache = [
  '/',
  '/profile/',
  '/profile',
  '/show',
  '/show/',
  '/show/api/shows',
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
  '/soundboard',
  '/soundboard/',
  '/home',
  '/home/',
  '/fallback.html',
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
  '/static/storage.js',
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

self.addEventListener('install', event => {
  console.log('Service Worker: Installing');
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('Opened cache');
      return cache.addAll(urlsToCache).then(() => {
        console.log('All resources cached successfully');
      }).catch(error => {
        console.error('Failed to cache resources:', error);
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener('fetch', event => {
  console.log('Service Worker: Fetching', event.request.url);
  event.respondWith(
    fetch(event.request).then(response => {
      if (!response || response.status !== 200 || response.type !== 'basic') {
        return response;
      }

      const responseToCache = response.clone();
      caches.open(CACHE_NAME).then(cache => {
        console.log('Caching new resource', event.request.url);
        cache.put(event.request, responseToCache);
      });

      return response;
    }).catch(() => {
      return caches.match(event.request).then(response => {
        return response || caches.match('/fallback.html');
      });
    })
  );
});

self.addEventListener('activate', event => {
  console.log('Service Worker: Activating');
  const cacheWhitelist = [CACHE_NAME];

  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (!cacheWhitelist.includes(cacheName)) {
            console.log('Deleting old cache', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});