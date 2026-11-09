#pragma once
#include "CoreMinimal.h"

// Engine-owned values. Controllers may request actions, never edit these rules.
enum class EWardenAction : uint8 { Ready, Strike, Dodge, Heal, Dead, Hurt, Jump };
struct FWardenStrike
{
    const TCHAR* Name;
    const TCHAR* Animation;
    const TCHAR* Bone;
    int32 Windup, Active, Recovery;
    float AnimationContactStart, AnimationContactEnd, AnimationEnd;
    float Damage, Radius, Advance;
    float Cost = -1;     // stamina; -1 uses WardenRules::StrikeCost
    int32 Stance = 1;    // boss poise removed per hit
    int32 Total() const { return Windup + Active + Recovery; }
};

namespace WardenRules
{
    inline constexpr double Step = 1.0 / 60.0;
    // Souls-style player calibration (owner request 2026-11-09; docs/SOULS_CONTROLS.md):
    // roll protected for 26 of 40 ticks (~0.43 s, Elden Ring's 13-14 frames at 30 fps),
    // roll ~14% of the bar, 45 stamina/s regeneration after 0.5 s, sprint 1.5x run.
    inline constexpr int32 DodgeTicks = 40, DodgeInvulnerableStart = 2, DodgeInvulnerableEnd = 28;
    inline constexpr int32 RollAttackOpen = 28, RollChainOpen = 32;
    // Jump: snappy 40-tick arc; the jump attack hangs 4 ticks with the blade raised, then
    // plunges (gravity ease-in) to land exactly at contact, keeping the jump's momentum.
    inline constexpr int32 JumpTicks = 46, JumpAttackOpen = 4, JumpAttackClose = 32, JumpAttackHang = 4;
    inline constexpr float JumpHeight = 125, JumpCost = 12, AirControl = .25f;
    // Movement during actions (Elden Ring style): walk while drinking, carry run momentum
    // into a swing and brake it, steer a swing during its wind-up, and walk straight out
    // of late recovery (attack from contact + 14, jump attack + 28, roll from age 34).
    inline constexpr float HealWalkSpeed = 190, EntryBrake = 4200, SteerDegreesPerSecond = 540;
    inline constexpr int32 MoveCancelAfterContact = 14, JumpAttackMoveCancel = 28, RollMoveCancel = 34;
    inline constexpr int32 HealTicks = 78, HealCommit = 60, RecoveryGap = 8;
    // A broken boss stance staggers it long enough to punish (Elden Ring stance break), and
    // blows landed on a staggered boss deal critical damage.
    inline constexpr int32 InputBufferTicks = 18, HurtTicks = 18, BossHurtTicks = 84;
    inline constexpr float StaggerCritical = 2.5f;
    inline constexpr int32 RegenDelayTicks = 30, BossRegenDelayTicks = 42, BossPoise = 4;
    // The flask costs no stamina (as in Elden Ring); only the drinking time commits you.
    inline constexpr float StrikeCost = 22, DodgeCost = 14, HealCost = 0;
    inline constexpr float StaminaRegen = 45, BossStaminaRegen = 26;
    // Rehearsal moves 0-2 plus the opt-in Funeral Regent moves 3-15 (WardenRegent.h).
    inline constexpr int32 BossMoveCount = 16;
    enum EPlayerMove : int32 { CutOne, CutTwo, CutThree, JumpAttack, RollAttack, RunAttack, PlayerMoveCount };
    inline constexpr float WalkSpeed=420, SprintSpeed=630, SprintCostPerSecond=12, SprintStartStamina=10;
    const FWardenStrike& Strike(int32 Index, bool Boss = true);
    float DodgeDistance(float Age);
    float JumpLift(float Age);
    // Player light chain: the next cut may start (buffered input carries into it).
    bool ChainOpen(int32 Move, int32 Age);
    // Player may roll out of an attack's late recovery.
    bool RecoveryCancelOpen(int32 Move, int32 Age);
}

struct FWardenFighterState
{
    EWardenAction Action = EWardenAction::Ready;
    int32 Age = 0, Move = 0, Gap = 0, RegenDelay = 0, Heals = 3, AttackInstance = 0;
    float Health = 100, MaxHealth = 100, Stamina = 100;
    bool HitConsumed = false;
    bool Sprinting=false, SprintExhausted=false;
    void UpdateSprint(bool Requested, bool Moving);
    bool IsBoss = false;
    int32 Cooldowns[WardenRules::BossMoveCount] = {};
    int32 Poise = WardenRules::BossPoise, MaxPoise = WardenRules::BossPoise, PoiseReset = 0, ImpactTicks = 0;
    const FWardenStrike& Definition() const { return WardenRules::Strike(Move,IsBoss); }
    bool CanStrike(int32 Index) const { return Ready() && Affordable(Index); }
    // Strike legality without the ready requirement (cancels check their own windows).
    bool Affordable(int32 Index) const;
    float StrikeCostOf(int32 Index) const;
    // The player's attack for the current context: jump attack, rolling thrust, next cut
    // in the chain, running cut while sprinting, else the first cut.
    int32 NextPlayerMove() const;
    bool CancelOpen(EWardenAction Requested, int32 MoveIndex) const;
    // Player only: movement input may end this action's late recovery and walk on.
    bool MoveCancelOpen() const;
    bool CancelIntoMove();
    bool Alive() const { return Health > 0 && Action != EWardenAction::Dead; }
    bool Ready() const { return Alive() && Action == EWardenAction::Ready && Gap == 0; }
    bool Invulnerable() const;
    bool Active() const;
    bool Request(EWardenAction Requested, int32 MoveIndex = 0);
    // Called after geometry/damage. Lethal damage therefore cancels a same-tick heal.
    void Advance();
    // Flinch=false is lingering chip damage (Regent fire pools): no hurt state or poise.
    bool Damage(float Amount, bool Flinch = true, int32 Stance = 1);
    float AnimationTime() const;
};
