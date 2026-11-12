#pragma once
#include "CoreMinimal.h"
#include "WardenCombat.h"

// Opt-in Funeral Regent moveset (-BossLabRegent, docs/REGENT_MOVESET.md). Engine-owned
// like the rehearsal moves: boss indices 3.. of WardenRules::Strike. The default
// encounter, policies and tests never select them.
namespace WardenRegent
{
    enum EMove : int32 { Thrust=3, Rite, Arc, Bell, Volley, Drift, Dash, Furrow, AshStep, Pyre, Wakes, HeldThrust, Circle, Raise, End };
    enum class EKind : uint8 { Blade, Censer, Cast, Move, Vanish, Ring, Transition };
    inline constexpr int32 First=Thrust, Count=End-Thrust;
    inline constexpr int32 Skulls=3, MaxPools=4, AshVanish=20, AshAppear=44;
    // Boss-scale health and stance (2026-11-10): a disciplined test bot beat the 240 hp
    // Regent in 26 s under the souls-style player rules; this aims at minutes, not seconds.
    inline constexpr float Health=600, PhaseTwoHealth=300, ArenaRadius=1180, FloorRadius=1400;
    inline constexpr int32 Poise=6;
    inline constexpr float SkullSpeed=720, SkullRadius=30, SkullDamage=16, SkullTurnDegrees=2, SkullLockDistance=350;
    inline constexpr float PoolDamage=5, BellPoolRadius=250, PyrePoolRadius=200, PyreSpread=340;
    inline constexpr int32 PoolInterval=30, PoolIgnite=18, BellPoolTicks=180, PyrePoolTicks=240;
    inline constexpr int32 FurrowMarks=8, FurrowSpacing=150, FurrowStagger=5, FurrowWarn=30, FurrowBurst=12;
    inline constexpr int32 SkullRegrow=480, SkullRegrowPhaseTwo=300, SkullLife=300;
    // Witness Circle (phase two): the skulls circle the player, then converge together.
    inline constexpr int32 CircleOrbitTicks=54;
    inline constexpr float CircleRadius=320, CircleDiveSpeed=860;
    // Raise the Dead: two slow skeletons climb out of rune circles beside the Regent. Any three
    // blows fell one; each blow staggers it. They crumble after SkeletonLife, and the Regent
    // does not raise more while any stand.
    inline constexpr int32 RaisedSkeletons=2, SkeletonHits=3;
    inline constexpr int32 SkeletonRise=54, SkeletonWindup=42, SkeletonActive=8, SkeletonRecover=50, SkeletonStagger=20, SkeletonFall=60, SkeletonLife=1800;
    inline constexpr float SkeletonSpeed=95, SkeletonTurnDegrees=3, SkeletonReach=150, SkeletonArcDegrees=60, SkeletonDamage=14, SkeletonBody=40, SkeletonSpacing=90;
    // Censer floor contact (0-1): the Arc's sweep dips and slows on the floor; the Bell drags
    // back along it after the slam. Engine-owned like the censer path itself.
    float CenserGround(int32 Move,int32 Age,bool Striking);

    const FWardenStrike& Strike(int32 Index);
    inline bool IsRegent(int32 Move) { return Move>=First && Move<End; }
    EKind Kind(int32 Move);
    // Melee contact windows. Rite has three; every other melee move uses [Windup, Windup+Active).
    bool Contact(int32 Move,int32 Age);
    // A new contact window opens at this age, so one action may land more than once.
    bool Rearm(int32 Move,int32 Age);
    bool Vanished(int32 Move,int32 Age);
    // Censer head relative to the actor origin in its yaw frame (X forward, Y right), cm.
    // Engine-owned: the censer hit samples use it, the visible censer follows it.
    FVector CenserOffset(int32 Move,int32 Age,bool Striking);
    // Shoulder the chain leaves from, same frame.
    inline FVector ChainAnchor() { return FVector(4,-30,52); }
    // Orbit slot of one floating skull above the Regent, same frame but world-yaw fixed.
    FVector SkullOrbit(int32 Slot,int32 Tick);
    // Rehearsal distance band for a move: the boss walks until it is inside, then commits.
    FVector2D Band(int32 Move);
    // Ticks the rehearsal waits after a move before choosing the next: long after the big
    // commitments (punish windows), none after the drift that sets up the dash.
    int32 Pause(int32 Move);
}

struct FRegentSkull
{
    FVector Position=FVector::ZeroVector, Velocity=FVector::ZeroVector;
    int32 Slot=0, Age=0;
    int32 Orbit=0;              // Witness Circle: ticks left circling the player
    float OrbitAngle=0;
    bool Homing=true, Passed=false;
};
enum class ERegentSkeletonState : uint8 { Rise, Walk, Windup, Strike, Recover, Stagger, Fall };
struct FRegentSkeleton
{
    FVector Position=FVector::ZeroVector;
    float Yaw=0;
    ERegentSkeletonState State=ERegentSkeletonState::Rise;
    int32 Age=0, Life=0, Hits=0, LastHitBy=-1, Id=0;
    bool Struck=false;
    bool Standing() const { return State!=ERegentSkeletonState::Fall; }
};
enum class ERegentHazard : uint8 { Pool, Eruption, Mark };
struct FRegentHazard
{
    ERegentHazard Kind=ERegentHazard::Pool;
    FVector Center=FVector::ZeroVector;
    float Radius=0, Damage=0;
    int32 Start=0, Arm=0, End=0, NextHit=0;
    bool Spent=false;
    bool Live(int32 Tick) const { return Tick>=Start && Tick<End && !Spent; }
    bool Armed(int32 Tick) const { return Live(Tick) && Tick>=Arm; }
};
struct FWardenRegentState
{
    bool PhaseTwo=false;
    int32 Step=0, Waiting=90, Seeking=0;
    int32 Regrow[WardenRegent::Skulls]={0,0,0};   // 0 = orbiting and ready
    TArray<FRegentSkull> Flying;
    TArray<FRegentHazard> Hazards;
    FVector FurrowOrigin=FVector::ZeroVector, FurrowDirection=FVector::ForwardVector;
    FVector AshTarget=FVector::ZeroVector;
    TArray<FRegentSkeleton> Skeletons;
    FVector RaiseAt[WardenRegent::RaisedSkeletons];
    int32 NextSkeletonId=0;
    bool CenserGrounded=false;
    int32 StandingSkeletons() const { int32 N=0; for(const auto& S:Skeletons) N+=S.Standing(); return N; }
    int32 ReadySkulls() const { int32 N=0; for(int32 R:Regrow) N+=R==0; return N; }
    float PoolArea(int32 Tick) const;
};
