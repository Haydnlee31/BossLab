#pragma once
#include "CoreMinimal.h"
#include "WardenCombat.h"
#include "BellbreakerSoles.h"

class AActor; class USkeletalMeshComponent; class UStaticMeshComponent;
// The bell hammer in a rig's right fist, grip solved from the reference pose (WardenSmeltery.cpp).
UStaticMeshComponent* WardenAttachBellHammer(AActor* Owner,USkeletalMeshComponent* C,float WorldScale);
// Presentation actors: no collision by every switch, and every fighter's capsule ignores them when moving.
void WardenNeverCollide(AActor* A);

// Opt-in Bellbreaker greybox (-BossLabBellbreaker, docs/BELLBREAKER_GREYBOX.md), 2026-11-18. Engine-owned
// like the rehearsal and Regent moves: boss indices 20.. of WardenRules::Strike. The default encounter,
// policies and tests never select them. Fixed labelled sequence, no AI. The giant's body is a presentation
// actor (the rigged TRELLIS model playing retargeted HY clips) that follows the hidden combat capsule; the
// hammer's hit path below is analytic and engine-owned, never read from the clip.
namespace WardenBellbreaker
{
    enum EMove : int32 { HammerFall=20, Sweep, Quake, BellBreaks,
        // Readiness pass 2026-11-23 (docs/BELLBREAKER_READY_2026-11-23.md): ten more engine-owned rows, each
        // with its own repeat lock (cooldown). Cyclone and Knell open only in phase two.
        Backhand, Stamp, Charge, Uppercut, Toll, Fling, HeldNote, Cyclone, Knell, StridingFall, End };
    inline constexpr int32 First=HammerFall, Count=End-HammerFall;
    inline bool IsBellbreaker(int32 Move) { return Move>=First && Move<End; }
    inline constexpr float Health=900, PhaseTwoHealth=450, Scale=2.55f, StandZ=95*Scale;   // same convention as the Regent (capsule 34 x 90, player at 95)
    inline constexpr int32 Poise=8;
    inline constexpr float CapsuleRadius=40;   // unscaled; x Scale = 102 cm (v3 model is slimmer than v2's 48)
    // Bell Quake: the bell lands ImpactAhead in front of him. Within BlastRadius at impact: BlastDamage
    // and a kneeling knockdown. Then a crest runs along the floor from RingStart to RingEnd at RingSpeed;
    // a player it passes is stunned unless airborne above AirborneLift or inside roll i-frames.
    inline constexpr float BlastRadius=240, BlastDamage=30, WaveDamage=10;
    inline constexpr float RingStart=120, RingEnd=1000, RingSpeed=850, CrestHalfWidth=30, AirborneLift=30;
    // Owner 2026-11-18: a stun lasts 1-2 s at most, then the player moves (walk-out: WardenRules::StunWalkOut).
    inline constexpr int32 WaveStun=60, BlastStun=72;
    // Twin Quake gap: long enough that every pair of answers recovers in time (roll-roll via the roll
    // chain, jump-jump, jump-roll, roll-jump); at 30 ticks no second answer could come out in time.
    inline constexpr int32 TwinDelay=45;
    // Anvil Stamp: a boot blast around his front foot (anti-hugging); roll, jump or step out.
    inline constexpr float StampRadius=300, StampDamage=22, StampAhead=110;
    // The Toll: a sound ring at body height. Only a roll's i-frames pass it (jumping does not help).
    inline constexpr float TollStart=140, TollEnd=1100, TollSpeed=760, TollDamage=18;
    // Slag Fling: three molten blobs land on the floor marks LandDelay ticks after release.
    inline constexpr float SlagRadius=125, SlagDamage=20; inline constexpr int32 SlagFlight=42, SlagCount=3;
    // Death Knell: three slams on the same mark, the last sends a crest. Gap between slams in ticks.
    inline constexpr int32 KnellGap=30; inline constexpr float KnellRadius=210, KnellDamage=20;
    // Forge Cyclone: one full turn during the active window (presentation spins the body by the same angle).
    float CycloneSpin(int32 Move,float Age);
    inline constexpr float BellReach=282;   // grip to bell along the haft, cm (the visible hammer matches)

    const FWardenStrike& Strike(int32 Index);
    // Bell (hammer head) relative to the floor point under the actor, yaw frame (X forward, Y right), cm.
    FVector BellOffset(int32 Move,int32 Age,bool Striking);
    FVector BellOffsetAt(int32 Move,float Age,bool Striking);   // same path at a fractional age (presentation)
    // Grip end of the haft in the same frame: BellReach back toward the swing pivot.
    FVector GripOffset(int32 Move,int32 Age,bool Striking);
    // Where the Quake's bell lands (impact and shockwave centre), same frame, on the floor.
    FVector QuakeImpactOffset();
    // Rehearsal distance band and pause after each move (punish windows after the slams).
    FVector2D Band(int32 Move);
    int32 Pause(int32 Move);
    int32 RepeatLock(int32 Move);
    inline float WaveRadius(int32 TicksSinceStart) { return RingStart+TicksSinceStart*RingSpeed*WardenRules::Step; }
    // Swept annulus for one fixed tick. Keep both combat and the bright floor band in world cm.
    inline FVector2D WaveBand(int32 Age)
    {
        return FVector2D(WaveRadius(FMath::Max(0,Age-1))-CrestHalfWidth,WaveRadius(Age)+CrestHalfWidth);
    }

}

