#include "WardenPrototype.h"
#include "WardenRegent.h"
#include "Engine/World.h"
#include "Components/PoseableMeshComponent.h"
#include "Engine/Engine.h"
#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#define REGENT_TEST(Type,Name) IMPLEMENT_SIMPLE_AUTOMATION_TEST(Type,Name,(EAutomationTestFlags::EditorContext|EAutomationTestFlags::ClientContext)|EAutomationTestFlags::EngineFilter)
namespace {
UWorld* NewWorld() { auto* W=UWorld::CreateWorld(EWorldType::Game,false); GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W); return W; }
void CloseWorld(UWorld* W) { GEngine->DestroyWorldContext(W); W->DestroyWorld(false); }
AWardenArenaMode* RegentArena(UWorld* W)
{
    auto* M=W->SpawnActor<AWardenArenaMode>();
    M->Player=W->SpawnActor<AWardenChallenger>(FVector(-450,0,95),FRotator::ZeroRotator); M->Player->DispatchBeginPlay(); M->Player->ResetFighter(false);
    M->DispatchBeginPlay(); M->Warden->DispatchBeginPlay();
    M->EnableRegent(); M->ConfigureEncounter(303,true,1);
    return M;
}
// One committed Regent move against a player standing at Distance in front of it.
// RollAt is the boss action age at which the player rolls along RollDirection (-1: never;
// Skulls: roll whenever a skull is about to arrive). Returns damage taken.
constexpr int32 SkullRoll=-2;
float Duel(int32 Move,float Distance,int32 RollAt,FVector RollDirection)
{
    auto* W=NewWorld(); auto* M=RegentArena(W);
    M->bScriptedPlayer=false; M->Regent.Waiting=1000000;
    M->Warden->SetActorLocation(FVector(0,0,128)); M->Warden->SetActorRotation(FRotator::ZeroRotator);
    M->Player->SetActorLocation(FVector(Distance,0,95));
    M->Warden->BeginAction(EWardenAction::Strike,Move,FVector::ForwardVector);
    const int32 Ticks=M->Warden->Fight.Definition().Total()+120;
    for(int32 T=0;T<Ticks;++T)
    {
        bool Roll=T==RollAt;
        if(RollAt==SkullRoll)
            for(const auto& K:M->Regent.Flying) Roll|=FVector::Dist(K.Position,M->Player->GetActorLocation())<160 && M->Player->Fight.Ready();
        if(Roll) { M->Player->PendingAction=EWardenAction::Dodge; M->Player->PendingDirection=RollDirection; }
        M->FixedStep();
    }
    const float Taken=M->Player->Fight.MaxHealth-M->Player->Fight.Health;
    CloseWorld(W);
    return Taken;
}
}
REGENT_TEST(FRegentTableTest,"BossLab.Regent.MoveTableAndTelegraphs");
bool FRegentTableTest::RunTest(const FString&)
{
    using namespace WardenRegent;
    TestEqual(TEXT("Default rehearsal moves unchanged"),FString(WardenRules::Strike(0).Name)+WardenRules::Strike(1).Name+WardenRules::Strike(2).Name,FString(TEXT("BROAD SWEEPHELD OVERHEADRISING CLEAVE")));
    TestEqual(TEXT("Regent moves fill the boss table"),First+Count,WardenRules::BossMoveCount);
    for(int32 M=First;M<First+Count;++M)
    {
        const auto& D=WardenRules::Strike(M);
        TestTrue(FString::Printf(TEXT("%s has active and recovery phases"),D.Name),D.Active>0 && D.Recovery>0);
        // Every damaging telegraph is readable: at least 0.4 s from the visible start
        // (or the ash-step reappearance) to the first contact.
        const int32 Readable=M==AshStep ? D.Windup-AshAppear : D.Windup;
        if(D.Damage>0) TestTrue(FString::Printf(TEXT("%s telegraph >= 24 ticks (%d)"),D.Name,Readable),Readable>=24);
    }
    TestTrue(TEXT("Furrow marks warn for at least 0.4 s"),FurrowWarn>=24);
    TestTrue(TEXT("Ash Step destination shown 24 ticks before reappearing"),AshAppear-AshVanish>=24);
    FWardenFighterState S; S.IsBoss=true;
    TestTrue(TEXT("Rite starts"),S.Request(EWardenAction::Strike,Rite));
    int32 Contact=0, Rearms=0;
    for(int32 I=0;I<WardenRules::Strike(Rite).Total();++I) { if(S.Active()) { ++Contact; if(!S.HitConsumed) { ++Rearms; S.HitConsumed=true; } } S.Advance(); }
    TestEqual(TEXT("Rite has 26 contact ticks"),Contact,26);
    TestEqual(TEXT("Rite can land three separate thrusts"),Rearms,3);
    const float Floor=PI*FloorRadius*FloorRadius, Worst=MaxPools*PI*FMath::Square(FMath::Max(BellPoolRadius,PyrePoolRadius));
    TestTrue(TEXT("Fire pools never cover more than 15% of the floor"),Worst<=.15f*Floor);
    FWardenFighterState P; P.Health=50;
    TestTrue(TEXT("Pool chip damage lands"),P.Damage(PoolDamage,false));
    TestTrue(TEXT("Pool chip damage does not flinch"),P.Action==EWardenAction::Ready && P.ImpactTicks==0);
    AddInfo(FString::Printf(TEXT("Worst-case pool cover %.1f%% of the floor"),100*Worst/Floor));
    return true;
}
REGENT_TEST(FRegentRollTest,"BossLab.Regent.RollBeatsEveryAttack");
bool FRegentRollTest::RunTest(const FString&)
{
    using namespace WardenRegent;
    struct FCase { int32 Move; float Distance; int32 RollAt; FVector Direction; };
    const FVector Side=FVector::RightVector, Back=FVector::ForwardVector;  // player stands on +X
    const FCase Cases[]={
        {Thrust,250,32,Side},{Rite,230,26,Side},{Arc,300,52,Back},{Bell,300,62,Side},{Volley,600,SkullRoll,Side},
        {Dash,700,40,Side},{Furrow,500,60,Side},{AshStep,300,64,Side},{Pyre,300,68,Back},{HeldThrust,250,54,Side}};
    for(const auto& C:Cases)
    {
        const TCHAR* Name=WardenRules::Strike(C.Move).Name;
        const float Still=Duel(C.Move,C.Distance,-1,FVector::ZeroVector);
        const float Rolled=Duel(C.Move,C.Distance,C.RollAt,C.Direction);
        AddInfo(FString::Printf(TEXT("%s: standing still takes %.0f, timed roll takes %.0f"),Name,Still,Rolled));
        TestTrue(FString::Printf(TEXT("%s hurts a player who stands still"),Name),Still>0);
        TestEqual(FString::Printf(TEXT("%s is beaten by one timed roll"),Name),Rolled,0.f);
    }
    return true;
}
REGENT_TEST(FRegentSequenceTest,"BossLab.Regent.SequenceBudgetAndDeterminism");
bool FRegentSequenceTest::RunTest(const FString&)
{
    using namespace WardenRegent;
    {
        // Same fixed ticks at 60 and 30 rendered fps give the same fight.
        auto* WA=NewWorld(); auto* WB=NewWorld(); auto* A=RegentArena(WA); auto* B=RegentArena(WB);
        for(int32 I=0;I<1200;++I) A->Tick(1.f/60);
        for(int32 I=0;I<600;++I) B->Tick(1.f/30);
        TestEqual(TEXT("Same fixed tick count"),A->CombatTick,B->CombatTick);
        TestEqual(TEXT("Same player health"),A->Player->Fight.Health,B->Player->Fight.Health);
        TestEqual(TEXT("Same boss health"),A->Warden->Fight.Health,B->Warden->Fight.Health);
        TestTrue(TEXT("Same boss transform"),A->Warden->GetActorLocation().Equals(B->Warden->GetActorLocation(),.01));
        TestTrue(TEXT("Regent combat occurred"),A->BossDamage+A->PlayerDamage>0);
        CloseWorld(WA); CloseWorld(WB);
    }
    // Long scripted fight through both phases; the fighters cannot die here so the budget
    // and sequence are exercised. Pools, skulls and position stay inside their limits.
    auto* W=NewWorld(); auto* M=RegentArena(W);
    auto Endure=[&] { M->Player->Fight.Health=M->Player->Fight.MaxHealth=100000; };
    Endure(); M->Warden->Fight.Health=100000;
    TSet<int32> Used; int32 MaxSkulls=0; float MaxPool=0, MaxRadius=0; bool Finite=true;
    for(int32 I=0;I<9000;++I)
    {
        if(I==4500) M->Warden->Fight.Health=PhaseTwoHealth-10;
        if(M->Regent.PhaseTwo && M->Warden->Fight.Health<1000) M->Warden->Fight.Health=100000;
        M->Tick(1.f/60);
        if(M->Warden->Fight.Action==EWardenAction::Strike) Used.Add(M->Warden->Fight.Move);
        MaxSkulls=FMath::Max(MaxSkulls,M->Regent.Flying.Num());
        MaxPool=FMath::Max(MaxPool,M->Regent.PoolArea(M->CombatTick));
        MaxRadius=FMath::Max(MaxRadius,float(FVector2D(M->Warden->GetActorLocation()).Size()));
        Finite&=!M->Warden->GetActorLocation().ContainsNaN();
    }
    FString Missing;
    for(int32 Move=First;Move<First+Count;++Move) if(!Used.Contains(Move)) Missing+=FString(WardenRules::Strike(Move).Name)+TEXT(" ");
    AddInfo(FString::Printf(TEXT("%d of %d Regent moves used; max %d skulls in flight; max pool cover %.1f%%; max boss radius %.0f cm; player took %.0f"),Used.Num(),Count,MaxSkulls,100*MaxPool/(PI*FloorRadius*FloorRadius),MaxRadius,M->BossDamage));
    TestTrue(TEXT("Second phase reached"),M->Regent.PhaseTwo);
    TestTrue(FString(TEXT("Every Regent move occurs; missing: "))+Missing,Missing.IsEmpty());
    TestTrue(TEXT("At most three skulls in flight"),MaxSkulls<=Skulls);
    TestTrue(TEXT("Pools stay within 15% of the floor"),MaxPool<=.15f*PI*FloorRadius*FloorRadius);
    TestTrue(TEXT("Regent stays on the fight floor"),MaxRadius<FloorRadius-60);
    TestTrue(TEXT("Finite transforms"),Finite);
    CloseWorld(W);
    return true;
}
#endif
#if WITH_DEV_AUTOMATION_TESTS
REGENT_TEST(FRegentPoseTest,"BossLab.Regent.LungesLeanIntoTheThrust");
bool FRegentPoseTest::RunTest(const FString&)
{
    using namespace WardenRegent;
    // Head ahead of the pelvis (actor forward, cm) at guard and at contact: a lunge must
    // carry the upper body toward the target, never tip it away.
    auto* W=NewWorld(); auto* B=W->SpawnActor<AWardenChallenger>(FVector(0,0,128),FRotator::ZeroRotator);
    B->DispatchBeginPlay(); B->ResetFighter(true); B->bRegent=true; B->SetActorScale3D(FVector(1.35));
    auto Lead=[&]()
    {
        const FVector Head=B->VisualBody->GetBoneLocationByName(TEXT("head"),EBoneSpaces::WorldSpace);
        const FVector Pelvis=B->VisualBody->GetBoneLocationByName(TEXT("pelvis"),EBoneSpaces::WorldSpace);
        return float(FVector::DotProduct(Head-Pelvis,B->GetActorForwardVector()));
    };
    for(int32 I=0;I<4;++I) B->CombatPose(FVector::ZeroVector);
    const float Guard=Lead();
    for(const int32 Move:{int32(Thrust),int32(HeldThrust),int32(Dash),int32(AshStep)})
    {
        B->SetActorLocation(FVector(0,0,128)); B->ResetFighter(true); B->bRegent=true;
        B->BeginAction(EWardenAction::Strike,Move,FVector::ForwardVector);
        float AtContact=0, Least=1000;
        for(int32 T=0;T<B->Fight.Definition().Total();++T)
        {
            B->Fight.Age=T; B->CombatPose(FVector::ZeroVector);
            if(T==B->Fight.Definition().Windup+2) AtContact=Lead();
            // The wind-up may draw back (anticipation); contact itself must not.
            if(T>=B->Fight.Definition().Windup && T<B->Fight.Definition().Windup+B->Fight.Definition().Active) Least=FMath::Min(Least,Lead());
        }
        AddInfo(FString::Printf(TEXT("%s: head lead guard %.1f cm, contact %.1f cm, least near contact %.1f cm"),WardenRules::Strike(Move).Name,Guard,AtContact,Least));
        TestTrue(FString::Printf(TEXT("%s leans into the thrust"),WardenRules::Strike(Move).Name),AtContact>Guard+4);
        TestTrue(FString::Printf(TEXT("%s never tips back during contact"),WardenRules::Strike(Move).Name),Least>Guard);
    }
    CloseWorld(W); return true;
}
#endif
