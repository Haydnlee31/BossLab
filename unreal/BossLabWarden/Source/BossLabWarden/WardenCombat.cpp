#include "WardenCombat.h"
#include "WardenRegent.h"

float WardenRules::DodgeDistance(float Age)
{
    // Integrated smooth velocity: six-tick push, fourteen-tick carry, twenty-tick
    // landing. Exactly 320 cm; no frame-rate dependence or abrupt speed changes.
    const float T=FMath::Clamp(Age,0.f,float(DodgeTicks));
    const float V=320.f/27;
    auto Integral=[](float U) { return U*U*U-.5f*U*U*U*U; };
    if(T<6) return V*6*Integral(T/6);
    if(T<20) return V*(3+T-6);
    const float U=(T-20)/20;
    return V*(17+20*(U-Integral(U)));
}
float WardenRules::JumpLift(float Age)
{
    const float U=FMath::Clamp(Age/float(JumpTicks),0.f,1.f);
    return 4*JumpHeight*U*(1-U);
}
bool WardenRules::ChainOpen(int32 Move, int32 Age)
{
    if(Move!=CutOne && Move!=CutTwo && Move!=CutThree) return false;
    const auto& D=Strike(Move,false);
    return Age>=D.Windup+D.Active+2 && Age<D.Total();
}
bool WardenRules::RecoveryCancelOpen(int32 Move, int32 Age)
{
    // A jump attack leaves you open after landing; everything else can roll out early.
    const auto& D=Strike(Move,false);
    return Age>=D.Windup+D.Active+(Move==JumpAttack ? 24 : 8);
}

const FWardenStrike& WardenRules::Strike(int32 Index, bool Boss)
{
    // Name, pose, bone, windup, active, recovery, (unused anim times), damage, radius,
    // advance, stamina, stance. Later cuts start faster; the third is a heavy finisher.
    static const FWardenStrike Player[PlayerMoveCount]={
        {TEXT("GREATSWORD CUT I"),TEXT("AuthoredSword"),TEXT("hand_r"),24,16,28,0.f,0.f,1.f,30,6,22,18,1},
        {TEXT("GREATSWORD CUT II"),TEXT("AuthoredSword"),TEXT("hand_r"),20,16,28,0.f,0.f,1.f,30,6,20,18,1},
        {TEXT("GREATSWORD CUT III"),TEXT("AuthoredSword"),TEXT("hand_r"),28,18,38,0.f,0.f,1.f,46,7,36,22,2},
        {TEXT("JUMP ATTACK"),TEXT("AuthoredSword"),TEXT("hand_r"),18,14,40,0.f,0.f,1.f,52,7,30,14,2},
        {TEXT("ROLLING THRUST"),TEXT("AuthoredSword"),TEXT("hand_r"),12,10,32,0.f,0.f,1.f,24,6,80,16,1},
        {TEXT("RUNNING CUT"),TEXT("AuthoredSword"),TEXT("hand_r"),16,16,34,0.f,0.f,1.f,36,6,120,20,1}};
    if (!Boss) { check(Index >= 0 && Index < PlayerMoveCount); return Player[Index]; }
    if (WardenRegent::IsRegent(Index)) return WardenRegent::Strike(Index);
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
    Stamina=FMath::Max(0.f,Stamina-Cost); RegenDelay=IsBoss?WardenRules::BossRegenDelayTicks:WardenRules::RegenDelayTicks; Sprinting=true;
    if(Stamina<=KINDA_SMALL_NUMBER) SprintExhausted=true;
}

