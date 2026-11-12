/* Инглишко на шиш – service worker.
   Кешира цялото приложение при първото отваряне, за да работи после без интернет. */
const VERSION='721d6691ea';
const CACHE='inglishko-'+VERSION;
const ASSETS=["./","index.html","ree/ree.js","manifest.webmanifest","fonts.css","icons/icon-192.png","icons/icon-512.png","icons/icon-maskable-512.png","icons/sc-cards.png","icons/sc-review.png","icons/sc-today.png","fonts/golos-text-cyrillic-400-normal.woff2","fonts/golos-text-cyrillic-500-normal.woff2","fonts/golos-text-cyrillic-600-normal.woff2","fonts/golos-text-cyrillic-700-normal.woff2","fonts/golos-text-cyrillic-ext-400-normal.woff2","fonts/golos-text-cyrillic-ext-500-normal.woff2","fonts/golos-text-cyrillic-ext-600-normal.woff2","fonts/golos-text-cyrillic-ext-700-normal.woff2","fonts/golos-text-latin-400-normal.woff2","fonts/golos-text-latin-500-normal.woff2","fonts/golos-text-latin-600-normal.woff2","fonts/golos-text-latin-700-normal.woff2","fonts/golos-text-latin-ext-400-normal.woff2","fonts/golos-text-latin-ext-500-normal.woff2","fonts/golos-text-latin-ext-600-normal.woff2","fonts/golos-text-latin-ext-700-normal.woff2","fonts/jetbrains-mono-cyrillic-500-normal.woff2","fonts/jetbrains-mono-cyrillic-ext-500-normal.woff2","fonts/jetbrains-mono-latin-500-normal.woff2","fonts/jetbrains-mono-latin-ext-500-normal.woff2","fonts/unbounded-cyrillic-500-normal.woff2","fonts/unbounded-cyrillic-700-normal.woff2","fonts/unbounded-cyrillic-ext-500-normal.woff2","fonts/unbounded-cyrillic-ext-700-normal.woff2","fonts/unbounded-latin-500-normal.woff2","fonts/unbounded-latin-700-normal.woff2","fonts/unbounded-latin-ext-500-normal.woff2","fonts/unbounded-latin-ext-700-normal.woff2"];

self.addEventListener('install',e=>{
  e.waitUntil((async()=>{
    const c=await caches.open(CACHE);
    // add one by one: a single failure must not abandon the whole install
    await Promise.all(ASSETS.map(u=>c.add(new Request(u,{cache:'reload'})).catch(()=>{})));
  })());
});

self.addEventListener('activate',e=>{
  e.waitUntil((async()=>{
    const keys=await caches.keys();
    await Promise.all(keys.filter(k=>k.startsWith('inglishko-')&&k!==CACHE).map(k=>caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('message',e=>{if(e.data==='skipWaiting')self.skipWaiting()});

self.addEventListener('fetch',e=>{
  const req=e.request;
  if(req.method!=='GET')return;
  const url=new URL(req.url);
  if(url.origin!==self.location.origin)return;   // nothing external to serve
  // page loads: cached app first, so opening offline works
  if(req.mode==='navigate'){
    e.respondWith((async()=>{
      const c=await caches.open(CACHE);
      return (await c.match('index.html'))||(await c.match('./'))||fetch(req).catch(()=>new Response(
        '<meta charset=utf-8><p style="font:16px sans-serif;padding:24px">Приложението още не е запазено за offline. Отворете го веднъж с интернет.',
        {headers:{'Content-Type':'text/html; charset=utf-8'}}));
    })());
    return;
  }
  // everything else: cache first, then network, and keep what the network gave
  e.respondWith((async()=>{
    const c=await caches.open(CACHE);
    const hit=await c.match(req,{ignoreSearch:true});
    if(hit)return hit;
    try{
      const res=await fetch(req);
      if(res&&res.ok&&res.type==='basic')c.put(req,res.clone());
      return res;
    }catch(err){
      return hit||Response.error();
    }
  })());
});
