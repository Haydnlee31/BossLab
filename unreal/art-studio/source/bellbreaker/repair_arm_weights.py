"""Repair arm/torso ownership on the original Bellbreaker FBX. No DCC or network job.

Run with NumPy and SciPy: python3 unreal/art-studio/source/bellbreaker/repair_arm_weights.py
Retains every polygon at rest. Splits shared cuff/tunic vertices along the authored underarm seam.
"""
from pathlib import Path
import array
import hashlib
import heapq
import json
import sys
import types
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "artifacts/unreal/bellbreaker-dialogue"
MODEL = ROOT / "artifacts/art/bellbreaker-boss-2026-11-18/rig-v3/out/SKM_BellbreakerRig.fbx"
# Reuse the binary FBX reader/writer shipped with the project-local Blender.
package = types.ModuleType("bosslab_fbx")
package.__path__ = [str(ROOT / "unreal/art-studio/tools/Blender.app/Contents/Resources/4.5/scripts/addons_core/io_scene_fbx")]
sys.modules[package.__name__] = package
from bosslab_fbx import encode_bin, parse_fbx


def field(node, name):
    return next(item for item in node.elems if item.id == name)


def geometry(doc):
    objects = field(doc, b'Objects').elems
    mesh = next(n for n in objects if n.id == b'Geometry')
    positions = np.asarray(field(mesh, b'Vertices').props[0]).reshape(-1, 3)
    indices = np.asarray(field(mesh, b'PolygonVertexIndex').props[0])
    ends = np.flatnonzero(indices < 0)
    indices = np.where(indices < 0, -indices-1, indices)
    starts = np.r_[0, ends[:-1]+1]
    fans = []
    for i in range(1, max(ends-starts)):
        used = starts+i+1 <= ends
        fans.append(np.column_stack((indices[starts[used]], indices[starts[used]+i], indices[starts[used]+i+1])))
    tris = np.vstack(fans)
    clusters = [n for n in objects if n.id == b'Deformer' and n.props[2] == b'Cluster' and any(k.id == b'Weights' for k in n.elems)]
    names = [c.props[1].split(b'\x00')[0].decode() for c in clusters]
    weights = np.zeros((len(positions),len(names)))
    for i,c in enumerate(clusters):
        weights[np.asarray(field(c,b'Indexes').props[0]),i] = np.asarray(field(c,b'Weights').props[0])
    return positions,tris,clusters,names,weights


