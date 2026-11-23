"""Read actual HF GLB geometry without a DCC; not a collision/visual certificate."""
from pathlib import Path
import hashlib, json, struct
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'artifacts/art/bellbreaker-smeltery-2026-11-16'

def audit(path):
    raw = path.read_bytes()
    magic, version, size = struct.unpack_from('<4sII', raw)
    assert (magic, version, size) == (b'glTF', 2, len(raw))
    at, chunks = 12, {}
    while at < len(raw):
        length, kind = struct.unpack_from('<II', raw, at)
        chunks[kind] = raw[at+8:at+8+length]
        at += 8+length
    doc = json.loads(chunks[0x4E4F534A]); buf = chunks[0x004E4942]
    def arr(index):
        a=doc['accessors'][index]; v=doc['bufferViews'][a['bufferView']]
        assert not a.get('sparse') and v.get('buffer',0)==0
        dtype=np.dtype({5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']])
        n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
        return np.ndarray((a['count'],n),dtype,buf,v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',n*dtype.itemsize),dtype.itemsize))
    tris=vertices=bad=tiny=0; bounds=[]
    for mesh in doc.get('meshes',[]):
        for primitive in mesh['primitives']:
            assert primitive.get('mode',4)==4
            p=arr(primitive['attributes']['POSITION']); idx=arr(primitive['indices']).reshape(-1,3)
            assert np.isfinite(p).all() and idx.max()<len(p)
            tri=p[idx].astype('float64'); area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2
            tris+=len(idx);vertices+=len(p);bad+=int(np.count_nonzero(area==0));tiny+=int(np.count_nonzero(area<=1e-12))
            bounds.append({'min':p.min(axis=0).tolist(),'max':p.max(axis=0).tolist()})
    return {'asset':path.parent.name,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'triangles':tris,'vertices':vertices,'zero_area_triangles':bad,'triangles_area_le_1e_minus_12_source_units':tiny,'mesh_count':len(doc.get('meshes',[])),'material_count':len(doc.get('materials',[])),'embedded_images':all('bufferView' in i for i in doc.get('images',[])),'image_count':len(doc.get('images',[])),'external_buffers':any('uri' in b for b in doc.get('buffers',[])),'bounds':bounds}

if __name__=='__main__':
    results=[audit(p) for p in sorted((OUT/'generated').glob('*/model.glb'))]
    report={'scope':'Source binary and triangle audit only. Generated maps are not calibrated PBR; derived runtime copies require independent cleanup and visual inspection.','assets':results}
    (OUT/'source-glb-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
