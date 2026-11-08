#pragma once
#include "WardenCombat.h"

struct FWardenPlayerCommand
{
    FVector Movement=FVector::ZeroVector;
    EWardenAction Action=EWardenAction::Ready;
};
// Development/demo player only. Never passed to the boss controller.
struct FWardenPlayerScript
{
    int32 Style=1, SwitchTick=1800, LastRespondedInstance=-1, ReactionOffset=0;
    FWardenPlayerCommand Decide(int32 Tick,const FVector& Position,const FWardenFighterState& Own,
        const FVector& VisibleBossPosition,EWardenAction VisibleBossAction,int32 VisibleMove,int32 VisibleAge,int32 VisibleInstance);
};
