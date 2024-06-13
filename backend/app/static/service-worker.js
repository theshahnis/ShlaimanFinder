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
          // Add other assets you want to cache here
        ]);
      })
    );
  });
  
  self.addEventListener('fetch', function(event) {
    event.respondWith(
      caches.match(event.request).then(function(response) {
        return response || fetch(event.request);
      })
    );
  });
  