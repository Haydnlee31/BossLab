"""Line the opened forge underarm seams with recessed panels sampled from the original dark leather."""
from collections import Counter,defaultdict
import array
import json
import numpy as np


def add_underarm_linings(original_file, seam_file, destination):
    from repair_arm_weights import field,geometry,parse_fbx,write_doc
    old,_=parse_fbx.parse(str(original_file));doc,version=parse_fbx.parse(str(seam_file))
    v,old_tris,clusters,names,weights=geometry(doc)
    def edges(f):
        mesh=next(k for k in field(f,b'Objects').elems if k.id==b'Geometry')
        poly=np.array(field(mesh,b'PolygonVertexIndex').props[0])
        ends=np.flatnonzero(poly<0); vertex=np.where(poly<0,-1-poly,poly)
        end_vertex=np.roll(vertex,-1);end_vertex[ends]=vertex[np.r_[0,ends[:-1]+1]]
        return mesh,poly,np.column_stack((vertex,end_vertex))
    _,original_poly,original_edges=edges(old)
    mesh,poly,new_edges=edges(doc)
    assert len(original_poly)==len(poly)
    shared=defaultdict(list)
    for i,edge in enumerate(original_edges): shared[tuple(sorted(edge))].append(i)
    border={}
    for ids in shared.values():
        es=new_edges[ids];keys=[tuple(sorted(pair)) for pair in es]
        if len(set(keys))>1:
            for pair in set(keys):border[pair]=tuple(es[keys.index(pair)])
    neighbors=defaultdict(set)
    for a,b in border:
        neighbors[a].add(b);neighbors[b].add(a)
    assert all(len(n)==2 for n in neighbors.values())
    rings=[]; unseen=set(neighbors)
    while unseen:
        start=min(unseen)
        ring=[start];prev=None;cur=start
        while True:
            other=min(x for x in neighbors[cur] if x!=prev)
            if other==start:break
            ring.append(other);prev,cur=cur,other
        unseen.difference_update(ring)
        # A rest slit has two coincident arcs and two shared hinge endpoints.
        counts=Counter(tuple(v[i]) for i in ring)
        hinges=[j for j,i in enumerate(ring) if counts[tuple(v[i])]==1]
        assert len(hinges)==2
        i,j=hinges;rings.extend((ring[i:j+1],ring[j:]+ring[:i+1]))
    assert len(rings)==8
    armcols=[i for i,n in enumerate(names) if n.endswith(('_r','_l')) and not n.startswith(('thigh','calf','foot','ball','clavicle'))]
    verts=list(v);wout=list(weights);triangles=[];uv={}
    def add_vertex(pos,weight):
        top=np.argsort(weight)[-4:];final=np.zeros(len(weight))
        final[top]=weight[top]/weight[top].sum()
        i=len(verts);verts.append(pos);wout.append(final)
        return i
    panel_types=[]
    for boundary in rings:
        # Reverse the direction of the existing face at the zipper seam.
        aligned=sum(border[tuple(sorted((a,b)))]==(a,b) for a,b in zip(boundary,boundary[1:]))
        if aligned>len(boundary)//2: boundary=boundary[::-1]
        pos=v[boundary]; centre=pos.mean(0)
        w=weights[boundary]; low=pos[:,2]<1.40
        is_sleeve=w[low][:,armcols].sum(1).mean()>.5
        panel_types.append('sleeve' if is_sleeve else 'torso')
        inward=np.array([np.sign(centre[0])*(1 if is_sleeve else -1),0.,0.])
        # Each shell gets its own lining, recessed into that shell at rest, so
        # opposing panels never lie on top of one another. The hinge endpoints
        # still share the natural shoulder join.
        weights_mid=w.mean(0)
        if is_sleeve: weights_mid[[j for j in range(len(names)) if j not in armcols]]=0
        else: weights_mid[armcols]=0
        weights_mid/=weights_mid.sum()
        inner=[];coords={}
        for i,point,wi in zip(boundary,pos,w):
            j=add_vertex(centre+.57*(point-centre)+inward*.023,.65*wi+.35*weights_mid)
            inner.append(j);coords[i]=point;coords[j]=centre+.57*(point-centre)
        centre_index=add_vertex(centre+inward*.032,weights_mid);coords[centre_index]=centre
        # Map each panel onto a contiguous worn-leather swatch of the existing
        # 2048px texture (measured without crossing neighboring atlas islands).
        span=pos[:,1:3].max(0)-pos[:,1:3].min(0);min_yz=pos[:,1:3].min(0)
        panel_uv={i:np.array([(170+116*(q[1:3]-min_yz)[0]/span[0])/2048,
                              1-(498-84*(q[1:3]-min_yz)[1]/span[1])/2048]) for i,q in coords.items()}
        for j,a in enumerate(boundary):
            k=(j+1)%len(boundary);b=boundary[k]
            for face in [(a,b,inner[k]),(a,inner[k],inner[j]),(inner[j],inner[k],centre_index)]:
                triangles.append(face);uv[len(triangles)-1]=[panel_uv[q] for q in face]
    assert panel_types.count('sleeve')==4
    verts=np.asarray(verts);wout=np.asarray(wout);faces=np.asarray(triangles)
    corner=faces.copy();corner[:,-1]=-corner[:,-1]-1
    fullpoly=np.r_[poly,corner.flatten()]
    def setarray(node,key,values,code):
        target=field(node,key);target.props[0]=array.array(code,values.astype({'d':'<f8','i':'<i4'}[code]).tobytes())
    def append(node,key,values,code):
        target=field(node,key);target.props[0].extend(array.array(code,values.astype({'d':'<f8','i':'<i4'}[code]).tobytes()))
    setarray(mesh,b'Vertices',verts.ravel(),'d')
    setarray(mesh,b'PolygonVertexIndex',fullpoly,'i')
    _,_,es=edges(doc)
    _,single=np.unique(np.sort(es,axis=1),axis=0,return_index=True)
    setarray(mesh,b'Edges',np.sort(single),'i')
    norms=field(mesh,b'LayerElementNormal');uvlayer=field(mesh,b'LayerElementUV')
    normal_offset=len(field(norms,b'Normals').props[0])//3
    uvoffset=len(field(uvlayer,b'UV').props[0])//2
    # Soft lining normals; retain the original exported rim normals outside.
    normals=np.cross(verts[faces[:,1]]-verts[faces[:,0]],verts[faces[:,2]]-verts[faces[:,0]])
    assert (np.linalg.norm(normals,axis=1)>1e-8).all()
    vertex_normals=np.zeros_like(verts)
    for j in range(3):np.add.at(vertex_normals,faces[:,j],normals)
    vertex_normals/=np.maximum(np.linalg.norm(vertex_normals,axis=1,keepdims=True),1e-12)
    append(norms,b'Normals',vertex_normals[faces].ravel(),'d')
    append(norms,b'NormalsIndex',normal_offset+np.arange(faces.size),'i')
    append(uvlayer,b'UV',np.array(list(uv.values())).ravel(),'d')
    append(uvlayer,b'UVIndex',uvoffset+np.arange(faces.size),'i')
    append(field(mesh,b'LayerElementMaterial'),b'Materials',np.zeros(len(faces)),'i')
    append(field(mesh,b'LayerElementSmoothing'),b'Smoothing',np.ones(len(faces)),'i')
    for j,c in enumerate(clusters):
        ids=np.flatnonzero(wout[:,j]>0)
        setarray(c,b'Indexes',ids,'i')
        setarray(c,b'Weights',wout[ids,j],'d')
    write_doc(doc,version,destination)
    reread,_=parse_fbx.parse(str(destination));v2,f2,_,_,w2=geometry(reread)
    assert np.array_equal(v2,verts) and np.allclose(w2,wout)
    # geometry() expands quad fans in batches. Hash the original triangulated
    # surface independently of the insertion point for the extra triangles.
    _,poly2,finished_edges=edges(reread)
    rim_counts=Counter(tuple(sorted(pair)) for pair in finished_edges)
    assert all(rim_counts[key]>=2 for key in border)
    cap_position_keys=[tuple(sorted(map(tuple,verts[face]))) for face in faces]
    assert len(set(cap_position_keys))==len(cap_position_keys)
    assert np.array_equal(poly2[:len(poly)],poly) and len(f2)==len(old_tris)+len(faces)
    out={'panels':len(rings),'sleeve_panels':4,'torso_panels':4,'added_triangles':len(faces),'added_vertices':len(verts)-len(v),
         'covered_boundary_edges':len(border),'boundary_edges_still_open':0,'coincident_cap_triangles':0,'exterior_corner_indices_preserved':True,'result_triangles':len(f2),
         'recess_cm':[2.3,3.2], 'material':'existing BossLab Bellbreaker leather atlas'}
    (destination.parent/'underarm-lining.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out)
