"""Original Keeper of the Last Vigil studio asset; meters, Z-up, front=-Y.
No downloaded meshes/textures. Studio asset, not the current Unreal character.
"""
import bpy, math, random, json, sys, time, os, struct
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi,sqrt,exp
import numpy as np
R=Path(__file__).resolve().parents[3]; D=R/'unreal/art-studio'; E=R/'artifacts/art/last-vigil'
args=sys.argv[sys.argv.index('--')+1:]; mode=args[0]; random.seed(710)
E.mkdir(parents=True,exist_ok=True);(D/'textures').mkdir(exist_ok=True)
S=bpy.context.scene

def mesh(name,vs,fs,mat,smooth=True):
 m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.update();o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o)
 if mat:m.materials.append(mat)
 if smooth:
  for p in m.polygons:p.use_smooth=True
 return o

def bevel(o,w=.002,n=3):
 m=o.modifiers.new('Forged edge radius','BEVEL');m.width=w;m.segments=n
 return o

def sub(o,n=1):
 m=o.modifiers.new('Surface continuity','SUBSURF');m.levels=n;m.render_levels=n
 return o

def solid(o,t=.003):
 m=o.modifiers.new('Actual plate thickness','SOLIDIFY');m.thickness=t;m.offset=0
 return o

def curve(name,pts,r,mat,closed=False):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=2;c.bevel_depth=r;c.bevel_resolution=2
 s=c.splines.new('POLY');s.points.add(len(pts)-1)
 for p,v in zip(s.points,pts):p.co=(*v,1)
 s.use_cyclic_u=closed;o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);c.materials.append(mat);return o

def sphere(name,loc,scale,mat,seg=32,rings=20):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o

def loft(name,rows,mat,n=64):
 # rows z,rx,ry,cx,cy; all original cross-sections
 vs=[(cx+rx*cos(2*pi*i/n),cy+ry*sin(2*pi*i/n),z) for z,rx,ry,cx,cy in rows for i in range(n)]
 fs=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(rows)-1) for i in range(n)]
 fs += [tuple(reversed(range(n))),tuple((len(rows)-1)*n+i for i in range(n))]
 return mesh(name,vs,fs,mat)

def ring(name,c,u,v,rad,r,mat,start=0,end=2*pi,n=80):
 c,u,v=Vector(c),Vector(u),Vector(v)
 return curve(name,[c+rad*(u*cos(start+(end-start)*i/n)+v*sin(start+(end-start)*i/n)) for i in range(n+1)],r,mat)

def rivet(loc,r=.0035,mat=None):return sphere('Peened rivet',loc,(r,r*.55,r),mat or gold,12,8)

