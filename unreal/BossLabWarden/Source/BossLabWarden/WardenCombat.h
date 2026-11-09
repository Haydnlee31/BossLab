#pragma once
#include "CoreMinimal.h"

// Engine-owned values. Controllers may request actions, never edit these rules.
enum class EWardenAction : uint8 { Ready, Strike, Dodge, Heal, Dead, Hurt };
struct FWardenStrike
{
    const TCHAR* Name;
    const TCHAR* Animation;
    const TCHAR* Bone;
    int32 Windup, Active, Recovery;
    float AnimationContactStart, AnimationContactEnd, AnimationEnd;
    float Damage, Radius, Advance;
    int32 Total() const { return Windup + Active + Recovery; }
};

namespace WardenRules
{
    inline constexpr double Step = 1.0 / 60.0;
    inline constexpr int32 DodgeTicks = 36, DodgeInvulnerableStart = 4, DodgeInvulnerableEnd = 18;
    inline constexpr int32 HealTicks = 78, HealCommit = 60, RecoveryGap = 8;
    inline constexpr int32 InputBufferTicks = 12, HurtTicks = 18, BossHurtTicks = 36;
    inline constexpr float StrikeCost = 22, DodgeCost = 28, HealCost = 12;
    // Rehearsal moves 0-2 plus the opt-in Funeral Regent moves 3-14 (WardenRegent.h).
    inline constexpr int32 BossMoveCount = 15;
    inline constexpr float WalkSpeed=360, SprintSpeed=540, SprintCostPerSecond=12, SprintStartStamina=10;
    const FWardenStrike& Strike(int32 Index, bool Boss = true);
    float DodgeDistance(float Age);
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
    int32 Poise = 3, PoiseReset = 0, ImpactTicks = 0;
    const FWardenStrike& Definition() const { return WardenRules::Strike(Move,IsBoss); }
    bool CanStrike(int32 Index) const { return Index >= 0 && Index < WardenRules::BossMoveCount && (IsBoss || Index == 0) && Ready() && Stamina >= WardenRules::StrikeCost && Cooldowns[Index] == 0; }
    bool Alive() const { return Health > 0 && Action != EWardenAction::Dead; }
    bool Ready() const { return Alive() && Action == EWardenAction::Ready && Gap == 0; }
    bool Invulnerable() const;
    bool Active() const;
    bool Request(EWardenAction Requested, int32 MoveIndex = 0);
    // Called after geometry/damage. Lethal damage therefore cancels a same-tick heal.
    void Advance();
    // Flinch=false is lingering chip damage (Regent fire pools): no hurt state or poise.
    bool Damage(float Amount, bool Flinch = true);
    float AnimationTime() const;
};
