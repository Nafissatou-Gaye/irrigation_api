const CACHE = "irrigation-v1";
const ASSETS = ["/dashboard", "/manifest.json"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", e => {
  e.waitUntil(clients.claim());
});

self.addEventListener("fetch", e => {
  // API calls : toujours en réseau (données temps réel)
  if (e.request.url.includes("/status") ||
      e.request.url.includes("/history") ||
      e.request.url.includes("/manual") ||
      e.request.url.includes("/decision")) {
    e.respondWith(fetch(e.request));
    return;
  }
  // Autres ressources : cache en priorité
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request))
  );
});