def node_mat(name,color,metal,rough,noise_scale=70,bump=.00025):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF')
 bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 if metal>.7 and 'Anisotropic IOR Level' in bs.inputs:bs.inputs['Anisotropic IOR Level'].default_value=.25
 coord=n.new('ShaderNodeTexCoord')
 tex=n.new('ShaderNodeTexNoise');l.new(coord.outputs['Object'],tex.inputs['Vector']);tex.inputs['Scale'].default_value=noise_scale;tex.inputs['Detail'].default_value=3;tex.inputs['Roughness'].default_value=.7
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(*[x*.68 for x in color],1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(*[min(x*1.24,1) for x in color],1)
 l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
 roughmap=n.new('ShaderNodeMapRange');roughmap.inputs['From Min'].default_value=0;roughmap.inputs['From Max'].default_value=1;roughmap.inputs['To Min'].default_value=max(.12,rough-.12);roughmap.inputs['To Max'].default_value=min(.99,rough+.16);l.new(tex.outputs['Fac'],roughmap.inputs[0]);l.new(roughmap.outputs[0],bs.inputs['Roughness'])
 micro=n.new('ShaderNodeTexNoise');l.new(coord.outputs['Object'],micro.inputs['Vector']);micro.inputs['Scale'].default_value=900;micro.inputs['Detail'].default_value=2
 b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.25;b.inputs['Distance'].default_value=bump;l.new(micro.outputs['Fac'],b.inputs['Height']);l.new(b.outputs['Normal'],bs.inputs['Normal'])
 return m

def collision(o):
 o.modifiers.new('Cloth contact','COLLISION');o.collision.thickness_outer=.006;o.collision.cloth_friction=8
 return o

def ell_path(rx,ry,z,cx=0,cy=0,n=100):return [(cx+rx*cos(2*pi*i/n),cy+ry*sin(2*pi*i/n),z) for i in range(n+1)]

def scroll(name,mapfn,x,z,scale,mat,mirror=1):
 # A growing acanthus scroll with three leaf ribs, placed on the actual surface.
 pts=[]
 for i in range(70):
  t=i/69;ang=t*1.65*2*pi;rr=scale*(.07+.93*t);pts.append(mapfn(x+mirror*rr*cos(ang),z+rr*sin(ang)))
 curve(name,pts,.0012,mat)
 for t in [.62,.78,.92]:
  a=t*1.65*2*pi;rr=scale*(.07+.93*t);xx=x+mirror*rr*cos(a);zz=z+rr*sin(a)
  points=[mapfn(xx+mirror*.013*sin(pi*k/12)*cos(a+.8),zz+.024*k/12) for k in range(13)]
  curve(name+' rib',points,.001,mat)
  # Lobed embossed leaf blade, with a center ridge and thin rolled edges.
  vs=[];fs=[];length=scale*.85;width=scale*.29;direction=a+1.05
  for j in range(15):
   q=j/14;ww=width*(sin(pi*q)**.75)*(1+.15*sin(q*8*pi))
   for side in [-1,0,1]:
    px=xx+mirror*(length*q*cos(direction)-side*ww*sin(direction));pz=zz+length*q*sin(direction)+side*ww*cos(direction)
    p=Vector(mapfn(px,pz));p.y-=.00035+.0010*sin(pi*q)*(1-abs(side));vs.append(p)
  for j in range(14):
   for k in range(2):f=j*3+k;fs.append((f,f+1,f+4,f+3))
  leaf=mesh(name+' leaf relief',vs,fs,mat);solid(leaf,.00035)


def chain_patch(name,rows,cols,fn,mat,radius=.006):
 vs=[];fs=[]
 for j in range(rows):
  for i in range(cols):
   c=Vector(fn(i,j));a=.65 if (i+j)%2 else -.65
   u=Vector((1,0,0));v=Vector((0,sin(a),cos(a)));w=u.cross(v);base=len(vs)
   for k in range(12):
    theta=2*pi*k/12;direction=u*cos(theta)+v*sin(theta)
    for q in range(4):
     phi=2*pi*q/4;vs.append(c+direction*(radius+.0011*cos(phi))+w*(.0011*sin(phi)))
   for k in range(12):
    for q in range(4):fs.append((base+k*4+q,base+((k+1)%12)*4+q,base+((k+1)%12)*4+(q+1)%4,base+k*4+(q+1)%4))
 return mesh(name,vs,fs,mat)

def cape_texture():
 # Painted original UV-space embroidery; it deforms with cloth, not floating curves.
 n=1536; yy,xx=np.mgrid[0:n,0:n].astype(np.float32);u=xx/(n-1);v=yy/(n-1)
 mask=np.zeros((n,n),dtype=np.float32)
 def line(points,width=1.8):
  for (ax,ay),(bx,by) in zip(points[:-1],points[1:]):
   ax*=n;ay*=n;bx*=n;by*=n
   x0=max(0,int(min(ax,bx)-width-2));x1=min(n,int(max(ax,bx)+width+3));y0=max(0,int(min(ay,by)-width-2));y1=min(n,int(max(ay,by)+width+3))
   if x0>=x1 or y0>=y1:continue
   X=xx[y0:y1,x0:x1];Y=yy[y0:y1,x0:x1];d=(bx-ax)**2+(by-ay)**2
   t=np.clip(((X-ax)*(bx-ax)+(Y-ay)*(by-ay))/max(d,.001),0,1);dst=np.sqrt((X-ax-t*(bx-ax))**2+(Y-ay-t*(by-ay))**2)
   mask[y0:y1,x0:x1]=np.maximum(mask[y0:y1,x0:x1],np.clip(width+.7-dst,0,1))
 for border in [.045,.064,.936,.955]:line([(border,.035),(border,.975)],1.2)
 for x in [.045,.955]:
  for j in range(28):
   y=.055+j*.032
   line([(x-.012,y),(x,y+.011),(x+.012,y),(x,y-.011),(x-.012,y)],.8)
 for y in [.045,.067]:line([(.045,y),(.955,y)],1.2)
 # Tree of seven extinguished lanterns: a single coherent heraldic device.
 line([(.5,.18),(.492,.3),(.508,.43),(.496,.56),(.5,.75)],3.2)
 for j in range(3):
  base=.32+j*.12
  for sign in [-1,1]:
   line([(.5,base),(.5+sign*.055,base+.035),(.5+sign*(.16-j*.027),base+.035),(.5+sign*(.19-j*.027),base+.105)],2)
   cx=.5+sign*(.19-j*.027);cy=base+.105
   line([(cx-.017,cy),(cx,cy+.05),(cx+.017,cy),(cx,cy-.022),(cx-.017,cy)],2)
 line([(.482,.77),(.5,.83),(.518,.77),(.5,.744),(.482,.77)],2)

 # Fine embroidered scrollwork and lantern cages enrich the same seven-oath device.
 for sign in [-1,1]:
  for j in range(5):
   cx=.5+sign*(.085+.013*j);cy=.27+j*.093;rad=.035
   points=[]
   for t in np.linspace(0,1,80):
    a=t*2*pi*1.4;rr=rad*(.08+.92*t);points.append((cx+sign*rr*cos(a),cy+rr*sin(a)))
   line(points,1.65)
   for k in range(3):
    a=.6+k*.8;px=cx+sign*rad*cos(a);py=cy+rad*sin(a)
    line([(px,py),(px+sign*.012,py+.008),(px+sign*.016,py+.025),(px+sign*.004,py+.017),(px,py)],1.3)
  for j in range(3):
   cx=.5+sign*(.19-j*.027);cy=.425+j*.12
   line([(cx-.013,cy+.008),(cx+.013,cy+.008)],1.5)
   line([(cx-.01,cy+.02),(cx+.01,cy+.02)],1.0)
 # A broken halo, echoed by the hilt; stitched double line with small stitch gaps.
 for radius in [.254,.26]:
  for k in range(36):
   a=.25+k*(2*pi-.5)/36
   line([(.5+radius*cos(t),.52+radius*sin(t)) for t in np.linspace(a,a+.12,12)],1.3)
 # Wreath and meander framing.
 for sign in [-1,1]:
  points=[(.5+sign*.3*sin(t*pi*.77),.22+.65*t) for t in np.linspace(0,1,90)];line(points,1.6)
  for t in np.linspace(.1,.9,15):
   x=.5+sign*.3*sin(t*pi*.77);y=.22+.65*t
   line([(x,y),(x+sign*.026,y+.022),(x+sign*.006,y+.041),(x,y)],1.1)
 rng=np.random.default_rng(11);fleck=rng.random((n,n))
 wear=(np.sin(xx*.031+np.sin(yy*.022))*np.sin(yy*.027)+1)/2
 mask*=np.where((fleck<.08)|(wear<.08),.15,1)
 rgba=np.ones((n,n,4),np.float32);rgba[:,:,:3]=mask[:,:,None]
 image=bpy.data.images.new('Original seven-lantern embroidery',width=n,height=n);image.pixels.foreach_set(rgba.ravel());image.filepath_raw=str(D/'textures/seven-lantern-embroidery.png');image.file_format='PNG';image.save();image.pack()
 # UV-space abrasion map: dust and worn fiber concentrated near the hem/edges.
 abrasion=np.clip((.23-v)*2.2,0,.42)*(0.5+0.5*wear)+np.maximum(0,1-np.minimum(u,1-u)/.035)*.18
 arr=np.ones((n,n,4),np.float32);arr[:,:,:3]=abrasion[:,:,None]
 worn=bpy.data.images.new('Original cloth abrasion',width=n,height=n);worn.pixels.foreach_set(arr.ravel());worn.filepath_raw=str(D/'textures/cloth-abrasion.png');worn.file_format='PNG';worn.save();worn.pack()
 return image

def fabric(name,color,embroidery=None):
 m=node_mat(name,color,0,.87,12,.0006);n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF');bs.inputs['Sheen Weight'].default_value=.07
 bs.inputs['Specular IOR Level'].default_value=.16
 for link in list(bs.inputs['Roughness'].links):l.remove(link)
 bs.inputs['Roughness'].default_value=.93
 tex=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(tex.outputs['UV'],sep.inputs[0]);waves=[]
 for a in ['X','Y']:
  mult=n.new('ShaderNodeMath');mult.operation='MULTIPLY';mult.inputs[1].default_value=1900;l.new(sep.outputs[a],mult.inputs[0]);sn=n.new('ShaderNodeMath');sn.operation='SINE';l.new(mult.outputs[0],sn.inputs[0]);waves.append(sn)
 mix=n.new('ShaderNodeMath');mix.operation='MULTIPLY';l.new(waves[0].outputs[0],mix.inputs[0]);l.new(waves[1].outputs[0],mix.inputs[1]);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.16;b.inputs['Distance'].default_value=.00012;l.new(mix.outputs[0],b.inputs['Height']);l.new(b.outputs[0],bs.inputs['Normal'])
 if embroidery:
  im=n.new('ShaderNodeTexImage');im.image=embroidery;im.interpolation='Linear';l.new(tex.outputs['UV'],im.inputs['Vector']);colorlink=bs.inputs['Base Color'].links[0].from_socket
  worn=n.new('ShaderNodeTexImage');worn.image=bpy.data.images['Original cloth abrasion'];l.new(tex.outputs['UV'],worn.inputs['Vector'])
  dust=n.new('ShaderNodeMixRGB');l.new(worn.outputs['Color'],dust.inputs[0]);l.new(colorlink,dust.inputs[1]);dust.inputs[2].default_value=(.066,.045,.026,1)
  mx=n.new('ShaderNodeMixRGB');l.new(im.outputs['Color'],mx.inputs[0]);l.new(dust.outputs[0],mx.inputs[1]);mx.inputs[2].default_value=(.32,.20,.075,1);l.new(mx.outputs[0],bs.inputs['Base Color'])
  l.new(im.outputs['Color'],bs.inputs['Metallic']);emb=n.new('ShaderNodeBump');emb.inputs['Distance'].default_value=.0009;emb.inputs['Strength'].default_value=.6;l.new(im.outputs['Color'],emb.inputs['Height']);l.new(b.outputs[0],emb.inputs['Normal']);l.new(emb.outputs[0],bs.inputs['Normal'])
 return m

def make():
 global steel,silver,gold,dark,leather,cloth,mail
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 steel=node_mat('01 | Blackened tempered steel',(.085,.079,.068),.9,.46)
 silver=node_mat('02 | Worn silver edges',(.29,.275,.25),.9,.42)
 gold=node_mat('03 | Tarnished electrum inlay',(.36,.23,.085),.85,.38)
 dark=node_mat('04 | Recess and soot',(.009,.011,.012),.25,.65)
 leather=node_mat('05 | Hand-oiled dark leather',(.031,.018,.013),0,.56,130,.0005)
 mail=node_mat('06 | Oiled iron mail',(.085,.092,.098),.9,.45)
 cloth=fabric('07 | Charcoal quilted linen',(.009,.007,.008))
 cape_mat=fabric('08 | Wine wool and worn gold thread',(.035,.004,.008),cape_texture())
 hem=fabric('09 | Faded oxblood binding',(.105,.022,.026))
 bone=node_mat('10 | Smoked ivory grip insets',(.37,.32,.23),.05,.52)
 # Human foundation; all faces concealed by purpose-built garments/armor.
 torso=loft('Padded arming doublet',[(1.00,.14,.105,0,0),(1.08,.16,.11,0,0),(1.19,.155,.11,0,0),(1.32,.19,.13,0,0),(1.49,.24,.135,0,.012),(1.58,.21,.11,0,.015),(1.63,.10,.085,0,.01)],cloth);sub(torso,2);collision(torso)
 # Central breastplate: broad upper chest, narrow waist, forged medial ridge.
 rows=[(1.18,.148,.115,0,-.006),(1.21,.153,.123,0,-.008),(1.29,.176,.144,0,-.006),(1.40,.217,.153,0,.002),(1.50,.229,.137,0,.012),(1.56,.19,.108,0,.012),(1.59,.13,.095,0,.01)]
 breast=loft('Cuirass | shaped front and back',rows,steel);bevel(breast,.002);sub(breast,1);collision(breast)
 def breast_y(x,z):
  for a,b in zip(rows[:-1],rows[1:]):
   if a[0]<=z<=b[0]:
    t=(z-a[0])/(b[0]-a[0]);rx=a[1]*(1-t)+b[1]*t;ry=a[2]*(1-t)+b[2]*t;cy=a[4]*(1-t)+b[4]*t;return cy-ry*sqrt(max(.05,1-(x/rx)**2))-.003
  return -.12
 def chest(x,z):return (x,breast_y(x,z),z)
 # Silver border follows actual tapered plate surface.
 for sign in [-1,1]:
  pts=[chest(sign*x,z) for x,z in [(0,1.587),(.10,1.58),(.166,1.553),(.205,1.495),(.189,1.40),(.155,1.30),(.136,1.22),(0,1.195)]]
  curve('Rolled cuirass rim',pts,.003,silver)
  for x,z in [(.12,1.54),(.17,1.48),(.145,1.30),(.11,1.22)]:rivet(chest(sign*x,z),.003,gold)
  for x,z,sc in [(.09,1.47,.036),(.115,1.38,.034),(.075,1.29,.025)]:scroll('Cuirass chased foliate scroll',chest,sign*x,z,sc,silver,sign)
  curve('Ribbed chest arch',[chest(sign*(.015+.16*t),1.53-.14*t+.018*sin(pi*t)) for t in np.linspace(0,1,60)],.0018,gold)
 curve('Forged sternum arris',[chest(.0,z) for z in np.linspace(1.215,1.57,65)],.0025,silver)
 ring('Broken oath halo',chest(0,1.462),(1,0,0),(0,0,1),.042,.0026,gold,.28,5.98)
 for j in range(7):
  a=.5+j*.79;rivet(chest(.032*cos(a),1.462+.032*sin(a)),.0023,silver)
 # Abdominal sliding lames, under cuirass overlap.
 for j in range(4):
  z=1.18-j*.033;rx=.157+j*.008;ry=.115+j*.004
  o=loft('Sliding fauld lame %02d'%j,[(z-.037,rx+.009,ry+.005,0,0),(z-.03,rx+.011,ry+.007,0,0),(z,rx,ry,0,0),(z+.003,rx,ry,0,0)],steel);bevel(o,.0015)
  curve('Fauld rolled lip',ell_path(rx+.009,ry+.006,z-.032),.0017,silver)
  for x in [-.11,.11]:rivet((x,-sqrt(max(.001,ry**2*(1-(x/rx)**2)))-.006,z-.018),.0028,gold)
 # Broad belt and two-layer buckle / leather suspension straps.
 belt=loft('Waist | double stitched belt',[(1.041,.191,.141,0,0),(1.08,.186,.139,0,0)],leather);bevel(belt,.002)
 for z in [1.047,1.074]:curve('Belt stitched edge',ell_path(.191,.143,z),.0008,gold)
 curve('Buckle | open forged rectangle',[(-.026,-.149,1.04),(.026,-.149,1.04),(.026,-.149,1.082),(-.026,-.149,1.082)],.004,gold,True);curve('Buckle tongue',[(0,-.152,1.045),(0,-.152,1.079)],.002,silver)
 # Gorget, ring-by-ring mail collar and helmet.
 gorget=loft('Gorget | articulated neck',[(1.565,.126,.103,0,0),(1.59,.12,.098,0,0),(1.64,.097,.087,0,0),(1.66,.095,.084,0,0)],steel);bevel(gorget,.002)
 for z,rx,ry in [(1.585,.122,.101),(1.624,.102,.09),(1.658,.096,.085)]:curve('Gorget silver lip',ell_path(rx,ry,z),.002,silver)
 chain_patch('Visible coif rings',7,46,lambda i,j:(.092*cos(i/46*2*pi),.081*sin(i/46*2*pi),1.635+j*.009),mail,.0058)
 # Helmet cranial shell with a real visor separation; front portions layered.
 shell=loft('Helm | raised skull shell',[(1.706,.089,.083,0,.011),(1.75,.11,.10,0,.012),(1.83,.114,.105,0,.015),(1.90,.091,.088,0,.018),(1.946,.036,.045,0,.018),(1.952,.004,.008,0,.018)],steel);sub(shell,2)
 # Visor upper and lower surfaces form narrow eye gap at z1.799..1.81.
 def visor(name,zs):
  vs=[];fs=[];N=48
  for z,rx,ry in zs:
   for i in range(N+1):
    a=pi+pi*i/N;vs.append((rx*cos(a),.004+ry*sin(a)-.011*exp(-((i/N-.5)/.14)**2),z+.006*abs(cos(a))))
  for j in range(len(zs)-1):
   for i in range(N):a=j*(N+1)+i;fs.append((a,a+1,a+N+2,a+N+1))
  o=mesh(name,vs,fs,steel);solid(o,.003);bevel(o,.002);return o
 visor('Helm | sculpted lower visor',[(1.697,.07,.082),(1.72,.091,.106),(1.76,.107,.12),(1.797,.111,.119)])
 visor('Helm | protective brow',[(1.814,.112,.115),(1.832,.112,.111),(1.862,.106,.103)])
 # Black inset under slit and raised silver eyebrow; the gap remains visually recessed.
 curve('Visor eye recess',[(-.087,-.079,1.804),(-.05,-.106,1.804),(0,-.122,1.804),(.05,-.106,1.804),(.087,-.079,1.804)],.0055,dark)
 curve('Visor brow | silver sweep',[(-.098,-.068,1.818),(-.06,-.105,1.821),(0,-.127,1.824),(.06,-.105,1.821),(.098,-.068,1.818)],.0028,silver)
 curve('Helm | central keel',[(0,-.09,1.704),(0,-.133,1.763),(0,-.132,1.817),(0,-.106,1.88),(0,-.056,1.93),(0,.005,1.955),(0,.065,1.92)],.0035,gold)
 for sign in [-1,1]:
  for j in range(5):
   x=sign*(.032+j*.011);y=-.119*sqrt(1-(x/.112)**2)-.004
   curve('Recessed visor breathing flute',[(x,y,1.735),(x+sign*.003,y-.003,1.773)],.0015,dark)
  sphere('Helm | visor pivot',(sign*.112,-.006,1.807),(.009,.006,.009),gold,20,12)
  for j in range(3):
   theta=sign*(.25+j*.26);pts=[]
   for k in range(35):
    t=k/34;z=1.84+.102*t;r=.113*sqrt(max(.03,1-((z-1.825)/.13)**2));pts.append((r*sin(theta),.016-r*cos(theta)-.002,z))
   curve('Helm chased fluting',pts,.0013,silver)
 # Short swept crest, individual curved fine strands; quiet silhouette, not horns.
 furmat=node_mat('11 | Smoke grey mantle fibers',(.11,.10,.085),0,.9,28,.0002)
 fiber=bpy.data.curves.new('Mantle individual fibers','CURVE');fiber.dimensions='3D';fiber.bevel_depth=.00055;fiber.bevel_resolution=1
 for j in range(2900):
  angle=random.uniform(.05,pi-.05);rx=random.uniform(.16,.265);x=rx*cos(angle);y=.015+.105*sin(angle);z=1.57+.047*sin(angle)+random.uniform(-.008,.02);length=random.uniform(.055,.13)
  sp=fiber.splines.new('POLY');sp.points.add(4)
  for k,p in enumerate(sp.points):
   t=k/4;p.co=(x+x*.22*t+.006*sin(t*pi+j),y+.055*t+.01*sin(j),z+.014*sin(pi*t)-length*t,1);p.radius=(1-t)**.7+.03
 fo=bpy.data.objects.new('Mantle | individually tapered smoke fibers',fiber);bpy.context.collection.objects.link(fo);fiber.materials.append(furmat)
 # Arms follow relaxed natural A stance, shaped pieces instead of scaled primitives.
 for sign,label in [(-1,'L'),(1,'R')]:
  cx=sign*.287
  upper=loft(label+' | arming sleeve',[(1.19,.068,.067,sign*.335,.015),(1.28,.08,.078,sign*.319,.015),(1.44,.095,.087,sign*.278,.018),(1.51,.088,.08,sign*.256,.019)],cloth,40);sub(upper,1);collision(upper)
  # Shoulder shells are half ellipsoids across y/x; curved lamellae step outward/down.
  for j in range(3):
   vs=[];fs=[];N=40;M=10;px=sign*(.259+j*.022);pz=1.50-j*.045
   for k in range(M+1):
    elev=.14+(pi*.52-.14)*k/M
    for i in range(N+1):
     a=2*pi*i/N;vs.append((px+sign*(.113-j*.008)*sin(elev)*cos(a),.017+(.128-j*.008)*sin(elev)*sin(a),pz+(.115-j*.008)*cos(elev)))
   for k in range(M):
    for i in range(N):a=k*(N+1)+i;fs.append((a,a+1,a+N+2,a+N+1))
   fs.append(tuple(reversed(range(N))) if sign>0 else tuple(range(N)))
   pa=mesh(label+' | articulated pauldron '+str(j),vs,fs,steel);solid(pa,.003);bevel(pa,.0015)
   curve('Pauldron rolled perimeter',vs[M*(N+1):],.0028,silver)
   for i in [4,12,20,28,36]:rivet(vs[M*(N+1)+i],.003,gold)
  # Upper arm plate and elbow fan.
  vam=loft(label+' | rerebrace',[(1.22,.074,.074,sign*.334,.015),(1.26,.078,.078,sign*.326,.015),(1.38,.087,.081,sign*.296,.015),(1.405,.084,.078,sign*.29,.015)],steel,48);bevel(vam,.002)
  for z,rx,ry,x in [(1.235,.076,.077,.331),(1.39,.086,.081,.293)]:curve('Rerebrace rolled edge',ell_path(rx,ry,z,sign*x,.015),.002,silver)
  sphere(label+' | couter fan',(sign*.351,.017,1.187),(.081,.08,.072),steel)
  ring('Couter chased oval',(sign*.353,-.065,1.187),(1,0,0),(0,0,1),.045,.002,gold)
  fore=loft(label+' | tapered vambrace',[(.96,.045,.048,sign*.387,-.012),(.99,.05,.051,sign*.383,-.009),(1.10,.064,.068,sign*.364,.007),(1.16,.068,.07,sign*.355,.01)],steel,48);bevel(fore,.002)
  for z,rx,ry,x in [(.972,.048,.051,.385),(1.142,.067,.071,.358)]:curve('Vambrace rolled lip',ell_path(rx,ry,z,sign*x,.007),.0025,silver)
  def arm_map(x,z,sg=sign):return (sg*(.387-(z-.96)*.16)+x,-.052-(z-.96)*.10,z)
  scroll('Vambrace vine',arm_map,0,1.055,.026,silver,sign)
  for j in range(3):
   z=1.00+j*.047;curve('Vambrace longitudinal flutes',[arm_map(sign*.023,z),arm_map(sign*.019,z+.035)],.0012,gold)
  # Articulated glove, separate fingers and knuckle caps.
  sphere(label+' | leather glove',(sign*.394,-.018,.913),(.049,.032,.07),leather)
  for j in range(3):
   z=.932-j*.018;loft(label+' | metacarpal lame',[(z-.012,.046,.034,sign*.394,-.021),(z+.01,.046,.034,sign*.394,-.021)],steel,32)
  for f in range(4):
   x=sign*.394+(f-1.5)*.018
   for j in range(3):
    z=.88-j*.019;y=-.02-.007*j
    sphere('Gauntlet | finger segment',(x,y,z),(.0085,.010,.013),steel,16,10)
   rivet((x,-.052,.922),.004,silver)
  sphere('Gauntlet | thumb',(sign*.444,-.019,.907),(.012,.018,.04),steel,20,12)
  # Legs with real knee clearances and riveted cuisses/greaves.
  leg=loft(label+' | padded chausses',[(.43,.075,.079,sign*.112,.006),(.65,.086,.092,sign*.108,0),(.83,.104,.107,sign*.102,.005),(1.05,.115,.109,sign*.095,.006)],cloth,48);sub(leg,1);collision(leg)
  thigh=loft(label+' | cuisse',[(.60,.076,.083,sign*.115,-.003),(.64,.085,.094,sign*.114,0),(.82,.101,.107,sign*.109,.002),(.91,.102,.108,sign*.106,.005)],steel,48);bevel(thigh,.002)
  for z,rx,ry in [(.625,.083,.093),(.893,.103,.11)]:curve('Cuisse rolled rim',ell_path(rx,ry,z,sign*.11),.0025,silver)
  sphere(label+' | pointed poleyn',(sign*.118,-.038,.559),(.084,.076,.07),steel)
  curve('Knee raised arris',[(sign*.118,-.115,.51),(sign*.118,-.12,.56),(sign*.118,-.10,.607)],.0025,silver)
  for side in [-1,1]:sphere('Poleyn articulated wing',(sign*.118+side*.071,-.002,.558),(.026,.043,.051),steel,24,16)
  shin=loft(label+' | forged greave',[(.12,.048,.052,sign*.13,.01),(.17,.052,.057,sign*.129,.008),(.29,.062,.07,sign*.126,.005),(.43,.07,.076,sign*.122,0),(.501,.062,.066,sign*.12,0)],steel,48);bevel(shin,.002)
  for z,rx,ry in [(.155,.053,.058),(.48,.065,.071)]:curve('Greave rolled edge',ell_path(rx,ry,z,sign*.125,.005),.0025,silver)
  def shinmap(x,z,sg=sign):return (sg*.125+x,-.071-.006*sin((z-.15)/.34*pi),z)
  for side in [-1,1]:curve('Greave fluting',[shinmap(side*.022*sin(pi*t),.17+t*.30) for t in np.linspace(0,1,70)],.0015,gold)
  scroll('Greave silver foliage',shinmap,0,.33,.025,silver,sign)
  # Sabaton with overlapping toe plates and leather sole.
  sphere(label+' | leather boot',(sign*.132,-.052,.074),(.063,.139,.064),leather)
  for j in range(6):
   y=-.145+j*.032;z=.067+.019*sin(j/5*pi);rx=.05+.009*sin(j/5*pi)
   o=loft('Sabaton overlapping toe lame',[(z-.015,rx,.027,sign*.132,y),(z+.025,rx*.94,.023,sign*.132,y),(z+.034,rx*.8,.017,sign*.132,y)],steel,32);bevel(o,.002)
  curve('Sabaton welt',[(sign*.132+.062*cos(a),-.054+.14*sin(a),.037) for a in np.linspace(0,2*pi,100)],.003,dark,True)
 # Two hanging mail panels and protective tassets, center allows stride.
 for sign in [-1,1]:
  chain_patch('Riveted mail skirt',22,17,lambda i,j,sg=sign:(sg*(.027+i*.01),-.125-.012*sin(i*.35),1.032-j*.011),mail,.006)
  for j in range(4):
   z=1.016-j*.041;cx=sign*(.115+j*.004);width=.072+j*.001
   vs=[(cx-width,-.151,z),(cx+width,-.149,z),(cx+width+.004,-.156,z-.047),(cx-width-.004,-.16,z-.047)]
   o=mesh('Suspended tasset lame',vs,[(0,1,2,3)],steel);solid(o,.003);bevel(o,.003)
   curve('Tasset chased edge',[vs[3],vs[2]],.002,silver)
   for x in [cx-width+.012,cx+width-.012]:rivet((x,-.163,z-.025),.0025,gold)
 # Cape continuous woven sheet, cut hem; shoulder attachment is only pinned region.
 nx,ny=48,64;vs=[];fs=[]
 def capept(u,v):
  x=(u-.5)*(.48+.52*v);z=1.594-.027*sin(pi*u)*(1-v)-1.43*v+(.018*sin(u*17*pi)+.011*sin(u*31*pi)+.008*sin(u*47*pi))*(v**9)+.045*(abs(u-.5)*2)**5*v
  y=.18+.09*v+.045*sin(6*pi*u+.35)*sin(pi*v*.8)+.016*sin(14*pi*u)*v-.24*(abs(2*u-1)**2.4)*((1-v)**5)
  # Fit the initial sewn cape outside the upper sleeve volumes. A planar
  # shoulder wrap previously began inside the arm and stretched on frame2.
  if v>.025:
   sleeve=[(1.19,.335,.068,.067),(1.28,.319,.08,.078),(1.44,.278,.095,.087),(1.51,.256,.088,.08)]
   for a,b in zip(sleeve[:-1],sleeve[1:]):
    if a[0]<=z<=b[0]:
     t=(z-a[0])/(b[0]-a[0]);cx=a[1]*(1-t)+b[1]*t;rx=a[2]*(1-t)+b[2]*t;ry=a[3]*(1-t)+b[3]*t
     for sg in [-1,1]:
      k=((x-sg*cx)/rx)**2
      if k<1:y=max(y,.015+ry*sqrt(1-k)+.014)
   for sg in [-1,1]:
    k=((x-sg*.356)/.088)**2+((z-1.17)/.28)**2
    if k<1:y=max(y,.012+.095*sqrt(1-k)+.014)
  return (x,y,z)
 for j in range(ny+1):
  for i in range(nx+1):vs.append(capept(i/nx,j/ny))
 for j in range(ny):
  for i in range(nx):
   if j>60 and i in [8,35]:continue
   a=j*(nx+1)+i;fs.append((a,a+nx+1,a+nx+2,a+1))
 cap=mesh('Cape | seven-lantern ceremonial wool',vs,fs,cape_mat);uv=cap.data.uv_layers.new(name='Tailored cloth UV')
 for poly in cap.data.polygons:
  for li in poly.loop_indices:
   vi=cap.data.loops[li].vertex_index;uv.data[li].uv=(vi%(nx+1)/nx,1-vi//(nx+1)/ny)
 pins=cap.vertex_groups.new(name='Shoulder fastenings')
 for i in range((nx+1)*2):pins.add([i],1 if i<nx+1 else .8,'REPLACE')
 cm=cap.modifiers.new('Weighted wool simulation','CLOTH');cm.settings.quality=12;cm.settings.mass=.2;cm.settings.air_damping=3;cm.settings.tension_stiffness=80;cm.settings.compression_stiffness=80;cm.settings.shear_stiffness=50;cm.settings.bending_stiffness=.35;cm.settings.vertex_group_mass=pins.name
 cm.collision_settings.use_self_collision=True;cm.collision_settings.self_distance_min=.0025;cm.collision_settings.distance_min=.004;cm.collision_settings.collision_quality=4;cm.point_cache.frame_start=1;cm.point_cache.frame_end=100
 sub(cap,1);solid(cap,.0024)
 # Shoulder clasps and physical leather tabs.
 for sign in [-1,1]:
  sphere('Cape hammered clasp',(sign*.176,-.087,1.568),(.021,.008,.024),gold)
  ring('Clasp inlaid silver',(sign*.176,-.097,1.568),(1,0,0),(0,0,1),.014,.0016,silver,.2,6.0)
  curve('Cape suspension cord',[(sign*.176,-.092,1.56),(sign*.12,-.128,1.54),(sign*.06,-.13,1.53)],.0025,gold)
 # Root supports a small physical turn test; no combat animation claim.
 root=bpy.data.objects.new('CHARACTER | shoulder-turn study',None);bpy.context.collection.objects.link(root)
 for o in list(S.objects):
  if o!=root and o.type in ['MESH','CURVE']:o.parent=root
 root['scope']='Original studio outfit. No production skinning; cloth test is a shoulder-turn, not a gameplay attack.'
 make_sword(steel,silver,gold,leather,bone,dark)
 refine(chest,root)
 setup()
 bpy.context.view_layer.objects.active=cap;cap.select_set(True)
 bpy.ops.wm.save_as_mainfile(filepath=str(D/'last-vigil.blend'))
 inventory()


def make_sword(steel,silver,gold,leather,bone,dark):
 # Display hilt at z1.45, point down. Full blade length1.28m, grip .28m.
 parts=[];before=set(bpy.context.scene.objects);sx=.71;sy=-.01
 # Carefully sectioned fuller, raised lands, sharpened bevels, tapered spear point.
 rows=[(.10,.0),(.23,.025),(.48,.042),(1.05,.050),(1.24,.054),(1.30,.049),(1.37,.049)]
 vs=[];fs=[];N=10
 # Profile across width: edge, bevel, flat, groove shoulder, groove valley, ridge mirrored.
 profile=[(-1,.0008),(-.77,.0055),(-.32,.006),(-.23,.004),(-.12,.003),(.12,.003),(.23,.004),(.32,.006),(.77,.0055),(1,.0008)]
 for z,w in rows:
  for x,thick in profile:vs.append((sx+x*w,sy-thick,z))
 for j in range(len(rows)-1):
  for i in range(N-1):a=j*N+i;fs.append((a,a+1,a+N+1,a+N))
 blade=mesh('OATHWAKE | forged blade with recessed fuller',vs,fs,steel,False);solid(blade,.006);bevel(blade,.0006,2)
 for sign in [-1,1]:
  # Bright polished bevel strip distinct from blackened body.
  v=[];f=[]
  for z,w in rows:
   v.extend([(sx+sign*w,sy-.001,z),(sx+sign*w*.77,sy-.0061,z)])
  for j in range(len(rows)-1):f.append((j*2,j*2+1,j*2+3,j*2+2))
  mesh('Oathwake | tempered cutting bevel',v,f,silver,False)
 # Gold repair seam zigzags through original steel; not a glow strip.
 repair=[(-.041,1.03),(-.018,1.019),(-.008,1.032),(.008,1.014),(.022,1.025),(.044,1.01)]
 curve('Oathwake | gold brazed fracture',[(sx+x,sy-.010,z) for x,z in repair],.0009,gold)
 # Seven oath marks in fuller, each a designed tiny gate sigil.
 for j in range(7):
  z=.64+j*.052
  curve('Oath mark %d'%(j+1),[(sx-.005,sy-.010,z),(sx-.005,sy-.010,z+.017),(sx+.005,sy-.010,z+.017),(sx+.005,sy-.010,z)],.0006,gold)
  curve('Oath mark crossbar',[(sx-.008,sy-.010,z+.009),(sx+.008,sy-.010,z+.009)],.0005,gold)
 # Ricasso blind arcade, spine medallion.
 for side in [-1,1]:
  curve('Ricasso silver outline',[(sx+side*.039,sy-.008,1.25),(sx+side*.025,sy-.008,1.32),(sx+side*.032,sy-.008,1.366)],.0014,gold)
 ring('Ricasso sun seal',(sx,sy-.008,1.321),(1,0,0),(0,0,1),.018,.0015,gold,.2,6)
 # Guard follows protective swept quillons with carved terminals, not a loose sketch circle.
 for sign in [-1,1]:
  pts=[(sx,sy,1.393),(sx+sign*.045,sy,1.40),(sx+sign*.09,sy+.003,1.39),(sx+sign*.145,sy+.004,1.372),(sx+sign*.175,sy+.005,1.386)]
  curve('Oathwake | swept protective quillon',pts,.009,steel)
  curve('Oathwake | silver guard chase',[(x,y-.009,z+.003) for x,y,z in pts],.0018,gold)
  sphere('Oathwake | lantern quillon terminal',(sx+sign*.175,sy+.005,1.387),(.012,.011,.023),gold,24,16)
  for k in [-1,0,1]:curve('Terminal pierced cage',[(sx+sign*.175+k*.004,sy-.006,1.372),(sx+sign*.175+k*.004,sy-.008,1.402)],.0008,dark)
 # Broken annular relic sits structurally around blade shoulder, 3D socket behind crossguard.
 ring('Oathwake | broken reliquary halo',(sx,sy+.004,1.40),(1,0,0),(0,0,1),.043,.006,gold,.38,5.94)
 for z in [1.43,1.69]:loft('Oathwake grip ferrule',[(z-.009,.019,.014,sx,sy),(z+.009,.019,.014,sx,sy)],gold,32)
 grip=loft('Oathwake | long two-handed leather grip',[(1.436,.016,.012,sx,sy),(1.48,.017,.012,sx,sy),(1.62,.015,.011,sx,sy),(1.683,.016,.012,sx,sy)],leather,48)
 pts=[]
 for i in range(650):
  t=i/649;a=t*2*pi*17;pts.append((sx+.0165*cos(a),sy+.0125*sin(a),1.444+.233*t))
 curve('Oathwake | spiral leather binding seam',pts,.0008,dark)
 for side in [-1,1]:curve('Oathwake ivory grip splint',[(sx+side*.006,sy-.0125,1.452),(sx+side*.005,sy-.012,1.672)],.0013,bone)
 pom=loft('Oathwake | fluted lantern pommel',[(1.699,.012,.011,sx,sy),(1.712,.026,.019,sx,sy),(1.744,.023,.019,sx,sy),(1.764,.008,.007,sx,sy)],steel,48);bevel(pom,.001)
 for i in range(8):
  a=2*pi*i/8;curve('Pommel silver flute',[(sx+.012*cos(a),sy+.011*sin(a),1.704),(sx+.026*cos(a),sy+.019*sin(a),1.72),(sx+.021*cos(a),sy+.018*sin(a),1.748),(sx+.008*cos(a),sy+.007*sin(a),1.763)],.0015,gold)
 swordroot=bpy.data.objects.new('OATHWAKE | display assembly',None);bpy.context.collection.objects.link(swordroot)
 for o in set(S.objects)-before:
  if o!=swordroot:o.parent=swordroot
 swordroot['lore']='Seven keepers swore at the gate. The last broke this blade sealing the Warden inside. Reforged around its fracture, Oathwake carries seven dark oath marks and a missing piece of its reliquary halo.'


def refine(chest,root):
 before=set(S.objects)
 # Reduce exposed neck, keep true eye gap and metal thickness.
 for o in list(S.objects):
  if o.name.startswith(('Helm','Visor','Recessed visor')):o.location.z-=.036
 # Replace buried toe pieces and round knee/elbow ball silhouettes.
 for o in list(S.objects):
  if o.name.startswith(('Sabaton overlapping','Poleyn articulated wing')) or 'pointed poleyn' in o.name or 'couter fan' in o.name:
   bpy.data.objects.remove(o,do_unlink=True)
 # Stitching / worn hem shader. No arbitrary painted rust blankets.
 lining=fabric('12 | Heavy charcoal surcoat',(.014,.012,.013))
 trim=fabric('13 | Antique gold woven binding',(.14,.09,.035))
 for sign,label in [(-1,'L'),(1,'R')]:
  nx,ny=22,30;vs=[];fs=[]
  def tab(u,v):return (sign*(.022+(.18+.03*v)*u),-.139-.014*sin(u*pi*4)*(v*.6+.4)-.028*v,1.035-.52*v+.025*sin(pi*u)*v)
  for j in range(ny+1):
   for i in range(nx+1):vs.append(tab(i/nx,j/ny))
  for j in range(ny):
   for i in range(nx):a=j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
  o=mesh(label+' | tailored split surcoat skirt',vs,fs,lining);solid(o,.0025);sub(o,1)
  uv=o.data.uv_layers.new(name='Woven garment')
  for p in o.data.polygons:
   for k in p.loop_indices:
    vi=o.data.loops[k].vertex_index;uv.data[k].uv=(vi%(nx+1)/nx,vi//(nx+1)/ny)
  for u in [.04,.96]:
   curve('Surcoat gold binding',[(x,y-.003,z) for x,y,z in [tab(u,v) for v in np.linspace(0,1,100)]],.0022,trim)
   for j in range(35):
    x,y,z=tab(u,j/35);curve('Surcoat saddle stitch',[(x-.001,y-.004,z),(x+.001,y-.004,z-.005)],.00055,gold)
  curve('Surcoat stitched lower hem',[(x,y-.003,z) for x,y,z in [tab(u,.97) for u in np.linspace(.04,.96,80)]],.002,trim)
  # Engraved upper arms interrupt empty tubes; retain real part separations.
  def arm(x,z,sg=sign):
   center=sg*(.334-(z-1.22)*.28);r=.076+(z-1.22)*.04
   return (center+x,.015-sqrt(max(.002,r*r-x*x))-.003,z)
  for j in range(2):scroll('Rerebrace chased leaves',arm,0,1.275+j*.069,.023,silver,sign)
  for off in [-.044,.044]:curve('Rerebrace border chase',[arm(off,z) for z in np.linspace(1.25,1.385,50)],.0012,gold)
  # Pointed forged joint caps. Broad rim, medial ridge, subdued wings.
  for joint,cx,cy,cz,rx,rz in [('Poleyn',sign*.118,-.044,.559,.077,.061),('Couter',sign*.351,-.004,1.187,.071,.058)]:
   vs=[];fs=[];N=48;M=14
   for j in range(M+1):
    r=j/M
    for i in range(N):
     a=i/N*2*pi;x=rx*r*cos(a);z=rz*r*sin(a);y=cy-.025-.042*(1-r*r)-.013*exp(-(x/.014)**2)*(1-r)
     vs.append((cx+x,y,cz+z))
   for j in range(M):
    for i in range(N):a=j*N+i;b=j*N+(i+1)%N;fs.append((a,b,b+N,a+N))
   o=mesh(label+' | sculpted '+joint,vs,fs,steel);solid(o,.003);bevel(o,.001)
   curve(joint+' | raised rim',vs[M*N:],.0022,silver,True)
   curve(joint+' | central forged keel',[(cx,cy-.034,cz-rz),(cx,cy-.085,cz),(cx,cy-.035,cz+rz)],.002,silver)
   # Curved guard wings, pointed and folded instead of spheres.
   for sg in [-1,1]:
    pp=[(cx+sg*.05,cy,cz+.032),(cx+sg*.09,cy+.015,cz+.047),(cx+sg*.10,cy+.02,cz),(cx+sg*.085,cy+.012,cz-.045),(cx+sg*.05,cy,cz-.028)]
    wing=mesh(joint+' | scalloped wing',pp,[(0,1,2,3,4)],steel);solid(wing,.003);bevel(wing,.003);curve(joint+' wing silver edge',pp,.0016,silver,True)
  # Sabaton wraps over leather last, each plate actually above the boot.
  for j in range(7):
   ya=-.191+j*.036;yb=ya+.043;cx=sign*.132;vs=[];fs=[];N=28
   for y in [ya,yb]:
    rel=(y+.052)/.145;width=.062*sqrt(max(.08,1-rel*rel));height=.057*sqrt(max(.12,1-rel*rel))
    for i in range(N+1):
     a=pi*i/N;vs.append((cx+width*cos(a),y,.078+height*sin(a)+.007))
   for i in range(N):fs.append((i,i+1,N+2+i,N+1+i))
   o=mesh(label+' | fitted sabaton plate '+str(j),vs,fs,steel);solid(o,.002);bevel(o,.0012)
   curve('Sabaton turned edge',vs[:N+1],.0014,silver)
   for i in [5,23]:rivet(vs[i],.002,gold)
  # Leather retention straps and buckles explain how the metal is worn.
  for z,cx,rx,ry in [(1.31,sign*.313,.086,.086),(.385,sign*.123,.074,.08),(.75,sign*.11,.106,.114)]:
   strap=loft('Leather retention strap',[(z-.009,rx,ry,cx,.006),(z+.009,rx,ry,cx,.006)],leather,48)
   x=cx+sign*rx*.82;y=-ry*.65
   curve('Retention buckle',[(x-.009,y,z-.012),(x+.009,y,z-.012),(x+.009,y,z+.012),(x-.009,y,z+.012)],.0018,gold,True)
  # Shoulder embossed floral medallion and edge filigree.
  cx=sign*.259;cy=-.102;cz=1.52
  ring('Pauldron | chased medallion',(cx,cy,cz),(1,0,0),(0,0,1),.029,.0015,gold)
  for j in range(6):
   a=j*2*pi/6;points=[]
   for t in np.linspace(0,2*pi,40):
    u=.011+.01*cos(t);v=.004*sin(t);points.append((cx+u*cos(a)-v*sin(a),cy-.002,cz+u*sin(a)+v*cos(a)))
   curve('Pauldron six-petal relief',points,.0011,silver,True)
 # Deliberate small repair across chest rather than random noise as storytelling.
 for j in range(4):
  x=-.115+j*.011;z=1.343+j*.004
  p=chest(x,z);curve('Cuirass repaired seam',[(p[0]-.004,p[1]-.001,p[2]-.005),(p[0]+.004,p[1]-.001,p[2]+.005)],.001,gold)
 # Finer filigree flanks the existing main scrolls; embossed relief stays <=1mm.
 for sign in [-1,1]:
  for x,z in [(.132,1.45),(.14,1.34),(.055,1.39),(.046,1.31)]:scroll('Cuirass secondary leaf engraving',chest,sign*x,z,.014,silver,sign)
 # Oathwake: restrained acanthus etching follows the fuller shoulder.
 def bladeface(x,z):return (.71+x,-.017,z)
 for sign in [-1,1]:
  for j in range(3):scroll('Oathwake | engraved gate vine',bladeface,sign*.024,1.09+j*.06,.011,gold,sign)

 # Conform all shoulder relief to the ellipsoidal shell; no floating half-medallions.
 for o in S.objects:
  if o.type=='CURVE' and o.name.startswith(('Pauldron | chased','Pauldron six-petal')):
   for sp in o.data.splines:
    for p in sp.points:
     x,y,z,w=p.co;cx=.259 if x>0 else -.259
     p.co.y=.017-.128*sqrt(max(.015,1-((x-cx)/.113)**2-((z-1.50)/.115)**2))-.0018
 # Thick fitted fur collar forms a soft transition from helm to plate, tapered fibers.
 fibercols=[(.065,.057,.047),(.13,.12,.10),(.22,.205,.18)]
 for tier,col in enumerate(fibercols):
  mat=node_mat('Mantle natural fiber '+str(tier),col,0,.91,30,.00015)
  c=bpy.data.curves.new('Short mantle fibers '+str(tier),'CURVE');c.dimensions='3D';c.bevel_depth=.00048;c.bevel_resolution=1
  for j in range(1800):
   a=random.uniform(0,2*pi);r=random.uniform(.75,1.1);x=.17*cos(a)*r;y=.119*sin(a)*r;z=1.603+.017*sin(a)+random.uniform(-.01,.01);length=random.uniform(.035,.072)
   sp=c.splines.new('POLY');sp.points.add(5)
   for k,p in enumerate(sp.points):
    t=k/5;p.co=(x+.024*cos(a)*t+.004*sin(j+t*3),y+.03*sin(a)*t,z+.011*sin(pi*t)-length*t,1);p.radius=.85*(1-t)**.9+.015
  o=bpy.data.objects.new('Mantle | layered silvered guard hair '+str(tier),c);bpy.context.collection.objects.link(o);c.materials.append(mat)
 # Repaired field pouch sits on the right hip, suspended from two real straps.
 pouch=loft('Field pouch | creased oiled hide',[(.895,.045,.025,.218,.004),(.91,.056,.034,.218,.004),(.991,.054,.031,.218,.004),(1.008,.043,.025,.218,.004)],leather,40);bevel(pouch,.006,4);sub(pouch,1)
 flap=mesh('Field pouch | overlapping flap',[(.164,-.034,1.012),(.272,-.034,1.012),(.265,-.043,.964),(.219,-.048,.947),(.171,-.043,.964)],[(0,1,2,3,4)],leather);solid(flap,.003);bevel(flap,.005)
 curve('Pouch hand-sewn flap perimeter',[(.171,-.039,1.004),(.265,-.039,1.004),(.258,-.048,.967),(.219,-.052,.957),(.178,-.048,.967)],.0008,gold)
 rivet((.219,-.052,.961),.004,gold)
 for x in [.188,.246]:curve('Pouch leather suspension',[(x,-.021,.997),(x,-.015,1.07),(x,.003,1.08)],.004,leather)
 # Seven keeper memorial tags; left hip, one vacant broken link at the end.
 for j in range(7):
  x=-.18-j*.009;z=1.035-.016*j;y=-.075
  ring('Memorial chain link',(x,y,z),(1,0,0),(0,0,1),.008,.0012,gold)
  if j%2==0:
   o=mesh('Keeper memorial tag',[(x-.008,y-.002,z-.011),(x+.008,y-.002,z-.011),(x+.007,y-.003,z-.038),(x-.007,y-.003,z-.038)],[(0,1,2,3)],silver);solid(o,.0015);bevel(o,.001)
   for k in range(j//2+1):curve('Tag incised tally',[(x-.004+k*.002,y-.005,z-.018),(x-.004+k*.002,y-.005,z-.031)],.00035,dark)
 # Small leather repair stitched onto surcoat; readable history without global grime.
 patch=mesh('Surcoat | field repair patch',[(-.169,-.177,.681),(-.108,-.182,.687),(-.099,-.187,.622),(-.165,-.181,.616)],[(0,1,2,3)],leather);solid(patch,.001)
 for j in range(8):
  x=-.162+j*.007;curve('Repair cross stitch',[(x,-.186,.624),(x+.003,-.187,.632)],.0006,gold)
 # Cape fibers at the lower hem: material weathering is localized, not random rust.
 # Kept on the cloth UV/material during motion; no unbound geometry fringe is added.

 # Hidden rounded collision stand-ins cover armor volume, including lower legs/boots.
 # The prior study only had cloth contact on padded thighs and exposed greave penetration.
 for sg in [-1,1]:
  for label,loc,size in [
   ('arm',(sg*.356,.012,1.17),(.088,.095,.28)),
   ('thigh',(sg*.109,.006,.80),(.12,.126,.29)),
   ('calf',(sg*.125,.009,.33),(.092,.103,.26)),
   ('boot',(sg*.132,-.052,.082),(.074,.155,.086))]:
   o=sphere('COLLIDER | '+label,loc,size,dark,24,16);o.hide_render=True;o.display_type='WIRE';collision(o)
 o=sphere('COLLIDER | pelvis',(0,.006,1.02),(.204,.153,.16),dark,32,20);o.hide_render=True;o.display_type='WIRE';collision(o)
 # Refinement objects belong to the character except weapon detail.
 for o in set(S.objects)-before:
  o.parent=bpy.data.objects['OATHWAKE | display assembly'] if o.name.startswith('Oathwake') else root


def setup():
 S.render.engine='CYCLES';S.cycles.samples=32;S.cycles.use_denoising=True
 try:
  pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
  for d in pref.devices:d.use=d.type=='METAL'
  S.cycles.device='GPU'
 except Exception: S.cycles.device='CPU'
 if os.environ.get('BOSSLAB_ART_DEVICE','CPU')!='METAL':S.cycles.device='CPU'
 S.render.resolution_x=1100;S.render.resolution_y=1400;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.render.fps=30
 S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=-.15
 S.world.color=(.12,.12,.12);S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.10,.12,.15,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.4
 wn=S.world.node_tree.nodes;wl=S.world.node_tree.links;path=wn.new('ShaderNodeLightPath');mix=wn.new('ShaderNodeMixShader');back=wn.new('ShaderNodeBackground');back.inputs[0].default_value=(.004,.005,.006,1);back.inputs[1].default_value=.3;wl.new(path.outputs['Is Camera Ray'],mix.inputs[0]);wl.new(wn['Background'].outputs[0],mix.inputs[1]);wl.new(back.outputs[0],mix.inputs[2]);wl.new(mix.outputs[0],wn['World Output'].inputs['Surface'])
 stage=node_mat('Studio charcoal stone',(.025,.029,.032),.1,.76,5,.0008)
 bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=1.05,depth=.06,location=(.18,0,-.018));o=bpy.context.object;o.name='STUDIO | plinth';o.data.materials.append(stage);bevel(o,.015,4)
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.05));o=bpy.context.object;o.name='STUDIO | backdrop';o.data.materials.append(stage)
 def area(name,loc,power,size,color,target):
  data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color;o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 area('Key | large softbox',(-2.6,-3.3,3.8),480,3,(.97,.94,.89),(0,0,1.2))
 area('Rim | warm silver separation',(1.5,1.5,3.0),480,2,(1,.77,.53),(0,0,1.2))
 area('Fill | front long strip',(2,-2,2.2),280,2,(.7,.82,1),(0,0,1.3))
 area('Back cape | softbox',(-1,3,2.7),380,2,(.84,.89,1),(0,0,1.1))
 cam=bpy.data.cameras.new('Studio camera');o=bpy.data.objects.new('Studio camera',cam);bpy.context.collection.objects.link(o);S.camera=o;cam.lens=65
 camera('hero');S.frame_start=1;S.frame_end=100
 S['evidence']='Actual original Blender geometry render; not gameplay, no generative image or downloaded asset.'

def camera(view):
 views={'hero':((2.55,-5.4,2.35),(.16,0,1.0),78), 'front':((.15,-6,2.0),(.16,0,1.0),75),'back':((-2.5,5.1,2.5),(0,.1,1.04),75),'armor':((1.55,-3.1,2.05),(0,-.02,1.48),90),'sword':((1.6,-3.0,1.3),(.71,0,.94),58),'hilt':((1.28,-1.65,1.75),(.71,0,1.48),95),'cloth':((-2.4,4.7,2.5),(0,.15,1.08),70)}
 pos,target,lens=views.get(view,views['hero']);o=S.camera;o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens

def inventory():
 meshes=[o for o in S.objects if o.type=='MESH' and not o.name.startswith('STUDIO')]
 data={'kind':'Original editable Blender studio model; not integrated into Unreal','mesh_objects':len(meshes),'curve_objects':len([o for o in S.objects if o.type=='CURVE']),'base_vertices':sum(len(o.data.vertices) for o in meshes),'base_polygons':sum(len(o.data.polygons) for o in meshes),'materials':len(bpy.data.materials),'blender_version':bpy.app.version_string,'generated_images':[im.name for im in bpy.data.images if im.packed_file],'cloth_vertices':len(bpy.data.objects['Cape | seven-lantern ceremonial wool'].data.vertices),'external_character_assets':False,'gameplay_changes':False,'lore':bpy.data.objects['OATHWAKE | display assembly']['lore']}
 (E/'model-inventory.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data))

def render(view):
 camera(view);S.render.filepath=str(E/(view+'.png'));bpy.ops.render.render(write_still=True)

def audit_cloth():
 cap=bpy.data.objects['Cape | seven-lantern ceremonial wool'];root=bpy.data.objects['CHARACTER | shoulder-turn study']
 pc=cap.modifiers['Weighted wool simulation'].point_cache
 assert pc.is_baked
 after=False;disabled=[]
 for mod in cap.modifiers:
  if after:disabled.append((mod,mod.show_viewport));mod.show_viewport=False
  if mod.type=='CLOTH':after=True
 base=[v.co.copy() for v in cap.data.vertices];edges=[(e.vertices[0],e.vertices[1]) for e in cap.data.edges]
 rest=[(base[a]-base[b]).length for a,b in edges];samples=[];last=None;probe_index=64*49+24;probes=[]
 for f in range(1,101):
  S.frame_set(f);ev=cap.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[v.co.copy() for v in me.vertices]
  assert len(pts)==len(base),(len(pts),len(base))
  assert all(math.isfinite(v) for p in pts for v in p)
  world=[ev.matrix_world@p for p in pts];ratios=[(pts[a]-pts[b]).length/r for (a,b),r in zip(edges,rest) if r>1e-6]
  samples.append({'frame':f,'max_edge_stretch':max(ratios),'p99_edge_stretch':sorted(ratios)[int(.99*(len(ratios)-1))],'worst_edge':list(edges[ratios.index(max(ratios))]),'min_world_z':min(p.z for p in world),'hem_local':list(pts[probe_index]),'max_vertex_step':max((p-q).length for p,q in zip(pts,last)) if last else 0})
  probes.append(pts[probe_index]);last=pts;ev.to_mesh_clear()
 for mod,val in disabled:mod.show_viewport=val
 data={'kind':'Numerical baked cloth checks; not proof of zero clipping or production animation','frames':100,'vertices':len(base),'max_edge_stretch':max(x['max_edge_stretch'] for x in samples),'min_world_z':min(x['min_world_z'] for x in samples),'max_vertex_step_m':max(x['max_vertex_step'] for x in samples),'hem_local_displacement_m':max((p-probes[0]).length for p in probes),'samples':samples}
 (E/'cloth-audit.json').write_text(json.dumps(data,indent=2)+'\n');print('CLOTH_AUDIT',json.dumps({k:v for k,v in data.items() if k!='samples'}))

def asset_audit():
 dg=bpy.context.evaluated_depsgraph_get();count=0;tri=0;objects=0;bounds=[]
 for o in S.objects:
  if o.type not in ['MESH','CURVE'] or o.hide_render or o.name.startswith('STUDIO'):continue
  ev=o.evaluated_get(dg);me=ev.to_mesh();objects+=1;count+=len(me.vertices)
  for v in me.vertices:
   assert all(math.isfinite(a) for a in v.co),o.name
  me.calc_loop_triangles();tri+=len(me.loop_triangles)
  bounds.extend([list(ev.matrix_world@Vector(v)) for v in o.bound_box]);ev.to_mesh_clear()
 data={'kind':'Editable studio geometry validation, not a game-performance or artistic-quality test','renderable_objects':objects,'evaluated_vertices':count,'evaluated_triangles':tri,'finite_vertices':True,'packed_authored_images':len([x for x in bpy.data.images if x.packed_file]),'bounds_m':[[min(p[i] for p in bounds) for i in range(3)],[max(p[i] for p in bounds) for i in range(3)]],'production_body_rig':False,'runtime_lods':False,'blender':bpy.app.version_string}
 (E/'asset-audit.json').write_text(json.dumps(data,indent=2)+'\n');print('ASSET_AUDIT',json.dumps(data))

if mode=='draft':
 make()
 if len(args)<2 or args[1]!='no-render':render('hero')
else:
 bpy.ops.wm.open_mainfile(filepath=str(D/('last-vigil-motion.blend' if mode=='finish' else 'last-vigil.blend')));S=bpy.context.scene
 try:
  pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
  for dev in pref.devices:dev.use=dev.type=='METAL'
  S.cycles.device='GPU'
 except Exception:S.cycles.device='CPU'
 if os.environ.get('BOSSLAB_ART_DEVICE','CPU')!='METAL':S.cycles.device='CPU'
 if mode=='polish':
  import bmesh
  for filename in ['last-vigil.blend','last-vigil-motion.blend']:
   bpy.ops.wm.open_mainfile(filepath=str(D/filename));S=bpy.context.scene
   for ob in S.objects:
    if ' | articulated pauldron ' in ob.name:
     bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table()
     inds=list(reversed(range(40))) if ob.name.startswith('R') else list(range(40))
     try:bm.faces.new([bm.verts[i] for i in inds])
     except ValueError:pass
     bm.normal_update();bm.to_mesh(ob.data);bm.free()
    if ob.type=='CURVE' and (ob.name.startswith('Oath mark') or ob.name.startswith('Oathwake | gold brazed fracture')):
     for sp in ob.data.splines:
      for pt in sp.points:pt.co.y=-.020
   S['cosmetic_revision']='Closed pauldron caps and visible oath marks; cape mesh/cache unchanged from cloth clip'
   S.cycles.device='CPU';bpy.ops.wm.save_as_mainfile(filepath=str(D/filename))
  print('Cosmetic correction saved; existing cloth cache preserved.')
 elif mode=='render':
  for v in args[1:] or ['front','back','armor','hilt']:render(v)
 elif mode=='finish':
  cap=bpy.data.objects['Cape | seven-lantern ceremonial wool'];assert cap.modifiers['Weighted wool simulation'].point_cache.is_baked
  camera('cloth');S.cycles.samples=12;S.render.resolution_x=720;S.render.resolution_y=900
  folder=E/'cloth-frames';folder.mkdir(exist_ok=True)
  for frame in range(1,101):
   S.frame_set(frame);dest=folder/f'frame-{frame-1:06d}.png'
   if not dest.exists():S.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
   print('FINAL_FRAME',frame,flush=True)
  S.frame_set(25);S.render.resolution_x=1400;S.render.resolution_y=1800;S.cycles.samples=48
  for v in ['hero','front','back','armor','hilt','sword']:
   dest=E/(v+'.png')
   if not dest.exists() or struct.unpack('>II',dest.read_bytes()[16:24])!=(1400,1800):render(v)
  camera('hero');S['last_review_render_device']=S.cycles.device;S.cycles.device='CPU'
  for mat in bpy.data.materials:
   if mat.use_nodes:
    ramps=[n for n in mat.node_tree.nodes if n.type=='VALTORGB']
    if ramps:mat.diffuse_color=ramps[0].color_ramp.elements[-1].color
  for screen in bpy.data.screens:
   for area in screen.areas:
    if area.type=='VIEW_3D':
     sp=area.spaces.active;sp.region_3d.view_location=Vector((.12,0,1.0));sp.region_3d.view_distance=3.7;sp.region_3d.view_rotation=S.camera.rotation_euler.to_quaternion();sp.overlay.show_extras=False;sp.shading.color_type='MATERIAL'
  for ob in S.objects:
   if ob.name.startswith('COLLIDER |'):ob.hide_set(True)
  bpy.ops.wm.save_as_mainfile(filepath=str(D/'last-vigil-motion.blend'))
  audit_cloth();inventory();asset_audit()


 elif mode=='audit':inventory()
 elif mode=='cloth':
  root=bpy.data.objects['CHARACTER | shoulder-turn study'];cap=bpy.data.objects['Cape | seven-lantern ceremonial wool']
  for frame,angle,x in [(1,0,0),(25,0,0),(45,.42,.05),(65,-.26,-.04),(85,0,0),(100,0,0)]:
   root.rotation_euler.z=angle;root.location.x=x;root.keyframe_insert('rotation_euler',frame=frame);root.keyframe_insert('location',frame=frame)
  S.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(D/'last-vigil-motion.blend'))
  pc=cap.modifiers['Weighted wool simulation'].point_cache;pc.use_disk_cache=True;pc.frame_start=1;pc.frame_end=100
  with bpy.context.temp_override(point_cache=pc,active_object=cap,object=cap):bpy.ops.ptcache.bake(bake=True)
  assert pc.is_baked,'Cloth bake not completed'
  (E/'cloth-bake.json').write_text(json.dumps({'baked':pc.is_baked,'frames':100,'vertices':len(cap.data.vertices),'pin_group':'Shoulder fastenings','self_collision':True,'motion':'Authored root turn only, not locomotion/combat animation'},indent=2)+'\n')
  camera('cloth');S.render.engine='CYCLES';S.cycles.samples=12;S.render.resolution_x=720;S.render.resolution_y=900
  folder=E/'cloth-frames';folder.mkdir(exist_ok=True);trace=[]
  for frame in range(1,101):
   S.frame_set(frame);dg=bpy.context.evaluated_depsgraph_get();obj=cap.evaluated_get(dg);me=obj.to_mesh();world=[obj.matrix_world@v.co for v in me.vertices];trace.append({'frame':frame,'min_z':min(p.z for p in world),'max_y':max(p.y for p in world),'min_y':min(p.y for p in world),'hem_probe':list(world[min(len(world)-1,3184)])});obj.to_mesh_clear()
   if len(args)<2 or args[1]!='probe' or frame in [1,25,45,65,100]:
    S.render.filepath=str(folder/f'frame-{frame-1:06d}.png');bpy.ops.render.render(write_still=True)
   print('CLOTH_FRAME',frame,flush=True)
  (E/'cloth-trace.json').write_text(json.dumps(trace,indent=2)+'\n');bpy.ops.wm.save_as_mainfile(filepath=str(D/'last-vigil-motion.blend'));audit_cloth()
