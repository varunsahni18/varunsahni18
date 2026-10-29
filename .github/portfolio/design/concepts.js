(()=>{const s=document.querySelector('.concept-switcher select');s?.addEventListener('change',()=>{const target=new URL(s.value,location.origin);target.search=location.search;target.hash=location.hash;location.href=target.href;});})();
(()=>{
const canvas=document.querySelector('.systems-field');if(!canvas)return;
const stage=canvas.parentElement,ctx=canvas.getContext('2d');if(!ctx)return;
const reduced=matchMedia('(prefers-reduced-motion:reduce)'),mobile=matchMedia('(max-width:650px)');
const links=[...stage.querySelectorAll('[data-globe-index]')],counter=stage.querySelector('.globe-count'),buttons=[...stage.querySelectorAll('[data-globe-step]')];
const preview=new URLSearchParams(location.search).has('preview');
const groupSize=6;let page=0,w=0,h=0,raf=0,last=0,visible=true,px=0,py=0,rx=0,ry=0,targets=[];
function measure(){const box=stage.getBoundingClientRect();targets=links.map(link=>{if(link.hidden)return null;const b=link.getBoundingClientRect();return {x:(b.left+b.right)/2-box.left,y:(b.top+b.bottom)/2-box.top};});}
function resize(){const box=stage.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2);w=box.width;h=box.height;canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);measure();draw(0);}
function showPage(next){page=Math.max(0,Math.min(Math.ceil(links.length/groupSize)-1,next));links.forEach((link,i)=>{link.hidden=Math.floor(i/groupSize)!==page;});counter.textContent=`${String(page*groupSize+1).padStart(2,'0')}–${String(Math.min((page+1)*groupSize,links.length)).padStart(2,'0')} of ${links.length} projects`;buttons.forEach(b=>{b.disabled=Number(b.dataset.globeStep)<0?page===0:(page+1)*groupSize>=links.length;});measure();draw(last);}
buttons.forEach(b=>b.addEventListener('click',()=>showPage(page+Number(b.dataset.globeStep))));
function draw(time){
 ctx.clearRect(0,0,w,h);const viewH=mobile.matches?230:h-50,r=Math.min(w*.35,viewH*.34),cx=w*.5,cy=viewH*.48;
 const styles=getComputedStyle(stage),rgb=styles.getPropertyValue('--globe-rgb').trim()||'166,246,215',accent=styles.getPropertyValue('--accent').trim()||'#a6f6d7';
 rx+=(px-rx)*.035;ry+=(py-ry)*.035;const spin=time*.000055+rx,tilt=-.23+ry;
 const project=(lat,lon)=>{let x=r*Math.cos(lat)*Math.cos(lon),z=r*Math.cos(lat)*Math.sin(lon),y=r*Math.sin(lat);const a=x*Math.cos(spin)+z*Math.sin(spin);z=-x*Math.sin(spin)+z*Math.cos(spin);x=a;const b=y*Math.cos(tilt)-z*Math.sin(tilt);z=y*Math.sin(tilt)+z*Math.cos(tilt);y=b;const depth=(z/r+1)/2,scale=650/(650-z);return{x:cx+x*scale,y:cy+y*scale,depth};};
 for(let row=1;row<20;row++){const lat=-Math.PI/2+row*Math.PI/20;ctx.beginPath();for(let col=0;col<=64;col++){const p=project(lat,col*Math.PI/32);col?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y);}ctx.strokeStyle=`rgba(${rgb},.14)`;ctx.lineWidth=.65;ctx.stroke();}
 for(let col=0;col<24;col++){ctx.beginPath();for(let row=0;row<=40;row++){const p=project(-Math.PI/2+row*Math.PI/40,col*Math.PI/12);row?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y);}ctx.strokeStyle=`rgba(${rgb},.11)`;ctx.lineWidth=.6;ctx.stroke();}
 for(let row=1;row<19;row++)for(let col=0;col<36;col++){const p=project(-Math.PI/2+row*Math.PI/20,col*Math.PI/18);ctx.beginPath();ctx.arc(p.x,p.y,.6+p.depth*.7,0,Math.PI*2);ctx.fillStyle=`rgba(${rgb},${.1+p.depth*.42})`;ctx.fill();}
 // Fibonacci sampling gives every project its own point on the sphere.
 links.forEach((link,i)=>{const nodeIndex=(i*9)%links.length,lat=Math.asin(1-2*(nodeIndex+.5)/links.length),lon=nodeIndex*Math.PI*(3-Math.sqrt(5)),p=project(lat,lon),active=!link.hidden;
  if(active&&!mobile.matches&&targets[i]){const t=targets[i];ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(t.x,t.y);ctx.strokeStyle=`rgba(${rgb},.3)`;ctx.lineWidth=.8;ctx.stroke();}
  ctx.beginPath();ctx.arc(p.x,p.y,active?3.3:1.8,0,Math.PI*2);ctx.fillStyle=active?accent:`rgba(${rgb},.4)`;if(active){ctx.shadowColor=accent;ctx.shadowBlur=10;}ctx.fill();ctx.shadowBlur=0;
  if(active){ctx.beginPath();ctx.arc(p.x,p.y,7,0,Math.PI*2);ctx.strokeStyle=`rgba(${rgb},.4)`;ctx.stroke();}
 });
 ctx.beginPath();ctx.ellipse(cx,cy,r*1.25,r*.25,-.48,0,Math.PI*2);ctx.strokeStyle=`rgba(${rgb},.15)`;ctx.lineWidth=.7;ctx.stroke();
}
function frame(now){if(now-last>32){draw(now);last=now;}if(visible&&!document.hidden&&!reduced.matches&&!preview)raf=requestAnimationFrame(frame);else raf=0;}
function sync(){cancelAnimationFrame(raf);raf=0;if(visible&&!document.hidden&&!reduced.matches&&!preview)raf=requestAnimationFrame(frame);else draw(0);}
stage.addEventListener('pointermove',e=>{const b=stage.getBoundingClientRect();px=((e.clientX-b.left)/b.width-.5)*.6;py=((e.clientY-b.top)/b.height-.5)*.35;if(reduced.matches)draw(0);});
stage.addEventListener('pointerleave',()=>{px=0;py=0;});
new ResizeObserver(resize).observe(stage);new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync();}).observe(stage);
document.addEventListener('visibilitychange',sync);reduced.addEventListener('change',sync);mobile.addEventListener('change',resize);document.fonts?.ready.then(resize);resize();sync();
})();
