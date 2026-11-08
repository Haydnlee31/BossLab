import {RULES,ATTACKS,PLAYER_ATTACK} from '../core/config.js';
import {rng} from '../core/math.js';
export class Renderer {
  constructor(canvas){this.canvas=canvas;this.ctx=canvas.getContext('2d');this.particles=[];this.lastEvent=0;this.lastId='';this.motion=true;this.background=document.createElement('canvas');this.background.width=1280;this.background.height=720;this.paintArena(this.background.getContext('2d'));}
  path(c,points,fill,stroke){c.beginPath();points.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();if(fill){c.fillStyle=fill;c.fill();}if(stroke){c.strokeStyle=stroke;c.stroke();}}
  circle(c,x,y,r,fill,stroke){c.beginPath();c.arc(x,y,r,0,Math.PI*2);if(fill){c.fillStyle=fill;c.fill();}if(stroke){c.strokeStyle=stroke;c.stroke();}}
  paintArena(c){
    const rand=rng(319);c.fillStyle='#0b1014';c.fillRect(0,0,1280,720);c.save();c.translate(700,355);
    const outer=c.createRadialGradient(0,0,100,0,0,490);outer.addColorStop(0,'#394040');outer.addColorStop(.7,'#202a2d');outer.addColorStop(1,'#080d12');c.fillStyle=outer;c.fillRect(-700,-355,1280,720);
    // Individually cut stone courses, seams and chipped edges.
    for(let ring=0;ring<8;ring++){const r0=ring*43,r1=r0+41,n=Math.max(8,ring*10),off=ring*.17;for(let j=0;j<n;j++){const a=j/n*Math.PI*2+off,b=(j+1)/n*Math.PI*2+off;const shade=26+Math.floor(rand()*13);c.fillStyle=`rgb(${shade},${shade+6},${shade+8})`;c.strokeStyle='#080e12';c.lineWidth=2;c.beginPath();c.arc(0,0,r1,a+.009,b-.009);c.arc(0,0,r0,b-.009,a+.009,true);c.closePath();c.fill();c.stroke();c.strokeStyle='#67706a15';c.lineWidth=1;c.beginPath();c.arc(0,0,r1-2,a+.014,b-.014);c.stroke();}}
    for(const r of [64,68,205,209,281,285,302,310]){this.circle(c,0,0,r,null,r===285?'#99825980':'#9f8b592e');}
    for(let i=0;i<80;i++){const a=i*Math.PI/40;c.save();c.rotate(a);c.strokeStyle=i%5===0?'#b5a17764':'#8072543f';c.beginPath();c.moveTo(287,0);c.lineTo(296,i%5===0?0:3);c.stroke();c.restore();}
    // Central seal: interleaved blade forms, never collision geometry.
    c.strokeStyle='#a99e7628';c.lineWidth=1;for(let i=0;i<8;i++){c.save();c.rotate(i*Math.PI/4);this.path(c,[[0,-63],[12,-19],[0,-30],[-12,-19]],null,'#a99e7635');c.restore();}
    for(let i=0;i<150;i++){const a=rand()*Math.PI*2,r=rand()*280,x=Math.cos(a)*r,y=Math.sin(a)*r;c.strokeStyle='#080d1188';c.beginPath();c.moveTo(x,y);c.lineTo(x+rand()*18-9,y+rand()*15);c.lineTo(x+rand()*25-12,y+rand()*25);c.stroke();}
    for(let i=0;i<8;i++){const a=i*Math.PI/4+Math.PI/8,x=Math.cos(a)*330,y=Math.sin(a)*330;c.save();c.translate(x,y);c.rotate(a);this.path(c,[[-16,22],[5,66],[32,66],[22,20]],'#050a0db0');this.path(c,[[-22,-22],[22,-22],[25,22],[-25,22]],'#151d23','#59615b');this.path(c,[[-15,-16],[15,-16],[17,14],[-17,14]],'#30393b','#72736588');this.path(c,[[-10,-12],[10,-12],[10,10],[-10,10]],'#252f33','#606c6380');for(let j=0;j<3;j++){c.fillStyle='#050b10';c.fillRect(-9+j*7,-12,3,22);}c.restore();}
    for(let i=0;i<55;i++){const a=rand()*Math.PI*2,r=312+rand()*90,x=Math.cos(a)*r,y=Math.sin(a)*r;c.save();c.translate(x,y);c.rotate(rand()*6);const s=3+rand()*9;this.path(c,[[-s,-s],[s*.7,-s*.6],[s,s],[-s*.6,s*.4]],'#293235','#12191c');c.restore();}
    for(const [x,y] of [[-254,-224],[254,-224],[-254,224],[254,224]]){let g=c.createRadialGradient(x,y,0,x,y,100);g.addColorStop(0,'#d9882b30');g.addColorStop(.4,'#c9762220');g.addColorStop(1,'#0000');c.fillStyle=g;c.fillRect(x-100,y-100,200,200);this.circle(c,x,y,13,'#171b1d','#6e6551');this.circle(c,x,y,7,'#ad6427','#edbb63');}
    c.restore();const vignette=c.createRadialGradient(700,360,190,640,360,720);vignette.addColorStop(0,'#0000');vignette.addColorStop(.72,'#03081044');vignette.addColorStop(1,'#03070cea');c.fillStyle=vignette;c.fillRect(0,0,1280,720);
  }
  telegraph(c,actor,a,phase){
    c.save();c.translate(actor.x,actor.y);c.rotate(actor.facing);const active=phase==='active',locked=phase==='aim-locked';c.fillStyle=active?'#ffd59d69':locked?'#cc943522':'#c9973710';c.strokeStyle=active?'#fff2cc':locked?'#e2b66e9f':'#d2a75c60';c.lineWidth=active?2:1;c.setLineDash(active?[]:[5,6]);
    c.beginPath();if(a.geometry==='capsule'){c.roundRect(-a.width,-a.width,a.range+a.width*2,a.width*2,a.width);}else{c.moveTo(0,0);c.arc(0,0,a.range,-a.arc,a.arc);c.closePath();}c.fill();c.stroke();c.setLineDash([]);
    if(active){c.shadowBlur=18;c.shadowColor='#f4ba73';c.strokeStyle='#fff0c2';c.lineWidth=4;c.beginPath();if(a.geometry==='capsule'){c.moveTo(20,0);c.lineTo(a.range,0);}else{c.arc(0,0,a.range*.86,-a.arc,a.arc);}c.stroke();}
    c.restore();
  }
  actor(c,actor,boss,world){
    const attacking=actor.state==='attack',phase=boss?world.phase():attacking?(actor.age<10?'windup':actor.age<14?'active':'recovery'):actor.state;
    c.save();c.translate(actor.x,actor.y);this.circle(c,4,9,boss?30:17,'#0007');c.rotate(actor.facing);
    if(boss){
      // Tattered burgundy mantle, segmented shoulders, horned visor and pole-cleaver.
      this.path(c,[[-10,-22],[-36,-27],[-29,-10],[-39,0],[-29,11],[-35,27],[-10,22],[9,12]],'#462e2a','#8c634345');
      this.path(c,[[-23,-15],[0,-21],[17,-11],[20,10],[0,21],[-23,15]],'#454c49','#a0a28a');
      this.path(c,[[-11,-10],[7,-12],[15,0],[7,12],[-11,10]],'#69716b','#c0baa1');
      for(const s of [-1,1]){this.path(c,[[-13,s*14],[-17,s*28],[5,s*30],[18,s*18],[6,s*12]],'#535c58','#a7a28b');this.path(c,[[0,s*15],[9,s*20],[3,s*24],[-8,s*22]],'#81877b');this.path(c,[[-15,s*9],[-26,s*7],[-27,s*16],[-16,s*17]],'#222b2e','#5e6861');}
      this.path(c,[[4,-10],[17,-8],[25,0],[17,8],[4,10],[-2,0]],'#909486','#d4c9a7');this.path(c,[[12,-7],[22,0],[12,7],[13,2],[5,0],[13,-2]],'#1b2529');
      c.shadowBlur=10;c.shadowColor='#ffb84b';c.fillStyle='#f3c077';c.fillRect(14,-5,3,10);c.shadowBlur=0;
      for(const s of [-1,1])this.path(c,[[6,s*8],[-3,s*16],[-15,s*19],[-4,s*10]],'#b3aa8a','#393d38');
      c.save();c.translate(5,23);c.rotate(phase==='windup'?-.8:phase==='aim-locked'?-.4:phase==='recovery'?.55:0);
      c.strokeStyle='#171c1d';c.lineWidth=7;c.beginPath();c.moveTo(-26,0);c.lineTo(66,0);c.stroke();c.strokeStyle='#ad9971';c.lineWidth=3;c.stroke();this.path(c,[[42,-3],[57,-23],[73,-21],[77,-6],[71,19],[53,24],[60,3]],'#99a296','#ddd0a8');this.path(c,[[65,-19],[73,-19],[77,-6],[70,18],[60,21],[68,7]],'#d8cfb0');c.restore();
    }else{
      const dodging=actor.state==='dodge';if(dodging){this.circle(c,0,0,18,null,world.invulnerable()?'#b5efdbcc':'#77958a44');}
      this.path(c,[[-5,-12],[-25,-16],[-21,-4],[-28,2],[-22,14],[-5,12],[6,5]],'#2c6d70','#81b5ad');this.path(c,[[-8,-8],[8,-9],[14,0],[6,10],[-10,8]],'#58797b','#9db5ac');this.path(c,[[0,-8],[10,-7],[16,0],[10,7],[0,8],[-4,0]],'#adbeb4','#d3d6c3');this.path(c,[[8,-4],[15,0],[8,4],[5,0]],'#223d42');
      this.path(c,[[-7,-11],[-1,-16],[8,-12],[11,-7]],'#9b9b83');c.strokeStyle='#6c5337';c.lineWidth=4;c.beginPath();c.moveTo(3,12);c.lineTo(18,12);c.stroke();this.path(c,[[17,9],[46,9],[54,12],[46,15],[17,15]],'#bdcdc4','#e1debf');c.strokeStyle='#cdb888';c.lineWidth=3;c.beginPath();c.moveTo(17,5);c.lineTo(17,20);c.stroke();
    }c.restore();
  }
  draw(world,seconds,{title=false,reduced=false}={}){
    const canvas=this.canvas,c=this.ctx,dpr=Math.min(devicePixelRatio||1,2),w=canvas.clientWidth,h=canvas.clientHeight;if(canvas.width!==w*dpr||canvas.height!==h*dpr){canvas.width=w*dpr;canvas.height=h*dpr;}
    c.setTransform(dpr,0,0,dpr,0,0);c.fillStyle='#080d11';c.fillRect(0,0,w,h);const scale=Math.min(w/1280,h/720);c.translate((w-1280*scale)/2,(h-720*scale)/2);c.scale(scale,scale);c.drawImage(this.background,0,0);
    c.save();c.translate(700,355);
    // Ambient ember light; presentation time has no effect on combat.
    if(!reduced)for(let i=0;i<24;i++){const x=Math.sin(i*78.7)*330,y=((i*87-seconds*(9+i%4))%620+620)%620-310;this.circle(c,x,y,1+(i%3)*.3,`rgba(221,167,85,${.12+.16*Math.sin(i+seconds)**2})`);}
    if(world){
      if(this.lastId!==world.id){this.lastId=world.id;this.lastEvent=0;this.particles=[];}
      for(const e of world.events.slice(this.lastEvent)){if(e.type==='hit'){const t=e.target==='boss'?world.boss:world.player;for(let i=0;i<14;i++)this.particles.push({x:t.x,y:t.y,vx:Math.cos(i*2.4)*2.5,vy:Math.sin(i*2.4)*2.5,t:seconds,color:e.target==='boss'?'#e9c786':'#b9705d'});}}
      this.lastEvent=world.events.length;
      const b=world.boss,p=world.player;if(b.state==='attack'&&world.phase()!=='recovery')this.telegraph(c,b,ATTACKS[b.action],world.phase());
      if(p.state==='attack'&&p.age>=10&&p.age<14)this.telegraph(c,p,PLAYER_ATTACK,'active');
      if(p.state==='dodge'&&!reduced){for(let i=4;i>0;i--)this.circle(c,p.x-p.dx*i*7,p.y-p.dy*i*7,12-i,'#98d5c31a');}
      if(p.state==='heal'){this.circle(c,p.x,p.y,27,'#96cfa715','#bbdda388');c.strokeStyle='#d2e8b1';c.lineWidth=2;c.beginPath();c.arc(p.x,p.y,29,-Math.PI/2,-Math.PI/2+p.age/72*Math.PI*2);c.stroke();}
      this.actor(c,b,true,world);this.actor(c,p,false,world);
      for(const e of world.events.slice(-12)){if(e.type==='hit'&&world.tick-e.tick<24){const t=e.target==='boss'?b:p;c.fillStyle='#f7dfb7';c.font='14px Georgia';c.textAlign='center';c.fillText(`−${e.damage}`,t.x,t.y-35-(world.tick-e.tick));}}
      this.particles=this.particles.filter(p=>seconds-p.t<.5);if(!reduced)for(const p of this.particles){const age=(seconds-p.t)*35;c.globalAlpha=1-(seconds-p.t)*2;this.circle(c,p.x+p.vx*age,p.y+p.vy*age,1.5,p.color);}c.globalAlpha=1;
    }c.restore();
    if(title){c.fillStyle='#c6ab7b66';c.textAlign='center';c.font='9px Arial';c.letterSpacing='3px';c.fillText('OBSERVE  /  ADAPT  /  OVERCOME',855,655);c.letterSpacing='0px';}
  }
  worldPoint(clientX,clientY){const r=this.canvas.getBoundingClientRect(),s=Math.min(r.width/1280,r.height/720);return {x:(clientX-r.left-(r.width-1280*s)/2)/s-700,y:(clientY-r.top-(r.height-720*s)/2)/s-355};}
}
