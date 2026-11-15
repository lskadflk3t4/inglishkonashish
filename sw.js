/* Инглишко на шиш – service worker.
   Кодът на приложението (index.html, .js, .css) се взема първо от интернет,
   за да виждат всички веднага новата версия; без интернет се отваря запазеното копие.
   Шрифтове, икони и аудио се пазят в кеша. Не е нужно да се сменя VERSION при ново качване. */
const VERSION='4125e56fc8';
const CACHE='inglishko-'+VERSION;
const ASSETS=["./","index.html","ree/ree.js","manifest.webmanifest","fonts.css","icons/icon-192.png","icons/icon-512.png","icons/icon-maskable-512.png","icons/sc-cards.png","icons/sc-review.png","icons/sc-today.png","fonts/golos-text-cyrillic-400-normal.woff2","fonts/golos-text-cyrillic-500-normal.woff2","fonts/golos-text-cyrillic-600-normal.woff2","fonts/golos-text-cyrillic-700-normal.woff2","fonts/golos-text-cyrillic-ext-400-normal.woff2","fonts/golos-text-cyrillic-ext-500-normal.woff2","fonts/golos-text-cyrillic-ext-600-normal.woff2","fonts/golos-text-cyrillic-ext-700-normal.woff2","fonts/golos-text-latin-400-normal.woff2","fonts/golos-text-latin-500-normal.woff2","fonts/golos-text-latin-600-normal.woff2","fonts/golos-text-latin-700-normal.woff2","fonts/golos-text-latin-ext-400-normal.woff2","fonts/golos-text-latin-ext-500-normal.woff2","fonts/golos-text-latin-ext-600-normal.woff2","fonts/golos-text-latin-ext-700-normal.woff2","fonts/jetbrains-mono-cyrillic-500-normal.woff2","fonts/jetbrains-mono-cyrillic-ext-500-normal.woff2","fonts/jetbrains-mono-latin-500-normal.woff2","fonts/jetbrains-mono-latin-ext-500-normal.woff2","fonts/unbounded-cyrillic-500-normal.woff2","fonts/unbounded-cyrillic-700-normal.woff2","fonts/unbounded-cyrillic-ext-500-normal.woff2","fonts/unbounded-cyrillic-ext-700-normal.woff2","fonts/unbounded-latin-500-normal.woff2","fonts/unbounded-latin-700-normal.woff2","fonts/unbounded-latin-ext-500-normal.woff2","fonts/unbounded-latin-ext-700-normal.woff2"];

self.addEventListener('install',e=>{
  self.skipWaiting();
  e.waitUntil((async()=>{
    const c=await caches.open(CACHE);
    await Promise.all(ASSETS.map(u=>c.add(new Request(u,{cache:'reload'})).catch(()=>{})));
  })());
});

self.addEventListener('activate',e=>{
  e.waitUntil((async()=>{
    const keys=await caches.keys();
    const old=keys.filter(k=>k.startsWith('inglishko-')&&k!==CACHE);
    // keep cached audio from the old version so it still works offline
    for(const k of old){
      try{const oc=await caches.open(k),nc=await caches.open(CACHE);
        for(const r of await oc.keys()){if(/\.mp3$/.test(new URL(r.url).pathname)&&!(await nc.match(r)))await nc.put(r,await oc.match(r))}}catch(_){}
      await caches.delete(k);
    }
    await self.clients.claim();
    // phones stuck on an old copy: reload open windows once onto the new version
    if(old.length){
      for(const cl of await self.clients.matchAll({type:'window'})){try{cl.navigate(cl.url)}catch(_){}}
    }
  })());
});

self.addEventListener('message',e=>{if(e.data==='skipWaiting')self.skipWaiting()});

const isCode=p=>p.endsWith('/')||/\.(html|js|css|webmanifest)$/.test(p);

async function networkFirst(req,key){
  const c=await caches.open(CACHE);
  try{
    const res=await Promise.race([
      fetch(req.url,{cache:'no-cache',credentials:'same-origin'}),
      new Promise((_,rej)=>setTimeout(()=>rej(new Error('slow')),6000))
    ]);
    if(res&&res.ok){c.put(key||req,res.clone());return res}
    throw new Error('bad');
  }catch(err){
    return (await c.match(key||req,{ignoreSearch:true}))||(await c.match('./'))||(req.mode==='navigate'?new Response(
      '<meta charset=utf-8><p style="font:16px sans-serif;padding:24px">Приложението още не е запазено за offline. Отворете го веднъж с интернет.',
      {headers:{'Content-Type':'text/html; charset=utf-8'}}):Response.error());
  }
}

self.addEventListener('fetch',e=>{
  const req=e.request;
  if(req.method!=='GET')return;
  const url=new URL(req.url);
  if(url.origin!==self.location.origin)return;
  if(req.mode==='navigate'){e.respondWith(networkFirst(req,'index.html'));return}
  if(isCode(url.pathname)){e.respondWith(networkFirst(req));return}
  // fonts, icons, audio: cache first
  e.respondWith((async()=>{
    const c=await caches.open(CACHE);
    const hit=await c.match(req,{ignoreSearch:true});
    if(hit)return hit;
    try{
      const res=await fetch(req);
      if(res&&res.ok&&res.type==='basic')c.put(req,res.clone());
      return res;
    }catch(err){return Response.error()}
  })());
});
