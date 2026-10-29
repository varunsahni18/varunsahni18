(()=>{
 const themes={mint:'Mint',cobalt:'Cobalt',paper:'Paper','new-york':'New York'};
 const params=new URLSearchParams(location.search);
 const requested=params.get('theme')||document.documentElement.dataset.defaultTheme||'mint';
 const theme=Object.hasOwn(themes,requested)?requested:'mint';
 document.documentElement.dataset.theme=theme;
 document.addEventListener('DOMContentLoaded',()=>{
  const preview=params.has('preview');
  const themeColors={mint:'#080d11',cobalt:'#0b1021',paper:'#f5f1e8','new-york':'#f3f1e9'};
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content',themeColors[theme]);
  if(preview)document.documentElement.classList.add('theme-preview');
  function decorateLink(a){
   const url=new URL(a.getAttribute('href'),location.href);
   if(url.origin!==location.origin||/\.[a-z0-9]+$/i.test(url.pathname)||!url.pathname.endsWith('/')||a.hasAttribute('data-theme-link'))return;
   if(url.pathname==='/new-york/')url.searchParams.set('theme','new-york');
   else if(theme!=='mint')url.searchParams.set('theme',theme);
   a.href=url.pathname+url.search+url.hash;
  }
  for(const a of document.querySelectorAll('a[href]'))decorateLink(a);
  document.addEventListener('click',event=>{const a=event.target.closest('a[href]');if(a)decorateLink(a);},true);
  if(!preview&&location.pathname!=='/themes/'){
   const bar=document.createElement('nav');bar.className='theme-picker';bar.setAttribute('aria-label','Website appearance');
   const label=document.createElement('label');label.textContent='Theme ';
   const select=document.createElement('select');select.setAttribute('aria-label','Choose website theme');
   for(const [key,name] of Object.entries(themes)){const o=document.createElement('option');o.value=key;o.textContent=name;o.selected=key===theme;select.append(o);}
   label.append(select);bar.append(label);
   const compare=document.createElement('a');compare.href='/themes/';compare.textContent='Compare';bar.append(compare);document.body.append(bar);
   select.addEventListener('change',()=>{const url=new URL(location.href);url.searchParams.delete('preview');url.searchParams.set('theme',select.value);if(url.pathname==='/new-york/'&&select.value!=='new-york')url.pathname='/';location.href=url.href;});
  }
  const frames=[...document.querySelectorAll('.theme-frame')];
  for(const frame of frames)new ResizeObserver(entries=>{const scale=entries[0].contentRect.width/1280;frame.style.setProperty('--preview-scale',scale);frame.style.height=(800*scale)+'px';}).observe(frame);
  if(theme==='new-york'){
   const hero=document.querySelector('.hero-story');
   if(hero){const line=document.createElement('p');line.className='nyc-edition';line.textContent='NEW YORK, NY · NYU COURANT';hero.prepend(line);}
   const stage=document.querySelector('.orb-stage');
   if(stage){const city=document.createElement('div');city.className='nyc-skyline';city.setAttribute('aria-hidden','true');stage.prepend(city);}
  }
 });
})();
