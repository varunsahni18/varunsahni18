(() => {
'use strict';
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const menu=$('.menu-button'),rail=$('.rail');
const setMenu=open=>{rail.classList.toggle('open',open);document.body.classList.toggle('nav-open',open);$('.site-canvas').inert=open;menu.setAttribute('aria-expanded',String(open));menu.firstChild.textContent=open?'Close ':'Menu ';$('use',menu).setAttribute('href','/design/icons.svg#'+(open?'close':'menu'));};
menu.addEventListener('click',()=>setMenu(!rail.classList.contains('open')));
addEventListener('keydown',e=>{if(e.key==='Escape'&&rail.classList.contains('open')){setMenu(false);menu.focus();}});
matchMedia('(min-width:'+(document.body.dataset.concept==='dark'?901:document.body.dataset.concept==='minimal'?801:651)+'px)').addEventListener('change',e=>{if(e.matches)setMenu(false);});
const tabs=$$('[role=tab]'),panels=$$('[role=tabpanel]');
function activateTab(tab){tabs.forEach(t=>{const active=t===tab;t.setAttribute('aria-selected',active);t.tabIndex=active?0:-1;});panels.forEach(p=>p.hidden=p.id!==tab.getAttribute('aria-controls'));}
tabs.forEach((tab,i)=>{tab.addEventListener('click',()=>activateTab(tab));tab.addEventListener('keydown',e=>{let n;if(e.key==='ArrowRight')n=(i+1)%tabs.length;if(e.key==='ArrowLeft')n=(i-1+tabs.length)%tabs.length;if(e.key==='Home')n=0;if(e.key==='End')n=tabs.length-1;if(n!==undefined){e.preventDefault();activateTab(tabs[n]);tabs[n].focus();}});});
$$('[data-reel-step]').forEach(b=>b.addEventListener('click',()=>{const current=tabs.findIndex(t=>t.getAttribute('aria-selected')==='true');activateTab(tabs[(current+Number(b.dataset.reelStep)+tabs.length)%tabs.length]);}));
const rows=$$('.work-row'),preview=$('.work-preview'),filters=$$('[data-filter]'),projectInput=$('.project-search input');
function showPreview(row){if(!row)return;rows.forEach(r=>r.classList.toggle('is-active',r===row));const template=$('.project-preview-template',row);if(preview&&template)preview.replaceChildren(template.content.cloneNode(true));}
if(rows.length){let active='All';const params=new URLSearchParams(location.search);if(filters.some(b=>b.dataset.filter===params.get('category')))active=params.get('category');projectInput.value=params.get('q')||'';
 function filter(update=true){const q=projectInput.value.toLowerCase().trim();let visible=[];for(const row of rows){row.hidden=!((active==='All'||row.dataset.group===active)&&row.dataset.name.toLowerCase().includes(q));if(!row.hidden)visible.push(row);}filters.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.filter===active)));$('.results-count').textContent=visible.length+' '+(visible.length===1?'project':'projects')+(active==='All'?'':' / '+active);$('.empty-state').hidden=!!visible.length;if(preview)preview.hidden=!visible.length;if(visible.length)showPreview(visible[0]);if(update){const u=new URL(location);active==='All'?u.searchParams.delete('category'):u.searchParams.set('category',active);q?u.searchParams.set('q',projectInput.value.trim()):u.searchParams.delete('q');history.replaceState(null,'',u);}}
 rows.forEach(row=>{row.addEventListener('pointerenter',()=>showPreview(row));row.addEventListener('focusin',()=>showPreview(row));});filters.forEach(b=>b.addEventListener('click',()=>{active=b.dataset.filter;filter();}));projectInput.addEventListener('input',()=>filter());$('.clear-filters').addEventListener('click',()=>{active='All';projectInput.value='';filter();projectInput.focus();});filter(false);
}
const route=$('.route-map');if(route){const svg=$('.route-line',route),path=$('path',svg);function draw(){const box=route.getBoundingClientRect(),pts=$$('.route-node',route).map(n=>{const b=n.getBoundingClientRect();return{x:b.left-box.left+b.width/2,y:b.top-box.top+b.height/2};});svg.setAttribute('viewBox',`0 0 ${box.width} ${box.height}`);let d=`M${pts[0].x} ${pts[0].y}`;for(let i=1;i<pts.length;i++){const a=pts[i-1],b=pts[i];if(Math.abs(a.y-b.y)<5)d+=` L${b.x} ${b.y}`;else if((route.dataset.vertical==='true'||matchMedia('(max-width:650px)').matches)){const mid=(a.y+b.y)/2;d+=` C${a.x} ${mid},${b.x} ${mid},${b.x} ${b.y}`;}else{const dir=i>1&&a.x<pts[i-2].x?-1:1,turn=dir>0?box.width-8:8,r=Math.min(34,Math.abs(turn-a.x)),inner=turn-dir*r;d+=` L${inner} ${a.y} Q${turn} ${a.y},${turn} ${a.y+r} L${turn} ${b.y-r} Q${turn} ${b.y},${inner} ${b.y} L${b.x} ${b.y}`;}}path.setAttribute('d',d);}new ResizeObserver(draw).observe(route);document.fonts.ready.then(draw);draw();}
const dialog=$('.search-dialog'),search=$('#site-search'),results=$('.search-results');let data,trigger;
async function renderSearch(){try{if(!data){const r=await fetch(document.body.dataset.searchIndex||'/design/search.json');if(!r.ok)throw Error();data=await r.json();}const words=search.value.toLowerCase().trim().split(/\s+/).filter(Boolean),matches=data.filter(d=>words.every(w=>(d.title+' '+d.type).toLowerCase().includes(w))).slice(0,10);results.replaceChildren();if(!matches.length){const p=document.createElement('p');p.className='search-empty';p.textContent='No matches. Try a project name or page.';results.append(p);}for(const item of matches){const a=document.createElement('a');a.className='search-result';a.href=item.path;const d=document.createElement('div'),t=document.createElement('strong'),s=document.createElement('small'),arrow=document.createElement('span');t.textContent=item.title;s.textContent=item.type;arrow.textContent='↗';d.append(t,s);a.append(d,arrow);results.append(a);}}catch{results.textContent='Search is unavailable. All pages are in the navigation.';}}
function openSearch(t){if(dialog.open)return;trigger=t||document.activeElement;setMenu(false);dialog.showModal();search.value='';search.focus();renderSearch();}
$('.search-open').addEventListener('click',e=>openSearch(e.currentTarget));$('.search-close').addEventListener('click',()=>dialog.close());dialog.addEventListener('close',()=>trigger?.focus());search.addEventListener('input',renderSearch);addEventListener('keydown',e=>{if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();openSearch();}});
const media=$('.media-dialog');let imageTrigger;
$$('.image-zoom').forEach(b=>b.addEventListener('click',()=>{imageTrigger=b;const i=document.createElement('img');i.src=b.dataset.image;i.alt=b.dataset.alt;$('.media-content').replaceChildren(i);media.showModal();$('.media-close').focus();}));$('.media-close').addEventListener('click',()=>media.close());media.addEventListener('close',()=>{$('.media-content').replaceChildren();imageTrigger?.focus();});
const demo=$('.demo-dialog');let demoTrigger;
const demoVideo=demo&&$('video',demo), demoStatus=demo&&$('.demo-status',demo);
function startVideo(video,status){
 status.textContent='Loading demo…';
 video.play().then(()=>{status.textContent='';}).catch(error=>{status.textContent=error.name==='NotAllowedError'?'Press play to start the demo.':'Could not play the recording. Use the video link to open it directly.';});
}
if(demo){
 demoVideo.addEventListener('playing',()=>demoStatus.textContent='');
 demoVideo.addEventListener('waiting',()=>demoStatus.textContent='Buffering…');
 demoVideo.addEventListener('error',()=>demoStatus.textContent='The recording could not load. Use Open video below.');
 $('.demo-close').addEventListener('click',()=>demo.close());
 demo.addEventListener('close',()=>{demoVideo.pause();demoVideo.removeAttribute('src');demoVideo.load();demoStatus.textContent='';demoTrigger?.focus();});
}
$$('.demo-open').forEach(a=>a.addEventListener('click',e=>{
 if(e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;
 const inline=a.dataset.demoMode==='inline'&&$('#project-demo video');
 if(!inline&&!demo)return;
 e.preventDefault();$$('video').forEach(v=>v.pause());
 if(inline){
  history.replaceState(null,'','#project-demo');$('#project-demo').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth',block:'start'});
  inline.focus({preventScroll:true});startVideo(inline,$('.inline-video-status'));return;
 }
 demoTrigger=a;$('#demo-title').textContent=a.dataset.title+' · demo';
 demoVideo.poster=a.dataset.poster||'';demoVideo.src=a.dataset.video;demoVideo.setAttribute('aria-label',a.dataset.title+' project demo');
 $('.demo-file-link').href=a.dataset.video;
 $('.demo-project-link').href=a.dataset.project||a.href;
 demo.showModal();$('.demo-close').focus();startVideo(demoVideo,demoStatus);
}));
$$('.case-video video').forEach(v=>{
 v.tabIndex=0;const status=$('.inline-video-status',v.closest('figure'));
 v.addEventListener('playing',()=>status.textContent='Project recording');
 v.addEventListener('error',()=>{status.textContent='The recording could not load. ';const a=document.createElement('a');a.href=$('source',v).src;a.textContent='Open video directly';status.append(a);});
});
$$('[data-copy]').forEach(b=>b.addEventListener('click',async()=>{const status=$('.copy-status');try{await navigator.clipboard.writeText(b.dataset.copy);status.textContent='Email address copied.';b.firstChild.textContent='Copied ';}catch{status.textContent='Select the email address above to copy it, or click it to send a message.';}}));
for(const d of [dialog,media,demo].filter(Boolean)){d.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();d.close();}});d.addEventListener('click',e=>{if(e.target!==d)return;const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();});}
})();
