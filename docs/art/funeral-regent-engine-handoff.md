# Funeral Regent — engine constraints for construction

2026-11-08. Read-only builder review, recorded by orchestrator. No new implementation or verification run.

- Existing boss Manny skeleton and actor scale 1.35 are the reference. Base capsule radius34/half-height90 gives scaled45.9/121.5cm. Do not resize collision, weapon reach or lock-on for a concept crown.
- Align foot, head/neck, clavicle, shoulder, elbow and wrist landmarks in all construction views. Crown and mask need gorget clearance at chin tuck, full cast and overhead poses.
- Long mantle is required by selected B: weighted separated panels, front stride opening and independent left-arm passage. The V13 player's rigid cape is not a final rig solution.
- Reel/bracer anchor is `lowerarm_l`; glove is articulated at `hand_l`. Choose a bracer-fixed guide that clears the wrist and palm; one rigid housing must not bridge the wrist joint. Chain travels outside cloth, chest and neck.
- Existing sword poses assume two hands. Cast must explicitly release the left hand and retain sword in right, then use a deliberately authored one-handed thrust or a distinct regrip branch. No instantaneous hand snapping between poses.
- Skull silhouettes stay behind/outside crown and shoulders. They cannot hide hook contact, player dodge lanes or feet.
- Dedicated hook/capture/release state remains necessary. Visual chain is not a physical rope authority. No AI, model integration or engine changes in this sheet stage.

These constraints must be checked against actual clay poses and runtime animation later; a concept drawing cannot prove clearances or performance.