bool FWardenFighterState::Invulnerable() const
{
    if (Action == EWardenAction::Strike && WardenRegent::Vanished(Move,Age)) return true;
    return Action == EWardenAction::Dodge && Age >= WardenRules::DodgeInvulnerableStart && Age < WardenRules::DodgeInvulnerableEnd;
}
bool FWardenFighterState::Active() const
{
    if (Action != EWardenAction::Strike || !Alive()) return false;
    if (WardenRegent::IsRegent(Move)) return WardenRegent::Contact(Move,Age);
    const auto& Def = Definition();
    return Age >= Def.Windup && Age < Def.Windup + Def.Active;
}
bool FWardenFighterState::Affordable(int32 Index) const
{
    return Index >= 0 && Index < (IsBoss ? WardenRules::BossMoveCount : int32(WardenRules::PlayerMoveCount))
        && Stamina >= StrikeCostOf(Index) && Cooldowns[Index] == 0;
}
float FWardenFighterState::StrikeCostOf(int32 Index) const
{
    const float Cost=WardenRules::Strike(Index,IsBoss).Cost;
    return Cost>=0 ? Cost : WardenRules::StrikeCost;
}
int32 FWardenFighterState::NextPlayerMove() const
{
    using namespace WardenRules;
    if(Action==EWardenAction::Jump) return JumpAttack;
    if(Action==EWardenAction::Dodge) return RollAttack;
    if(Action==EWardenAction::Strike && (Move==CutOne || Move==CutTwo || Move==CutThree)) return Move==CutThree ? CutOne : Move+1;
    return Sprinting ? RunAttack : CutOne;
}
bool FWardenFighterState::CancelOpen(EWardenAction Requested, int32 MoveIndex) const
{
    using namespace WardenRules;
    if(IsBoss || !Alive()) return false;
    switch(Action)
    {
        case EWardenAction::Strike:
            if(Requested==EWardenAction::Strike) return ChainOpen(Move,Age) && MoveIndex==NextPlayerMove();
            return Requested==EWardenAction::Dodge && RecoveryCancelOpen(Move,Age);
        case EWardenAction::Dodge:
            if(Requested==EWardenAction::Strike) return Age>=RollAttackOpen && MoveIndex==RollAttack;
            return Requested==EWardenAction::Dodge && Age>=RollChainOpen;
        case EWardenAction::Jump:
            return Requested==EWardenAction::Strike && MoveIndex==JumpAttack && Age>=JumpAttackOpen && Age<=JumpAttackClose;
        default: return false;
    }
}
bool FWardenFighterState::Request(EWardenAction Requested, int32 MoveIndex)
{
    if (!Ready() && !CancelOpen(Requested,MoveIndex)) return false;
    // Context attacks only come from their context (a jump attack needs a jump, etc.).
    if (!IsBoss && Requested==EWardenAction::Strike && Ready() && MoveIndex!=NextPlayerMove()) return false;
    float Cost = 0;
    switch (Requested)
    {
        case EWardenAction::Strike:
            if (!Affordable(MoveIndex)) return false;
            Cost = StrikeCostOf(MoveIndex); break;
        case EWardenAction::Dodge: Cost = WardenRules::DodgeCost; break;
        case EWardenAction::Jump:
            if (IsBoss) return false;
            Cost = WardenRules::JumpCost; break;
        case EWardenAction::Heal:
            if (Heals <= 0 || Health >= MaxHealth) return false;
            Cost = WardenRules::HealCost; break;
        default: return false;
    }
    if (Stamina < Cost) return false;
    Sprinting=false;
    Stamina -= Cost; RegenDelay = IsBoss ? WardenRules::BossRegenDelayTicks : WardenRules::RegenDelayTicks; Action = Requested; Age = 0; Gap = 0;
    if (Requested == EWardenAction::Strike) { Move = MoveIndex; ++AttackInstance; HitConsumed = false; Cooldowns[Move] = Definition().Total()+(IsBoss ? 60 : 8); }
    if (Requested == EWardenAction::Heal) --Heals;
    return true;
}
void FWardenFighterState::Advance()
{
    if (!Alive()) return;
    if(ImpactTicks>0) --ImpactTicks;
    if(PoiseReset>0 && --PoiseReset==0) Poise=MaxPoise;
    for(int32& Cooldown : Cooldowns) if(Cooldown > 0) --Cooldown;
    if (Gap > 0) --Gap;
    if (RegenDelay > 0) --RegenDelay;
    else if (Action == EWardenAction::Ready) Stamina = FMath::Min(100.f,Stamina+(IsBoss?WardenRules::BossStaminaRegen:WardenRules::StaminaRegen)/60.f);
    if (Action == EWardenAction::Ready) return;
    ++Age;
    if (Action == EWardenAction::Strike && WardenRegent::Rearm(Move,Age)) HitConsumed = false;
    if (Action == EWardenAction::Heal && Age == WardenRules::HealCommit) Health = FMath::Min(MaxHealth,Health+45.f);
    const int32 Duration = Action == EWardenAction::Strike ? Definition().Total() : Action == EWardenAction::Dodge ? WardenRules::DodgeTicks : Action==EWardenAction::Hurt ? (IsBoss?WardenRules::BossHurtTicks:WardenRules::HurtTicks) : Action==EWardenAction::Jump ? WardenRules::JumpTicks : WardenRules::HealTicks;
    if (Age >= Duration) { Action = EWardenAction::Ready; Age = 0; Gap = WardenRules::RecoveryGap; }
}
bool FWardenFighterState::Damage(float Amount, bool Flinch, int32 Stance)
{
    if (!Alive() || Invulnerable() || Amount <= 0 || !FMath::IsFinite(Amount)) return false;
    if (Flinch) Sprinting=false;
    Health = FMath::Max(0.f,Health-Amount);
    if (Health == 0) { Action = EWardenAction::Dead; Age = 0; }
    else if (Flinch)
    {
        ImpactTicks=18;
        if(IsBoss) { Poise-=Stance; PoiseReset=300; }
        // Player takes a short committed flinch. A boss's stance (BossPoise points) breaks
        // under accumulated stance damage: heavy finishers and jump attacks take two.
        // This rule is identical for every controller.
        if(!IsBoss || Poise<=0)
        {
            Action=EWardenAction::Hurt; Age=0; Gap=0; HitConsumed=true;
            if(IsBoss) { Poise=MaxPoise; PoiseReset=0; }
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
