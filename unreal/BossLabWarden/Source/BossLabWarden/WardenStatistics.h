#pragma once
#include "WardenPolicy.h"

struct FWardenCounts
{
    int32 Samples=0;
    float Recent[3]={0,0,0}, Long[3]={0,0,0}, Direction[3]={0,0,0};
    void Add(int32 Response,int32 Heading);
    float Probability(int32 Category,bool Slow=false) const;
    float DirectionProbability(int32 Category) const;
    float EffectiveCount() const { return Recent[0]+Recent[1]+Recent[2]; }
};
struct FWardenResponse
{
    int32 Encounter=0, Attack=0, Family=0, CueTick=0, CloseTick=0, DeliveredTick=0;
    int32 Response=2, Heading=-1;
    bool Censored=false;
};
struct FWardenStatistics
{
    FWardenCounts Pooled, Family[3];
    TArray<FWardenResponse> Events;
    int32 Censored=0, Rejected=0;
    void Observe(const FWardenObservation& O);
    void Censor();
    void NewEncounter(int32 Generation,bool Retain=false);
    const FWardenCounts& Context(int32 Move) const { return Family[Move].Samples>=6?Family[Move]:Pooled; }
private:
    int32 Encounter=0, LastSample=-1, LastAttack=-1;
    bool Pending=false;
    FWardenResponse Window;
    void Close(bool Censored);
};
FWardenDecision WardenAdaptiveDecision(const FWardenObservation& O,const FWardenSelfView& Self,const FWardenStatistics& Stats,float Draw);
