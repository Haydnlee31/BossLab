"""Last Vigil v5: original constructive character revision, separate studio master.
Uses v1 authoring utilities and its saved static master; never overwrites v1 evidence.
No imported character art. Static tailored folds are not a simulated cache.
"""
from pathlib import Path
base=Path(__file__).with_name('last_vigil.py')
exec(compile(base.read_text().split("if mode=='draft':")[0],str(base),'exec'))
D=R/'unreal/art-studio/revision-v5-2026-11-07';E=R/'artifacts/art/last-vigil-v5';D.mkdir(exist_ok=True);E.mkdir(exist_ok=True)

base_curve=curve
def curve(*a,**kw):
 o=base_curve(*a,**kw);o.data.use_fill_caps=True;return o

def drop(starts):
 for o in list(S.objects):
  if any(o.name.startswith(p) or p.startswith('*') and p[1:] in o.name for p in starts):bpy.data.objects.remove(o,do_unlink=True)

def mat_simple(name,color,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough;m.diffuse_color=(*color,1);return m

def wornsteel(name,color):
 m=mat_simple(name,color,.88,.47);n=m.node_tree.nodes;l=m.node_tree.links;b=n.get('Principled BSDF');co=n.new('ShaderNodeTexCoord')
 noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=155;noise.inputs['Detail'].default_value=2;l.new(co.outputs['Object'],noise.inputs['Vector'])
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.00008;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],b.inputs['Normal'])
 r=n.new('ShaderNodeMapRange');r.inputs['To Min'].default_value=.43;r.inputs['To Max'].default_value=.54;l.new(noise.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],b.inputs['Roughness'])
 # Restrained micro-tonal steel grain, distinct from the rejected broad cloudy mottling.
 colors=n.new('ShaderNodeValToRGB');colors.color_ramp.elements[0].color=(*[x*.97 for x in color],1);colors.color_ramp.elements[1].color=(*[x*1.03 for x in color],1);l.new(noise.outputs['Fac'],colors.inputs[0]);l.new(colors.outputs['Color'],b.inputs['Base Color'])
 # Fine directional polishing is roughness/bump, not cloudy base color.
 mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(4,4,95);l.new(co.outputs['Object'],mapping.inputs[0])
 scratches=n.new('ShaderNodeTexNoise');scratches.inputs['Scale'].default_value=60;scratches.inputs['Detail'].default_value=2;l.new(mapping.outputs[0],scratches.inputs['Vector'])
 fine=n.new('ShaderNodeBump');fine.inputs['Strength'].default_value=.12;fine.inputs['Distance'].default_value=.000055;l.new(scratches.outputs['Fac'],fine.inputs['Height']);l.new(bump.outputs[0],fine.inputs['Normal']);l.new(fine.outputs[0],b.inputs['Normal'])
 return m

def surface(name,rows,mat,n=64):
 # Cross-sections front=-Y, broad temples taper to actual chin/waist. Deliberate planes.
 vs=[];fs=[]
 for z,rx,ry,cy,ridge in rows:
  for i in range(n):
   a=2*pi*i/n;x=rx*cos(a);y=cy+ry*sin(a)-ridge*max(0,-sin(a))**16
   vs.append((x,y,z))
 for j in range(len(rows)-1):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;fs.append((a,b,b+n,a+n))
 fs.extend([tuple(reversed(range(n))),tuple((len(rows)-1)*n+i for i in range(n))]);o=mesh(name,vs,fs,mat);bevel(o,.0015,3);return o

def plate_patch(name,vs,faces,mat,t=.002):
 o=mesh(name,vs,faces,mat);solid(o,t);bevel(o,.0012);return o

def v5_curve(points,t):
 q=max(0,min(1,t))*(len(points)-1);j=min(len(points)-2,int(q));f=q-j;a=Vector(points[j]);b=Vector(points[j+1]);prev=Vector(points[max(0,j-1)]);nxt=Vector(points[min(len(points)-1,j+2)])
 return (2*f**3-3*f*f+1)*a+(f**3-2*f*f+f)*(b-prev)*.4+(-2*f**3+3*f*f)*b+(f**3-f*f)*(nxt-a)*.4

def v5_wool(material,base=None):
 n=material.node_tree.nodes;l=material.node_tree.links;bs=n.get('Principled BSDF')
 if base is not None:
  for link in list(bs.inputs['Base Color'].links):l.remove(link)
  bs.inputs['Base Color'].default_value=(*base,1)
 bs.inputs['Metallic'].default_value=0;bs.inputs['Specular IOR Level'].default_value=.07;bs.inputs['Sheen Weight'].default_value=.035
 for socket in ['Roughness','Normal']:
  for link in list(bs.inputs[socket].links):l.remove(link)
 co=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(co.outputs['Object'],sep.inputs[0]);waves=[]
 for axis,pitch in [('X',.0008),('Z',.0011)]:
  scale=n.new('ShaderNodeMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=2*pi/pitch;l.new(sep.outputs[axis],scale.inputs[0]);wave=n.new('ShaderNodeMath');wave.operation='SINE';l.new(scale.outputs[0],wave.inputs[0]);waves.append(wave)
 twill=n.new('ShaderNodeMath');twill.operation='MULTIPLY';l.new(waves[0].outputs[0],twill.inputs[0]);l.new(waves[1].outputs[0],twill.inputs[1]);b=n.new('ShaderNodeBump');b.inputs['Distance'].default_value=.00014;b.inputs['Strength'].default_value=.35;l.new(twill.outputs[0],b.inputs['Height']);l.new(b.outputs[0],bs.inputs['Normal']);rough=n.new('ShaderNodeMapRange');rough.inputs['From Min'].default_value=-1;rough.inputs['From Max'].default_value=1;rough.inputs['To Min'].default_value=.90;rough.inputs['To Max'].default_value=.98;l.new(twill.outputs[0],rough.inputs[0]);l.new(rough.outputs[0],bs.inputs['Roughness'])
 material['weave_pitch_m']=[.0008,.0011];material['scope']='Physical-scale woven bump/roughness; no simulation or scanned texture.'

def v5_stitches(name,surface,u,count,material,back=False):
 data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=.00025;data.bevel_resolution=0
 for j in range(count):
  v=.025+.95*j/max(1,count-1);a=Vector(surface(u-.002,v-.001));b=Vector(surface(u+.002,v+.001));a.y+=.001 if back else -.001;b.y+=.001 if back else -.001
  sp=data.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1)
 ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob);data.materials.append(material);return ob


