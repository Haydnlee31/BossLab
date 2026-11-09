"""Bake the dungeon floor's procedural masks into one texture (an optimisation).

Run: .venv-gen3d/bin/python unreal/art-studio/source/arena/bake_floor_masks.py <out.png>
Evaluates the same world-space mask maths as ue_import_floor.py's runtime version over the
floor disc (2900 x 2900 cm centred on the arena, 2048 px, ~1.4 cm/texel) and writes RGBA:
R flagstone ring, G puddle, B grime (+ old blood above 0.5), A crack. The floor material
then samples this once per pixel instead of ~100 hash/noise evaluations.
"""
import sys
import numpy as np
from PIL import Image

N, SPAN = 2048, 2900.0
xs = (np.arange(N) + .5) / N * SPAN - SPAN / 2
X, Y = np.meshgrid(xs, -xs)          # image row 0 = +Y (north), matches the material's UV
def h(px, py):
    return np.modf(np.sin(px * 127.1 + py * 311.7) * 43758.5453)[0] % 1.0
def vn(px, py):
    ix, iy = np.floor(px), np.floor(py); fx, fy = px - ix, py - iy
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b, c, d = h(ix, iy), h(ix + 1, iy), h(ix, iy + 1), h(ix + 1, iy + 1)
    return (a + (b - a) * fx) + ((c + (d - c) * fx) - (a + (b - a) * fx)) * fy
def fbm(px, py):
    return vn(px, py) * .55 + vn(px * 2.03 + 7.1, py * 2.03 + 7.1) * .3 + vn(px * 4.1 + 3.3, py * 4.1 + 3.3) * .15
def smooth(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)
r = np.hypot(X, Y)
edge = fbm(X / 180, Y / 180) * 120
ring = smooth(360, 430, r + edge) * (1 - smooth(1080, 1160, r + edge))
# Soft edges: hard-edged dark ovals read as holes in the floor.
pud = np.clip(smooth(.6, .76, fbm(X / 330 + 11.3, Y / 330 + 11.3)) * (.45 + .55 * fbm(X / 90, Y / 90)) * 1.3, 0, 1)
grime = smooth(.45, .85, fbm(X / 260 + 4.2, Y / 260 + 4.2))
# Cracks: voronoi edge distance on a 140 cm lattice.
cx, cy = X / 140, Y / 140; icx, icy = np.floor(cx), np.floor(cy)
d1 = np.full_like(cx, 9.0); d2 = np.full_like(cx, 9.0)
for oy in (-1, 0, 1):
    for ox in (-1, 0, 1):
        gx, gy = icx + ox, icy + oy
        qx = gx + h(gx, gy) - cx; qy = gy + h(gx + 5.1, gy + 5.1) - cy
        d = qx * qx + qy * qy
        closer = d < d1
        d2 = np.where(closer, d1, np.minimum(d2, d)); d1 = np.where(closer, d, d1)
crack = (1 - smooth(0, .035, np.sqrt(d2) - np.sqrt(d1))) * smooth(.55, .7, fbm(X / 200 + 8.8, Y / 200 + 8.8))
blood = smooth(.7, .78, fbm(X / 120 + 21.7, Y / 120 + 21.7)) * (1 - smooth(250, 700, r))
# B packs grime in [0, .5] and blood in (.5, 1].
b = np.where(blood > .05, .5 + .5 * blood, .5 * grime)
rgba = np.stack([ring, pud, b, crack], -1)
Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), 'RGBA').save(sys.argv[1])
print('BOSSLAB floor masks', sys.argv[1], N, SPAN)
