(()=>{
const canvas=document.querySelector('.systems-field');if(!canvas)return;
const stage=canvas.parentElement,ctx=canvas.getContext('2d'),reduced=matchMedia('(prefers-reduced-motion:reduce)');let w=0,h=0,raf=0,last=0,visible=true,px=0,py=0,rx=0,ry=0;
function resize(){const box=stage.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2);w=box.width;h=box.height;canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);draw(0);}
function draw(time){ctx.clearRect(0,0,w,h);const r=Math.min(w*.36,h*.35),cx=w*.5,cy=h*.465;rx+=(px-rx)*.035;ry+=(py-ry)*.035;const spin=time*.000075+rx,tilt=-.23+ry;
const project=(lat,lon)=>{let x=r*Math.cos(lat)*Math.cos(lon),z=r*Math.cos(lat)*Math.sin(lon),y=r*Math.sin(lat);const a=x*Math.cos(spin)+z*Math.sin(spin);z=-x*Math.sin(spin)+z*Math.cos(spin);x=a;const b=y*Math.cos(tilt)-z*Math.sin(tilt);z=y*Math.sin(tilt)+z*Math.cos(tilt);y=b;const depth=(z/r+1)/2,scale=500/(500-z);return{x:cx+x*scale,y:cy+y*scale,depth};};
for(let row=1;row<20;row++){const lat=-Math.PI/2+row*Math.PI/20;ctx.beginPath();for(let col=0;col<=64;col++){const p=project(lat,col*Math.PI/32);col?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y);}ctx.strokeStyle='rgba(113,210,183,.13)';ctx.lineWidth=.65;ctx.stroke();}
for(let col=0;col<24;col++){ctx.beginPath();for(let row=0;row<=40;row++){const p=project(-Math.PI/2+row*Math.PI/40,col*Math.PI/12);row?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y);}ctx.strokeStyle='rgba(113,210,183,.1)';ctx.lineWidth=.6;ctx.stroke();}
for(let row=1;row<19;row++)for(let col=0;col<36;col++){const p=project(-Math.PI/2+row*Math.PI/20,col*Math.PI/18);ctx.beginPath();ctx.arc(p.x,p.y,.6+p.depth*.7,0,Math.PI*2);ctx.fillStyle=`rgba(173,251,217,${.1+p.depth*.42})`;ctx.fill();}
for(let i=0;i<3;i++){const p=project([-.35,.14,.55][i],[.8,3.3,5.1][i]);ctx.beginPath();ctx.arc(p.x,p.y,3,0,Math.PI*2);ctx.fillStyle='#c7ffe5';ctx.shadowColor='#9cf4d3';ctx.shadowBlur=12;ctx.fill();ctx.shadowBlur=0;ctx.beginPath();ctx.arc(p.x,p.y,7,0,Math.PI*2);ctx.strokeStyle='#a6f6d750';ctx.stroke();}
ctx.beginPath();ctx.ellipse(cx,cy,r*1.28,r*.25,-.48,0,Math.PI*2);ctx.strokeStyle='rgba(144,218,208,.13)';ctx.lineWidth=.7;ctx.stroke();}
function frame(now){if(now-last>32){draw(now);last=now;}if(visible&&!document.hidden&&!reduced.matches)raf=requestAnimationFrame(frame);else raf=0;}
function sync(){cancelAnimationFrame(raf);raf=0;if(visible&&!document.hidden&&!reduced.matches)raf=requestAnimationFrame(frame);else draw(0);}
stage.addEventListener('pointermove',e=>{const b=stage.getBoundingClientRect();px=((e.clientX-b.left)/b.width-.5)*.6;py=((e.clientY-b.top)/b.height-.5)*.35;if(reduced.matches)draw(0);});stage.addEventListener('pointerleave',()=>{px=0;py=0;});new ResizeObserver(resize).observe(stage);new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync();}).observe(stage);document.addEventListener('visibilitychange',sync);reduced.addEventListener('change',sync);resize();sync();
})();
