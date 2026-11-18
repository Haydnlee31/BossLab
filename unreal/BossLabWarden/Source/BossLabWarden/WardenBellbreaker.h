#pragma once
#include "CoreMinimal.h"
#include "WardenCombat.h"

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
    enum EMove : int32 { HammerFall=20, Sweep, Quake, BellBreaks, End };
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
    inline constexpr float BellReach=230;   // grip to bell along the haft, cm (the visible hammer matches)

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
    inline float WaveRadius(int32 TicksSinceStart) { return RingStart+TicksSinceStart*RingSpeed*WardenRules::Step; }
}

struct FBellbreakerWave
{
    FVector Center=FVector::ZeroVector;
    int32 Start=0;
    bool PlayerResolved=false;   // stunned, blasted or cleanly avoided: one outcome per crest
    bool Live(int32 Tick) const { return Tick>=Start && WardenBellbreaker::WaveRadius(Tick-Start)<=WardenBellbreaker::RingEnd; }
};
enum class EBellbreakerOutcome : uint8 { None, Jumped, Rolled, Stunned, Blasted, OutOfReach };
struct FWardenBellbreakerState
{
    bool PhaseTwo=false;
    int32 Step=0, Waiting=90, Seeking=0;
    TArray<FBellbreakerWave> Waves;
    // Test/HUD evidence: how the latest crest met the player.
    EBellbreakerOutcome LastOutcome=EBellbreakerOutcome::None;
    int32 Stuns=0, Avoided=0;
};

// Presentation-only view state for the rigged Bellbreaker (WardenBellbreaker.cpp, AnimateBellbreakerView).
struct FWardenBellbreakerView
{
    TWeakObjectPtr<class UPoseableMeshComponent> Body;           // the corrected pose that is rendered
    TWeakObjectPtr<class UInstancedStaticMeshComponent> Sparks;  // bell-on-stone sparks
    TArray<FTransform> Frozen;                                   // last shown pose, for clip crossfades
    TArray<FTransform> Stance;                                   // idle frame 0: the planted stance strikes are layered over
    TWeakObjectPtr<class UAnimSequence> LastClip;
    float BlendFrom=-100, Lift=0, LastTime=-1, ScrapeReady=0, LastSpeed=0;
    FVector LastBell=FVector::ZeroVector;
    bool bContact=false;
    int32 ScrapeVariant=0;
    struct FSpark { float Start=-100; FVector At=FVector::ZeroVector, Velocity=FVector::ZeroVector; };
    static constexpr int32 MaxSparks=128;
    FSpark Buffer[MaxSparks];
    int32 Next=0;
    // Evidence for the study capture: worst intrusions seen after the corrections (world cm).
    float WorstFloor=0, WorstBody=0, WorstLeftGap=0;   // + left palm to its haft point (world cm)
    float SignR=-1, SignL=-1;   // grip orientation along the haft (hysteresis)
    float LeftGrip=1;           // 1 = left hand on the haft, 0 = relaxed hang (eased)
    float PalmSign=1;           // right-hand palm side (left = mirror, negated)
    float Shift=0;              // right hand moved toward the left to share the haft (component cm, eased)
};