def surface_labels(v,edges):
    # At 1.18 m the torso and both bent forearms are topologically separate even
    # though their nearest Euclidean points nearly touch. Seed from the three
    # large components and extend ownership around the armpit by surface distance.
    neighbors = [[] for _ in v]
    for a,b in edges:
        d = np.linalg.norm(v[a]-v[b])
        neighbors[a].append((b,d))
        neighbors[b].append((a,d))
    low = v[:,2] < 1.18
    seen = ~low
    groups = []
    for start in np.flatnonzero(low):
        if seen[start]: continue
        component = [start]
        seen[start] = True
        for i in component:
            for j,_ in neighbors[i]:
                if not seen[j]:
                    seen[j] = True
                    component.append(j)
        if len(component)>1000: groups.append(np.array(component))
    assert len(groups)==3
    groups.sort(key=lambda g:v[g,0].mean())
    assert v[groups[0],0].mean()<-.4 and abs(v[groups[1],0].mean())<.1 and v[groups[2],0].mean()>.4
    # Find laterally separate surfaces in narrow horizontal cuts above the elbows.
    # A fused cuff or cloth bridge lower down must not merge the entire upper
    # sleeve into the abdomen. Truly connected upper shoulders stay unseeded.
    seeds=[set(g) for g in groups]
    for z in np.arange(1.18,1.39,.024):
        band=np.abs(v[:,2]-z)<.020
        seen=~band
        for start in np.flatnonzero(band):
            if seen[start]: continue
            group=[start];seen[start]=True
            for k in group:
                for j,_ in neighbors[k]:
                    if not seen[j]:
                        group.append(j);seen[j]=True
            points=v[group]; lo,hi=np.quantile(points[:,0],[.04,.96])
            if hi-lo>.18 and lo<-.17 and hi>.17 and lo>-.34 and hi<.34: label=1
            elif lo>.17 and hi>.34: label=2
            elif hi<-.17 and lo<-.34: label=0
            elif max(abs(lo),abs(hi))<.22: label=1
            else: continue
            seeds[label].update(group)
    # Classify tiny disconnected trim by proximity to the underlying main surfaces.
    # Each island gets one owner so fixed metal decorations do not shear.
    seen[:]=False
    for start in range(len(v)):
        if seen[start]: continue
        island=[start];seen[start]=True
        for k in island:
            for j,_ in neighbors[k]:
                if not seen[j]: island.append(j);seen[j]=True
        if len(island)>500 or max(v[island,2])>1.35:continue
        centre=v[island].mean(0)
        if max(v[island,2])<.78 or abs(centre[0])<.13:continue
        dist=[np.min(np.linalg.norm(v[list(group)]-centre,axis=1)) for group in seeds]
        owner=np.argmin(dist)
        for group in seeds:group.difference_update(island)
        seeds[owner].update(island)
    # Disconnected slivers can make a horizontal band misidentify a patch of
    # outer cuff as rib cage. The projected Quake shows ca. x = ±43 cm at
    # z = 126 cm: this is physically outside the smith's chest. Anchor the
    # outer sleeve and sternum along their actual bind-space anatomy before
    # assigning the ambiguous contact patches by surface distance.
    for i,(x,y,z) in enumerate(v):
        if not 1.12 <= z <= 1.42: continue
        xx=abs(x)
        if xx>=.305: label=2 if x>0 else 0
        elif xx<.166 or (xx<.205 and abs(y)>.14): label=1
        else: continue
        for g in seeds: g.discard(i)
        seeds[label].add(i)
    distances=[]
    for seed in seeds:
        group=np.array(list(seed))
        ds=np.full(len(v),np.inf)
        ds[group]=0
        todo=[(0.,i) for i in group if any(j not in seed for j,_ in neighbors[i])]
        heapq.heapify(todo)
        while todo:
            d,i=heapq.heappop(todo)
            if d!=ds[i]: continue
            for j,cost in neighbors[i]:
                nxt=d+cost
                if nxt<ds[j] and v[j,2]<1.46:
                    ds[j]=nxt
                    heapq.heappush(todo,(nxt,j))
        distances.append(ds)
    return groups,np.array(distances)


def smooth(x):
    u=np.clip(x,0,1)
    return u*u*(3-2*u)


def write_doc(doc,version,path):
    methods=dict(zip("BCZYILFDRSilfdbc","bool char int8 int16 int32 int64 float32 float64 bytes string int32_array int64_array float32_array float64_array bool_array byte_array".split()))
    def convert(node):
        n=encode_bin.FBXElem(node.id)
        for typ,value in zip(node.props_type,node.props):
            getattr(n,"add_"+methods[chr(typ)])(value)
        n.elems=[convert(ch) for ch in node.elems]
        return n
    encode_bin.write(str(path),convert(doc),version)


def unchanged_signature(node,parent=b''):
    digest=hashlib.sha256()
    def visit(n,prev):
        if prev==b'Deformer' and n.id in (b'Weights',b'Indexes'): return
        if prev==b'Geometry' and n.id in (b'Vertices',b'PolygonVertexIndex',b'Edges'): return
        digest.update(n.id)
        digest.update(bytes(n.props_type))
        for prop in n.props:
            digest.update(prop.tobytes() if isinstance(prop,array.array) else repr(prop).encode())
        for ch in n.elems: visit(ch,n.id)
    visit(node,parent)
    return digest.hexdigest()


