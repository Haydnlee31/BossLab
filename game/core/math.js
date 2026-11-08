export const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
export const distance=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
export const angle=(a,b)=>Math.atan2(b.y-a.y,b.x-a.x);
export const wrap=a=>Math.atan2(Math.sin(a),Math.cos(a));
export function turn(a,b,max){return a+clamp(wrap(b-a),-max,max);}
export function rng(seed=1){let s=seed>>>0;return ()=>{s+=0x6D2B79F5;let t=s;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return ((t^t>>>14)>>>0)/4294967296;};}
export function freeze(x){if(x&&typeof x==='object'){Object.values(x).forEach(freeze);Object.freeze(x);}return x;}
export function hitGeometry(source,target,a){
  const dx=target.x-source.x,dy=target.y-source.y,d=Math.hypot(dx,dy),r=target.radius||0;
  if(a.geometry==='capsule'){const f=dx*Math.cos(source.facing)+dy*Math.sin(source.facing),side=-dx*Math.sin(source.facing)+dy*Math.cos(source.facing);return Math.hypot(f-clamp(f,0,a.range),side)<=a.width+r;}
  return d<=a.range+r && Math.abs(wrap(Math.atan2(dy,dx)-source.facing))<=a.arc+Math.asin(Math.min(1,r/Math.max(1,d)));
}
