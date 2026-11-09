#include "WardenPrototype.h"
#include "WardenRegent.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#define CONTROLS_TEST(Type,Name) IMPLEMENT_SIMPLE_AUTOMATION_TEST(Type,Name,(EAutomationTestFlags::EditorContext|EAutomationTestFlags::ClientContext)|EAutomationTestFlags::EngineFilter)
namespace {
UWorld* NewWorld() { auto* W=UWorld::CreateWorld(EWorldType::Game,false); GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W); return W; }
void CloseWorld(UWorld* W) { GEngine->DestroyWorldContext(W); W->DestroyWorld(false); }
AWardenArenaMode* Arena(UWorld* W,bool Regent)
{
    auto* M=W->SpawnActor<AWardenArenaMode>();
    M->Player=W->SpawnActor<AWardenChallenger>(FVector(-450,0,95),FRotator::ZeroRotator); M->Player->DispatchBeginPlay(); M->Player->ResetFighter(false);
    M->DispatchBeginPlay(); M->Warden->DispatchBeginPlay();
    if(Regent) M->EnableRegent();
    M->ConfigureEncounter(303,false,1);
    return M;
}
}
CONTROLS_TEST(FWardenChainTest,"BossLab.Controls.ChainCancelsAndJump");
bool FWardenChainTest::RunTest(const FString&)
{
    using namespace WardenRules;
    // Light chain: each cut opens the next after contact; the third loops to the first.
    FWardenFighterState S;
    TestTrue(TEXT("Cut I starts"),S.Request(EWardenAction::Strike,CutOne));
    TestFalse(TEXT("Cut II cannot start during cut I's wind-up"),S.Request(EWardenAction::Strike,CutTwo));
    while(!ChainOpen(S.Move,S.Age)) S.Advance();
    TestFalse(TEXT("Chain only continues in order"),S.Request(EWardenAction::Strike,CutThree));
    TestTrue(TEXT("Cut II chains after cut I's contact"),S.Request(EWardenAction::Strike,CutTwo));
    while(!ChainOpen(S.Move,S.Age)) S.Advance();
    TestTrue(TEXT("Cut III chains"),S.Request(EWardenAction::Strike,CutThree));
    TestEqual(TEXT("Three cuts cost their sum"),S.Stamina,100-Strike(CutOne,false).Cost-Strike(CutTwo,false).Cost-Strike(CutThree,false).Cost);
    // Recovery is roll-cancellable late, never during wind-up or contact.
    FWardenFighterState R; R.Request(EWardenAction::Strike,CutOne);
    const auto& D=Strike(CutOne,false);
    for(int32 A=0;A<D.Total();++A) { FWardenFighterState Probe=R; Probe.Age=A; TestEqual(FString::Printf(TEXT("Roll cancel at age %d"),A),Probe.Request(EWardenAction::Dodge),A>=D.Windup+D.Active+8); }
    // Jump: arc, the jump attack window, and landing at contact.
    FWardenFighterState J; TestTrue(TEXT("Jump starts"),J.Request(EWardenAction::Jump));
    TestEqual(TEXT("Jump peak height"),JumpLift(JumpTicks/2.f),JumpHeight);
    TestFalse(TEXT("A plain cut cannot start in the air"),J.Request(EWardenAction::Strike,CutOne));
    for(int32 A=0;A<JumpTicks;++A) { FWardenFighterState Probe=J; Probe.Age=A; TestEqual(FString::Printf(TEXT("Jump attack window at age %d"),A),Probe.Request(EWardenAction::Strike,JumpAttack),A>=JumpAttackOpen && A<=JumpAttackClose); }
    TestFalse(TEXT("Jump attack needs a jump"),FWardenFighterState().Request(EWardenAction::Strike,JumpAttack));
    // Stamina: ~7 rolls from full, 45 per second once regeneration starts.
    FWardenFighterState T; int32 Rolls=0;
    while(T.Request(EWardenAction::Dodge)) { ++Rolls; T.Age=RollChainOpen; }
    TestEqual(TEXT("Seven back-to-back rolls from full stamina"),Rolls,7);
    FWardenFighterState G; G.Stamina=10; for(int32 I=0;I<60;++I) G.Advance();
    TestTrue(TEXT("45 stamina per second"),FMath::IsNearlyEqual(G.Stamina,55.f,.1f));
    // In the world: the jump really lifts the capsule; the jump attack lands at contact.
    auto* W=NewWorld(); auto* M=Arena(W,false); AWardenChallenger* P=M->Player;
    const float Ground=P->GetActorLocation().Z; float Peak=0;
    P->BeginAction(EWardenAction::Jump,0,FVector::ForwardVector);
    for(int32 A=0;A<12;++A) { P->StepFighter(FVector::ZeroVector); P->Fight.Advance(); Peak=FMath::Max(Peak,float(P->GetActorLocation().Z-Ground)); }
    TestTrue(TEXT("Jump attack accepted mid-air"),P->BeginAction(EWardenAction::Strike,JumpAttack,FVector::ForwardVector));
    float AtContact=-1;
    for(int32 A=0;A<Strike(JumpAttack,false).Total();++A) { P->StepFighter(FVector::ZeroVector); if(P->Fight.Age==Strike(JumpAttack,false).Windup) AtContact=P->GetActorLocation().Z-Ground; P->Fight.Advance(); }
    AddInfo(FString::Printf(TEXT("Jump rose %.1f cm in 12 ticks; jump attack height at contact %.2f cm"),Peak,AtContact));
    TestTrue(TEXT("Jump lifts the capsule"),Peak>40);
    TestTrue(TEXT("Jump attack lands at contact"),FMath::Abs(AtContact)<1);
    TestTrue(TEXT("Back on the floor"),FMath::IsNearlyEqual(float(P->GetActorLocation().Z),Ground,.01f));
    // Hit-stop freezes the fight clock for its ticks.
    const int32 Tick=M->CombatTick; M->Impact(4,0); M->RehearsalWait=100000;
    for(int32 I=0;I<4;++I) M->FixedStep();
    TestEqual(TEXT("Hit-stop holds the fight clock"),M->CombatTick,Tick);
    M->FixedStep(); TestEqual(TEXT("Clock resumes after hit-stop"),M->CombatTick,Tick+1);
    CloseWorld(W); return true;
}
namespace {
// A reasonable player, written against engine state (test-only): rolls sideways just
// before contact or a skull's arrival, sidesteps hazards, punishes recovery with two
// cuts, heals when low and safe. Returns the fight outcome.
struct FBotResult { bool Won=false; float PlayerHealth=0, BossHealth=0, Seconds=0; int32 Rolls=0, Cuts=0, Heals=0; };
FBotResult Fight(bool Regent,int32 Seed)
{
    using namespace WardenRules;
    auto* W=NewWorld(); auto* M=Arena(W,Regent);
    M->Player->SetLocked(true);
    FBotResult R; int32 LastInstance=-1, Rolled=-1, Chain=0;
    FRandomStream Random(Seed);
    M->TestPilot=[&](AWardenArenaMode& Mode,FVector& Intent)
    {
        AWardenChallenger* P=Mode.Player; AWardenChallenger* B=Mode.Warden; const auto& F=P->Fight; const auto& E=B->Fight;
        const FVector To=(B->GetActorLocation()-P->GetActorLocation()).GetSafeNormal2D();
        const FVector Side=FVector(-To.Y,To.X,0)*(Random.FRand()<.5f?1.f:-1.f);
        const float Distance=FVector::Dist2D(B->GetActorLocation(),P->GetActorLocation());
        Intent=FVector::ZeroVector;
        if(!F.Alive()) return;
        bool Threat=false;
        if(E.Action==EWardenAction::Strike && E.Health>=0)
        {
            const auto& D=E.Definition();
            const int32 Contact=D.Windup;
            // Rite: one roll per contact window.
            const int32 Next=Regent && E.Move==WardenRegent::Rite ? (E.Age<=Contact ? Contact : E.Age<=Contact+20 ? Contact+20 : Contact+56) : Contact;
            Threat=D.Damage>0 && E.Age>=Next-6 && E.Age<=Next-3 && Distance<(Regent && E.Move==WardenRegent::Pyre ? 520.f : Regent && E.Move==WardenRegent::Dash ? 900.f : 450.f) && Rolled!=E.AttackInstance*100+Next;
            if(Threat) Rolled=E.AttackInstance*100+Next;
        }
        for(const auto& K:Mode.Regent.Flying) Threat|=FVector::Dist(K.Position,P->GetActorLocation())<170 && F.Ready();
        for(const auto& H:Mode.Regent.Hazards)
            if(H.Kind!=ERegentHazard::Mark && FVector::Dist2D(H.Center,P->GetActorLocation())<H.Radius+40 && (H.Kind==ERegentHazard::Pool || H.Arm-Mode.CombatTick<8))
                Intent=(P->GetActorLocation()-H.Center).GetSafeNormal2D();
        if(Threat && F.Stamina>=DodgeCost) { P->PendingAction=EWardenAction::Dodge; P->PendingDirection=Side; ++R.Rolls; return; }
        const bool Opening=E.Action==EWardenAction::Hurt || E.Action==EWardenAction::Ready ? Distance<260 :
            E.Action==EWardenAction::Strike && E.Age>=E.Definition().Windup+E.Definition().Active+4 && E.Age<E.Definition().Total()-14;
        if(F.Health<45 && F.Heals>0 && F.Ready() && (Distance>500 || (E.Action==EWardenAction::Strike && E.Age>E.Definition().Windup+E.Definition().Active))) { P->PendingAction=EWardenAction::Heal; ++R.Heals; return; }
        if(Intent.IsNearlyZero()) Intent=Distance>210 ? To : Distance<140 ? -To*.6f : FVector::ZeroVector;
        if(Opening && Distance<250 && F.Stamina>=30 && (F.Ready() || (F.Action==EWardenAction::Strike && Chain<2)))
        {
            if(F.Ready()) Chain=0;
            if(P->PendingAction==EWardenAction::Ready) { P->PendingAction=EWardenAction::Strike; ++Chain; ++R.Cuts; }
        }
    };
    for(int32 I=0;I<60*240 && M->Player->Fight.Alive() && M->Warden->Fight.Alive();++I) M->FixedStep();
    R.Won=!M->Warden->Fight.Alive(); R.PlayerHealth=M->Player->Fight.Health; R.BossHealth=M->Warden->Fight.Health; R.Seconds=M->CombatTick/60.f;
    M->TestPilot=nullptr; CloseWorld(W);
    return R;
}
}
CONTROLS_TEST(FWardenBeatableTest,"BossLab.Controls.ReactiveBotCanWin");
bool FWardenBeatableTest::RunTest(const FString&)
{
    // Evidence for "can't beat the boss": a disciplined bot should win most fights, and a
    // fight should take long enough to be a fight. Reported, with a minimum bar.
    for(const bool Regent:{false,true})
    {
        int32 Wins=0; float Time=0;
        for(int32 Seed=1;Seed<=6;++Seed)
        {
            const FBotResult R=Fight(Regent,Seed);
            Wins+=R.Won; Time+=R.Seconds;
            AddInfo(FString::Printf(TEXT("%s seed %d: %s in %.0fs, player %.0f hp, boss %.0f hp, rolls %d, cuts %d, heals %d"),Regent?TEXT("Regent"):TEXT("Warden"),Seed,R.Won?TEXT("WIN"):TEXT("loss"),R.Seconds,R.PlayerHealth,R.BossHealth,R.Rolls,R.Cuts,R.Heals));
        }
        AddInfo(FString::Printf(TEXT("%s: bot won %d of 6, mean %.0fs"),Regent?TEXT("Regent"):TEXT("Warden"),Wins,Time/6));
        TestTrue(FString::Printf(TEXT("%s is beatable by disciplined play"),Regent?TEXT("Regent"):TEXT("Warden")),Wins>=3);
    }
    return true;
}
#endif