def split_underarm_vertices(source,v,names,weights,original,owner):
    mesh=next(k for k in field(source,b'Objects').elems if k.id==b'Geometry')
    oldp=np.array(field(mesh,b'PolygonVertexIndex').props[0]);ends=np.flatnonzero(oldp<0)
    corners=np.where(oldp<0,-1-oldp,oldp)
    starts=np.r_[0,ends[:-1]+1]; counts=ends-starts+1
    poly_owner=np.add.reduceat(owner[corners].astype(int),starts)*2>=counts
    corner_owner=np.repeat(poly_owner,counts)
    region=(np.abs(v[:,0])>.155)&(v[:,2]>1.05)&(v[:,2]<1.445)
    newp=corners.copy();duplicates=[];new_weights=[]
    armcols=[i for i,n in enumerate(names) if n.endswith(('_r','_l')) and not n.startswith(('clavicle','ball','calf','thigh','foot'))]
    sides=[([i for i in armcols if names[i].endswith('_r')],'upperarm_r'),([i for i in armcols if names[i].endswith('_l')],'upperarm_l'),([i for i in range(len(names)) if i not in armcols],'spine_04')]
    for group,arm,fallback in [(True,0,'upperarm_r'),(True,1,'upperarm_l'),(False,2,'spine_04')]:
        request=(corner_owner==group)&(owner[corners]!=group)&region[corners]
        if group: request&=(v[corners,0]<0 if arm==0 else v[corners,0]>=0)
        ids,index=np.unique(corners[request],return_inverse=True)
        newp[request]=len(v)+len(duplicates)+index
        cols=sides[arm][0]
        family=original[np.ix_(ids,cols)].copy()
        empty=family.sum(1)<1e-8
        family[empty,cols.index(names.index(fallback))]=1
        family/=family.sum(1)[:,None]
        strength=smooth((v[ids,2]-1.05)/.07)*(1-smooth((v[ids,2]-1.35)/.095))
        new=weights[ids]*(1-strength[:,None]);new[:,cols]+=family*strength[:,None]
        top=np.argpartition(new,-4)[:,-4:]; reduced=np.zeros_like(new);rows=np.arange(len(ids))[:,None];reduced[rows,top]=new[rows,top];reduced/=reduced.sum(1)[:,None]
        new_weights.extend(reduced);duplicates.extend(ids)
    duplicates=np.array(duplicates,dtype=int)
    vout=np.vstack((v,v[duplicates]))
    weights=np.vstack((weights,new_weights))
    newp[ends]=-newp[ends]-1
    field(mesh,b'Vertices').props[0]=array.array('d',vout.astype('<f8').tobytes())
    field(mesh,b'PolygonVertexIndex').props[0]=array.array('i',newp.astype('<i4').tobytes())
    # FBX Edges stores representative face-corner offsets. Regenerate only their
    # references so duplicates get their own half-edges; all existing corner
    # normals/UVs, face smoothing and material IDs remain valid.
    nc=np.where(newp<0,-1-newp,newp)
    nextc=np.roll(nc,-1);nextc[ends]=nc[starts]
    _,single=np.unique(np.sort(np.column_stack((nc,nextc)),axis=1),axis=0,return_index=True)
    field(mesh,b'Edges').props[0]=array.array('i',np.sort(single).astype('<i4').tobytes())
    return vout,weights,len(duplicates),int(np.count_nonzero(corners!=nc))


