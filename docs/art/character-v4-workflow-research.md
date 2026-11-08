# V4 workflow research and diagnosis — 2026-11-07

The current bottleneck is our modeling quality and method. A single concept image supplies projected shape, light and material cues, but does not specify hidden surfaces, depth, mesh topology or garment construction. These require authored decisions. No physics setting converts a round simplified helmet into the concept’s angular forged plates. Storage currently permits this form work; adding memory or polygons alone does not solve it.

Official sources consulted:
- [Epic Skeletal Meshes](https://dev.epicgames.com/documentation/en-us/unreal-engine/skeletal-mesh-assets-in-unreal-engine): visual mesh and skeleton are built externally/imported; physics and animation are distinct components.
- [Epic Clothing Tool](https://dev.epicgames.com/documentation/en-us/unreal-engine/clothing-tool-in-unreal-engine): cloth simulation uses existing skeletal-mesh sections and collision physics assets. It handles motion, not initial outfit design fidelity.
- [Blender sculpting overview](https://www.blender.org/features/sculpting/): official search excerpt describes dynamic topology adding/removing detail; full page fetch failed in this session. Do not treat remeshing/density as anatomy or artistic correctness.

Applied judgment from actual images: replace rounded helmet profile with explicit brow/cheek/visor planes; make mantle drape over shoulders instead of a radial brush ring; shape armor taper/plate edges to the concept. Check front/side/clay before fine wear. Then repair glove anatomy and UVs. Subsequent production steps remain topology/UV/bake, skeleton/weights, deformation/cloth/collision, LOD/runtime testing. These are separate readiness gates, and no new AI work is authorized before other foundations are ready.
