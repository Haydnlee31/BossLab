# Undead Warden: animation and asset proposal

Planning only,2026-11-08. Nothing here is implemented. User direction: an undead Warden, floating blue-flame skulls, and a cast chain that hooks the player, pulls them in, then leads into a stab. Boss AI remains deferred; first implementation should be an explicitly fixed rehearsal. Engine-owned phases, hit tests and movement remain authoritative; animation illustrates them.

## Three feasible silhouettes

| Direction | Large readable forms | Animation/asset cost |
|---|---|---|
| **Gallows Warden — recommended** | Tall, lean corpse; sunken rib plate; one exposed long chain arm; opposite hand holds a narrow execution blade; three skulls form an uneven arc behind shoulders. Torn hip panels leave legs visible. | Existing humanoid proportions can support a dedicated skinned body. Limited cloth avoids repeating the stiff full-cape problem. Asymmetric arms clearly identify cast versus stab. |
| Reliquary Gaoler | Broad bowed shoulders around a hollow chest cage; small recessed dead face; skulls hover above the open cage. Heavy staggered steps and short explosive lunges. | More armor overlap/shoulder clearance work. Keep the body under armor narrow enough for an actual cross-body cast; avoid a rigid barrel torso. |
| Funeral Bailiff | Stooped corpse with a long spinal silhouette, split burial stole, low dangling hook hand; two skulls hover at unequal heights. Head slowly lifts before attacks. | Strong mood with few surfaces, but robe deformation and ground clearance are harder. Use knee-length split panels, not a floor-length rigid cone. |

The first option best separates the actions at gameplay distance without requiring elaborate cloth. Original art direction, not a copy of an existing boss. Lock front/side silhouettes and one attack pose before surface detail.

## Rig and mesh approach

Build one continuous weighted torso/pelvis/limb base around an explicit humanoid rest pose. Retargeting can provide locomotion starting poses, but the chain and stab need authored whole-body clips. Do not make the final boss from independent static glove, skirt and chest chunks attached to bones as in the V13 trial: that trial demonstrated transfer, not acceptable deformation.

- Rigid plates receive rigid or tightly localized skin weights; cloth and exposed tissue receive deliberate shoulder/hip/elbow deformation loops. Test a deep cast, torso twist, crouch and recovery before decoration.
- Shoulder motion begins in clavicle/scapula and spine. Hand/weapon IK maintains actual grip; it does not drag an otherwise stationary torso through an attack.
- A separate chain path drives repeated link geometry visually. Do not simulate every link as an authoritative rigid body. Keep a visible launch point, hook tip and player attachment socket; the engine provides the endpoints/contact event.
- Skulls are separate small meshes on controlled orbit transforms with independent slow tilt. Flame is bounded cosmetic VFX. Start with three skulls and one modest shared blue illumination contribution, rather than a light per flame or dense translucent smoke.
- Start with short weighted cloth panels. Add cosmetic secondary motion only after static poses are clear. No long cape or new cloth simulation is necessary for this identity.

## Chain → pull → stab pose sequence

These are pose beats, not approved frame timings. Combat design must specify the durations and dodge windows before implementation; never lengthen engine windows to accommodate a clip silently.

1. **Recognizable preparation:** plant rear foot, lower pelvis, rotate chest away; chain hand draws beside the ribs with elbow back. Blade hand stays distinct near the opposite hip. Skulls widen their spacing and flame briefly tightens; the arm/chain silhouette remains the primary tell.
2. **Cast:** front foot braces, pelvis rotates, chest follows, then shoulder/elbow release the hook. A brief straightened arm silhouette shows the cast direction. Tracking ends at the approved commitment point; the chain must not visually bend around an already dodging player.
3. **Miss branch:** hook passes or hits the arena; chain loses tension, boss reels it back with a visible open stance. Include a real recovery pose instead of snapping directly to idle.
4. **Confirmed hook:** only the authoritative contact event attaches the hook. The line straightens; the boss visibly takes the load through bent knees and a backward hip shift. No preemptive player grab from the animation alone.
5. **Pull:** chain hand draws to the waist while the boss steps back/braces; blade elbow retracts into a clear thrust preparation. Player movement is engine-controlled along a validated path; use a drag/stumble response instead of teleporting or playing a running cycle in place.
6. **Stab:** a distinct braced thrust silhouette and brief readable release/arrival beat precede contact. Recommend an authored escape opportunity at this transition rather than an unexplained guaranteed second hit; combat designer decides the actual rule. Both success and escape need separate recovery poses, without camera-forced choreography.
7. **Recover:** blade withdraws, chain slackens, body uncoils through hips/spine, then feet settle. Preserve momentum into the next idle rather than stopping every limb simultaneously.

## Readability and failure gates

Review at the actual arena camera first: can cast, miss, tension, pull and stab be distinguished with gray materials and effects disabled? Then add skulls/flames without hiding hands, hook, player or floor tells. Blue flame must not be the only signal; preserve silhouette and sound cues for color-independent readability.

Before art acceptance, inspect slow and normal-speed clips from front/side/gameplay angles: no sliding planted feet, detached shoulders, grip drift, chain passing through the casting wrist, rigid skirt crossing thighs, or motion whose only moving element is the weapon. Include interruption/death during every chain state, wall contact, close-range cast, maximum range, player dodge and escaped stab. On interruption the cosmetic chain clears coherently and never keeps pulling after the engine cancels the action.

Risks requiring engine/design agreement: blocked pull paths, camera collision, arrival inside the boss, a hook appearing attached despite invulnerability, and unfair tracking during the stab. Address these before decorative flame or surface polish. Tests and observed captures must distinguish contact correctness from artistic quality; no production rig, physics, AI or animation result is claimed by this plan.
