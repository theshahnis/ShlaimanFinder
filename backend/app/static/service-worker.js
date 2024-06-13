self.addEventListener('install', function(event) {
    event.waitUntil(
      caches.open('shlaiman-cache').then(function(cache) {
        return cache.addAll([
          '/',
          '/static/styles.css',
          '/static/dark-mode.css',
          '/static/images/favicon.ico',
          '/static/images/logo1.png',
          '/static/images/background.png',
          '/static/images/background2.png',
          '/static/images/background3.png',
          '/static/images/background4.png'
        ]);
      })
    );
  });
  
  self.addEventListener('install', function(event) {
    event.waitUntil(
      caches.open(CACHE_NAME)
        .then(function(cache) {
          console.log('Opened cache');
          return cache.addAll(urlsToCache);
        })
    );
  });
  
  self.addEventListener('fetch', function(event) {
    event.respondWith(
      caches.match(event.request)
        .then(function(response) {
          if (response) {
            return response;
          }
          return fetch(event.request);
        }
      )
    );
  });