struct FBellbreakerWave
{
    FVector Center=FVector::ZeroVector;
    int32 Start=0;
    bool PlayerResolved=false;   // stunned, blasted or cleanly avoided: one outcome per crest
    bool bToll=false;            // The Toll: a sound ring, only rolled (not jumped), no stun
    float Radius(int32 Tick) const { return bToll ? WardenBellbreaker::TollStart+(Tick-Start)*WardenBellbreaker::TollSpeed*WardenRules::Step : WardenBellbreaker::WaveRadius(Tick-Start); }
    FVector2D Band(int32 Tick) const
    {
        if(!bToll) return WardenBellbreaker::WaveBand(Tick-Start);
        const float Step=WardenBellbreaker::TollSpeed*WardenRules::Step;
        return FVector2D(Radius(Tick)-Step-WardenBellbreaker::CrestHalfWidth,Radius(Tick)+WardenBellbreaker::CrestHalfWidth);
    }
    bool Live(int32 Tick) const { return Tick>=Start && Radius(Tick)<=(bToll ? WardenBellbreaker::TollEnd : WardenBellbreaker::RingEnd); }
};
struct FBellbreakerSlag { FVector From=FVector::ZeroVector, At=FVector::ZeroVector; int32 Launch=0, Land=0; };
enum class EBellbreakerOutcome : uint8 { None, Jumped, Rolled, Stunned, Blasted, OutOfReach };
struct FWardenBellbreakerState
{
    bool PhaseTwo=false;
    float GroundAge=1.f, GroundAmplitude=0.f; // render-only camera envelope, seconds
    int32 Step=0, Waiting=90, Seeking=0;
    TArray<FBellbreakerWave> Waves;
    TArray<FBellbreakerSlag> Slag;
    // Test/HUD evidence: how the latest crest met the player.
    EBellbreakerOutcome LastOutcome=EBellbreakerOutcome::None;
    int32 Stuns=0, Avoided=0;
};

// Presentation-only view state for the rigged Bellbreaker (WardenBellbreaker.cpp, AnimateBellbreakerView).
struct FWardenBellbreakerView
{
    TWeakObjectPtr<class UPoseableMeshComponent> Body;           // the corrected pose that is rendered
    TWeakObjectPtr<class UInstancedStaticMeshComponent> Sparks;  // bell-on-stone sparks
    TArray<FTransform> LastSourcePose, Frozen;                   // blended source and transition origin before procedural corrections
    FBellbreakerSoles Soles;
    TArray<FTransform> Stance;                                   // idle frame 0: the planted stance strikes are layered over
    TWeakObjectPtr<class UAnimSequence> LastClip;
    float BlendFrom=-100, SourceBlendSeconds=.20f, Lift=0, LastTime=-1, ScrapeReady=0, LastSpeed=0;
    struct FWalkFoot { FVector Anchor=FVector::ZeroVector, SwingFrom=FVector::ZeroVector, Correction=FVector::ZeroVector; FQuat GroundRotation=FQuat::Identity; bool Planted=false; };
    FWalkFoot WalkFeet[2];
    TWeakObjectPtr<class UStaticMeshComponent> SoleShades[2];
    FVector PreviousFloor=FVector::ZeroVector, WalkCarryDelta=FVector::ZeroVector;
    float WalkCarryPitch=0;
    float WalkPhase=0, WalkEntryTime=-100, WalkYaw=0, WalkTurnRate=0, WalkSpeed=0;
    bool HasPreviousFloor=false, WasGroundGait=false;
    FVector LastBell=FVector::ZeroVector;
    FVector ClearPush=FVector::ZeroVector;   // body-clearance offset of the whole hammer (facing frame, cm)
    bool bContact=false;
    int32 ScrapeVariant=0;
    struct FSpark { float Start=-100; FVector At=FVector::ZeroVector, Velocity=FVector::ZeroVector; };
    static constexpr int32 MaxSparks=128;
    FSpark Buffer[MaxSparks];
    int32 Next=0;
    // Effects pass (2026-11-23): glowing floor cracks, dust, fire bursts/embers and cooling slag puddles on
    // instanced planes with a per-instance fade (FLUX textures, /Game/BossLab/Bellbreaker/FX). Presentation only.
    enum EFx : uint8 { FxCrack, FxDust, FxFire, FxPuddle, FxKinds };
    struct FFx { float Start=-100, Life=1, Size0=50, Size1=100, Rise=0, Spin=0; FVector At=FVector::ZeroVector, Velocity=FVector::ZeroVector; };
    TArray<FFx> Fx[FxKinds];
    int32 FxNext[FxKinds]={0,0,0,0};
    TWeakObjectPtr<class UInstancedStaticMeshComponent> FxLayer[FxKinds];
    float FxClock=0, EmberDue=0, TrailDue=0;
    int32 FxTick=-1;
    // Evidence for the study capture: worst intrusions seen after the corrections (world cm).
    float WorstFloor=0, WorstBody=0, WorstLeftGap=0;   // + left palm to its haft point (world cm)
    struct FArmGrip
    {
        bool bValid=false;
        double ElbowSwivel=0, Pronation=0;
        FVector PreviousPalmNormal=FVector::ZeroVector;
    };
    FArmGrip ArmGrip[2];
    // Anatomy governor evidence (study logs): worst input before the limits, worst chest twist after.
    struct FGovernor { float WorstPelvisIn=0, WorstTwistIn=0, WorstTwistOut=0, WorstHeadYawIn=0, WorstHeadPitchIn=0, WorstHeadPitchOut=0, WorstSquatIn=0; };
    FGovernor GovernorStats;
    float PalmSign=1;           // right-hand palm side (left = mirror, negated)
    bool bHammerWasStriking=false;
    float WeaponReleaseTime=-100;
    FVector PreviousShaft=FVector::ForwardVector, PreviousGrip=FVector::ZeroVector;
    FVector ReturnFromShaft=FVector::ForwardVector, ReturnFromGrip=FVector::ZeroVector;
};
