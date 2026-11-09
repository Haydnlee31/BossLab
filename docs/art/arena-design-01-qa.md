# Arena design01 — independent QA

2026-11-09. Final status: ready for human studio layout review only (candidate03). This review concerns an offline arena proposal derived from the current Claude-revamp branch, not a tested Unreal map. No gameplay tests, renderer launches, source edits or FPS measurements were performed by QA.

## Review contract

- Existing nominal floor R14m; wall inner face R13.325m; eight pillar inward extrema R13.05m. Preserve existing actors/collision rather than replacing them with these rounded dimensions.
- Primary tactical disk R12m and proposed clear art disk R12.8m are distinct guides, neither a smaller gameplay boundary. No raised props, steps, trim, chains or cover within the disk; decorative floor bands remain flush.
- Spawn X−4.5m/+3m gives7.5m separation. Entry−X/apse+X; scenic supports R16.5m+ require their complete footprints, not centres alone, checked for encroachment.
- Future hook lanes must remain unobstructed, but hook mechanics are not implemented or validated here. Studio clearance cannot certify sweep collision, iframe semantics or escape timing.
- Actual floorplan overlay, player-height axial/near-wall views and clay construction must accompany beauty images. A1.7m entrance camera is a human-height architecture view, not an exact Unreal spring-arm/FOV75 test.

## Acceptance questions

Do actual visible floor and enclosing boundary explain where movement stops? Architecture several metres behind the existing collision risks an apparently accessible blocked strip. Do wall/pillar silhouettes remain legible near the camera? Existing620cm spring arm/collision retraction and24m lock-break distance remain limitations, not solved by a wider scenic room.

Are boss silhouette and chain hand readable against the apse, with cold skull flames the strongest saturated blue rather than ambient fixtures? Check lights/effects disabled too. A proxy without actual costume/skull effects supports only preliminary value/silhouette review.

Do arches meet capitals, vault ribs meet supports and sealed oculus close the roof without floating construction? Director requests a sealed chamber; older engine suggestion of an optional open upper arcade is a studio-design alternative, not authority to add runtime roof collision.

## Protected scope

Parent owns the43-file game/config/Revamp protection baseline and final integrity audit. No current character, animation, combat, AI, collision or lighting changes are authorized by this studio review.10GB Unreal/24GiB reserve and one heavy-job owner remain in effect. Final judgment will distinguish numeric layout, observed appearance and untested runtime behavior.

## Candidate02 interim source/layout review

Read actual geometry/readback JSON and inspected gameplay-height and near-boundary-inward renders. Nominal floor/wall/pillar dimensions agree with the contract; spawn references give7.5m separation. Source floor treatment is thickness-free mesh atZ0.001m, not literally coplanar withZ0: future material baking/noncollision treatment remains required. Clear floor and continuous visible inner boundary are legible in these views. The central existing pillar obscures the throne/door axis; candidate03 is correcting the visual arrangement without moving collision.

Candidate02 support JSON measures a.38m shaft radius only. Final source uses the full.62m plinth: centre distance hypot(16.8,2.65) minus.62 gives16.3877188m minimum conservative circular footprint.16.18m is the more conservative radial-axis bound, not the exact centre-distance result. Await final saved-scene full geometry audit rather than extending shaft numbers to all architecture.

Read proposed final audit implementation: visible evaluated nonfloor triangles are clipped toZ0..3m and their projected polygons measured from the origin, improving on vertex-only/shaft-only sampling. Hidden ruler/plan and floor exclusions are explicit. This is static mesh occupancy, not swept capsules, camera collision or chain simulation. Flagged floor sampling: the R14 slab perimeter vertices fall outside the<=R12.8 filter, so inlay samples alone cannot demonstrate slab-top flatness; an explicit plane check is needed. Artist notified.

The current witnesses are passive pale-blue architectural lamps and fighters are simple rulers. No actual three-skull effect/chain-hand/costume readability pass follows from these images. Near-boundary camera is one chosen static position, not worst-case spring-arm retraction testing.

## Final candidate03 — ready for human layout review, not runtime acceptance

Independently viewed all five actual final images: hero-entry, gameplay-height, near-boundary-inward, side-architecture and annotated-plan. Four are1280×800, plan1280×1280. The uninterrupted floor, visible continuous2.6m boundary, clear column-backed arcade and sealed ribbed dome communicate a coherent enclosed duel chamber. The plan shows scenic architecture outside the original footprint, with entry−X and apse+X. Final throne offset exposes the seat beside the central preserved pillar; the pillar still dominates the central axis. Near-boundary inward image shows the reverse portal and clear floor without an unexpected interior obstruction. Pale simplified materials, repeated bays and plain reliefs remain studio-draft craft, not finished realism.

Read final geometry.json and saved-scene-audit.json. Full plinth centre/radius recomputation yields16.3877188m inward radius, not the old shaft-only number. Spawn planar separation is7.5m. The evaluated triangle audit reports nearest nonfloor projected occupancy13.0578459m, the existing-envelope memorial pier base, outside the proposed12.8m disk. Its scope clips visible nonfloor triangles toZ0..3m, with explicit annotation/ruler/floor exclusions; it does not certify all heights, character sweeps or Unreal collision.133,314 visible evaluated triangles describe this saved studio scene, not runtime draw cost.

The earlier slab sampling weakness is corrected:81 vertical BVH rays across centre and five rings yield all hits atZ0..5.96046448e−8m. Inlay vertices are separately reported at.001m. This supports a flat sampled slab with thickness-free visual inlays; no collision change or continuous-surface proof is inferred. Final audit restores the saved opening camera only and records an unchanged geometry digest; its final scene hash supersedes the earlier render readback hash, not the geometry or images.

[Independent integrity check](arena-design-01-qa-check.json):43/43 protected game/config/Revamp files unchanged;16/16 delivery entries match hashes; all five PNG dimensions verified. Final source010e38ffbb3c061027d2af1f2dbc90d7f8ada7cf0d60ed5ec34c27204b56fc34; scene8aebd21390fd89399f0a86624f2dce7d663c2f3161fa85d1f3780e2d86b98b54. Free space29,950,246,912bytes at QA check. No heavy jobs or Unreal tests run by QA.

Remaining acceptance gates: real costume/chain-hand/skull-effect silhouette and value tests; actual near-wall/tangential spring-arm and lock-on framing; unchanged collider/swept-roll and future hook obstruction behavior; same-build performance comparison after any separately authorized integration. The ruler proxies and passive blue fixtures do not demonstrate these. No AI changes or FPS/readability guarantee. Human approval concerns this layout draft only.
