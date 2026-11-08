#pragma once
#include "CoreMinimal.h"
#include "WardenCombat.h"

// Value-only boundary. No UObject, input, player resources, script identity or seed.
struct FWardenObservation
{
    int32 Encounter = 0, SampleTick = 0, DeliveredTick = 0;
    FVector PlayerPosition = FVector::ZeroVector;
    FVector PlayerVelocity = FVector::ZeroVector;
    EWardenAction VisibleAction = EWardenAction::Ready;
    int32 VisibleActionAge = 0;
    FVector SelfPosition=FVector::ZeroVector;
    int32 SelfAttack=0, SelfMove=0, SelfAge=0;
    bool SelfStriking=false;
};
enum class EWardenChoice : uint8 { Attack, Approach, Reposition, Wait };
struct FWardenDecision
{
    int32 Encounter = 0, Tick = 0, Move = 0;
    EWardenChoice Choice = EWardenChoice::Wait;
    FVector Direction = FVector::ZeroVector;
    float Adjustments[3]={0,0,0};
    float Utilities[3] = {0,0,0};
    float Probabilities[3] = {0,0,0};
};
struct FWardenSelfView
{
    FVector Position = FVector::ZeroVector;
    bool Legal[3] = {false,false,false};
};
FWardenDecision WardenStaticDecision(const FWardenObservation& Observation, const FWardenSelfView& Self, float RandomDraw);

FWardenDecision WardenUtilityDecision(const FWardenObservation& O,const FWardenSelfView& Self,float Draw,const float Bias[3]);
