#include "WardenStatistics.h"
void FWardenCounts::Add(int32 Response,int32 Heading)
{
    ++Samples;
    for(int32 I=0;I<3;++I) { Recent[I]*=.82f; Long[I]*=.97f; Direction[I]*=.82f; }
    Recent[Response]+=1; Long[Response]+=1;
    if(Heading>=0 && Heading<3) Direction[Heading]+=1;
}
float FWardenCounts::Probability(int32 Category,bool Slow) const
{
    const float* Values=Slow?Long:Recent;
    return (1+Values[Category])/(3+Values[0]+Values[1]+Values[2]);
}
float FWardenCounts::DirectionProbability(int32 Category) const
{ return (1+Direction[Category])/(3+Direction[0]+Direction[1]+Direction[2]); }
void FWardenStatistics::NewEncounter(int32 Generation,bool Retain)
{
    Censor();
    if(!Retain) { Pooled=FWardenCounts(); for(auto& C:Family) C=FWardenCounts(); Events.Reset(); Censored=Rejected=0; }
    Encounter=Generation; LastSample=-1; LastAttack=-1; Pending=false;
}
void FWardenStatistics::Close(bool IsCensored)
{
    if(!Pending) return;
    Window.Censored=IsCensored;
    if(IsCensored) ++Censored;
    else { Pooled.Add(Window.Response,Window.Heading); Family[Window.Family].Add(Window.Response,Window.Heading); }
    Events.Add(Window); if(Events.Num()>256) Events.RemoveAt(0);
    Pending=false;
}
void FWardenStatistics::Censor() { Close(true); }
void FWardenStatistics::Observe(const FWardenObservation& O)
{
    if(O.Encounter!=Encounter || O.DeliveredTick-O.SampleTick!=12 || O.SampleTick<=LastSample) { ++Rejected; return; }
    if(LastSample>=0 && O.SampleTick!=LastSample+1) Censor();
    LastSample=O.SampleTick;
    if(Pending) Window.DeliveredTick=O.DeliveredTick;
    if(Pending && O.SampleTick>=Window.CloseTick) { Window.DeliveredTick=O.DeliveredTick; Close(false); }
    if(O.SelfStriking && O.SelfAttack!=LastAttack)
    {
        Censor(); LastAttack=O.SelfAttack;
        if(O.SelfMove<0 || O.SelfMove>2) { ++Rejected; return; }
        Window=FWardenResponse(); Window.Encounter=Encounter; Window.Attack=O.SelfAttack; Window.Family=O.SelfMove;
        Window.CueTick=O.SampleTick-O.SelfAge;
        const auto& Def=WardenRules::Strike(O.SelfMove);
        Window.CloseTick=Window.CueTick+Def.Windup+Def.Active;
        Pending=O.SampleTick<Window.CloseTick;
    }
    if(Pending && Window.Response==2 && O.VisibleAction==EWardenAction::Dodge)
    {
        const int32 Onset=O.SampleTick-O.VisibleActionAge;
        if(Onset>=Window.CueTick && Onset<Window.CloseTick)
        {
            Window.Response=Onset-Window.CueTick < .55f*WardenRules::Strike(Window.Family).Windup ? 0:1;
            const float Dot=FVector::DotProduct(O.PlayerVelocity.GetSafeNormal2D(),(O.SelfPosition-O.PlayerPosition).GetSafeNormal2D());
            Window.Heading=Dot>.5f?0:Dot<-.5f?1:2;
        }
    }
}
FWardenDecision WardenAdaptiveDecision(const FWardenObservation& O,const FWardenSelfView& Self,const FWardenStatistics& Stats,float Draw)
{
    float Bias[3]={0,0,0};
    if(Stats.Pooled.Samples>=6)
        for(int32 I=0;I<3;++I)
        {
            const auto& C=Stats.Context(I);
            const float Early=C.Probability(0), Late=C.Probability(1), None=C.Probability(2);
            Bias[I]=FMath::Clamp(I==0 ? .9f*(Late-1.f/3)+.6f*(None-1.f/3) : I==1 ? 1.8f*(Early-1.f/3)-.7f*(Late-1.f/3) : 1.2f*(C.DirectionProbability(1)-1.f/3)-.7f*(C.DirectionProbability(2)-1.f/3),-.8f,.8f);
        }
    return WardenUtilityDecision(O,Self,Draw,Bias);
}
