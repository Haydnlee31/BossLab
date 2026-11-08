#include "WardenPolicy.h"

FWardenDecision WardenUtilityDecision(const FWardenObservation& O,const FWardenSelfView& Self,float RandomDraw,const float Bias[3])
{
    FWardenDecision D; D.Encounter=O.Encounter; D.Tick=O.DeliveredTick;
    const FVector Offset=O.PlayerPosition-Self.Position;
    const float Distance=Offset.Size2D();
    D.Direction=Offset.GetSafeNormal2D();
    if (Distance>250) { D.Choice=EWardenChoice::Approach; return D; }
    float Sum=0;
    const float Ranges[3]={195,210,250};
    const float Base[3]={1.2f,1.f,.9f};
    for(int32 I=0;I<3;++I)
    {
        D.Adjustments[I]=Bias[I];
        D.Utilities[I]=Base[I]+Bias[I]+(I==2 ? FMath::Clamp((Distance-160)/120.f,-.35f,.6f) : 0);
        if(Self.Legal[I] && Distance<=Ranges[I])
        { D.Probabilities[I]=FMath::Exp(D.Utilities[I]); Sum+=D.Probabilities[I]; }
    }
    if(Sum>0)
    {
        D.Choice=EWardenChoice::Attack;
        float Cumulative=0;
        const float Draw=FMath::Clamp(RandomDraw,0.f,.999999f);
        for(int32 I=0;I<3;++I) D.Probabilities[I]/=Sum;
        for(int32 I=0;I<3;++I)
        {
            Cumulative+=D.Probabilities[I];
            if(Draw<Cumulative) { D.Move=I; break; }
        }
    }
    else if(Distance>190) D.Choice=EWardenChoice::Approach;
    else if(Distance<100)
    {
        D.Choice=EWardenChoice::Reposition;
        D.Direction=-D.Direction;
    }
    // With no legal strike at ordinary spacing, wait for engine recovery/stamina.
    return D;
}

FWardenDecision WardenStaticDecision(const FWardenObservation& O,const FWardenSelfView& Self,float Draw)
{ const float Bias[3]={0,0,0}; return WardenUtilityDecision(O,Self,Draw,Bias); }
