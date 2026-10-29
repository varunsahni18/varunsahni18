(()=>{
 const themes={mint:'Mint',cobalt:'Cobalt',paper:'Paper','new-york':'New York'};
 const params=new URLSearchParams(location.search);
 const requested=params.get('theme')||document.documentElement.dataset.defaultTheme||'mint';
 const theme=Object.hasOwn(themes,requested)?requested:'mint';
 document.documentElement.dataset.theme=theme;
 document.addEventListener('DOMContentLoaded',()=>{
  const preview=params.has('preview');
  const themeColors={mint:'#080d11',cobalt:'#0b1021',paper:'#f5f1e8','new-york':'#10151b'};
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
   const hero=document.querySelector('.dark-hero'),story=hero?.querySelector('.hero-story');
   if(hero&&story){
    const backdrop=document.createElement('div');backdrop.className='nyc-backdrop';backdrop.setAttribute('aria-hidden','true');
    const photo=document.createElement('img');photo.src='/assets/images/new-york-luca-bravo.jpg';photo.alt='';photo.fetchPriority='high';photo.decoding='async';backdrop.append(photo);hero.prepend(backdrop);
    const line=document.createElement('p');line.className='nyc-edition';line.textContent='BASED IN NEW YORK / NYU COURANT';story.prepend(line);
    const heading=story.querySelector('h1');heading.replaceChildren('Varun',document.createElement('br'),'Sahni');
    const projects=document.createElement('nav');projects.className='nyc-projects';projects.setAttribute('aria-label','Selected projects');
    for(const link of hero.querySelectorAll('.orb-tag')){const item=link.cloneNode(true);item.className='nyc-project-link';item.removeAttribute('data-globe-index');projects.append(item);}story.append(projects);
    const foot=document.createElement('div');foot.className='nyc-hero-footer';
    const place=document.createElement('span');place.textContent='NEW YORK, NY / 40.71° N, 74.01° W';foot.append(place);
    const credit=document.createElement('a');credit.href='https://unsplash.com/photos/_QdFx92MO2U';credit.target='_blank';credit.rel='noopener noreferrer';credit.textContent='Photo: Luca Bravo / Unsplash';foot.append(credit);hero.append(foot);
   }
  }
 });
})();
