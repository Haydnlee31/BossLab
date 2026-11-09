#include "WardenPrototype.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/BoxComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/PlayerController.h"
#include "Animation/BlendSpace.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "GameFramework/InputSettings.h"
#include "GameFramework/PlayerInput.h"
#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#define FUNDAMENTAL_TEST(Type,Name) IMPLEMENT_SIMPLE_AUTOMATION_TEST(Type,Name,(EAutomationTestFlags::EditorContext|EAutomationTestFlags::ClientContext)|EAutomationTestFlags::EngineFilter)
namespace {
UWorld* NewWorld() { auto* W=UWorld::CreateWorld(EWorldType::Game,false); GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W); return W; }
void CloseWorld(UWorld* W) { GEngine->DestroyWorldContext(W); W->DestroyWorld(false); }
AWardenChallenger* Fighter(UWorld* W,FVector P,bool Boss=false) { auto* A=W->SpawnActor<AWardenChallenger>(P,FRotator::ZeroRotator); A->DispatchBeginPlay(); A->ResetFighter(Boss); return A; }
AWardenArenaMode* Arena(UWorld* W) { auto* M=W->SpawnActor<AWardenArenaMode>(); M->Player=Fighter(W,FVector(-450,0,95)); M->DispatchBeginPlay(); M->Warden->DispatchBeginPlay(); M->ConfigureEncounter(303,true,1); return M; }
}
FUNDAMENTAL_TEST(FWardenInputTest,"BossLab.Fundamentals.ControlsAndDebugConflict");
bool FWardenInputTest::RunTest(const FString&)
{
    bool Tab=false,Space=false,InspectorTab=false,Shift=false,Escape=false,Quit=false;
    for(const auto& B:GetDefault<UInputSettings>()->GetActionMappings())
    { if(B.ActionName==TEXT("Sprint") && B.Key==EKeys::LeftShift) Shift=true; if(B.ActionName==TEXT("Pause") && B.Key==EKeys::Escape) Escape=true; if(B.ActionName==TEXT("QuitMenu") && B.Key==EKeys::Q) Quit=true; if(B.ActionName==TEXT("Lock") && B.Key==EKeys::Tab) Tab=true; if(B.ActionName==TEXT("Dodge") && B.Key==EKeys::SpaceBar) Space=true; if(B.ActionName==TEXT("Inspector") && B.Key==EKeys::Tab) InspectorTab=true; }
    TestTrue(TEXT("Tab owns targeting"),Tab && !InspectorTab); TestTrue(TEXT("Space owns roll"),Space);
    TestTrue(TEXT("Sprint and menu exit keys are mapped"),Shift && Escape && Quit);
    for(const auto& B:GetDefault<UPlayerInput>()->DebugExecBindings)
        TestFalse(TEXT("Game keys do not change engine debug view"),B.Key==EKeys::F1||B.Key==EKeys::F2||B.Key==EKeys::F3||B.Key==EKeys::F4||B.Key==EKeys::F5||B.Key==EKeys::F9);
    return true;
}
FUNDAMENTAL_TEST(FWardenSprintTest,"BossLab.Fundamentals.SprintTravelStaminaAndCommitment");
bool FWardenSprintTest::RunTest(const FString&)
{
    auto* W=NewWorld(); auto* P=Fighter(W,FVector(0,0,95));
    for(int32 I=0;I<60;++I) { P->StepFighter(FVector::ForwardVector); P->Fight.Advance(); }
    const float Walk=P->GetActorLocation().X;
    P->SetActorLocation(FVector(0,0,95)); P->ResetFighter(false);
    for(int32 I=0;I<60;++I) { P->StepFighter(FVector::ForwardVector,true); P->Fight.Advance(); }
    const float Sprint=P->GetActorLocation().X;
    TestTrue(TEXT("Sprint is substantially faster with the same acceleration"),Sprint>Walk*1.3f);
    TestTrue(TEXT("Sprint reaches sprint speed"),FMath::IsNearlyEqual(float(P->MoveVelocity.Size()),WardenRules::SprintSpeed,.1f));
    TestTrue(TEXT("One moving second costs12 stamina without regen"),FMath::IsNearlyEqual(P->Fight.Stamina,88.f,.01f));
    for(int32 I=0;I<11;++I) { P->StepFighter(FVector::ZeroVector,true); P->Fight.Advance(); }
    TestTrue(TEXT("Stationary Shift spends no stamina and brakes"),FMath::IsNearlyEqual(P->Fight.Stamina,88.f,.01f) && P->MoveVelocity.IsNearlyZero());
    P->StepFighter(FVector::ForwardVector,true);
    TestTrue(TEXT("Roll can start from sprint"),P->BeginAction(EWardenAction::Dodge,0,FVector::RightVector));
    const float RollStamina=P->Fight.Stamina;
    for(int32 I=0;I<WardenRules::RollMoveCancel;++I) { P->StepFighter(FVector::ForwardVector,true); TestFalse(TEXT("Sprint cannot override roll commitment"),P->Fight.Sprinting); P->Fight.Advance(); }
    TestTrue(TEXT("Shift does not drain stamina during roll"),FMath::IsNearlyEqual(P->Fight.Stamina,RollStamina,.01f));
    FWardenFighterState S;
    for(int32 I=0;I<600;++I) { S.UpdateSprint(true,true); S.Advance(); }
    TestTrue(TEXT("Exhaustion stops sprint and holds until key release"),S.SprintExhausted && !S.Sprinting && S.Stamina>=0);
    S.UpdateSprint(false,true); S.Stamina=50; S.UpdateSprint(true,true);
    TestTrue(TEXT("Release and repress permits recovered sprint"),S.Sprinting);
    S.Damage(100); S.UpdateSprint(true,true); TestFalse(TEXT("Dead fighter cannot sprint"),S.Sprinting);
    AddInfo(FString::Printf(TEXT("One second: walk %.3fcm, sprint %.3fcm; normal fixed-step costs"),Walk,Sprint));
    CloseWorld(W); return true;
}
FUNDAMENTAL_TEST(FWardenPauseMenuTest,"BossLab.Fundamentals.PauseMenuFreezeAndInputReset");
bool FWardenPauseMenuTest::RunTest(const FString&)
{
    auto* W=NewWorld(); auto* M=Arena(W); auto* PC=W->SpawnActor<APlayerController>(); PC->Possess(M->Player);
    M->Player->SprintHeld=true; M->Player->PendingAction=EWardenAction::Strike; M->Player->PendingDirection=FVector::ForwardVector;
    M->SetMenuOpen(true); const int32 Tick=M->CombatTick; const float Stamina=M->Player->Fight.Stamina;
    for(int32 I=0;I<120;++I) M->Tick(1.f/60);
    TestEqual(TEXT("Menu freezes combat clock"),M->CombatTick,Tick);
    TestEqual(TEXT("Menu freezes resources"),M->Player->Fight.Stamina,Stamina);
    TestTrue(TEXT("Menu exposes cursor and clicks"),PC->bShowMouseCursor && PC->bEnableClickEvents);
    TestTrue(TEXT("Menu clears held sprint and queued actions"),!M->Player->SprintHeld && M->Player->PendingAction==EWardenAction::Ready);
    M->SetMenuOpen(false);
    TestFalse(TEXT("Resume recaptures cursor"),PC->bShowMouseCursor || PC->bEnableClickEvents);
    M->Tick(1.f/60); TestEqual(TEXT("Resume advances without pause catch-up"),M->CombatTick,Tick+1);
    M->SetMenuOpen(true); M->ResetEncounter(); TestFalse(TEXT("Restart closes menu"),M->bPaused || PC->bShowMouseCursor);
    CloseWorld(W); return true;
}
FUNDAMENTAL_TEST(FWardenSwordGripTest,"BossLab.Fundamentals.TwoHandGripAndAuthoredArc");
bool FWardenSwordGripTest::RunTest(const FString&)
{
    auto* W=NewWorld(); auto* P=Fighter(W,FVector(0,0,95)); float MaxError=0,MaxTravel=0,MinMidCutTravel=10000;
    // Every player move (cut chain, jump slam, rolling thrust, running cut) and the three
    // boss rehearsal swings, posed tick by tick from the guard.
    for(int32 Family=-WardenRules::PlayerMoveCount;Family<3;++Family)
    {
        P->ResetFighter(Family>=0); P->BeginAction(EWardenAction::Strike,0,FVector::ForwardVector);
        P->Fight.Move=Family>=0 ? Family : Family+WardenRules::PlayerMoveCount;
        FVector Prior=P->BladePoint(1);
        float MoveTravel=0; int32 PeakAge=0;
        for(int32 T=0;T<P->Fight.Definition().Total();++T)
        {
            P->Fight.Age=T; P->CombatPose(FVector::ZeroVector); MaxError=FMath::Max(MaxError,P->GripError);
            const FVector Tip=P->BladePoint(1); TestFalse(TEXT("Finite authored blade transform"),Tip.ContainsNaN());
            const float Distance=FVector::Distance(Tip,Prior);
            MaxTravel=FMath::Max(MaxTravel,Distance);
            if(Distance>MoveTravel) { MoveTravel=Distance; PeakAge=T; }
            const auto& D=P->Fight.Definition();
            if(T>=D.Windup+D.Active*.4f && T<=D.Windup+D.Active*.6f)
                MinMidCutTravel=FMath::Min(MinMidCutTravel,Distance);
            Prior=Tip;
        }
        AddInfo(FString::Printf(TEXT("%s %s: peak tip travel %.1f cm/tick at age %d (windup %d)"),Family>=0?TEXT("Boss"):TEXT("Player"),P->Fight.Definition().Name,MoveTravel,PeakAge,P->Fight.Definition().Windup));
    }
    AddInfo(FString::Printf(TEXT("All sword poses: max grip error %.3f cm; max per-tick tip travel %.3f cm"),MaxError,MaxTravel));
    AddInfo(FString::Printf(TEXT("Minimum middle-of-cut blade travel %.3f cm/tick"),MinMidCutTravel));
    TestTrue(TEXT("Blade carries through the middle of the cut without stopping"),MinMidCutTravel>4.f);
    TestTrue(TEXT("Both palms stay on the two-handed hilt"),MaxError<3.f);
    TestTrue(TEXT("Swing has motion without a teleport"),MaxTravel>5 && MaxTravel<90);
    CloseWorld(W); return true;
}
FUNDAMENTAL_TEST(FWardenBladeTest,"BossLab.Fundamentals.ActualBladeContactAndWallOcclusion");
bool FWardenBladeTest::RunTest(const FString&)
{
    auto* W=NewWorld(); auto* P=Fighter(W,FVector(0,0,95)); auto* B=Fighter(W,FVector(170,0,95),true);
    P->BeginAction(EWardenAction::Strike,0,FVector::ForwardVector);
    int32 Hits=0;
    for(int32 T=0;T<WardenRules::Strike(0,false).Total();++T) { P->StepFighter(FVector::ZeroVector); if(P->ResolveStrike(B,false)) ++Hits; P->Fight.Advance(); }
    TestEqual(TEXT("Visible blade connects once per committed swing"),Hits,1);
    TestEqual(TEXT("Authored blade damage only once"),B->Fight.Health,240.f-WardenRules::Strike(0,false).Damage);
    P->SetActorLocation(FVector(0,0,95)); P->ResetFighter(false); B->ResetFighter(true);
    auto* Wall=W->SpawnActor<AActor>(); auto* Box=NewObject<UBoxComponent>(Wall); Wall->SetRootComponent(Box);
    Box->SetBoxExtent(FVector(15,250,220)); Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly); Box->SetCollisionResponseToAllChannels(ECR_Block); Box->RegisterComponent(); Wall->SetActorLocation(FVector(90,0,100));
    P->BeginAction(EWardenAction::Strike,0,FVector::ForwardVector);
    for(int32 T=0;T<WardenRules::Strike(0,false).Total();++T) { P->StepFighter(FVector::ZeroVector); P->ResolveStrike(B,false); P->Fight.Advance(); }
    TestEqual(TEXT("Wall blocks a blade reaching the fighter behind it"),B->Fight.Health,240.f);
    CloseWorld(W); return true;
}
FUNDAMENTAL_TEST(FWardenRollTest,"BossLab.Fundamentals.RollCommitmentTravelAndProtection");
bool FWardenRollTest::RunTest(const FString&)
{
    auto* W=NewWorld(); auto* P=Fighter(W,FVector(0,0,95)); P->BeginAction(EWardenAction::Dodge,0,FVector::RightVector);
    int32 Protected=0; float MaxError=0;
    for(int32 T=0;T<WardenRules::DodgeTicks;++T)
    {
        if(P->Fight.Invulnerable()) ++Protected;
        // A plain cut never cancels a roll; only the rolling thrust, and only after the
        // protected frames (checked on a copy so this roll continues).
        TestFalse(TEXT("Greatsword cannot cancel the roll"),P->BeginAction(EWardenAction::Strike));
        FWardenFighterState Probe=P->Fight; Probe.Stamina=100;
        TestEqual(TEXT("Rolling thrust opens only after protection"),Probe.Request(EWardenAction::Strike,WardenRules::RollAttack),T>=WardenRules::RollAttackOpen);
        // No stick input: the roll runs its full course (input would walk out from age 34).
        P->StepFighter(FVector::ZeroVector); MaxError=FMath::Max(MaxError,P->GripError); P->Fight.Advance();
    }
    TestEqual(TEXT("Twenty-six fixed protection ticks"),Protected,WardenRules::DodgeInvulnerableEnd-WardenRules::DodgeInvulnerableStart);
    TestTrue(TEXT("Roll travels 320 cm along its committed direction"),P->GetActorLocation().Equals(FVector(0,320,95),.1));
    AddInfo(FString::Printf(TEXT("Roll max grip error %.3f cm"),MaxError));
    TestTrue(TEXT("Roll maintains finite grip"),FMath::IsFinite(MaxError) && MaxError<3);
    TestFalse(TEXT("Recovery gap remains committed"),P->Fight.Ready());
    TestTrue(TEXT("Directional roll returns to facing without a yaw snap"),P->VisualBody->GetRelativeRotation().Quaternion().Equals(FRotator(0,-90,0).Quaternion(),.001));
    // Later stick input cannot steer the roll; it can only walk out after age 34.
    P->SetActorLocation(FVector(0,0,95)); P->ResetFighter(false); P->BeginAction(EWardenAction::Dodge,0,FVector::RightVector);
    for(int32 T=0;T<WardenRules::RollMoveCancel;++T) { P->StepFighter(FVector::ForwardVector); P->Fight.Advance(); }
    TestTrue(TEXT("Stick input does not steer the committed roll"),FMath::Abs(P->GetActorLocation().X)<.1f);
    TestEqual(TEXT("Still rolling until the move-cancel age"),int32(P->Fight.Action),int32(EWardenAction::Dodge));
    P->StepFighter(FVector::ForwardVector);
    TestEqual(TEXT("Stick input walks out of the roll's end"),int32(P->Fight.Action),int32(EWardenAction::Ready));
    CloseWorld(W); return true;
}
FUNDAMENTAL_TEST(FWardenRollContinuityTest,"BossLab.Fundamentals.DirectionalRollPoseContinuity");
bool FWardenRollContinuityTest::RunTest(const FString&)
{
    auto* W=NewWorld(); auto* P=Fighter(W,FVector(0,0,95));
    const FName Bones[]={TEXT("pelvis"),TEXT("head"),TEXT("foot_l"),TEXT("foot_r")};
    float MaxStep=0,MaxExit=0,LowestHead=10000,LowestBlade=10000;
    for(int32 DirectionIndex=0;DirectionIndex<8;++DirectionIndex)
    {
        const FVector Direction=FRotator(0,DirectionIndex*45.f,0).Vector();
        P->SetActorLocation(FVector(0,0,95)); P->SetActorRotation(FRotator(0,DirectionIndex%2?37.f:0.f,0)); P->ResetFighter(false);
        FVector Prior[4];
        for(int32 I=0;I<4;++I) Prior[I]=P->VisualBody->GetBoneLocationByName(Bones[I],EBoneSpaces::WorldSpace);
        P->BeginAction(EWardenAction::Dodge,0,Direction);
        for(int32 T=0;T<WardenRules::DodgeTicks;++T)
        {
            P->StepFighter(FVector::ZeroVector);
            for(int32 I=0;I<4;++I)
            {
                const FVector Point=P->VisualBody->GetBoneLocationByName(Bones[I],EBoneSpaces::WorldSpace);
                TestFalse(TEXT("Finite rolling joints"),Point.ContainsNaN());
                MaxStep=FMath::Max(MaxStep,FVector::Distance(Point,Prior[I])); Prior[I]=Point;
                if(I==1) LowestHead=FMath::Min(LowestHead,float(Point.Z));
            }
            for(int32 I=0;I<5;++I) LowestBlade=FMath::Min(LowestBlade,float(P->BladePoint(I/4.f).Z));
            P->Fight.Advance();
        }
        TestTrue(TEXT("Every normalized direction travels exactly 320 cm"),P->GetActorLocation().Equals(FVector(0,0,95)+Direction*320,.1));
        TestEqual(TEXT("Every direction pays the normal roll cost"),P->Fight.Stamina,100-WardenRules::DodgeCost);
        P->CombatPose(FVector::ZeroVector);
        for(int32 I=0;I<4;++I) MaxExit=FMath::Max(MaxExit,FVector::Distance(Prior[I],P->VisualBody->GetBoneLocationByName(Bones[I],EBoneSpaces::WorldSpace)));
    }
    AddInfo(FString::Printf(TEXT("Eight directions, varied facing: max joint step %.3f cm; exit %.3f cm; lowest head %.3f cm; lowest blade %.3f cm"),MaxStep,MaxExit,LowestHead,LowestBlade));
    TestTrue(TEXT("No tuck/untuck joint teleport"),MaxStep<45);
    TestTrue(TEXT("Landed pose joins guard without a pop"),MaxExit<8);
    TestTrue(TEXT("Rolling head has helmet clearance above the floor"),LowestHead>=19);
    TestTrue(TEXT("Rolling blade stays above the arena floor"),LowestBlade>=3);
    CloseWorld(W); return true;
}
FUNDAMENTAL_TEST(FWardenRollHitWindowTest,"BossLab.Fundamentals.RollInvulnerabilityActualBladeBoundary");
bool FWardenRollHitWindowTest::RunTest(const FString&)
{
    auto* W=NewWorld(); auto* Attacker=Fighter(W,FVector(0,0,95)); auto* Defender=Fighter(W,FVector(170,0,95),true);
    for(int32 Age:{WardenRules::DodgeInvulnerableStart-1,WardenRules::DodgeInvulnerableStart,WardenRules::DodgeInvulnerableEnd-1,WardenRules::DodgeInvulnerableEnd})
    {
        Attacker->SetActorLocation(FVector(0,0,95)); Attacker->ResetFighter(false);
        Defender->ResetFighter(true); Defender->BeginAction(EWardenAction::Dodge,0,FVector(1,1,0).GetSafeNormal());
        // Isolate damage gating at a held boundary age; leave the defender's
        // collision capsule in the strike path, so a miss cannot pass the test.
        Defender->Fight.Age=Age; Attacker->BeginAction(EWardenAction::Strike,0,FVector::ForwardVector);
        bool Dealt=false;
        for(int32 T=0;T<WardenRules::Strike(0,false).Total();++T)
        { Attacker->StepFighter(FVector::ZeroVector); Dealt|=Attacker->ResolveStrike(Defender,false); Attacker->Fight.Advance(); }
        const bool Protected=Age>=WardenRules::DodgeInvulnerableStart && Age<WardenRules::DodgeInvulnerableEnd;
        TestTrue(TEXT("Real blade sweep reaches the rolling defender"),Attacker->Fight.HitConsumed);
        TestEqual(TEXT("Only the protected interval rejects actual damage"),Dealt,!Protected);
        TestEqual(TEXT("Boundary health matches protection"),Defender->Fight.Health,Protected?240.f:240.f-WardenRules::Strike(0,false).Damage);
        AddInfo(FString::Printf(TEXT("Roll age %d: contact %d, damage %d, health %.0f"),Age,Attacker->Fight.HitConsumed,Dealt,Defender->Fight.Health));
    }
    CloseWorld(W); return true;
}
FUNDAMENTAL_TEST(FWardenEightWayRequestTest,"BossLab.Fundamentals.LockedAndUnlockedEightWayRollRequests");
bool FWardenEightWayRequestTest::RunTest(const FString&)
{
    auto* W=NewWorld(); auto* M=Arena(W); M->bRehearsal=false; M->bScriptedPlayer=false;
    for(int32 Locked=0;Locked<2;++Locked)
        for(int32 I=0;I<8;++I)
        {
            M->ResetEncounter(); M->Player->SetLocked(Locked!=0);
            TestEqual(TEXT("Requested lock state is actually established"),M->Player->IsLocked(),Locked!=0);
            const FVector Start=M->Player->GetActorLocation();
            const FVector Direction=FRotator(0,I*45.f,0).Vector();
            M->Player->PendingAction=EWardenAction::Dodge;
            M->Player->PendingDirection=Direction;
            for(int32 T=0;T<WardenRules::DodgeTicks;++T) M->FixedStep();
            TestTrue(TEXT("Queued roll follows chosen direction despite lock-on"),M->Player->GetActorLocation().Equals(Start+320*Direction,.1));
            TestEqual(TEXT("Queued directional roll pays once"),M->Player->Fight.Stamina,100-WardenRules::DodgeCost);
            TestEqual(TEXT("Queued directional roll completes"),int32(M->Player->Fight.Action),int32(EWardenAction::Ready));
        }
    AddInfo(TEXT("16 ordinary queued rolls: eight headings with lock on and off, each 320 cm and 14 stamina"));
    CloseWorld(W); return true;
}
FUNDAMENTAL_TEST(FWardenInputBufferTest,"BossLab.Fundamentals.BoundedInputBufferWithoutCancel");
bool FWardenInputBufferTest::RunTest(const FString&)
{
    auto* W=NewWorld(); auto* M=Arena(W); M->bRehearsal=false; M->bScriptedPlayer=false;
    M->Player->Fight.Gap=4; M->Player->PendingAction=EWardenAction::Dodge; M->Player->PendingDirection=FVector::RightVector;
    for(int32 I=0;I<5;++I) M->FixedStep();
    TestEqual(TEXT("Late roll input executes after recovery"),int32(M->Player->Fight.Action),int32(EWardenAction::Dodge));
    TestEqual(TEXT("Buffered request consumed once"),int32(M->Player->PendingAction),int32(EWardenAction::Ready));
    M->ResetEncounter(); M->Player->BeginAction(EWardenAction::Strike,0,FVector::ForwardVector); M->Player->PendingAction=EWardenAction::Dodge;
    for(int32 I=0;I<WardenRules::InputBufferTicks+2;++I) M->FixedStep();
    TestEqual(TEXT("Early roll cannot cancel sword"),int32(M->Player->Fight.Action),int32(EWardenAction::Strike));
    TestEqual(TEXT("Old buffered input expires after the buffer window"),int32(M->Player->PendingAction),int32(EWardenAction::Ready));
    for(int32 Remaining=0;Remaining<=4;++Remaining)
    {
        M->ResetEncounter(); M->Player->BeginAction(EWardenAction::Strike,0,FVector::ForwardVector);
        for(int32 T=0;T<WardenRules::Strike(0,false).Total()-Remaining;++T) M->Player->Fight.Advance();
        M->Player->PendingAction=EWardenAction::Dodge; M->Player->PendingDirection=FVector::RightVector;
        for(int32 T=0;T<Remaining+9;++T) M->FixedStep();
        TestEqual(TEXT("Last four recovery ticks and gap boundary retain dodge"),int32(M->Player->Fight.Action),int32(EWardenAction::Dodge));
        // Late recovery is roll-cancellable, so the buffered roll starts without regeneration.
        const float Paid=100-WardenRules::Strike(0,false).Cost-WardenRules::DodgeCost;
        TestTrue(TEXT("Buffered dodge costs once, after sword cost"),M->Player->Fight.Stamina>=Paid && M->Player->Fight.Stamina<Paid+8);
    }
    CloseWorld(W); return true;
}
FUNDAMENTAL_TEST(FWardenImpactTest,"BossLab.Fundamentals.HurtPoiseAndProtection");
bool FWardenImpactTest::RunTest(const FString&)
{
    FWardenFighterState P; P.Request(EWardenAction::Strike); P.Damage(24);
    TestEqual(TEXT("Player hit interrupts commitment with hurt"),int32(P.Action),int32(EWardenAction::Hurt));
    TestFalse(TEXT("Hurt cannot instantly roll cancel"),P.Request(EWardenAction::Dodge));
    for(int32 T=0;T<WardenRules::HurtTicks+WardenRules::RecoveryGap;++T) P.Advance();
    TestTrue(TEXT("Control returns after exact hurt recovery"),P.Ready());
    P.Request(EWardenAction::Dodge); P.Age=4;
    TestFalse(TEXT("Protected hit does not trigger hurt"),P.Damage(24));
    TestEqual(TEXT("Protected roll remains committed"),int32(P.Action),int32(EWardenAction::Dodge));
    FWardenFighterState B; B.IsBoss=true; B.Health=B.MaxHealth=240; B.Request(EWardenAction::Strike);
    B.Damage(32); B.Damage(32); B.Damage(32);
    TestEqual(TEXT("Three light hits leave armored boss attack intact"),int32(B.Action),int32(EWardenAction::Strike));
    B.Damage(32);
    TestEqual(TEXT("Fourth stance point breaks boss poise"),int32(B.Action),int32(EWardenAction::Hurt));
    TestFalse(TEXT("Broken attack cannot deal lingering damage"),B.Active());
    TestEqual(TEXT("Poise break does not change damage"),B.Health,112.f);
    for(int32 T=0;T<WardenRules::BossHurtTicks+WardenRules::RecoveryGap;++T) B.Advance();
    TestTrue(TEXT("Boss returns after explicit recovery"),B.Ready());
    B.Damage(1); for(int32 T=0;T<300;++T) B.Advance();
    TestEqual(TEXT("Poise restores after five seconds without damage"),B.Poise,WardenRules::BossPoise);
    FWardenFighterState Heavy; Heavy.IsBoss=true; Heavy.Health=Heavy.MaxHealth=240; Heavy.Request(EWardenAction::Strike);
    Heavy.Damage(46,true,2); Heavy.Damage(52,true,2);
    TestEqual(TEXT("Two heavy stance hits break the boss"),int32(Heavy.Action),int32(EWardenAction::Hurt));
    return true;
}
FUNDAMENTAL_TEST(FWardenMovementTest,"BossLab.Fundamentals.GroundedTravelAndAcceleration");
bool FWardenMovementTest::RunTest(const FString&)
{
    auto* W=NewWorld(); auto* P=Fighter(W,FVector(0,0,95));
    P->StepFighter(FVector::ForwardVector);
    TestTrue(TEXT("Walk accelerates rather than instant full speed"),P->MoveVelocity.X>0 && P->MoveVelocity.X<WardenRules::WalkSpeed);
    for(int32 I=0;I<12;++I) P->StepFighter(FVector::ForwardVector);
    TestEqual(TEXT("Walking reaches intended speed"),float(P->MoveVelocity.X),WardenRules::WalkSpeed);
    for(int32 I=0;I<7;++I) P->StepFighter(FVector::ZeroVector);
    TestTrue(TEXT("Walking brakes within seven ticks"),P->MoveVelocity.IsNearlyZero());
    float Previous=0,MaxChange=0;
    for(int32 I=0;I<WardenRules::DodgeTicks;++I)
    {
        const float Distance=WardenRules::DodgeDistance(I+1)-WardenRules::DodgeDistance(I);
        TestTrue(TEXT("Roll travel always forward"),Distance>=0);
        MaxChange=FMath::Max(MaxChange,FMath::Abs(Distance-Previous)); Previous=Distance;
    }
    TestTrue(TEXT("Last landing tick carries less than a centimetre"),Previous<1);
    TestTrue(TEXT("Roll has no old six-centimetre speed step"),MaxChange<3.2f);
    TestEqual(TEXT("Smooth roll preserves 320 cm"),WardenRules::DodgeDistance(WardenRules::DodgeTicks),320.f);
    P->Fight.Damage(999);
    for(int32 I=0;I<72;++I) P->StepFighter(FVector::ZeroVector);
    TestEqual(TEXT("Death presentation reaches settled state"),P->DeathAge,72.f);
    TestFalse(TEXT("Death pose is finite"),P->VisualBody->GetRelativeLocation().ContainsNaN());
    CloseWorld(W); return true;
}
FUNDAMENTAL_TEST(FWardenGaitTest,"BossLab.Fundamentals.ActualLocomotionStride");
bool FWardenGaitTest::RunTest(const FString&)
{
    auto* Asset=LoadObject<UBlendSpace>(nullptr,TEXT("/Game/Characters/Mannequins/Anims/Unarmed/BS_Idle_Walk_Run"));
    TestNotNull(TEXT("Installed directional locomotion asset"),Asset);
    if(!Asset) return false;
    AddInfo(FString::Printf(TEXT("Blend axes: %s [%.0f,%.0f], %s [%.0f,%.0f]"),*Asset->GetBlendParameter(0).DisplayName,Asset->GetBlendParameter(0).Min,Asset->GetBlendParameter(0).Max,*Asset->GetBlendParameter(1).DisplayName,Asset->GetBlendParameter(1).Min,Asset->GetBlendParameter(1).Max));
    auto* W=NewWorld(); auto* P=Fighter(W,FVector(0,0,95));
    float Low=10000,High=-10000;
    for(int32 I=0;I<90;++I)
    {
        P->StepFighter(FVector::ForwardVector);
        const FVector Foot=P->VisualBody->GetBoneLocationByName(TEXT("foot_l"),EBoneSpaces::ComponentSpace);
        if(I>15) { Low=FMath::Min(Low,float(Foot.Y)); High=FMath::Max(High,float(Foot.Y)); }
    }
    AddInfo(FString::Printf(TEXT("Actual forward gait foot excursion: %.3f cm"),High-Low));
    TestTrue(TEXT("Moving capsule produces a real stride, not frozen idle feet"),High-Low>20);
    CloseWorld(W); return true;
}
FUNDAMENTAL_TEST(FWardenStrikePlantTest,"BossLab.Fundamentals.MovingStrikeSupportFoot");
bool FWardenStrikePlantTest::RunTest(const FString&)
{
    auto* W=NewWorld(); auto* P=Fighter(W,FVector(0,0,95)); float MaxSlide=0,MaxLanding=0,MaxSkid=0;
    for(int32 Phase:{20,35,50,65})
    {
        P->SetActorLocation(FVector(0,0,95)); P->ResetFighter(false);
        const float StandingHeight=P->VisualBody->GetBoneLocationByName(TEXT("foot_r"),EBoneSpaces::WorldSpace).Z;
        for(int32 I=0;I<Phase;++I) P->StepFighter(FVector::ForwardVector);
        const FVector Start=P->VisualBody->GetBoneLocationByName(TEXT("foot_r"),EBoneSpaces::WorldSpace);
        FVector Anchor=Start; bool Settled=false;
        P->BeginAction(EWardenAction::Strike,0,FVector::ForwardVector);
        for(int32 I=0;I<30;++I)
        {
            P->StepFighter(FVector::ZeroVector);
            const FVector Foot=P->VisualBody->GetBoneLocationByName(TEXT("foot_r"),EBoneSpaces::WorldSpace);
            // Run momentum skids into the swing (by design); after the skid the support
            // foot must hold.
            if(!Settled && P->MoveVelocity.IsNearlyZero()) { Settled=true; Anchor=Foot; MaxSkid=FMath::Max(MaxSkid,float(FVector::Dist2D(Foot,Start))); }
            if(Settled) MaxSlide=FMath::Max(MaxSlide,float(FVector::Dist2D(Foot,Anchor)));
            if(I==29) MaxLanding=FMath::Max(MaxLanding,FMath::Abs(float(Foot.Z)-StandingHeight));
            P->Fight.Advance();
        }
    }
    AddInfo(FString::Printf(TEXT("Four moving entries: momentum skid up to %.1f cm, then support foot drift %.3f cm; height error versus standing ankle %.3f cm"),MaxSkid,MaxSlide,MaxLanding));
    TestTrue(TEXT("Run momentum carries into the swing"),MaxSkid>5);
    TestTrue(TEXT("Support foot does not skate during a moving-entry windup"),MaxSlide<3);
    TestTrue(TEXT("Raised walking foot settles to its standing ankle height"),MaxLanding<1.5f);
    CloseWorld(W); return true;
}
FUNDAMENTAL_TEST(FWardenCameraFrameTest,"BossLab.Fundamentals.CloseCameraFullBodyFraming");
bool FWardenCameraFrameTest::RunTest(const FString&)
{
    auto* W=NewWorld(); auto* P=Fighter(W,FVector(0,0,95)); auto* B=Fighter(W,FVector(170,0,128),true);
    B->SetActorScale3D(FVector(1.35)); B->CombatPose(FVector::ZeroVector);
    auto* PC=W->SpawnActor<APlayerController>(); PC->Possess(P); P->SetTarget(B); P->SetLocked(true);
    float MaxVertical=0,MinSeparation=10000;
    for(float Distance:{80.f,170.f,300.f})
    {
        B->SetActorLocation(FVector(Distance,0,128));
        for(int32 I=0;I<180;++I) { P->Tick(1.f/60); P->Arm->TickComponent(1.f/60,LEVELTICK_All,nullptr); }
        const auto View=P->Camera->GetComponentTransform();
        const float Tan=FMath::Tan(FMath::DegreesToRadians(P->Camera->FieldOfView*.5f));
        auto Screen=[&](FVector Point) { const FVector Q=View.InverseTransformPosition(Point); TestTrue(TEXT("Both fighters stay in front of camera"),Q.X>0); return FVector2D(Q.Y/(Q.X*Tan),Q.Z/(Q.X*Tan/(16.f/9))); };
        for(auto* F:{P,B}) for(const TCHAR* Bone:{TEXT("head"),TEXT("foot_l"),TEXT("foot_r")})
            MaxVertical=FMath::Max(MaxVertical,float(FMath::Abs(Screen(F->VisualBody->GetBoneLocationByName(Bone,EBoneSpaces::WorldSpace)).Y)));
        MinSeparation=FMath::Min(MinSeparation,float(FMath::Abs(Screen(P->GetActorLocation()).X-Screen(B->GetActorLocation()).X)*640));
    }
    AddInfo(FString::Printf(TEXT("Close camera: max vertical NDC %.3f; minimum center separation %.3f px at720p"),MaxVertical,MinSeparation));
    TestTrue(TEXT("Heads and feet retain a screen margin at close range"),MaxVertical<.9f);
    TestTrue(TEXT("Contact view avoids direct silhouette stacking"),MinSeparation>30);
    const float OpenDistance=FVector::Dist(P->Camera->GetComponentLocation(),P->GetActorLocation());
    auto* Wall=W->SpawnActor<AActor>(); auto* Box=NewObject<UBoxComponent>(Wall); Wall->SetRootComponent(Box);
    Box->SetBoxExtent(FVector(15,1000,1000)); Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Box->SetCollisionResponseToAllChannels(ECR_Block); Box->RegisterComponent();
    Wall->SetActorLocation((P->Camera->GetComponentLocation()+P->GetActorLocation())*.5f);
    P->Arm->TickComponent(1.f/60,LEVELTICK_All,nullptr);
    TestTrue(TEXT("Solid arena walls still retract the camera"),FVector::Dist(P->Camera->GetComponentLocation(),P->GetActorLocation())<OpenDistance*.8f);
    Wall->Destroy();
    P->SetLocked(false); for(int32 I=0;I<180;++I) P->Tick(1.f/60);
    TestTrue(TEXT("Unlocked camera restores accepted baseline arm"),FMath::IsNearlyEqual(P->Arm->TargetArmLength,500.f,.1f));
    TestTrue(TEXT("Unlocked camera restores accepted shoulder"),P->Arm->SocketOffset.Equals(FVector(0,45,100),.1f));
    CloseWorld(W); return true;
}
FUNDAMENTAL_TEST(FWardenSwordRulesTest,"BossLab.Fundamentals.CostsRecoveryHealingAndDeath");
bool FWardenSwordRulesTest::RunTest(const FString&)
{
    FWardenFighterState S; TestTrue(TEXT("Sword starts"),S.Request(EWardenAction::Strike)); TestEqual(TEXT("Cost once"),S.Stamina,100-WardenRules::Strike(0,false).Cost);
    TestFalse(TEXT("Roll does not cancel sword windup"),S.Request(EWardenAction::Dodge));
    int32 Active=0; for(int32 I=0;I<WardenRules::Strike(0,false).Total();++I) { if(S.Active()) ++Active; S.Advance(); }
    TestEqual(TEXT("Blade contact lasts the cut's active window"),Active,WardenRules::Strike(0,false).Active);
    for(int32 I=0;I<8;++I) S.Advance(); S.Health=40;
    TestTrue(TEXT("Heal starts"),S.Request(EWardenAction::Heal)); TestEqual(TEXT("Charge spent on commitment"),S.Heals,2);
    S.Damage(100); for(int32 I=0;I<90;++I) S.Advance(); TestEqual(TEXT("Lethal damage cannot heal-resurrect"),S.Health,0.f);
    return true;
}
FUNDAMENTAL_TEST(FWardenRehearsalTest,"BossLab.Fundamentals.FixedRehearsalAndFramePartition");
bool FWardenRehearsalTest::RunTest(const FString&)
{
    auto* WA=NewWorld(); auto* WB=NewWorld(); auto* A=Arena(WA); auto* B=Arena(WB);
    for(int32 I=0;I<1200;++I) A->Tick(1.f/60.f);
    for(int32 I=0;I<600;++I) B->Tick(1.f/30.f);
    TestTrue(TEXT("Actual sword combat occurred"),A->PlayerDamage+A->BossDamage>0);
    TestEqual(TEXT("Same fixed tick count"),A->CombatTick,B->CombatTick);
    TestEqual(TEXT("Same player health"),A->Player->Fight.Health,B->Player->Fight.Health); TestEqual(TEXT("Same boss health"),A->Warden->Fight.Health,B->Warden->Fight.Health);
    TestTrue(TEXT("Same player transform"),A->Player->GetActorLocation().Equals(B->Player->GetActorLocation(),.01));
    for(int32 I=0;I<3;++I) TestEqual(TEXT("Fixed move order agrees"),A->MoveCounts[I],B->MoveCounts[I]);
    TestEqual(TEXT("Opponent statistics inactive in fundamentals"),A->Statistics.Pooled.Samples,0);
    A->bRehearsal=false; A->ResetEncounter(); A->bScriptedPlayer=false;
    for(int32 I=0;I<600;++I) A->FixedStep(); TestEqual(TEXT("Dummy does not attack"),A->Warden->Fight.AttackInstance,0);
    CloseWorld(WA); CloseWorld(WB); return true;
}
#endif
