(()=>{const s=document.querySelector('.concept-switcher select');s?.addEventListener('change',()=>{const target=new URL(s.value,location.origin);target.search=location.search;target.hash=location.hash;location.href=target.href;});})();
(()=>{
const canvas=document.querySelector('.systems-field');if(!canvas||document.documentElement.dataset.theme==='new-york')return;
const stage=canvas.parentElement,ctx=canvas.getContext('2d');if(!ctx)return;
const reduced=matchMedia('(prefers-reduced-motion:reduce)'),preview=new URLSearchParams(location.search).has('preview');
let w=0,h=0,raf=0,last=0,visible=true,px=0,py=0,rx=0,ry=0;
function resize(){const box=stage.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2);w=box.width;h=box.height;canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);draw(0);}
function draw(time){
 ctx.clearRect(0,0,w,h);const r=Math.min(w*.405,h*.405),cx=w*.51,cy=h*.5;
 const rgb=getComputedStyle(stage).getPropertyValue('--globe-rgb').trim()||'166,246,215';
 rx+=(px-rx)*.035;ry+=(py-ry)*.035;const spin=time*.000035+rx,tilt=-.26+ry;
 const project=(lat,lon)=>{let x=r*Math.cos(lat)*Math.cos(lon),z=r*Math.cos(lat)*Math.sin(lon),y=r*Math.sin(lat);const a=x*Math.cos(spin)+z*Math.sin(spin);z=-x*Math.sin(spin)+z*Math.cos(spin);x=a;const b=y*Math.cos(tilt)-z*Math.sin(tilt);z=y*Math.sin(tilt)+z*Math.cos(tilt);y=b;const depth=(z/r+1)/2;return{x:cx+x,y:cy+y,depth};};
 for(let row=1;row<18;row++){const lat=-Math.PI/2+row*Math.PI/18;ctx.beginPath();for(let col=0;col<=64;col++){const p=project(lat,col*Math.PI/32);col?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y);}ctx.strokeStyle=`rgba(${rgb},.12)`;ctx.lineWidth=.6;ctx.stroke();}
 for(let col=0;col<22;col++){ctx.beginPath();for(let row=0;row<=36;row++){const p=project(-Math.PI/2+row*Math.PI/36,col*Math.PI/11);row?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y);}ctx.strokeStyle=`rgba(${rgb},.1)`;ctx.lineWidth=.6;ctx.stroke();}
 for(let row=1;row<18;row++)for(let col=0;col<32;col++){const p=project(-Math.PI/2+row*Math.PI/18,col*Math.PI/16);ctx.beginPath();ctx.arc(p.x,p.y,.55+p.depth*.65,0,Math.PI*2);ctx.fillStyle=`rgba(${rgb},${.07+p.depth*.36})`;ctx.fill();}
}
function frame(now){if(now-last>40){draw(now);last=now;}if(visible&&!document.hidden&&!reduced.matches&&!preview)raf=requestAnimationFrame(frame);else raf=0;}
function sync(){cancelAnimationFrame(raf);raf=0;if(visible&&!document.hidden&&!reduced.matches&&!preview)raf=requestAnimationFrame(frame);else draw(0);}
stage.addEventListener('pointermove',e=>{const b=stage.getBoundingClientRect();px=((e.clientX-b.left)/b.width-.5)*.4;py=((e.clientY-b.top)/b.height-.5)*.2;if(reduced.matches)draw(0);});stage.addEventListener('pointerleave',()=>{px=0;py=0;});
new ResizeObserver(resize).observe(stage);new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync();}).observe(stage);document.addEventListener('visibilitychange',sync);reduced.addEventListener('change',sync);resize();sync();
})();