def main():
    source,version=parse_fbx.parse(str(MODEL))
    sig=unchanged_signature(source)
    v,faces,clusters,names,original=geometry(source)
    edges=np.unique(np.sort(np.vstack((faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]])),axis=1),axis=0)
    groups,ds=surface_labels(v,edges)
    finite=np.isfinite(ds).any(0)
    labels=ds.argmin(0)
    # Soften the transition between neighboring branches, then fade out to
    # original shoulder and clavicle paint.
    second=np.sort(ds,axis=0)[1]
    delta=np.zeros(len(v))
    delta[finite]=second[finite]-ds.min(0)[finite]
    strength=smooth(delta/.035)*(1-smooth((v[:,2]-1.28)/.15))*finite
    arm_cols=[i for i,n in enumerate(names) if n.endswith(('_r','_l')) and not n.startswith(('ball','foot','calf','thigh','clavicle'))]
    torso_cols=[i for i in range(len(names)) if i not in arm_cols]
    fixed=original.copy()
    for group,cols,fallback in [(1,torso_cols,'spine_02'),(0,[i for i in arm_cols if names[i].endswith('_r')],'lowerarm_r'),(2,[i for i in arm_cols if names[i].endswith('_l')],'lowerarm_l')]:
        rows=np.flatnonzero((labels==group)&(strength>0))
        retained=original[np.ix_(rows,cols)].copy()
        zero=retained.sum(1)<1e-8
        retained[zero,cols.index(names.index(fallback))]=1
        retained/=retained.sum(1)[:,None]
        w=strength[rows,None]
        if group!=1:
            outer=smooth((np.abs(v[rows,0])-.265)/.06)*smooth((v[rows,2]-1.10)/.07)*(1-smooth((v[rows,2]-1.37)/.11))
            w=np.maximum(w,outer[:,None])
        fixed[rows]*=1-w
        fixed[np.ix_(rows,cols)]+=w*retained
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import maximum_flow,breadth_first_order
    # Join edges with capacities approximating geometric seam length. Min-cut
    # selects the thin fuse between two touching shells rather than bisecting a cuff.
    nn=len(v);aa=nn;bb=nn+1
    axis=np.abs(v[:,0]);z=v[:,2];y=v[:,1]
    arm_seed=((axis>.315)&(z<1.40)&(z>.78))
    body_seed=((axis<.16)&(z<1.58)) | (z<.69) | (z>1.55)
    arm_seed[np.r_[groups[0],groups[2]]]=True
    body_seed[groups[1]]=True
    arm_seed[body_seed]=False
    armdi=np.flatnonzero(arm_seed); bodi=np.flatnonzero(body_seed)
    # Penalize cutting broad connected surfaces; allow a natural shoulder seam
    # near the upper-arm pivot where blending is already required.
    capacity=np.maximum(1,np.linalg.norm(v[edges[:,0]]-v[edges[:,1]],axis=1)*20000).astype(int)
    a,b=edges.T
    rows=np.r_[a,b,np.full(len(armdi),aa),bodi]
    cols=np.r_[b,a,armdi,np.full(len(bodi),bb)]
    capacities=np.r_[capacity,capacity,np.full(len(armdi)+len(bodi),10000000)]
    graph=coo_matrix((capacities,(rows,cols)),shape=(nn+2,nn+2),dtype=np.int64).tocsr()
    flow=maximum_flow(graph,aa,bb)
    residual=graph-flow.flow;residual.eliminate_zeros()
    access=breadth_first_order(residual,i_start=aa,directed=True,return_predecessors=False)
    owner=np.zeros(nn,bool);owner[access[access<nn]]=True
    # Top of sleeve connects smoothly to the shoulder, fenced lower cuff moves
    # with elbow/arm. Preserve original arm rotation gradients in each family.
    for select,cols,fallback in [(owner&(v[:,0]<0),[i for i in arm_cols if names[i].endswith('_r')],'upperarm_r'),(owner&(v[:,0]>0),[i for i in arm_cols if names[i].endswith('_l')],'upperarm_l'),(~owner,torso_cols,'spine_04')]:
        strength=smooth((z-.74)/.11)*(1-smooth((z-1.33)/.12))*smooth((axis-.10)/.06)
        ids=np.flatnonzero(select&(strength>0));old=original[np.ix_(ids,cols)].copy()
        old[old.sum(1)<1e-8,cols.index(names.index(fallback))]=1
        old/=old.sum(1)[:,None]
        factor=strength[ids,None]
        fixed[ids]*=1-factor;fixed[np.ix_(ids,cols)]+=old*factor
    # Mark diffuse underarm bridges for an independent seam audit.

    fixed[fixed<1e-9]=0
    fixed/=fixed.sum(1)[:,None]
    changed=np.abs(fixed-original).max(1)>1e-5
    assert np.isfinite(fixed).all() and (fixed>=0).all() and (original.sum(1)>.999).all()

    # FBX importer keeps the four strongest weights. Normalize those explicitly.
    keep=np.argpartition(fixed,-4,axis=1)[:,-4:]
    weights=np.zeros_like(fixed);rows=np.arange(len(v))[:,None]
    weights[rows,keep]=fixed[rows,keep]
    weights/=weights.sum(1)[:,None]
    # Copy all untouched rows bit-for-bit.
    weights[~changed]=original[~changed]
    vout,weights,dupes,relinked=split_underarm_vertices(source,v,names,weights,original,owner)
    for i,c in enumerate(clusters):
        ids=np.flatnonzero(weights[:,i]>0)
        field(c,b'Indexes').props[0]=array.array('i',ids.astype(np.int32).tobytes())
        field(c,b'Weights').props[0]=array.array('d',weights[ids,i].astype(np.float64).tobytes())
    OUT.mkdir(parents=True,exist_ok=True)
    target=OUT/'SKM_BellbreakerForgeSkin.fbx'
    write_doc(source,version,target)
    reread,_=parse_fbx.parse(str(target))
    assert unchanged_signature(reread)==sig
    v2,faces2,_,outnames,check=geometry(reread)
    assert np.array_equal(v2[faces2],v[faces])
    assert outnames==names and np.array_equal(check,weights)
    # Synthetic raised arms, same pose for both weight maps. Rotating about
    # each shoulder exaggerates arm contamination on isolated tunic geometry.
    posed=[]
    for bind,paint in [(v,original),(vout,weights)]:
        points=bind.copy()
        for group,sgn,side in [(0,-1,'_r'),(2,1,'_l')]:
            pivot=np.array([sgn*.263,.026,1.413])
            angle=np.radians(-sgn*132)
            rot=np.array([[np.cos(angle),0,np.sin(angle)],[0,1,0],[-np.sin(angle),0,np.cos(angle)]])
            arm=paint[:,[i for i in arm_cols if names[i].endswith(side)]].sum(1)
            points+=(((bind-pivot)@rot.T+pivot)-bind)*arm[:,None]
        posed.append(points)
    def metrics(g,pts):
        mask=np.zeros(len(v),bool);mask[g]=True
        facemask=mask[faces].all(1)
        reference=v if len(pts)==len(v) else vout
        tri=faces[facemask] if len(pts)==len(v) else faces2[facemask]
        ed=np.unique(np.sort(np.vstack((tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]])),axis=1),axis=0)
        def lengths(mesh): return np.linalg.norm(mesh[ed[:,0]]-mesh[ed[:,1]],axis=1)
        def areas(mesh): return np.linalg.norm(np.cross(mesh[tri[:,1]]-mesh[tri[:,0]],mesh[tri[:,2]]-mesh[tri[:,0]]),axis=1)
        length=lengths(reference);area=areas(reference)
        lr=lengths(pts)[length>.001]/length[length>.001];ar=areas(pts)[area>.000004]/area[area>.000004]
        return dict(triangles=len(ar),edges_stretched_over_2x=int((lr>2).sum()),triangles_over_2x=int((ar>2).sum()), triangles_below_half=int((ar<.5).sum()),max_edge_ratio=round(lr.max(),3))
    report={"non_geometry_and_bind_signature":sig,"triangulated_corner_positions_identical":True,"added_seam_vertices":dupes,"relinked_face_corners":relinked,"output_vertices":len(vout),"changed_vertices":int(changed.sum()),"total_vertices":len(v),"synthetic_arm_raise_degrees":132,"regions":{}}
    for label,g in zip(['right_arm','torso','left_arm'],groups):
        report["regions"][label]={"original":metrics(g,posed[0]),"repainted":metrics(g,posed[1])}
    report['whole_mesh_raised_pose']={key:metrics(np.arange(len(v)),points) for key,points in zip(['original','repainted'],posed)}
    (OUT/'skin-repaint.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':
    main()
    from cap_cuff_lining import add_underarm_linings
    result=OUT/'SKM_BellbreakerForgeSkin.fbx'
    add_underarm_linings(MODEL,result,result)

