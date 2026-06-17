// PetFinder Smart Collar — Service Worker
// Versión del caché: incrementar al hacer deploy para forzar actualización
const CACHE_NAME = 'petfinder-v1';

// Recursos estáticos que se cachean al instalar el SW
const STATIC_ASSETS = [
  './dashboard.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  // CDN externas — se cachean en la primera visita
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap',
  'https://cdn.tailwindcss.com?plugins=forms',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js'
];

// INSTALL: pre-cachear assets estáticos
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('[SW] Precacheando assets estáticos');
      // Cachear uno a uno para que un fallo no bloquee todo
      return Promise.allSettled(
        STATIC_ASSETS.map(url => cache.add(url).catch(err => {
          console.warn('[SW] No se pudo cachear:', url, err);
        }))
      );
    }).then(() => self.skipWaiting())
  );
});

// ACTIVATE: borrar cachés viejos
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => {
          console.log('[SW] Eliminando caché viejo:', k);
          return caches.delete(k);
        })
      )
    ).then(() => self.clients.claim())
  );
});

// FETCH: estrategia por tipo de recurso
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Peticiones a Supabase → siempre Network First (datos en tiempo real)
  if (url.hostname.includes('supabase.co')) {
    event.respondWith(networkFirst(event.request));
    return;
  }

  // Assets estáticos → Cache First
  if (
    event.request.destination === 'style' ||
    event.request.destination === 'script' ||
    event.request.destination === 'font'  ||
    event.request.destination === 'image'
  ) {
    event.respondWith(cacheFirst(event.request));
    return;
  }

  // Documento HTML → Network First con fallback a caché
  if (event.request.destination === 'document') {
    event.respondWith(networkFirst(event.request));
    return;
  }

  // Todo lo demás → Network con fallback
  event.respondWith(networkFirst(event.request));
});

// ------- Helpers de estrategia -------

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return new Response('Recurso no disponible sin conexión.', { status: 503 });
  }
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok && request.method === 'GET') {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    if (cached) return cached;
    // Página offline de fallback
    if (request.destination === 'document') {
      return caches.match('./dashboard.html');
    }
    return new Response('Sin conexión.', { status: 503 });
  }
}
