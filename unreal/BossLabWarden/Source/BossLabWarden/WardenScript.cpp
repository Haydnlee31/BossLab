#include "WardenScript.h"
FWardenPlayerCommand FWardenPlayerScript::Decide(int32 Tick,const FVector& Position,const FWardenFighterState& Own,
    const FVector& BossPosition,EWardenAction BossAction,int32 Move,int32 Age,int32 Instance)
{
    FWardenPlayerCommand C;
    const FVector Toward=(BossPosition-Position).GetSafeNormal2D();
    const float Distance=FVector::Dist2D(Position,BossPosition);
    if(!Own.Alive()) return C;
    if(Own.Health<=50 && Own.Heals>0)
    {
        C.Movement=-Toward;
        if(Distance>320 && Own.Ready()) C.Action=EWardenAction::Heal;
        return C;
    }
    const auto& Def=WardenRules::Strike(Move);
    const bool Early=Style==0 || (Style==3 && Tick<SwitchTick);
    const int32 ResponseAge=(Early ? FMath::Max(3,Def.Windup/5) : Def.Windup-8)+ReactionOffset;
    if(BossAction==EWardenAction::Strike && Age>=ResponseAge && Age<Def.Windup+Def.Active && Instance!=LastRespondedInstance && Own.Ready() && Own.Stamina>=WardenRules::DodgeCost)
    {
        LastRespondedInstance=Instance;
        C.Action=EWardenAction::Dodge;
        C.Movement=Style==2 ? FVector(-Toward.Y,Toward.X,0) : Toward;
        return C;
    }
    if(Distance>140) C.Movement=Toward;
    if(Own.Ready() && Own.Stamina>=WardenRules::StrikeCost+WardenRules::DodgeCost && Distance<180 && BossAction==EWardenAction::Strike && Age>=Def.Windup+Def.Active)
        C.Action=EWardenAction::Strike;
    return C;
}
