#include "WardenPrototype.h"
#include "Components/PoseableMeshComponent.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#define ANIMATION_TEST(Type,Name) IMPLEMENT_SIMPLE_AUTOMATION_TEST(Type,Name,(EAutomationTestFlags::EditorContext|EAutomationTestFlags::ClientContext)|EAutomationTestFlags::EngineFilter)
namespace {
UWorld* NewWorld() { auto* W=UWorld::CreateWorld(EWorldType::Game,false); GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W); return W; }
void CloseWorld(UWorld* W) { GEngine->DestroyWorldContext(W); W->DestroyWorld(false); }
// Planted-foot slip: while walking steadily, the lower foot should hold still on the floor.
// Returns the mean horizontal speed of the planted foot divided by the body's travel speed
// (0 = perfect plant, 1 = the foot skates along with the body).
float Slip(AWardenChallenger* F,const FVector& Direction,AActor* FaceTarget,float& Travel)
{
    // Fighters start far apart so their capsules never block each other.
    F->SetActorLocation(FVector(0,F->bBoss?2000:-2000,F->bBoss?128:95)); F->SetActorRotation(FRotator::ZeroRotator); F->ResetFighter(F->bBoss);
    F->SetTarget(FaceTarget);
    const FVector Start=F->GetActorLocation();
    const int32 Steps=240;
    TArray<FVector> Feet[2];
    for(int32 I=0;I<Steps;++I)
    {
        F->StepFighter(Direction); F->Fight.Advance();
        Feet[0].Add(F->VisualBody->GetBoneLocationByName(TEXT("foot_l"),EBoneSpaces::WorldSpace));
        Feet[1].Add(F->VisualBody->GetBoneLocationByName(TEXT("foot_r"),EBoneSpaces::WorldSpace));
    }
    Travel=FVector::Dist2D(F->GetActorLocation(),Start)/(Steps/60.f);
    // A foot is planted while its ankle is within 1.5 cm of its lowest height in the run;
    // slip is its horizontal world speed then, as a fraction of the body's travel speed.
    float Sum=0; int32 Samples=0;
    for(int32 K=0;K<2;++K)
    {
        float Floor=1e9f; for(int32 I=60;I<Steps;++I) Floor=FMath::Min(Floor,float(Feet[K][I].Z));
        for(int32 I=61;I<Steps;++I)
            if(Feet[K][I].Z<Floor+1.5f && Feet[K][I-1].Z<Floor+1.5f) { Sum+=FVector::Dist2D(Feet[K][I],Feet[K][I-1])*60; ++Samples; }
    }
    return Samples ? Sum/Samples/FMath::Max(1.f,Travel) : 1;
}
}
ANIMATION_TEST(FWardenFootSlipTest,"BossLab.Animation.PlantedFeetHoldWhileWalking");
bool FWardenFootSlipTest::RunTest(const FString&)
{
    auto* W=NewWorld();
    auto* P=W->SpawnActor<AWardenChallenger>(FVector(0,0,95),FRotator::ZeroRotator); P->DispatchBeginPlay(); P->ResetFighter(false);
    auto* B=W->SpawnActor<AWardenChallenger>(FVector(0,0,128),FRotator::ZeroRotator); B->SetActorScale3D(FVector(1.35)); B->DispatchBeginPlay(); B->ResetFighter(true);
    // Far target straight ahead: the boss keeps facing it while walking in each direction.
    auto* Target=W->SpawnActor<AActor>(); Target->SetRootComponent(NewObject<USceneComponent>(Target)); Target->GetRootComponent()->RegisterComponent();
    Target->SetActorLocation(FVector(100000,2000,0));
    struct FCase { const TCHAR* Name; AWardenChallenger* Who; FVector Direction; AActor* Face; };
    const FCase Cases[]={
        {TEXT("player forward"),P,FVector::ForwardVector,nullptr},
        {TEXT("boss forward"),B,FVector::ForwardVector,Target},
        {TEXT("boss backward"),B,-FVector::ForwardVector,Target},
        {TEXT("boss sideways"),B,FVector::RightVector,Target}};
    // Report the play-rate sweep used to choose AWardenChallenger::GaitRate.
    const float Chosen=AWardenChallenger::GaitRate;
    for(const float Rate:{1.f,1.1f,1.2f,1.3f,1.4f})
    {
        AWardenChallenger::GaitRate=Rate; FString Line;
        for(const auto& C:Cases) { float Travel=0; Line+=FString::Printf(TEXT(" %s %.2f;"),C.Name,Slip(C.Who,C.Direction,C.Face,Travel)); }
        AddInfo(FString::Printf(TEXT("Gait rate %.1f slip:%s"),Rate,*Line));
    }
    AWardenChallenger::GaitRate=Chosen;
    for(const auto& C:Cases)
    {
        float Travel=0;
        const float Ratio=Slip(C.Who,C.Direction,C.Face,Travel);
        const float Yaw=C.Who->GetActorRotation().Yaw;
        AddInfo(FString::Printf(TEXT("%s: planted-foot slip %.2f of travel (%.0f cm/s), final yaw %.0f"),C.Name,Ratio,Travel,Yaw));
        TestTrue(FString::Printf(TEXT("%s: planted foot slips under 35%% of travel"),C.Name),Ratio<.35f);
        if(C.Face) TestTrue(FString::Printf(TEXT("%s: boss keeps facing its target"),C.Name),FMath::Abs(FRotator::NormalizeAxis(Yaw))<5);
    }
    CloseWorld(W); return true;
}
#endif
#if WITH_DEV_AUTOMATION_TESTS
ANIMATION_TEST(FWardenRenderBlendTest,"BossLab.Animation.SmoothBetweenFixedSteps");
bool FWardenRenderBlendTest::RunTest(const FString&)
{
    // 45 rendered fps against the 60 Hz step: frames alternately carry one or two steps.
    // The drawn body should still advance at an even speed while the boss walks in.
    auto* W=NewWorld(); auto* M=W->SpawnActor<AWardenArenaMode>();
    M->Player=W->SpawnActor<AWardenChallenger>(FVector(-450,0,95),FRotator::ZeroRotator); M->Player->DispatchBeginPlay(); M->Player->ResetFighter(false);
    M->DispatchBeginPlay(); M->Warden->DispatchBeginPlay(); M->ConfigureEncounter(303,false,1);
    M->RehearsalWait=100000;   // walk in only, no attacks during the measurement
    const float Dt=1.f/45;
    TArray<float> Drawn, Actor; FVector PriorDrawn=M->Warden->VisualBody->GetComponentLocation(), PriorActor=M->Warden->GetActorLocation();
    for(int32 I=0;I<60;++I)
    {
        M->Tick(Dt);
        const FVector D=M->Warden->VisualBody->GetComponentLocation(), A=M->Warden->GetActorLocation();
        if(I>8) { Drawn.Add(FVector::Dist2D(D,PriorDrawn)/Dt); Actor.Add(FVector::Dist2D(A,PriorActor)/Dt); }
        PriorDrawn=D; PriorActor=A;
    }
    auto Variation=[](const TArray<float>& V)
    {
        float Mean=0; for(float X:V) Mean+=X; Mean/=V.Num();
        float Var=0; for(float X:V) Var+=FMath::Square(X-Mean); return FMath::Sqrt(Var/V.Num())/FMath::Max(1.f,Mean);
    };
    const float Smooth=Variation(Drawn), Stepped=Variation(Actor);
    float DrawnMean=0, ActorMean=0; for(int32 I=0;I<Drawn.Num();++I) { DrawnMean+=Drawn[I]/Drawn.Num(); ActorMean+=Actor[I]/Actor.Num(); }
    AddInfo(FString::Printf(TEXT("At 45 fps: drawn body %.0f cm/s (variation %.3f), fixed-step actor %.0f cm/s (variation %.3f)"),DrawnMean,Smooth,ActorMean,Stepped));
    TestTrue(TEXT("Boss is walking during the measurement"),ActorMean>150);
    TestTrue(TEXT("Drawn body moves with the actor"),FMath::Abs(DrawnMean-ActorMean)<ActorMean*.1f);
    TestTrue(TEXT("Drawn motion is even between fixed steps"),Smooth<.1f && Smooth<Stepped*.5f);
    CloseWorld(W); return true;
}
#endif
#if WITH_DEV_AUTOMATION_TESTS
ANIMATION_TEST(FWardenTurnStepTest,"BossLab.Animation.TurningOnTheSpotSteps");
bool FWardenTurnStepTest::RunTest(const FString&)
{
    // A target circling the boss at 90 deg/s: the boss turns to face it without walking,
    // and its feet should step (lift) rather than pivot flat like a turntable.
    auto* W=NewWorld();
    auto* B=W->SpawnActor<AWardenChallenger>(FVector(0,0,128),FRotator::ZeroRotator); B->SetActorScale3D(FVector(1.35)); B->DispatchBeginPlay(); B->ResetFighter(true);
    auto* Target=W->SpawnActor<AActor>(); Target->SetRootComponent(NewObject<USceneComponent>(Target)); Target->GetRootComponent()->RegisterComponent();
    B->SetTarget(Target);
    float Low[2]={1e9f,1e9f}, High[2]={-1e9f,-1e9f}, MaxTurn=0;
    for(int32 I=0;I<240;++I)
    {
        const float A=FMath::DegreesToRadians(I*1.5f);
        Target->SetActorLocation(FVector(FMath::Cos(A),FMath::Sin(A),0)*400);
        B->StepFighter(FVector::ZeroVector); B->Fight.Advance();
        if(I<40) continue;
        MaxTurn=FMath::Max(MaxTurn,FMath::Abs(B->TurnRate));
        for(int32 K=0;K<2;++K)
        {
            const float Z=B->VisualBody->GetBoneLocationByName(K?TEXT("foot_r"):TEXT("foot_l"),EBoneSpaces::WorldSpace).Z;
            Low[K]=FMath::Min(Low[K],Z); High[K]=FMath::Max(High[K],Z);
        }
    }
    const float Lift=FMath::Min(High[0]-Low[0],High[1]-Low[1]);
    AddInfo(FString::Printf(TEXT("Turning at up to %.0f deg/s: smaller foot lift %.1f cm"),MaxTurn,Lift));
    TestTrue(TEXT("Boss turns to follow the target"),MaxTurn>60);
    TestTrue(TEXT("Both feet step while turning"),Lift>4);
    CloseWorld(W); return true;
}
#endif
