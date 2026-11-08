# Character animation research and BossLab diagnosis — 2026-11-06

The owner reports smoother gameplay but awkward boss sword motion and requests research before another refinement. This is a research/diagnosis pass; boss swing curves and final models are not changed. The separate controls implementation adds sprint and an accessible pause/quit menu.

## What the pipeline actually does

A character model is geometry; a skeleton is a hierarchy of joints; skinning maps mesh vertices to those joints. Animation supplies joint transforms over time. Game logic decides which pose/sequence to evaluate. A nicer model does not repair incorrect body mechanics. Unreal treats mesh, skeleton, animation sequences and runtime animation logic as distinct assets/systems. [Epic skeletal mesh overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/skeletal-mesh-assets-in-unreal-engine).

Skin weights influence how vertices deform around joints. Blender documents weights per vertex group and armature-based deformation. Skinning defects can look like collapsing shoulders, but poor joint timing is a separate cause. Search-accessible official Blender documentation supported this distinction; direct full-page retrieval was blocked, so no full Blender manual/course completion is claimed. [Blender vertex groups](https://docs.staging.blender.org/manual/en/latest/modeling/meshes/properties/vertex_groups/introduction.html).

FK rotates a joint hierarchy; IK solves a chain toward a goal. An IK hand constraint solves contact, not believable force or weight. Epic's IK tools can coordinate feet and hips, while Control Rig provides editable controls and Sequencer authoring directly inside Unreal. [IK Rig](https://dev.epicgames.com/documentation/en-us/unreal-engine/ik-rig-in-unreal-engine), [Control Rig](https://dev.epicgames.com/documentation/en-us/unreal-engine/control-rig-in-unreal-engine).

Weight reads through the order of movement: support and anticipation, body drive, arm/weapon follow, deceleration and recovery. Key poses alone leave the transitions unspecified; breakdown poses explain the causal motion between them. This calls for reference analysis and deliberate hip/chest/shoulder sequencing before curve polish. [Wayne Gilbert / Animation Mentor body mechanics](https://www.animationmentor.com/blog/animation-tips-tricks-what-makes-or-breaks-a-good-body-mechanics-shot/).

Montages organize animation sequences, sections and slots for runtime playback; they do not create good source motion automatically. Root-motion extraction can move the collision character with authored motion. Applying animated displacement and independent capsule displacement together risks mismatch; BossLab must keep one authoritative displacement path and revalidate actual blade contact. [Epic montages](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-montage-in-unreal-engine), [Epic root motion](https://dev.epicgames.com/documentation/en-us/unreal-engine/root-motion-in-unreal-engine).

## Online skills reviewed

Searched for character-animation/game-development agent skills as well as primary training material. Read the public [game-development SKILL.md](https://github.com/dylantarre/animation-principles/blob/main/skills/01-by-domain/game-development/SKILL.md). It gives a general principles checklist, but its generic timing tables, squash, hit-stop and blanket easing suggestions are not a character-rigging workflow or suitable rules to import into this project. In particular, its advice to adjust frame data to rendering frame rate conflicts with our fixed simulation authority. Reviewed as reference, not installed or adopted as project instructions.

Also found [unreal-engine-skills](https://github.com/kevinpbuckley/unreal-engine-skills); the repository was readable but the advertised animation-system file could not be fetched at the tested path. No claim of having read or installed that skill. Available local animation skills mainly concern web/UI motion; they are not substitutes for skeletal character animation. No skill/plugin/model downloads or global configuration changes were made.

## Diagnosis grounded in current source

These are source-backed limitations and hypotheses to test against individual awkward moments, not proof that every bad-looking frame has the same cause:

- `WardenSword.cpp` defines a small set of hilt/direction poses, interpolates them, then solves both arms to the shared hilt. Hand reach and grip can pass numerical checks while shoulders, elbows and wrist roll remain unnatural.
- The weapon orientation is built from its axis using `FindBetweenNormals`; an axis alone does not specify a complete authored wrist/blade-roll trajectory. Hand orientation and pole targets are derived heuristically. Near extension, small target changes can noticeably change the elbow silhouette.
- The body is composed from a guard/base blend plus procedural twist/lean and leg targets. This is not a separately authored full-body boss attack sequence. Three attack families share much of that construction.
- Support-foot anchoring fixes sliding, but cannot by itself supply convincing balance, pivot, chest lag or recovery. Rigid attached shoulder/cape geometry makes these deficiencies more conspicuous.
- Existing tests prove contact windows, grip reach, continuity and selected grounding properties. They do not prove realistic mechanics, appealing silhouette or artistic quality. The owner's swing feedback remains unresolved.

## Workflow for the next boss animation pass

1. Isolate one broad sweep on the current rig. Record front, side, rear three-quarter and gameplay-camera views with skeleton, weapon trail and support-foot markers. Keep the other families unchanged for comparison.
2. Use the owner's local reference to mark planted support, anticipation, pelvis initiation, chest/shoulder follow, blade release and recovery. Identify the force sequence; do not copy the boss design or infer hidden input/frame rules.
3. Block full-body poses in Control Rig/Sequencer (or an equivalent authored skeletal clip) before smoothing. Specify foot pivots, hip height, chest/shoulder motion, elbow direction and full weapon rotation. Retain the shared hilt constraint as a finishing constraint.
4. Add breakdowns and inspect arcs/spacing at real speed and slow motion. Check contact foot stability, joint extension, wrist/blade roll and self-intersection. Use IK for contact correction after the primary body motion is convincing.
5. Bake/evaluate the skeletal sequence at the engine-owned phase. Preserve current boss44/24/54,70/22/64,40/24/54 and player30/20/36 timing unless separately revised. Do not introduce a second source of root displacement or input-reading aim changes.
6. Re-run blade/wall/grip/iframe tests, retain failures and compare paired captures. Review motion before materials/capes/new character models. Measure FPS after integration; do not substitute fixed-rate capture for performance.

This establishes a concrete authoring direction. It does not claim animation mastery, a completed Control Rig migration, motion capture, new imported animations or resolved boss swing quality.