def revise():
 global S,steel,silver,gold,dark,leather,cloth,mail
 bpy.ops.wm.open_mainfile(filepath=str(R/'unreal/art-studio/last-vigil.blend'));S=bpy.context.scene;S.frame_set(1)
 root=bpy.data.objects['CHARACTER | shoulder-turn study'];root.animation_data_clear();root.location=(0,0,0);root.rotation_euler=(0,0,0)
 before=set(S.objects)
 steel=wornsteel('V2 | charcoal tempered steel',(.043,.044,.046));silver=wornsteel('V2 | rubbed steel edges',(.090,.091,.092));gold=wornsteel('V2 | subdued aged brass',(.20,.132,.052));dark=mat_simple('V2 | light absorbing recess',(.006,.007,.008),.15,.8)
 leather=mat_simple('V2 | dark oiled hide',(.019,.011,.008),0,.65);cloth=mat_simple('V2 | quilted arming cloth',(.012,.013,.015),0,.96);mail=wornsteel('V2 | iron mail',(.07,.075,.08))
 # Replace all cloud-noise armor with restrained fine grain; edge brightening is authored at actual edges.
 for o in S.objects:
  if o.type not in ['MESH','CURVE']:continue
  for i,ma in enumerate(o.data.materials):
   if not ma:continue
   if ma.name.startswith('01 '):o.data.materials[i]=steel
   elif ma.name.startswith('02 '):o.data.materials[i]=silver
   elif ma.name.startswith('03 '):o.data.materials[i]=gold
   elif ma.name.startswith('04 '):o.data.materials[i]=dark
   elif ma.name.startswith('05 '):o.data.materials[i]=leather
 # Remove repeated applique and primitive body assemblies rather than decorate them.
 drop(['Peened rivet','Helm','Visor','Recessed visor','Gorget','Visible coif','Mantle','*articulated pauldron','Pauldron','Cuirass chased','Cuirass secondary','Ribbed chest arch','Broken oath halo','Cuirass repaired seam','Vambrace vine','Vambrace longitudinal','Rerebrace chased','Rerebrace border','Greave silver foliage','Greave fluting','Couter chased','*leather glove','*metacarpal lame','Gauntlet','Cape hammered','Clasp inlaid','Cape suspension','Suspended tasset','Tasset chased','*tailored split surcoat','Surcoat gold','Surcoat saddle','Surcoat stitched','Surcoat | field repair','Repair cross','Cuirass | shaped','Rolled cuirass','Forged sternum'])
 # Fit padded underlayers INSIDE plate volumes; unchanged v1 sleeves protruded through replacement steel.
 for ob in S.objects:
  if ob.type=='MESH' and (ob.name=='Padded arming doublet' or 'arming sleeve' in ob.name):
   for vertex in ob.data.vertices:
    p=vertex.co
    if ob.name=='Padded arming doublet':p.x*=.86;p.y=.01+(p.y-.01)*.82
    else:
     center=(-1 if ob.name.startswith('L') else 1)*(.335-(p.z-1.19)*.25);p.x=center+(p.x-center)*.86;p.y=.015+(p.y-.015)*.83
 # Sculpted breast volume: flatter upper chest, deep sternum arris, rounded protective belly.
 surface('V2 | cuirass forged volume',[(1.16,.136,.111,-.002,.008),(1.20,.142,.119,0,.018),(1.29,.166,.139,0,.027),(1.39,.202,.146,.005,.030),(1.48,.224,.122,.012,.013),(1.54,.205,.10,.015,.005),(1.575,.112,.084,.018,0)],steel)
 # Asymmetrical seam and discreet peened repairs establish use rather than wire flowers.
 for sign in [-1,1]:
  pts=[(sign*x,y,z) for x,y,z in [(.11,-.02,1.572),(.178,-.067,1.538),(.209,-.061,1.46),(.176,-.082,1.31),(.14,-.065,1.19)]]
  curve('V2 | breastplate folded edge',pts,.0018,silver)
  for x,y,z in pts[1:-1]:rivet((x,y-.002,z),.0027,gold)
 curve('V2 | sternum forged arris',[(0,-.098,1.56),(0,-.144,1.48),(0,-.163,1.39),(0,-.165,1.29),(0,-.132,1.20)],.0012,silver)
 # High protective bevor envelops neck; no exposed cylindrical gorget.
 surface('V2 | enclosing bevor',[(1.53,.115,.085,.012,0),(1.58,.119,.097,.012,.015),(1.625,.108,.103,.013,.02),(1.67,.09,.09,.014,.012)],steel,64)
 curve('V2 | bevor folded upper lip',[(.092*cos(a),.014+.092*sin(a)-.012*max(0,-sin(a))**12,1.67) for a in np.linspace(0,2*pi,100)],.0018,silver)
 # Seated sallet skull; swept occipital tail and ridge replace elongated egg/crown.
 skull=surface('V2 | low ridged sallet',[(1.648,.084,.095,.03,0),(1.68,.102,.111,.025,.006),(1.75,.111,.111,.019,.008),(1.81,.102,.099,.021,.01),(1.845,.080,.078,.023,.005),(1.868,.052,.050,.022,.003),(1.879,.024,.023,.022,.001),(1.882,.003,.003,.022,0)],steel,64);sub(skull,1)
 # Rear neck flange sweeping down towards shoulder mantle.
 vs=[];fs=[];N=48
 for j in range(5):
  q=j/4
  for i in range(N+1):
   a=pi*i/N;vs.append(((.103+.025*q)*cos(a),.022+(.108+.05*q)*sin(a),1.70-.075*q+.012*cos(a)**2))
 for j in range(4):
  for i in range(N):k=j*(N+1)+i;fs.append((k,k+1,k+N+2,k+N+1))
 plate_patch('V2 | sallet swept neck flange',vs,fs,steel)
 curve('V2 | sallet flange rolled edge',vs[-N-1:],.002,silver)
 # Visor front forms deliberately faceted wedge, not a round can.
 rows=[(1.651,.064,-.098),(1.675,.091,-.122),(1.72,.105,-.145),(1.752,.109,-.127)]
 vs=[];fs=[]
 for z,rx,y in rows:
  vs.extend([(-rx,-.037,z),(-rx*.72,y+.025,z+.003),(0,y-.014,z+.006),(rx*.72,y+.025,z+.003),(rx,-.037,z)])
 for j in range(3):
  for i in range(4):k=j*5+i;fs.append((k,k+1,k+6,k+5))
 plate_patch('V2 | angular fitted visor',vs,fs,steel)
 curve('V2 | narrow eye slot',[(-.095,-.08,1.760),(-.065,-.123,1.761),(0,-.146,1.758),(.065,-.123,1.761),(.095,-.08,1.760)],.0035,dark)
 curve('V2 | peaked brow',[(-.104,-.057,1.77),(-.07,-.121,1.774),(0,-.148,1.77),(.07,-.121,1.774),(.104,-.057,1.77)],.002,silver)
 for sg in [-1,1]:
  sphere('V2 | visor flush pivot',(sg*.107,-.026,1.757),(.006,.003,.006),gold,20,12)
  for j in range(4):
   x=sg*(.033+.012*j);y=-.143+abs(x)*.33
   curve('V2 | breathing slot',[(x,y,1.692),(x+sg*.004,y+.001,1.71)],.0012,dark)
 # Seat head into bevor after all helmet fittings are built.
 for ob in S.objects:
  if ob.name.startswith(('V2 | low ridged','V2 | sallet','V2 | angular fitted','V2 | narrow eye','V2 | peaked brow','V2 | visor flush','V2 | breathing slot')):ob.location.z-=.022
 # Low overlapping swept shoulders. Each plate is a continuous open shell; left has larger rear protection.
 for sg,label in [(-1,'L'),(1,'R')]:
  for j in range(4):
   vs=[];fs=[];N=48;M=12;big=1.12 if sg==-1 else 1
   for k in range(M+1):
    q=k/M;ang=.25+q*1.45
    for i in range(N+1):
     a=2*pi*i/N;rear=max(0,sin(a));ca=math.copysign(abs(cos(a))**.7,cos(a));sa=math.copysign(abs(sin(a))**.7,sin(a));x=sg*(.252+j*.021+(.104-j*.008)*sin(ang)*ca*big);y=.018+(.122-j*.009)*sin(ang)*sa
     z=1.505-j*.033+(.038-j*.003)*cos(ang)-.026*rear*q+.009*cos(a)*q-.021*(max(0,-sin(a))**7)*(q**3)
     vs.append((x,y,z))
   for k in range(M):
    for i in range(N):a=k*(N+1)+i;fs.append((a,a+1,a+N+2,a+N+1))
   fs.append(tuple(range(N-1,-1,-1)));plate_patch('V2 | '+label+' swept shoulder lame '+str(j),vs,fs,steel)
   curve('V2 | shoulder turned steel edge',vs[-N-1:],.0016,silver)
   for i in [6,18,30,42]:rivet(vs[-N-1+i],.0026,gold)
  # Natural curved fingers with staggered lengths, knuckle plates and opposable thumb.
  cx=sg*.394;cy=-.018
  palm=sphere('V2 | '+label+' fitted palm',(cx,cy,.925),(.041,.025,.051),leather)
  vs=[];fs=[]
  for j in range(7):
   t=j/6;z=.956-.056*t;width=.038-.004*t
   for k in range(9):u=k/8;vs.append((cx+(u-.5)*2*width,-.045-.004*sin(pi*u),z))
  for j in range(6):
   for k in range(8):q=j*9+k;fs.append((q,q+1,q+10,q+9))
  plate_patch('V2 | '+label+' curved gauntlet backplate',vs,fs,steel)
  for f,length in enumerate([.060,.072,.067,.052]):
   x=cx+sg*(f-1.5)*.017
   def fp(t):return Vector((x+sg*.006*t,cy-.012-.033*t*t,.902-length*t))
   finger=curve('V2 | tapered curved leather finger',[fp(t) for t in np.linspace(0,1,20)],.0072,leather)
   for k,pt in enumerate(finger.data.splines[0].points):pt.radius=1-.38*k/19
   for j in range(3):
    vs=[];fs=[];t0=j/3;t1=(j+.9)/3
    for row in range(5):
     t=t0+(t1-t0)*row/4;c=fp(t);rad=.0073*(1-.32*t)
     for k in range(13):
      a=pi*k/12;vs.append((c.x+rad*cos(a),c.y-.002-rad*sin(a),c.z))
    for row in range(4):
     for k in range(12):q=row*13+k;fs.append((q,q+1,q+14,q+13))
    plate_patch('V2 | dorsal finger plate',vs,fs,steel,.0008)
   sphere('V2 | rounded leather finger tip',fp(1),(.0046,.0052,.0055),leather,20,12)
   sphere('V2 | flattened knuckle plate',(x,-.047,.907),(.0085,.0025,.0065),steel,20,12)
  thumbpts=[(cx-sg*.03,-.017,.946),(cx-sg*.045,-.025,.931),(cx-sg*.052,-.035,.91),(cx-sg*.046,-.049,.892)]
  thumb=curve('V2 | opposed padded thumb',thumbpts,.0115,leather)
  for k,pt in enumerate(thumb.data.splines[0].points):pt.radius=1-.35*k/3
  shell=curve('V2 | fitted thumb protective shell',[(x,y-.002,z+.001) for x,y,z in thumbpts[1:]],.009,steel)
  for k,pt in enumerate(shell.data.splines[0].points):pt.radius=1-.4*k/2
  sphere('V2 | rounded thumb terminus',thumbpts[-1],(.0062,.007,.0075),leather,20,12)
 # A pointed sanctuary gate panel: recessed dark center, forged surround, seven peened oath fixings.
 outline=[(-.026,1.23),(-.028,1.445),(-.018,1.475),(0,1.495),(.018,1.475),(.028,1.445),(.026,1.23)]
 def chestfront(x,z):
  rr=[(1.16,.136,.111,-.002,.008),(1.20,.142,.119,0,.018),(1.29,.166,.139,0,.027),(1.39,.202,.146,.005,.030),(1.48,.224,.122,.012,.013),(1.54,.205,.10,.015,.005),(1.575,.112,.084,.018,0)]
  for a,b in zip(rr[:-1],rr[1:]):
   if a[0]<=z<=b[0]:
    t=(z-a[0])/(b[0]-a[0]);rx=a[1]*(1-t)+b[1]*t;ry=a[2]*(1-t)+b[2]*t;cy=a[3]*(1-t)+b[3]*t;ridge=a[4]*(1-t)+b[4]*t;k=sqrt(max(.01,1-(x/rx)**2));return cy-ry*k-ridge*k**16-.003
  return -.14
 vs=[];fs=[];N=40;M=6
 for j in range(N+1):
  z=1.23+.265*j/N;width=.027 if z<1.445 else max(.0005,.027*max(0,1-((z-1.445)/.05)**1.8)**.72)
  for k in range(M+1):x=width*(k/M*2-1);vs.append((x,chestfront(x,z)-.001,z))
 for j in range(N):
  for k in range(M):a=j*(M+1)+k;fs.append((a,a+1,a+M+2,a+M+1))
 patch=mesh('V2 | recessed gate panel',vs,fs,dark);solid(patch,.0008)
 for sg in [-1,1]:
  pts=[]
  for z in np.linspace(1.23,1.495,90):
   x=sg*(.027 if z<1.445 else max(.0005,.027*max(0,1-((z-1.445)/.05)**1.8)**.72));pts.append((x,chestfront(x,z)-.002,z))
  curve('V2 | forged gate panel surround',pts,.0013,gold)
 curve('V2 | gate panel threshold',[(-.026,chestfront(-.026,1.23)-.002,1.23),(.026,chestfront(.026,1.23)-.002,1.23)],.0013,silver)
 for j in range(7):
  z=1.254+j*.028;rivet((0,chestfront(0,z)-.003,z),.0033,gold)
 # Crown arris directly follows actual shell rather than bridging free space above it.
 rows=[(1.745,-.100,.020),(1.770,-.091,.018),(1.795,-.083,.016),(1.825,-.055,.013),(1.846,-.020,.009),(1.857,.014,.004)]
 vs=[];fs=[]
 for z,y,w in rows:vs.extend([(-w,y+.001,z),(0,y-.004,z+.003),(w,y+.001,z)])
 for j in range(len(rows)-1):
  for k in range(2):f=j*3+k;fs.append((f,f+1,f+4,f+3))
 plate_patch('V2 | forged crown ridge planes',vs,fs,steel,.001)
 # One left shoulder is field-repaired with a small overlapping plate and real peened fastenings.
 repairmat=wornsteel('V2 | older shoulder repair',(.046,.049,.051))
 vs=[(-.36,-.069,1.506),(-.275,-.106,1.532),(-.254,-.118,1.506),(-.329,-.105,1.477)]
 plate_patch('V2 | left shoulder repair plate',vs,[(0,1,2,3)],repairmat,.002)
 curve('V2 | repaired shoulder bright broken lip',[vs[0],vs[3],vs[2]],.0011,silver)
 for q in [.15,.5,.84]:
  a=Vector(vs[0]).lerp(Vector(vs[1]),q);a.y-=.003;rivet(a,.0027,gold)
 # Narrow localized scuffs at shoulder plate overlaps with controlled lengths.
 for j in range(11):
  x=-.355+j*.008;z=1.486+j*.002;y=-.108
  curve('V2 | shoulder contact scuff',[(x,y,z),(x+.007,y-.0005,z+.003)],.00028,silver)
 # Garment panels tailored from suspension points. Asymmetric overlap, pinch folds and sewn bindings.
 wool=mat_simple('V2 | heavy charcoal surcoat',(.017,.014,.013),0,.97);v5_wool(wool,(.020,.017,.014))
 for sg in [-1,1]:
  vs=[];fs=[];nx,ny=36,42
  def tab(u,v):
   rows=[];length=.48 if sg<0 else .43
   yy=[[-.142,-.15,-.147,-.155,-.14],[-.16,-.19,-.165,-.20,-.16],[-.18,-.23,-.185,-.245,-.18],[-.19,-.26,-.20,-.27,-.19]]
   for row in range(4):
    t=row/3;width=.183+.045*t;pts=[]
    for col in range(5):
     q=col/4;pts.append((sg*(.012+width*q),yy[row][col],1.03-length*t+(.018*q*q-.012*q)*t*t))
    rows.append(v5_curve(pts,u))
   point=v5_curve(rows,v)
   # Clothing compresses behind rigid tassets; plates do not inherit fabric wrinkles.
   for plate in range(3):
    center=sg*(.114+.007*plate);pu=(point[0]-center)/.145+.5;cu=max(0,min(1,pu));pt=(1.005-plate*.047-point[2]+.005*cos(pi*(cu-.5)))/.050
    if -.10<pu<1.10 and -.15<pt<1.15:
     ct=max(0,min(1,pt));target=-.173-.018*sin(pi*cu)-.008*ct+.008
     weight=min(1,max(0,min((pu+.10)/.10,(1.10-pu)/.10,(pt+.15)/.15,(1.15-pt)/.15)))
     weight=weight*weight*(3-2*weight);point[1]+=max(0,target-point[1])*weight
   return point

  for j in range(ny+1):
   for i in range(nx+1):vs.append(tab(i/nx,j/ny))
  for j in range(ny):
   for i in range(nx):k=j*(nx+1)+i;fs.append((k,k+1,k+nx+2,k+nx+1))
  o=plate_patch('V2 | sewn overlapping surcoat '+str(sg),vs,fs,wool,.003);sub(o,1)
  for u in [.04,.96]:curve('V2 | garment stitched binding',[(x,y-.002,z) for x,y,z in [tab(u,v) for v in np.linspace(0,1,90)]],.0012,leather)
  for seam_u in [.04,.96]:v5_stitches('V5 | surcoat sewn side seam',tab,seam_u,85,leather)
  curve('V2 | uneven sewn hem',[(x,y-.002,z) for x,y,z in [tab(u,.98) for u in np.linspace(0,1,90)]],.0015,leather)
  for j in range(3):
   z=1.005-j*.047;cx=sg*(.114+.007*j);vs=[];fs=[];N=22;M=6
   for row in range(M+1):
    t=row/M
    for col in range(N+1):
     u=col/N;dx=(u-.5)*.145;vs.append((cx+dx,-.173-.018*sin(pi*u)-.008*t,z-.050*t+.005*cos(pi*(u-.5))))
   for row in range(M):
    for col in range(N):f=row*(N+1)+col;fs.append((f,f+1,f+N+2,f+N+1))
   plate_patch('V2 | shaped suspended tasset '+str(sg)+' '+str(j),vs,fs,steel)
   curve('V2 | tasset turned hem',vs[-N-1:],.0011,silver)
 # New static tailored cape from two shoulder points, wide lower drape and uneven sewn panels.
 cap=bpy.data.objects['Cape | seven-lantern ceremonial wool'];cape_mat=cap.data.materials[0]
 bpy.data.objects.remove(cap,do_unlink=True);nx,ny=64,84;vs=[];fs=[]
 def cape(u,v):
  widths=[.38,.48,.60,.70,.76];heights=[1.525,1.24,.90,.53,.20]
  yy=[[.145,.14,.14,.15,.14,.14,.145],[.23,.255,.29,.24,.28,.26,.23],[.28,.31,.39,.285,.38,.33,.28],[.32,.35,.43,.32,.44,.37,.32],[.35,.38,.46,.33,.45,.40,.35]]
  xx=[-.5,-.33,-.12,.06,.25,.39,.5];hem=[.055,.025,.005,.040,0,.045,.065];rows=[]
  for j in range(5):
   points=[(widths[j]*xx[k]+.020*(j/4),yy[j][k],heights[j]+hem[k]*(j/4)**4) for k in range(7)];rows.append(v5_curve(points,u))
  return v5_curve(rows,v)

 for j in range(ny+1):
  for i in range(nx+1):vs.append(cape(i/nx,j/ny))
 for j in range(ny):
  for i in range(nx):k=j*(nx+1)+i;fs.append((k,k+nx+1,k+nx+2,k+1))
 cap=mesh('V2 | tailored static cape - NOT SIMULATED',vs,fs,cape_mat);solid(cap,.003);sub(cap,1);uv=cap.data.uv_layers.new(name='Sewn cape UV')
 for poly in cap.data.polygons:
  for li in poly.loop_indices:
   vi=cap.data.loops[li].vertex_index;uv.data[li].uv=(vi%(nx+1)/nx,1-vi//(nx+1)/ny)
 # Tone down embroidery/cape sheen. Retain original authored motif, more woven and less metallic.
 bs=cape_mat.node_tree.nodes.get('Principled BSDF');links=cape_mat.node_tree.links
 for sock,val in [('Metallic',0),('Roughness',.98),('Specular IOR Level',.1),('Sheen Weight',.025)]:
  for l in list(bs.inputs[sock].links):links.remove(l)
  bs.inputs[sock].default_value=val
 for nd in cape_mat.node_tree.nodes:
  if nd.type=='MIX_RGB' and nd.inputs[2].default_value[0]>.2:nd.inputs[2].default_value=(.14,.085,.027,1)
 v5_wool(cape_mat)
 for u in [.03,.97]:curve('V2 | cape bound selvedge',[cape(u,v) for v in np.linspace(0,1,100)],.0016,leather)
 for u in [.34,.67]:curve('V2 | cape joining seam',[(x,y+.002,z) for x,y,z in [cape(u,v) for v in np.linspace(.04,.98,100)]],.0007,leather)
 for seam_u in [.03,.34,.67,.97]:v5_stitches('V5 | cape sewn panel seam',cape,seam_u,170,leather,True)
 curve('V5 | cape doubled hem',[cape(u,.995) for u in np.linspace(0,1,200)],.002,cape_mat)
 # Metal clasp at one shoulder only; other is an understated leather retaining tab.
 sphere('V2 | gate clasp',(-.175,-.073,1.555),(.018,.007,.024),gold,28,16)
 curve('V2 | cape leather tether',[(-.17,-.079,1.549),(-.1,-.12,1.526),(.04,-.123,1.532),(.15,-.081,1.548)],.003,leather)
 # Sword continuity and forged flowing guard. Existing blade lengths stay unchanged.
 drop(['Oathwake | swept','Oathwake | silver guard','Oathwake | lantern quillon','Terminal pierced','Oathwake | broken reliquary','Oathwake | engraved gate vine','Ricasso silver outline','Ricasso sun seal'])
 sx=.71;sy=-.01
 tang=surface('V2 | Oathwake continuous tang socket',[(1.35,.021,.012,sy,0),(1.39,.024,.015,sy,0),(1.433,.016,.012,sy,0)],steel,32);tang.location.x=sx
 for sg in [-1,1]:
  pts=[]
  for t in np.linspace(0,1,50):pts.append((sx+sg*.184*t,sy+.012*sin(pi*t),1.398-.022*sin(pi*t)+.008*t*t))
  curve('V2 | Oathwake forged swept guard',pts,.009,steel)
  curve('V2 | guard worn crest',[(x,y-.008,z+.002) for x,y,z in pts],.0012,silver)
  sphere('V2 | flattened lantern guard terminal',(sx+sg*.184,sy,1.406),(.015,.012,.018),steel,24,16)
 ring('V2 | backed broken reliquary',(sx,sy+.015,1.407),(1,0,0),(0,0,1),.031,.004,gold,.42,5.95)
 # Distinctive limited scar strokes on one shoulder/chest, not global color noise.
 for j in range(9):
  x=-.10+j*.006;z=1.38+j*.003
  curve('V2 | shallow field scuff',[(x,-.151,z),(x+.009,-.15,z+.015)],.00025,silver)
 # New pieces parent to display roots. No old physics/collision claims follow changed cloth.
 for o in set(S.objects)-before:
  if o.type in ['MESH','CURVE'] and not o.name.startswith('STUDIO'):
   o.parent=bpy.data.objects['OATHWAKE | display assembly'] if 'Oathwake' in o.name or 'guard worn' in o.name or 'reliquary' in o.name or 'lantern guard' in o.name else root
 for o in S.objects:
  if o.name.startswith('COLLIDER |'):o.hide_render=True;o.hide_set(True)
 focus_shell_glove()
 refine_v4_silhouette()
 refine_v5_mantle()
 authored_material_samples()
 S['v2_scope']='Static original constructive silhouette/material revision. New cape is authored geometry, not simulated; v1 cloth bake does not validate v2. No rig, no game integration.'
 S.render.resolution_x=1100;S.render.resolution_y=1400;S.cycles.samples=32;S.view_settings.exposure=-.15
 camera('hero');S.cycles.device='CPU'
 for collection in [bpy.data.meshes,bpy.data.curves,bpy.data.materials]:
  for datablock in list(collection):
   if datablock.users==0:collection.remove(datablock)
 bpy.ops.wm.save_as_mainfile(filepath=str(D/('last-vigil-v5-support.blend' if mode=='support' else 'last-vigil-v5.blend')))

def focus_shell_glove():
 """Replace complete helmet and glove surfaces with landmark-built fit; rest of outfit stable."""
 root=bpy.data.objects['CHARACTER | shoulder-turn study'];before=set(S.objects)
 drop(['V2 | low ridged','V2 | sallet','V2 | angular fitted','V2 | narrow eye','V2 | peaked brow','V2 | visor flush','V2 | breathing slot','V2 | enclosing bevor','V2 | bevor folded','V2 | forged crown','V2 | L fitted palm','V2 | R fitted palm','V2 | L curved gauntlet','V2 | R curved gauntlet','V2 | tapered curved leather finger','V2 | dorsal finger plate','V2 | rounded leather finger tip','V2 | flattened knuckle','V2 | opposed padded thumb','V2 | fitted thumb','V2 | rounded thumb'])
 # Ordered contour landmarks: median, cheek plane, temple, occiput and nape.
 contour=[(0,-1),(.65,-.82),(.96,-.30),(1,.10),(.75,.75),(0,1),(-.75,.75),(-1,.10),(-.96,-.30),(-.65,-.82)]
 def section(rx,front,rear,z,keel=0):
  points=[]
  for j,(a,b) in enumerate(zip(contour,contour[1:]+contour[:1])):
   prev=contour[(j-1)%len(contour)];nxt=contour[(j+2)%len(contour)]
   for k in range(5):
    t=k/5
    # Curved fields; median keel remains the one intentional front crease.
    vals=[]
    for d in range(2):
     m0=(b[d]-prev[d])*.43;m1=(nxt[d]-a[d])*.43
     if j==0:m0=(b[d]-a[d])*.65
     if j==len(contour)-1:m1=(b[d]-a[d])*.65
     vals.append((2*t**3-3*t*t+1)*a[d]+(t**3-2*t*t+t)*m0+(-2*t**3+3*t*t)*b[d]+(t**3-t*t)*m1)
    x=vals[0]*rx;y0=vals[1];y=y0*(front if y0<0 else rear)+.012
    points.append((x,y,z+keel*exp(-(x/.025)**2)*max(0,1-abs(y0)*.35)))
  return points
 def shell(name,rows,open_front=False):
  vs=[];fs=[];N=50
  if name=='FOCAL | forged landmark skull':
   dense=[]
   for j in range(len(rows)-1):
    a=rows[j];b=rows[j+1];prev=rows[max(0,j-1)];nxt=rows[min(len(rows)-1,j+2)]
    for k in range(4):
     t=k/4;vals=[]
     for d in range(5):
      if d==3:val=a[d]*(1-t)+b[d]*t
      else:
       dz=b[3]-a[3];m0=(b[d]-prev[d])/max(.001,b[3]-prev[3])*dz;m1=(nxt[d]-a[d])/max(.001,nxt[3]-a[3])*dz;val=(2*t**3-3*t*t+1)*a[d]+(t**3-2*t*t+t)*m0+(-2*t**3+3*t*t)*b[d]+(t**3-t*t)*m1
       if d<3:val=max(.002,val)
      vals.append(val)
     dense.append(tuple(vals))
   dense.append(rows[-1]);rows=dense
  for row in rows:vs+=section(*row)
  for j in range(len(rows)-1):
   for i in range(N):
    # Lower back helmet covers temples/occiput, leaves actual face opening.
    if open_front and (i<9 or i>=41):continue
    a=j*N+i;b=j*N+(i+1)%N;fs.append((a,b,b+N,a+N))
  o=mesh(name,vs,fs,steel);solid(o,.0025);return o
 # Forehead/crown form one shell. Close small top with a smooth longitudinal roof.
 upper=shell('FOCAL | forged landmark skull',[(.108,.123,.103,1.756,0),(.108,.123,.103,1.759,0),(.104,.120,.102,1.775,.002),(.096,.108,.098,1.808,.008),(.077,.088,.084,1.845,.014),(.048,.058,.06,1.869,.017),(.019,.033,.043,1.884,.004),(.002,.015,.022,1.890,.001)])
 # Top closure shares actual rim rather than an attached crest.
 top=section(.002,.015,.022,1.890,.001);roof=mesh('FOCAL | crown closure',top,[tuple(range(len(top)))],steel);solid(roof,.0025);bevel(roof,.001)
 lower=shell('FOCAL | fitted occiput and cheek sides',[(.070,.082,.089,1.641,0),(.083,.094,.101,1.665,0),(.101,.111,.106,1.711,0),(.108,.117,.103,1.761,0)],True)
 # Actual visor plates stop 5mm below brow. Center and cheek breaks are in the mesh.
 vs=[];fs=[];N=30
 face_rows=[(1.649,.077,.092),(1.659,.080,.096),(1.692,.092,.105),(1.730,.102,.115),(1.751,.106,.119)]
 for z,rx,depth in face_rows:
  for i in range(N+1):
   u=i/N*2-1;ax=abs(u)
   y=.012-depth+(.023*ax/.60 if ax<=.60 else .023+(depth-.031-.023)*(ax-.60)/.40)
   y+=.008*max(0,(ax-.88)/.12)**2
   vs.append((rx*u,y,z-.003*(ax**3)))
 for j in range(len(face_rows)-1):
  for i in range(N):a=j*(N+1)+i;fs.append((a,a+1,a+N+2,a+N+1))
 visor=mesh('FOCAL | continuous shaped lower visor',vs,fs,steel);solid(visor,.0025);bevel(visor,.001)
 # Restrict edge rolling to real plate perimeter, not interior profile strips.
 rim=visor.vertex_groups.new(name='Physical plate rim');rim.add([j*(N+1)+i for j in range(len(face_rows)) for i in range(N+1) if j in (0,len(face_rows)-1) or i in (0,N)],1,'REPLACE')
 visor.modifiers[-1].limit_method='VGROUP';visor.modifiers[-1].vertex_group=rim.name
 # Recessed black eye socket backing; separate surface behind the real opening.
 vs=[]
 for z in [1.746,1.760]:
  for i in range(N+1):
   u=i/N*2-1;vs.append((.103*u,.012-.108+.073*(abs(u)**1.48),z))
 mesh('FOCAL | recessed eye darkness',vs,[(i,i+1,i+N+2,i+N+1) for i in range(N)],dark)
 for sg in [-1,1]:
  sphere('FOCAL | visor hinge',(sg*.105,-.019,1.745),(.005,.003,.006),gold,20,12)
 # Short shaped gorget flares below the jaw; front lip projects around chin with dark clearance.
 gor=shell('FOCAL | fitted gorget collar',[(.126,.105,.10,1.546,0),(.124,.106,.101,1.55,0),(.101,.102,.09,1.586,0),(.086,.095,.08,1.626,0),(.082,.091,.079,1.650,0)])
 # Separate inside leather neck lining prevents bright tube illusion.
 neck=loft('FOCAL | padded neck seal',[(1.59,.073,.066,0,.012),(1.66,.073,.066,0,.012)],cloth,48)
 # Gloves: connected leather volume generated from anatomical sections then voxel-fused.
 glove=node_mat('FOCAL | supple leather glove',(.026,.016,.011),0,.72,1300,.00008)
 glove.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.72
 for sg,label in [(-1,'L'),(1,'R')]:
  cx=sg*.394;cy=-.012;pieces=[]
  # Flattened dorsal face, convex palm and narrowed wrist in one purposeful base mesh.
  rows=[(.977,.026,.012),(.961,.029,.013),(.941,.037,.014),(.922,.040,.0135),(.908,.039,.0125),(.899,.036,.010),(.894,.027,.0075)]
  vs=[];fs=[];N=40
  for z,rx,ry in rows:
   for i in range(N):
    a=2*pi*i/N;co=cos(a);si=sin(a);x=cx+rx*(1 if co>=0 else -1)*abs(co)**.78;y=cy+ry*(1 if si>=0 else -1)*abs(si)**.8
    if si<0:y=cy+ry*si*.72
    distal=max(0,min(1,(.932-z)/.038));lx=(x-cx)*sg/.041;zz=z-distal*.008+distal*(.008*abs(lx)**1.6+.003*lx)
    vs.append((x,y,zz))
  for j in range(len(rows)-1):
   for i in range(N):a=j*N+i;b=j*N+(i+1)%N;fs.append((a,b,b+N,a+N))
  fs.extend([tuple(reversed(range(N))),tuple((len(rows)-1)*N+i for i in range(N))]);pieces.append(mesh('FOCAL glove palm preunion',vs,fs,glove))
  pieces.append(sphere('FOCAL thenar pad preunion',(cx-sg*.028,cy+.006,.934),(.020,.0135,.025),glove,24,16))
  fingerpaths=[]
  for f,(ratio,rootz,off,width) in enumerate(zip([.87,1,.94,.74],[.899,.895,.898,.906],[-.027,-.009,.010,.027],[.0087,.0091,.0086,.0070])):
   length=.078*ratio;start=Vector((cx+sg*off,cy,.902+(rootz-.899)));points=[]
   lengths=[length*.45,length*.32,length*.23];angles=[math.radians(14+f*2),math.radians(37+f*2),math.radians(50+f*2)]
   ends=[start]
   for leng,ang in zip(lengths,angles):ends.append(ends[-1]+Vector((sg*(f-1.5)*.001,math.sin(ang)*leng,-math.cos(ang)*leng)))
   def path(t):
    q=t*3;j=min(2,int(q));return ends[j].lerp(ends[j+1],q-j)
   vs=[];fs=[];RN=16;ZN=24
   for j in range(ZN+1):
    t=j/ZN;c=path(t);tangent=(path(min(1,t+.001))-path(max(0,t-.001))).normalized();u=Vector((1,0,0));v=tangent.cross(u).normalized();rad=width*(1-.26*t)*(1+.07*exp(-((t-.34)/.07)**2)+.05*exp(-((t-.67)/.06)**2))
    tip=1 if t<.90 else sqrt(max(.01,1-((t-.90)/.105)**2))
    for i in range(RN):
     a=2*pi*i/RN;vs.append(c+u*(rad*cos(a)*tip)+v*(rad*.79*sin(a)*tip))
   for j in range(ZN):
    for i in range(RN):a=j*RN+i;b=j*RN+(i+1)%RN;fs.append((a,b,b+RN,a+RN))
   fs.extend([tuple(reversed(range(RN))),tuple(ZN*RN+i for i in range(RN))]);pieces.append(mesh('FOCAL digit preunion',vs,fs,glove));fingerpaths.append((ends,width))
  # Thumb opposes the palm, wide web narrows into two flexed segments.
  tp=[Vector((cx-sg*.025,cy+.002,.948)),Vector((cx-sg*.048,cy+.009,.928)),Vector((cx-sg*.055,cy+.021,.905)),Vector((cx-sg*.049,cy+.030,.888))]
  vs=[];fs=[];RN=20;ZN=30
  # Smooth bent thumb centerline and radius, no ellipsoid chain or separated pads.
  for j in range(ZN+1):
   t=j/ZN;q=t*3;k=min(2,int(q));f=q-k;a=tp[k];b=tp[k+1];prev=tp[max(0,k-1)];nxt=tp[min(3,k+2)];c=(2*f**3-3*f*f+1)*a+(f**3-2*f*f+f)*(b-prev)*.4+(-2*f**3+3*f*f)*b+(f**3-f*f)*(nxt-a)*.4
   tangent=(b-a).normalized();u=Vector((0,1,0));v=tangent.cross(u).normalized();rad=.014*(1-.42*t);tip=1 if t<.87 else sqrt(max(.005,1-((t-.87)/.135)**2))
   for i in range(RN):
    a=2*pi*i/RN;vs.append(c+u*(rad*.83*cos(a)*tip)+v*(rad*sin(a)*tip))
  for j in range(ZN):
   for i in range(RN):a=j*RN+i;b=j*RN+(i+1)%RN;fs.append((a,b,b+RN,a+RN))
  fs.extend([tuple(reversed(range(RN))),tuple(ZN*RN+i for i in range(RN))]);pieces.append(mesh('FOCAL thumb sweep preunion',vs,fs,glove))
  # Remesh fusion is the actual final connected volume, not overlapping primitive evidence.
  bpy.ops.object.select_all(action='DESELECT')
  for ob in pieces:ob.select_set(True)
  bpy.context.view_layer.objects.active=pieces[0];bpy.ops.object.join();hand=bpy.context.object;hand.name='FOCAL | '+label+' unified leather palm thumb and fingers'
  hand.data.remesh_voxel_size=.0014;bpy.ops.object.voxel_remesh();sm=hand.modifiers.new('Leather volume continuity','SMOOTH');sm.factor=.35;sm.iterations=3
  # Authored palm hollow and local compression, no transverse sausage band.
  for vertex in hand.data.vertices:
   p=vertex.co;lx=(p.x-cx)*sg
   if p.y>cy+.003:
    weight=max(0,min(1,(p.y-cy-.003)/.009))
    hollow=.0018*exp(-((lx-.003)/.022)**2-((p.z-.932)/.020)**2)
    thenarcrease=.0006*exp(-((lx-(-.019+.35*(p.z-.925)))/.0017)**2-((p.z-.929)/.019)**2)
    p.y-=weight*(hollow+thenarcrease)
    # Three staggered shallow root saddles articulate the MCP arcade.
    for x0,z0 in [(-.018,.902),(.0005,.900),(.019,.906)]:
     p.y-=weight*.0006*exp(-((lx-x0)/.006)**2-((p.z-z0)/.011)**2)
  for face in hand.data.polygons:face.use_smooth=True
  # Curved dorsal plate follows actual palm/knuckle arc, never a rectangular cover.
  vs=[];fs=[];nx,ny=16,20
  for j in range(ny+1):
   t=j/ny;width=.028+.010*sin(pi*t*.7)
   for i in range(nx+1):
    u=i/nx*2-1;x=cx+width*u;z=.961-.061*t+.004*u*u*t;y=cy-.019-.003*sin(pi*t)-.003*(1-u*u);vs.append((x,y,z))
  for j in range(ny):
   for i in range(nx):a=j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
  plate_patch('FOCAL | '+label+' formed metacarpal plate',vs,fs,steel,.0015)
  # One shallow knuckle lame, scalloped to the living knuckle arch.
  for f,(ends,width) in enumerate(fingerpaths):
   for j in range(3):
    a=ends[j];b=ends[j+1];vs=[];fs=[];nn=12;mm=6;tan=(b-a).normalized();ux=Vector((1,0,0));vy=tan.cross(ux).normalized()
    if vy.y>0:vy=-vy
    for row in range(mm+1):
     t=row/mm;c=a.lerp(b,.06+.86*t);rad=width*(1-.26*(j+t)/3)+.0015
     for k in range(nn+1):
      ang=pi*k/nn;vs.append(c+ux*(rad*cos(ang))+vy*(rad*.80*sin(ang)))
    for row in range(mm):
     for k in range(nn):q=row*(nn+1)+k;fs.append((q,q+1,q+nn+2,q+nn+1))
    plate_patch('FOCAL | dorsal finger lame',vs,fs,steel,.0008)
  # Fitted thumb dorsal cap, palm and thenar web remain exposed leather.
  for j in [1,2]:
   a,b=tp[j],tp[j+1];pts=[a.lerp(b,t) for t in np.linspace(.08,.88,8)];c=curve('FOCAL | curved thumb dorsal plate',[(p.x,p.y-.007,p.z) for p in pts],.0065,steel)
   for k,pt in enumerate(c.data.splines[0].points):pt.radius=1-.25*k/7
  # Flared cuff follows wrist, with an arming-glove separation at the forearm.
  cuff=loft('FOCAL | '+label+' flared gauntlet cuff',[(.957,.035,.023,cx,cy),(.978,.041,.029,cx,cy)],steel,48);bevel(cuff,.001)
  hand['scope']='Connected voxel-fused leather volume, relaxed static pose; not skinned or deformation tested.'
 for ob in set(S.objects)-before:
  if ob.type in ['MESH','CURVE']:ob.parent=root
 S['focal_revision']='Integrated landmark helmet, real eye gap, connected leather glove volume with fitted dorsal plates. Static only.'


def refine_v4_silhouette():
 """Concept-scale silhouette replacement: narrowed forged head, layered neck, open shoulder drape."""
 root=bpy.data.objects['CHARACTER | shoulder-turn study'];before=set(S.objects)
 # Hidden doublet must fit INSIDE the replacement neck, verified by first-pass raycasts.
 for vert in bpy.data.objects['Padded arming doublet'].data.vertices:
  p=vert.co
  if p.z>1.53:
   t=min(1,(p.z-1.53)/.05);p.x*=1-.35*t;p.y=.012+(p.y-.012)*(1-.40*t)
 # Fit helmet surfaces together with one common deformation, retaining the real eye opening.
 for ob in S.objects:
  if not ob.name.startswith('FOCAL | ') or not any(k in ob.name for k in ['skull','visor','occiput','crown closure','recessed eye']):continue
  if ob.type!='MESH':continue
  for vert in ob.data.vertices:
   p=vert.co;oldx=p.x;p.x*=.88
   if p.z<1.72:p.x*=.92+.08*max(0,(p.z-1.64)/.08)
   front=max(0,min(1,(-p.y+.012)/.13));p.z-=.011
   p.z-=.009*exp(-(oldx/.048)**2)*exp(-((p.z-1.747)/.05)**2)*front
   p.y-=.008*exp(-(oldx/.032)**2)*front
 # Remove exposed tube and replace with actual overlapping tapered neck lames.
 drop(['FOCAL | fitted gorget collar','V2 | breastplate folded edge','V2 | padded mantle','V2 | quilted mantle seam','V2 | clustered short mantle','V2 | mantle tapered clump mass'])
 for j in range(3):
  z=1.555+j*.026;rx=.119-j*.018;ry=.112-j*.012
  ob=surface('V4 | articulated gorget lame '+str(j),[(z,rx,ry,.014,.006),(z+.023,rx-.012,ry-.007,.014,.004)],steel,64)
 # Authored sloping plates replace the rounded parametric shoulder bowls entirely.
 drop(['V2 | L swept shoulder','V2 | R swept shoulder','V2 | shoulder turned steel edge','V2 | left shoulder repair','V2 | repaired shoulder','V2 | shoulder contact scuff'])
 for ob in list(S.objects):
  if ob.name.startswith('Peened rivet') and abs(ob.location.x)>.20 and 1.35<ob.location.z<1.60:bpy.data.objects.remove(ob,do_unlink=True)
 for sg in [-1,1]:
  for j in range(4):
   vs=[];fs=[];N=12;M=24
   for row in range(M+1):
    v=row/M*2-1;av=abs(v);frontback=(.124-j*.006)*v
    for col in range(N+1):
     u=col/N;inner=.186+j*.029;outer=.357+j*.010-.018*max(0,(av-.65)/.35)
     x=sg*(inner+(outer-inner)*u);y=.016+frontback
     z=1.575-j*.045-.071*u-.040*av**2+.004*sin(pi*u)
     # Lower outer corner sweeps down; left upper plate slightly broader at rear.
     if sg<0:x-=.008*u*max(0,v)
     vs.append((x,y,z))
   for row in range(M):
    for col in range(N):a=row*(N+1)+col;fs.append((a,a+1,a+N+2,a+N+1))
   ob=plate_patch('V4 | sloping forged shoulder lame '+str(j),vs,fs,steel,.0025)
   for face in ob.data.polygons:face.use_smooth=True
   edge=[vs[row*(N+1)+N] for row in range(M+1)];curve('V4 | narrow shoulder folded lip',edge,.0008,silver)
   if j in [0,2]:
    for row in [3,M-3]:rivet(vs[row*(N+1)+N-2],.0024,gold)
 for ob in set(S.objects)-before:
  if ob.type in ['MESH','CURVE']:ob.parent=root
 S['v4_scope']='Static silhouette replacement and landmark palm refinement; no rig/AI/integration.'

def refine_v5_mantle():
 """Sewn horseshoe support, continuous fine undercoat and irregular directional overcoat."""
 root=bpy.data.objects['CHARACTER | shoulder-turn study'];before=set(S.objects)
 liner=bpy.data.objects['FOCAL | padded neck seal'];lining=mat_simple('V5 | fitted dark padded neck liner',(.004,.004,.0045),0,.97);lining.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.08;liner.data.materials.clear();liner.data.materials.append(lining)
 for vertex in liner.data.vertices:
  p=vertex.co;p.x*=.88;p.y=.012+(p.y-.012)*.88;p.z-=.006*max(0,min(1,(p.z-1.59)/.07))
 drop(['V4 | asymmetric draped wool shoulder','V4 | draped soft fur fibers','V4 | narrow shoulder folded lip'])
 clothmat=mat_simple('V5 | soot wool yoke',(.009,.008,.007),0,.94)
 clothmat.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.12
 # Explicit neck / shoulder support / fold turn / hanging hem landmarks, right front around back to left front.
 cage=[
  [( .060,-.063,1.625),(.130,-.105,1.580),(.170,-.115,1.545),(.160,-.140,1.495)],
  [( .083,-.035,1.635),(.190,-.075,1.550),(.245,-.145,1.520),(.260,-.130,1.490)],
  [( .097, .005,1.620),(.225, .015,1.575),(.290, .020,1.545),(.310, .030,1.482)],
  [( .078, .060,1.615),(.200, .090,1.580),(.275, .130,1.530),(.280, .180,1.480)],
  [( .045, .080,1.615),(.120, .135,1.575),(.160, .185,1.525),(.170, .225,1.475)],
  [( .000, .087,1.615),(.000, .145,1.580),(.000, .195,1.530),(.000, .230,1.480)],
  [(-.045, .080,1.615),(-.125,.135,1.576),(-.175,.180,1.522),(-.185,.220,1.470)],
  [(-.078, .060,1.615),(-.205,.090,1.578),(-.280,.125,1.526),(-.290,.175,1.475)],
  [(-.097, .005,1.620),(-.230,.010,1.572),(-.295,.005,1.540),(-.315,.010,1.478)],
  [(-.083,-.035,1.635),(-.190,-.090,1.550),(-.250,-.165,1.515),(-.270,-.150,1.478)],
  [(-.060,-.063,1.625),(-.135,-.125,1.575),(-.180,-.145,1.535),(-.175,-.165,1.485)]
 ]
 # Local support sections retain a load fold; no periodic radial displacement.
 original=cage;expanded=[]
 for j,section in enumerate(original):
  expanded.append(section)
  if j not in [0,9]:continue
  neighbor=original[j+1]
  for t in ([.34,.48,.62] if j==0 else [.38,.55,.72]):
   points=[list(Vector(a).lerp(Vector(b),t)) for a,b in zip(section,neighbor)]
   middle=abs(t-(.48 if j==0 else .55))<.01
   if middle:
    inward=-1 if j==0 else 1
    points[1][2]-=.005;points[2][0]+=inward*.012;points[2][2]-=.014
   expanded.append(points)
 cage=expanded
 # A separate rear slack scoop dies into the attachment instead of mirroring front folds.
 for section in cage:
  if abs(section[0][0])<.01:
   section[1]=list(section[1]);section[2]=list(section[2]);section[1][2]-=.006;section[2][1]+=.008;section[2][2]-=.012
 def spline(points,q):
  if q<0:return points[0]+q*(points[1]-points[0])
  if q>len(points)-1:return points[-1]+(q-len(points)+1)*(points[-1]-points[-2])
  j=min(len(points)-2,int(q));t=q-j;a=points[j];b=points[j+1];prev=points[max(0,j-1)];nxt=points[min(len(points)-1,j+2)]
  return (2*t**3-3*t*t+1)*a+(t**3-2*t*t+t)*(b-prev)*.35+(-2*t**3+3*t*t)*b+(t**3-t*t)*(nxt-a)*.35
 def yoke(u,v):
  rows=[spline([Vector(cage[j][i]) for j in range(len(cage))],v*(len(cage)-1)) for i in range(4)]
  return spline(rows,u*3)
 cverts=[p for section in cage for p in section];cfaces=[]
 for j in range(len(cage)-1):
  for i in range(3):a=j*4+i;cfaces.append((a,a+1,a+5,a+4))
 control=mesh('V5 | authored mantle control cage',cverts,cfaces,clothmat);control.hide_render=True;control.hide_set(True);control['scope']='68 authored garment landmarks; hidden control cage, not groom or simulated cloth'
 (E/'mantle-control-cage.json').write_text(json.dumps({'bands':['neck attachment','shoulder support','fold turn','dropped hem'],'sections':cage,'scope':'Authored static garment control points, not simulated cloth'},indent=2)+'\n')
 N=48;M=100;vs=[];fs=[]
 for j in range(M+1):
  for i in range(N+1):vs.append(yoke(i/N,j/M))
 for j in range(M):
  for i in range(N):a=j*(N+1)+i;fs.append((a,a+1,a+N+2,a+N+1))
 ob=mesh('V5 | sewn horseshoe wool yoke',vs,fs,clothmat);solid(ob,.003);sub(ob,1)
 # Rolled cloth edge follows the actual sewn shape, no rectangular floating board.
 for side in [0,1]:curve('V5 | bound yoke opening',[yoke(u,side) for u in np.linspace(0,1,50)],.0015,clothmat)
 curve('V5 | bound yoke hem',[yoke(1,v) for v in np.linspace(0,1,180)],.0015,clothmat)
 colors=[(.014,.012,.010),(.026,.023,.019),(.046,.039,.031)]
 strand_count=0
 for coat in ([] if mode=='support' or args[1:] and all(v.startswith('bare_') for v in args[1:]) else ['undercoat','overcoat']):
  for shade,color in enumerate(colors):
   ma=mat_simple('V5 | '+coat+' tone '+str(shade),color,0,.9)
   c=bpy.data.curves.new('V5 '+coat,'CURVE');c.dimensions='3D';c.bevel_depth=.00013 if coat=='undercoat' else .00019;c.bevel_resolution=0
   count=6000 if coat=='undercoat' else 1600
   for j in range(count):
    if coat=='undercoat':u=sqrt(random.random());v=random.random();length=random.uniform(.008,.016);lift=.003
    else:
     guide=j%16;vc=(guide+.5)/16+.025*sin(guide*2.1);v=min(.995,max(.005,vc+random.gauss(0,.025)));u=min(.97,max(.08,.38+.28*sin(guide*1.7)+random.gauss(0,.12)));length=.032+.020*(.5+.5*sin(guide*2.9))+random.uniform(-.003,.003);lift=.006+.003*sin(guide*1.3)**2
    du=length/.23;dv=.025*sin(v*pi*2);sp=c.splines.new('POLY');K=5 if coat=='undercoat' else 8;sp.points.add(K-1)
    for k,p in enumerate(sp.points):
     q=k/(K-1);uq=u+du*q;vq=min(1,max(0,v+dv*q));pos=yoke(uq,vq)+Vector((0,0,.0015+lift*sin(pi*q)))
     p.co=(*pos,1);p.radius=(1-q)**.8+.005
    strand_count+=1
   hair=bpy.data.objects.new('V5 | '+coat+' fibers '+str(shade),c);bpy.context.collection.objects.link(hair);c.materials.append(ma)
 # Shallow fitted double curvature on the large plate field, retain explicit angular boundaries.
 for ob in S.objects:
  if not ob.name.startswith('V4 | sloping forged shoulder lame'):continue
  me=ob.data
  for v in me.vertices:
   p=v.co;x=abs(p.x);u=max(0,min(1,(x-.19)/.20));vv=(p.y-.016)/.125
   p.z+=.006*sin(pi*u)*(1-min(1,vv*vv))
  # Rounded bevel already controls physical edge; avoid decorative bright piping.
 S['v5_groom_strands']=strand_count
 for ob in set(S.objects)-before:
  if ob.type in ['MESH','CURVE']:ob.parent=root


base_camera=camera
def camera(view):
 if view in ['head','headside','palm','garment','cape_detail']:
  pos,target,lens={'head':((1.0,-2.2,1.95),(0,0,1.72),110),'headside':((-2.2,.05,1.87),(0,0,1.73),110),'palm':((.8,1.6,1.09),(.39,0,.91),135),'garment':((1.3,-2,1.10),(0,-.12,.80),100),'cape_detail':((1.4,2.5,1.25),(0,.25,.88),90)}[view]
  pos=Vector(pos);target=Vector(target);S.camera.location=pos;S.camera.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();S.camera.data.lens=lens
 elif view=='hand':
  pos=Vector((1.2,-2,1.16));target=Vector((.39,-.025,.94));S.camera.location=pos;S.camera.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();S.camera.data.lens=135
 elif view=='side':
  pos=Vector((-4,-.3,1.9));target=Vector((0,0,1));S.camera.location=pos;S.camera.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();S.camera.data.lens=60
 else:base_camera(view)

def render(view):
 requested_view=view
 if view.endswith('-detail'):view=view[:-7]
 isbare=view.startswith('bare_');hidden=[]
 if isbare:
  view='clay_'+view[5:]
  for ob in S.objects:
   if ob.name.startswith('V5 | ') and 'fibers' in ob.name:hidden.append(ob);ob.hide_render=True
 isclay=view.startswith('clay_');ismask=view.startswith('mask_');camera(view[5:] if isclay or ismask else view);restores=[]
 if isclay:
  clay=bpy.data.materials.get('FOCAL review clay') or mat_simple('FOCAL review clay',(.24,.24,.24),0,.8);S.view_layers[0].material_override=clay
 if ismask:
  for ob in S.objects:
   if ob.type!='MESH':continue
   for slot in ob.material_slots:
    old=slot.material
    if not old or not old.name.startswith('V3-authored'):continue
    maskname='steel-placement-mask' if 'steel' in old.name else 'leather-placement-mask'
    m=bpy.data.materials.get('Diagnostic '+maskname)
    if m is None:
     m=bpy.data.materials.new('Diagnostic '+maskname);m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links;uv=n.new('ShaderNodeUVMap');uv.uv_map='Authored sample UV';tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images[maskname];em=n.new('ShaderNodeEmission');out=n.new('ShaderNodeOutputMaterial');l.new(uv.outputs['UV'],tex.inputs['Vector']);l.new(tex.outputs['Color'],em.inputs['Color']);l.new(em.outputs[0],out.inputs['Surface'])
    restores.append((slot,old));slot.material=m
 outview=requested_view if requested_view.endswith('-detail') else ('bare_'+view[5:] if isbare else view)
 S.render.filepath=str(E/(outview+'.png'));bpy.ops.render.render(write_still=True);S.view_layers[0].material_override=None
 for ob in hidden:ob.hide_render=False
 for slot,old in restores:slot.material=old

def setdevice():
 S.cycles.device='CPU'
 if os.environ.get('BOSSLAB_ART_DEVICE')=='METAL':
  pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
  for dev in pref.devices:dev.use=dev.type=='METAL'
  S.cycles.device='GPU'

def audit_focal():
 results=[]
 for ob in S.objects:
  if not ob.name.startswith('FOCAL | ') or 'unified leather palm' not in ob.name:continue
  me=ob.data;adj=[[] for v in me.vertices];edgecounts={}
  for edge in me.edges:
   a,b=edge.vertices;adj[a].append(b);adj[b].append(a)
  unseen=set(range(len(adj)));sizes=[]
  while unseen:
   stack=[unseen.pop()];count=0
   while stack:
    a=stack.pop();count+=1
    for b in adj[a]:
     if b in unseen:unseen.remove(b);stack.append(b)
   sizes.append(count)
  for face in me.polygons:
   indices=list(face.vertices)
   for a,b in zip(indices,indices[1:]+indices[:1]):k=tuple(sorted((a,b)));edgecounts[k]=edgecounts.get(k,0)+1
  results.append({'object':ob.name,'vertices':len(me.vertices),'connected_components':len(sizes),'component_sizes':sorted(sizes,reverse=True),'edges_not_shared_by_two_faces':sum(v!=2 for v in edgecounts.values())})
 report={'scope':'Static connected leather base mesh topology, not rig/deformation validation','gloves':results,'nominal_front_eye_gap_m':.005,'gap_measure_scope':'Source section z difference before2.5mm plate thickness; temple/back layer overlap is separately visually reviewed','front_only_eye_opening_design_intent':True,'no_legacy_brow_rail':not any(o.name.startswith('V2 | peaked brow') for o in S.objects)}
 assert len(results)==2
 (E/'focal-topology-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('FOCAL_AUDIT',json.dumps(report))

def audit_static_clearance():
 from mathutils.bvhtree import BVHTree
 dg=bpy.context.evaluated_depsgraph_get();verts=[];faces=[];owners=[]
 root=bpy.data.objects['CHARACTER | shoulder-turn study']
 for ob in S.objects:
  if ob.type!='MESH' or ob.hide_render or ob.parent!=root or 'cape' in ob.name.lower() or 'mantle' in ob.name.lower() or (ob.name=='V5 | sewn horseshoe wool yoke' and not os.environ.get('BOSSLAB_AUDIT_INCLUDE_YOKE')):continue
  ev=ob.evaluated_get(dg);me=ev.to_mesh();offset=len(verts);verts.extend([ev.matrix_world@v.co for v in me.vertices]);faces.extend([tuple(offset+i for i in face.vertices) for face in me.polygons]);owners.extend([ob.name]*len(me.polygons));ev.to_mesh_clear()
 tree=BVHTree.FromPolygons(verts,faces,all_triangles=False)
 cap=bpy.data.objects['V2 | tailored static cape - NOT SIMULATED'];ev=cap.evaluated_get(dg);me=ev.to_mesh();samples=[];failures=[]
 for vertex in me.vertices:
  p=ev.matrix_world@vertex.co
  if p.z>1.515:continue
  hit,normal,index,distance=tree.ray_cast(Vector((p.x,2,p.z)),Vector((0,-1,0)),4)
  if hit is not None:
   samples.append(p.y-hit.y)
   if p.y-hit.y<0:failures.append({'clearance':p.y-hit.y,'cape_point':list(p),'hit_point':list(hit),'hit_object':owners[index]})
 ev.to_mesh_clear();assert samples
 report={'kind':'Static sampled cape-vs-body back-envelope check, not simulated cloth or motion validation','evaluated_cape_vertices_with_body_ray_hit':len(samples),'min_y_clearance_m':min(samples),'vertices_behind_body_surface':sum(v>=0 for v in samples),'vertices_in_front_of_body_back_surface':sum(v<0 for v in samples),'excluded':'Top attachment zone z>1.515m; mantle including explicitly named V5 sewn horseshoe wool yoke and all curves; cape lies beneath this outer garment; checks vertex rays, not arbitrary triangle intersections','passes_sampled_static_clearance':min(samples)>=.003,'diagnostic_include_outer_yoke':bool(os.environ.get('BOSSLAB_AUDIT_INCLUDE_YOKE')),'negative_counts_by_hit_object':{name:sum(f['hit_object']==name for f in failures) for name in sorted(set(f['hit_object'] for f in failures))},'worst_samples':sorted(failures,key=lambda f:f['clearance'])[:20]}
 (E/'static-cape-clearance.json').write_text(json.dumps(report,indent=2)+'\n');print('STATIC_CAPE',json.dumps(report))


def authored_material_samples():
 """Original UV-space painted masks; no downloaded image or concept projection."""
 texdir=D/'textures';texdir.mkdir(exist_ok=True)
 N=1024;u,v=np.meshgrid(np.linspace(0,1,N),np.linspace(0,1,N));rng=np.random.default_rng(713)
 report=[]
 def image_map(name,arr,color=False):
  img=bpy.data.images.new(name,width=N,height=N,alpha=True);img.colorspace_settings.name='sRGB' if color else 'Non-Color'
  rgba=np.ones((N,N,4),dtype=np.float32)
  if arr.ndim==2:rgba[:,:,:3]=arr[:,:,None]
  else:rgba[:,:,:3]=arr
  img.use_fake_user=True;img.pixels.foreach_set(rgba.reshape(-1));img.filepath_raw=str(texdir/(name+'.png'));img.file_format='PNG';img.save();img.pack();return img
 def material(name,color,rough,height,metal):
  m=mat_simple(name,(.05,.05,.05),metal,.6);n=m.node_tree.nodes;l=m.node_tree.links;b=n.get('Principled BSDF');coords=n.new('ShaderNodeUVMap');coords.uv_map='Authored sample UV'
  for title,arr,socket,iscolor in [('color',color,'Base Color',True),('roughness',rough,'Roughness',False)]:
   im=image_map(name+'-'+title,arr,iscolor);nd=n.new('ShaderNodeTexImage');nd.image=im;l.new(coords.outputs['UV'],nd.inputs['Vector']);l.new(nd.outputs['Color'],b.inputs[socket])
  im=image_map(name+'-relief',height);nd=n.new('ShaderNodeTexImage');nd.image=im;l.new(coords.outputs['UV'],nd.inputs['Vector']);bu=n.new('ShaderNodeBump');bu.inputs['Distance'].default_value=.00015;bu.inputs['Strength'].default_value=.25;l.new(nd.outputs['Color'],bu.inputs['Height']);l.new(bu.outputs['Normal'],b.inputs['Normal']);return m
 # Helmet sample: authored interrupted lower exposed rim rub and selected brushing scars.
 rim=np.exp(-((v-.014)/.013)**2)*(np.clip(.6+.4*np.sin(u*31)+.2*np.sin(u*97),0,1))
 grime=np.exp(-((v-.002)/.005)**2)*.8;scars=np.zeros_like(u)
 for a,b,c in [(.025,.27,.035),(.04,.29,.025),(.94,.56,.045),(.97,.58,.032),(.12,.21,.035)]:
  scars+=np.exp(-((u-a-.07*(v-b))/.0007)**2-((v-b)/c)**8)
 scars=np.clip(scars,0,1);grain=rng.random((N,N))-.5
 rgb=np.zeros((N,N,3))+np.array([.235,.239,.244]);rgb+=rim[:,:,None]*.12;rgb-=grime[:,:,None]*.035;rgb+=scars[:,:,None]*.04
 steelmat=material('V3-authored-steel',np.clip(rgb,0,1),np.clip(.51-.19*rim+.14*grime-.06*scars+grain*.025,0,1),np.clip(.5-scars*.25+grain*.05,0,1),.92)
 image_map('steel-placement-mask',np.stack([rim,grime,scars],axis=2))
 for ob in list(S.objects):
  if ob.type!='MESH' or not ob.name.startswith('FOCAL | ') or not any(k in ob.name for k in ['skull','visor','occiput','gorget','crown closure']):continue
  me=ob.data;uv=me.uv_layers.new(name='Authored sample UV');zmin=min(p.co.z for p in me.vertices);zmax=max(p.co.z for p in me.vertices)
  for poly in me.polygons:
   values=[]
   for li in poly.loop_indices:
    p=me.vertices[me.loops[li].vertex_index].co;values.append(((math.atan2(p.x,-(p.y-.012))/(2*pi))%1,(p.z-zmin)/max(.001,zmax-zmin)))
   wrap=max(a for a,b in values)-min(a for a,b in values)>.5
   for li,(a,b) in zip(poly.loop_indices,values):uv.data[li].uv=(a+1 if wrap and a<.5 else a,b)
  me.materials.clear();me.materials.append(steelmat);report.append({'object':ob.name,'uv':'cylindrical plate field; seam at front median, periodic U','material':steelmat.name})
 # Leather: localized thumb/index contact and crease darkening, not cloud noise.
 contact=np.exp(-((u-.22)/.17)**2-((v-.48)/.28)**2)+.5*np.exp(-((u-.52)/.25)**2-((v-.16)/.13)**2)
 crease=np.exp(-((v-(.66+.10*(u-.4)))/.008)**2)*np.exp(-((u-.42)/.10)**2)+.65*np.exp(-((u-(.24+.18*(v-.6)))/.009)**2)*np.exp(-((v-.61)/.10)**2)
 seam=np.exp(-((u-.79)/.004)**2)*np.exp(-((v-.71)/.17)**8);stitch=seam*(np.sin(v*2*pi*44)>.55)
 rgb=np.zeros((N,N,3))+np.array([.115,.066,.033]);rgb+=contact[:,:,None]*np.array([.025,.015,.008]);rgb-=crease[:,:,None]*.018;rgb-=seam[:,:,None]*.018;rgb+=stitch[:,:,None]*np.array([.10,.085,.06])
 leathermat=material('V3-authored-leather',np.clip(rgb,0,1),np.clip(.76-.18*contact+.08*crease+grain*.03,0,1),np.clip(.5-.15*crease-.08*seam+.24*stitch+grain*.08,0,1),0)
 image_map('leather-placement-mask',np.stack([np.clip(contact,0,1),crease,stitch],axis=2))
 for ob in list(S.objects):
  if 'unified leather palm' not in ob.name:continue
  me=ob.data;cx=-.394 if 'L unified' in ob.name else .394;sg=-1 if cx<0 else 1;uv=me.uv_layers.new(name='Authored sample UV')
  for li,loop in enumerate(me.loops):
   p=me.vertices[loop.vertex_index].co;uv.data[li].uv=(((p.x-cx)*sg+.065)/.115,(p.z-.81)/.17)
  me.materials.clear();me.materials.append(leathermat);report.append({'object':ob.name,'uv':'local mirrored X/Z palm projection; dorsal overlap disclosed, not production unwrap','material':leathermat.name})
 (E/'material-sample-audit.json').write_text(json.dumps({'scope':'Original authored1024 UV-space color/roughness/relief and placement masks; no external assets. Sample only, not production atlas.','mask_channels':{'steel':'R interrupted exposed rim rub,G recess grime,B sparse directional scratches','leather':'R thumb/index/pad contact,G compression crease,B cuff stitch-height mask'},'objects':report,'map_resolution':[N,N]},indent=2)+'\n')


def audit_uv_samples():
 results=[]
 for ob in S.objects:
  if ob.type!='MESH' or not ob.data.uv_layers or not any(m and m.name.startswith('V3-authored') for m in ob.data.materials):continue
  me=ob.data;uv=me.uv_layers.get('Authored sample UV');assert uv is not None;me.calc_loop_triangles();N=256;cover=np.zeros((N,N),dtype=np.uint8);wire=np.ones((512,512,4),dtype=np.float32);wire[:,:,:3]=.025;degenerate=0
  for tri in me.loop_triangles:
   pts=np.array([uv.data[i].uv[:] for i in tri.loops]);pts[:,0]-=np.floor(pts[:,0].min());pts*=N-1
   a,b,c=pts;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
   if abs(den)<1e-8:degenerate+=1;continue
   lo=np.maximum(0,np.floor(pts.min(axis=0)).astype(int));hi=np.minimum(N-1,np.ceil(pts.max(axis=0)).astype(int))
   if any(hi<lo):continue
   xx,yy=np.meshgrid(np.arange(lo[0],hi[0]+1)+.5,np.arange(lo[1],hi[1]+1)+.5)
   aa=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den;bb=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;mask=(aa>=0)&(bb>=0)&(aa+bb<=1)
   cover[lo[1]:hi[1]+1,lo[0]:hi[0]+1]|=mask.astype(np.uint8)
  for face in me.polygons:
   vals=[uv.data[i].uv[:] for i in face.loop_indices]
   for a,b in zip(vals,vals[1:]+vals[:1]):
    aa=np.array(a);bb=np.array(b);aa[0]%=1;bb[0]%=1
    if abs(aa[0]-bb[0])>.5:continue
    line=np.linspace(aa,bb,max(2,int(np.linalg.norm(bb-aa)*512)));x=np.clip((line[:,0]*511).astype(int),0,511);y=np.clip((line[:,1]*511).astype(int),0,511);wire[y,x,:3]=(.3,.65,.8)
  if 'lower visor' in ob.name or 'R unified' in ob.name:
   name='uv-visor' if 'visor' in ob.name else 'uv-glove';img=bpy.data.images.new(name,width=512,height=512,alpha=True);img.pixels.foreach_set(wire.reshape(-1));img.filepath_raw=str(E/(name+'.png'));img.file_format='PNG';img.save()
  coords=np.array([p.uv[:] for p in uv.data]);results.append({'object':ob.name,'uv_name':uv.name,'uv_layers':[x.name for x in me.uv_layers],'explicit_uvmap_nodes':[n.uv_map for m in me.materials if m for n in m.node_tree.nodes if n.type=='UVMAP'],'uv_loops':len(coords),'finite':bool(np.isfinite(coords).all()),'bounds':coords.min(axis=0).tolist()+coords.max(axis=0).tolist(),'degenerate_uv_triangles':degenerate,'approx_occupied_256_grid_fraction':float(cover.mean()),'coverage_scope':'Rasterized union of projected UV triangles clipped to first tile; does not certify no overlap or distortion'})
 images=[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images if im.name.startswith('V3-authored') or 'placement-mask' in im.name]
 (E/'uv-map-audit.json').write_text(json.dumps({'objects':results,'maps':images,'glove_limitation':'Mirrored planar sample projection overlaps front/back and compresses side edges; not a production unwrap or atlas.'},indent=2)+'\n')

if mode in ['draft','support']:
 if mode=='support':E=E/'support-03';E.mkdir(exist_ok=True)
 revise();setdevice();S.render.resolution_x=480 if mode=='support' else 720;S.render.resolution_y=620 if mode=='support' else 920;S.cycles.samples=8 if mode=='support' else 16
 for v in args[1:] or ['head','clay_head','palm','clay_palm']:render(v)
 asset_audit();audit_focal();audit_uv_samples()
elif mode in ['render','audit','probe']:
 bpy.ops.wm.open_mainfile(filepath=str(D/'last-vigil-v5.blend'));S=bpy.context.scene;setdevice()
 if mode in ['render','probe']:
  S.render.resolution_x=1400;S.render.resolution_y=1800;S.cycles.samples=48
  if mode=='probe':S.render.resolution_x=720;S.render.resolution_y=920;S.cycles.samples=16
  for v in args[1:] or ['front','back','armor','hilt','sword']:render(v)
 asset_audit();audit_static_clearance();audit_focal();audit_uv_samples()
