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
#if WITH_DEV_AUTOMATION_TESTS
CONTROLS_TEST(FWardenMoveDuringActionsTest,"BossLab.Controls.MovementDuringActions");
bool FWardenMoveDuringActionsTest::RunTest(const FString&)
{
    using namespace WardenRules;
    auto* W=NewWorld(); auto* M=Arena(W,false); AWardenChallenger* P=M->Player;
    M->Warden->SetActorLocation(FVector(3000,3000,128));
    auto Fresh=[&] { P->SetActorLocation(FVector(0,0,95)); P->SetActorRotation(FRotator::ZeroRotator); P->ResetFighter(false); P->SetLocked(false); };
    // Walk out of late recovery, not before.
    Fresh(); P->BeginAction(EWardenAction::Strike,CutOne,FVector::ForwardVector);
    const auto& D=Strike(CutOne,false);
    for(int32 T=0;T<D.Windup+D.Active+MoveCancelAfterContact-1;++T) { P->StepFighter(FVector::RightVector); P->Fight.Advance(); }
    TestEqual(TEXT("Stick input cannot end the swing early"),int32(P->Fight.Action),int32(EWardenAction::Strike));
    P->Fight.Advance(); P->StepFighter(FVector::RightVector);
    TestEqual(TEXT("Stick input walks out of late recovery"),int32(P->Fight.Action),int32(EWardenAction::Ready));
    // Momentum: a cut from a full run travels further than from standing.
    Fresh(); P->BeginAction(EWardenAction::Strike,CutOne,FVector::ForwardVector);
    for(int32 T=0;T<D.Windup+D.Active;++T) { P->StepFighter(FVector::ZeroVector); P->Fight.Advance(); }
    const float Standing=P->GetActorLocation().X;
    Fresh(); for(int32 T=0;T<30;++T) { P->StepFighter(FVector::ForwardVector); P->Fight.Advance(); }
    const float RunStart=P->GetActorLocation().X; P->BeginAction(EWardenAction::Strike,CutOne,FVector::ForwardVector);
    for(int32 T=0;T<D.Windup+D.Active;++T) { P->StepFighter(FVector::ZeroVector); P->Fight.Advance(); }
    const float Running=P->GetActorLocation().X-RunStart;
    AddInfo(FString::Printf(TEXT("Cut I travel: %.1f cm standing, %.1f cm from a run"),Standing,Running));
    TestTrue(TEXT("Run momentum carries into the cut"),Running>Standing+12);
    // Steering: during the wind-up the swing turns to the stick; it locks before contact.
    Fresh(); P->BeginAction(EWardenAction::Strike,CutOne,FVector::ForwardVector);
    for(int32 T=0;T<D.Windup;++T) { P->StepFighter(FVector::RightVector); P->Fight.Advance(); }
    const float Steered=P->CommittedDirection.Rotation().Yaw;
    AddInfo(FString::Printf(TEXT("Wind-up steering turned the cut %.0f degrees"),Steered));
    TestTrue(TEXT("Wind-up steering turns the cut toward the stick"),Steered>45);
    // Drinking: walks slowly, heal still lands at the commit tick.
    Fresh(); P->Fight.Health=40; P->BeginAction(EWardenAction::Heal,0,FVector::ZeroVector);
    for(int32 T=0;T<HealCommit+1;++T) { P->StepFighter(FVector::ForwardVector); P->Fight.Advance(); }
    AddInfo(FString::Printf(TEXT("Walked %.1f cm while drinking, health %.0f"),P->GetActorLocation().X,P->Fight.Health));
    TestTrue(TEXT("Walks while drinking"),P->GetActorLocation().X>150);
    TestTrue(TEXT("Drinking walk is slower than walking"),P->MoveVelocity.Size()<=HealWalkSpeed+.1f);
    TestEqual(TEXT("Heal still lands at the commit tick"),P->Fight.Health,85.f);
    // Jump: higher, with some air control.
    Fresh(); P->BeginAction(EWardenAction::Jump,0,FVector::ZeroVector); float Peak=0;
    for(int32 T=0;T<JumpTicks;++T) { P->StepFighter(FVector::RightVector); P->Fight.Advance(); Peak=FMath::Max(Peak,float(P->GetActorLocation().Z-95)); }
    AddInfo(FString::Printf(TEXT("Standing jump peak %.0f cm, air control drift %.0f cm"),Peak,P->GetActorLocation().Y));
    TestTrue(TEXT("Jump reaches 1.2 m"),Peak>=120);
    TestTrue(TEXT("Air control nudges a standing jump, but only nudges"),P->GetActorLocation().Y>20 && P->GetActorLocation().Y<100);
    CloseWorld(W); return true;
}
#endif
#if WITH_DEV_AUTOMATION_TESTS
CONTROLS_TEST(FWardenRunningJumpAttackTest,"BossLab.Controls.RunningJumpAttackAndHitFeedback");
bool FWardenRunningJumpAttackTest::RunTest(const FString&)
{
    using namespace WardenRules;
    auto* W=NewWorld(); auto* M=Arena(W,false); AWardenChallenger* P=M->Player; AWardenChallenger* B=M->Warden;
    M->RehearsalWait=1000000;
    // Sprint, then press jump and attack on consecutive frames: the attack must follow
    // the jump as a jump attack, not overwrite it as a running cut.
    B->SetActorLocation(FVector(1200,0,128));
    P->SetActorLocation(FVector(-400,0,95)); P->SetActorRotation(FRotator::ZeroRotator);
    for(int32 T=0;T<40;++T) { P->StepFighter(FVector::ForwardVector,true); P->Fight.Advance(); }
    const float RunSpeed=P->MoveVelocity.Size();
    P->QueueAction(EWardenAction::Jump); P->QueueAction(EWardenAction::Strike);
    const float TakeOff=P->GetActorLocation().X; bool SawJumpAttack=false;
    for(int32 T=0;T<60;++T) { M->FixedStep(); SawJumpAttack|=P->Fight.Action==EWardenAction::Strike && P->Fight.Move==JumpAttack; }
    AddInfo(FString::Printf(TEXT("Running jump attack from %.0f cm/s carried %.0f cm"),RunSpeed,P->GetActorLocation().X-TakeOff));
    TestTrue(TEXT("Sprint, jump, attack becomes a jump attack"),SawJumpAttack);
    TestTrue(TEXT("A running jump attack carries the run"),P->GetActorLocation().X-TakeOff>250);
    // The flask costs no stamina.
    P->ResetFighter(false); P->Fight.Health=40; P->Fight.Stamina=0;
    TestTrue(TEXT("Flask works at zero stamina"),P->BeginAction(EWardenAction::Heal,0,FVector::ZeroVector));
    TestEqual(TEXT("Flask costs no stamina"),P->Fight.Stamina,0.f);
    // A landed blow records recoil direction and a blood burst at the contact point.
    P->SetActorLocation(FVector(0,0,95)); P->SetActorRotation(FRotator::ZeroRotator); P->ResetFighter(false);
    B->SetActorLocation(FVector(170,0,128)); B->ResetFighter(true);
    const int32 Bled=B->BleedCount;
    P->BeginAction(EWardenAction::Strike,CutOne,FVector::ForwardVector);
    for(int32 T=0;T<Strike(CutOne,false).Total();++T) { P->StepFighter(FVector::ZeroVector); P->ResolveStrike(B,false); P->Fight.Advance(); }
    TestEqual(TEXT("One blood burst per landed blow"),B->BleedCount,Bled+1);
    TestTrue(TEXT("Recoil pushes the boss away from the attacker"),B->ImpactDir.X>.9f);
    TestTrue(TEXT("Blood starts at the boss, not the origin"),FVector::Dist2D(B->BleedAt,B->GetActorLocation())<120);
    CloseWorld(W); return true;
}
#endif
