#include "WardenCombat.h"

float WardenRules::DodgeDistance(float Age)
{
    // Integrated smooth velocity: six-tick push, twelve-tick carry, eighteen-tick
    // landing. Exactly 300 cm; no frame-rate dependence or abrupt speed changes.
    const float T=FMath::Clamp(Age,0.f,36.f);
    auto Integral=[](float U) { return U*U*U-.5f*U*U*U*U; };
    if(T<6) return 12.5f*6*Integral(T/6);
    if(T<18) return 12.5f*(3+T-6);
    const float U=(T-18)/18;
    return 12.5f*(15+18*(U-Integral(U)));
}

const FWardenStrike& WardenRules::Strike(int32 Index, bool Boss)
{
    static const FWardenStrike Player={TEXT("GREATSWORD CUT"),TEXT("AuthoredSword"),TEXT("hand_r"),30,20,36,0.f,0.f,1.f,32,6,45};
    if (!Boss) { check(Index == 0); return Player; }
    // Engine-owned rehearsal timings; authored sword poses use these same phases.
    static const FWardenStrike Moves[] = {
        {TEXT("BROAD SWEEP"), TEXT("AuthoredSword"), TEXT("hand_r"), 44,24,54, 0,0,1, 24,7,55},
        {TEXT("HELD OVERHEAD"), TEXT("AuthoredSword"), TEXT("hand_r"), 70,22,64, 0,0,1, 34,8,65},
        {TEXT("RISING CLEAVE"), TEXT("AuthoredSword"), TEXT("hand_r"), 40,24,54, 0,0,1, 28,7,70}
    };
    check(Index >= 0 && Index < UE_ARRAY_COUNT(Moves));
    return Moves[Index];
}

void FWardenFighterState::UpdateSprint(bool Requested, bool Moving)
{
    const bool WasSprinting=Sprinting;
    Sprinting=false;
    if(!Requested) SprintExhausted=false;
    if(!Requested || !Moving || !Ready() || SprintExhausted) return;
    if(!WasSprinting && Stamina<WardenRules::SprintStartStamina) return;
    const float Cost=WardenRules::SprintCostPerSecond*WardenRules::Step;
    if(Stamina+KINDA_SMALL_NUMBER<Cost) { SprintExhausted=true; return; }
    Stamina=FMath::Max(0.f,Stamina-Cost); RegenDelay=42; Sprinting=true;
    if(Stamina<=KINDA_SMALL_NUMBER) SprintExhausted=true;
}

bool FWardenFighterState::Invulnerable() const
{
    return Action == EWardenAction::Dodge && Age >= WardenRules::DodgeInvulnerableStart && Age < WardenRules::DodgeInvulnerableEnd;
}
bool FWardenFighterState::Active() const
{
    if (Action != EWardenAction::Strike || !Alive()) return false;
    const auto& Def = Definition();
    return Age >= Def.Windup && Age < Def.Windup + Def.Active;
}
bool FWardenFighterState::Request(EWardenAction Requested, int32 MoveIndex)
{
    if (!Ready()) return false;
    float Cost = 0;
    switch (Requested)
    {
        case EWardenAction::Strike:
            if (!CanStrike(MoveIndex)) return false;
            Cost = WardenRules::StrikeCost; break;
        case EWardenAction::Dodge: Cost = WardenRules::DodgeCost; break;
        case EWardenAction::Heal:
            if (Heals <= 0 || Health >= MaxHealth) return false;
            Cost = WardenRules::HealCost; break;
        default: return false;
    }
    if (Stamina < Cost) return false;
    Sprinting=false;
    Stamina -= Cost; RegenDelay = 42; Action = Requested; Age = 0;
    if (Requested == EWardenAction::Strike) { Move = MoveIndex; ++AttackInstance; HitConsumed = false; Cooldowns[Move] = Definition().Total()+(IsBoss ? 60 : 8); }
    if (Requested == EWardenAction::Heal) --Heals;
    return true;
}
void FWardenFighterState::Advance()
{
    if (!Alive()) return;
    if(ImpactTicks>0) --ImpactTicks;
    if(PoiseReset>0 && --PoiseReset==0) Poise=3;
    for(int32& Cooldown : Cooldowns) if(Cooldown > 0) --Cooldown;
    if (Gap > 0) --Gap;
    if (RegenDelay > 0) --RegenDelay;
    else if (Action == EWardenAction::Ready) Stamina = FMath::Min(100.f,Stamina+26.f/60.f);
    if (Action == EWardenAction::Ready) return;
    ++Age;
    if (Action == EWardenAction::Heal && Age == WardenRules::HealCommit) Health = FMath::Min(MaxHealth,Health+45.f);
    const int32 Duration = Action == EWardenAction::Strike ? Definition().Total() : Action == EWardenAction::Dodge ? WardenRules::DodgeTicks : Action==EWardenAction::Hurt ? (IsBoss?WardenRules::BossHurtTicks:WardenRules::HurtTicks) : WardenRules::HealTicks;
    if (Age >= Duration) { Action = EWardenAction::Ready; Age = 0; Gap = WardenRules::RecoveryGap; }
}
bool FWardenFighterState::Damage(float Amount)
{
    if (!Alive() || Invulnerable() || Amount <= 0 || !FMath::IsFinite(Amount)) return false;
    Sprinting=false;
    Health = FMath::Max(0.f,Health-Amount);
    if (Health == 0) { Action = EWardenAction::Dead; Age = 0; }
    else
    {
        ImpactTicks=18;
        if(IsBoss) { --Poise; PoiseReset=300; }
        // Player takes a short committed flinch. The Warden withstands two hits;
        // the third breaks poise. This rule is identical for every controller.
        if(!IsBoss || Poise<=0)
        {
            Action=EWardenAction::Hurt; Age=0; Gap=0; HitConsumed=true;
            if(IsBoss) { Poise=3; PoiseReset=0; }
        }
    }
    return true;
}
float FWardenFighterState::AnimationTime() const
{
    const auto& D = Definition();
    if (Age < D.Windup) return D.AnimationContactStart * Age / D.Windup;
    if (Age < D.Windup+D.Active) return FMath::Lerp(D.AnimationContactStart,D.AnimationContactEnd,float(Age-D.Windup)/D.Active);
    return FMath::Lerp(D.AnimationContactEnd,D.AnimationEnd,FMath::Clamp(float(Age-D.Windup-D.Active)/D.Recovery,0.f,1.f));
}
