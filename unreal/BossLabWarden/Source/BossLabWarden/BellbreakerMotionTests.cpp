// Render interpolation must not send the head of a heavy weapon past the last
// authored contact pose for a fractional frame before snapping into recovery.
#include "WardenBellbreaker.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBellbreakerMotionEndpointTest,
    "BossLab.Bellbreaker.MotionEndpoint",
    (EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext) | EAutomationTestFlags::EngineFilter)

bool FBellbreakerMotionEndpointTest::RunTest(const FString&)
{
    using namespace WardenBellbreaker;
    for(const int32 Move : {HammerFall,Sweep,Quake,BellBreaks})
    {
        const auto& Def=Strike(Move);
        const bool FloorBlast=Move==Quake || Move==BellBreaks;
        const int32 Contact=FloorBlast ? Def.Windup : Def.Windup+Def.Active-1;
        const FVector End=BellOffset(Move,Contact,true);
        const FVector Prior=BellOffset(Move,Contact-1,true);
        TestTrue(FString::Printf(TEXT("Move %d moves up to its contact pose"),Move),
            FVector::Dist(End,Prior)>1.f);
        for(const float SubTick : {0.25f,0.5f,0.75f,0.99f,1.f})
            TestTrue(FString::Printf(TEXT("Move %d stays at its endpoint at +%.2f tick"),Move,SubTick),
                BellOffsetAt(Move,Contact+SubTick,true).Equals(End,0.01f));
    }
    // The damaging sweep crosses the front once, without wrapping behind him.
    const auto& SweepDef=Strike(Sweep);
    FVector Previous=BellOffset(Sweep,SweepDef.Windup-1,true)-GripOffset(Sweep,SweepDef.Windup-1,true);
    double Arc=0;
    for(int32 Tick=0;Tick<SweepDef.Active;++Tick)
    {
        const FVector Next=BellOffset(Sweep,SweepDef.Windup+Tick,true);
        const FVector Shaft=Next-GripOffset(Sweep,SweepDef.Windup+Tick,true);
        const double Turn=FMath::FindDeltaAngleDegrees(Previous.Rotation().Yaw,Shaft.Rotation().Yaw);
        TestTrue(TEXT("Sweep stays in front and progresses in one direction"),Next.X>0 && Shaft.X>0 && Turn<=0);
        Arc-=Turn;
        Previous=Shaft;
    }
    TestTrue(TEXT("One front sweep swings the rigid shaft through 110–120 degrees"),Arc>=110 && Arc<=120);
    return true;
}
#endif
