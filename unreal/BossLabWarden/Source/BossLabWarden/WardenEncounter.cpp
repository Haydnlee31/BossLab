#include "WardenPrototype.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Animation/AnimSequence.h"
#include "Animation/BlendSpace.h"
#include "GameFramework/PlayerController.h"
#include "Engine/World.h"
#include "DrawDebugHelpers.h"
#include "UnrealClient.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "Misc/ScopeExit.h"
#include "GameFramework/SpringArmComponent.h"

FVector AWardenChallenger::MoveIntent() const
{
    if (!Controller) return FVector::ZeroVector;
    const FRotator Yaw(0,Controller->GetControlRotation().Yaw,0);
    return (Yaw.Vector()*ForwardInput+FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y)*RightInput).GetClampedToMaxSize(1.f);
}
void AWardenChallenger::MoveSwept(const FVector& Step)
{
    FHitResult Hit;
    AddActorWorldOffset(Step,true,&Hit);
    if (Hit.bBlockingHit) AddActorWorldOffset(FVector::VectorPlaneProject(Step*(1-Hit.Time),Hit.Normal),true);
}
void AWardenChallenger::ResetFighter(bool Boss)
{
    ClearGameplayInput();
    // A reset re-poses outside the fixed step: drop any blended frame and its history.
    bRenderBlended=false; bRenderValid=false; Arm->SetRelativeLocation(FVector::ZeroVector);
    bBoss = Boss; Fight = FWardenFighterState();
    FootLocked[0]=FootLocked[1]=false; FootRelease[0]=FootRelease[1]=1; FootLow[0]=FootLow[1]=1e9f;
    Fight.IsBoss = Boss;
    Fight.Health = Fight.MaxHealth = Boss ? 240.f : 100.f;
    PendingAction = EWardenAction::Ready; PendingAge=0; PendingDirection=FVector::ZeroVector; PresentedAction = -1;
    HitFlash = RejectFlash = DeathAge = 0; MoveVelocity=FVector::ZeroVector;
    Accumulator = 0; MotionBase.Empty();
    if(Locomotion) Body->PlayAnimation(Locomotion,true);
    DressFighter();
    CombatPose(FVector::ZeroVector);
}
bool AWardenChallenger::BeginAction(EWardenAction Action, int32 Move, FVector Aim)
{
    if (!Fight.Request(Action,Move)) return false;
    StrikeOrigin=GetActorLocation();
    PlayCue(Action==EWardenAction::Strike ? 0 : Action==EWardenAction::Heal ? 2 : 3);
    if (Action == EWardenAction::Strike)
    {
        // Carry the actual stance into commitment, including a cut begun mid-stride.
        StrikeFootAnchors[0]=VisualBody->GetBoneLocationByName(TEXT("foot_l"),EBoneSpaces::WorldSpace);
        StrikeFootAnchors[1]=VisualBody->GetBoneLocationByName(TEXT("foot_r"),EBoneSpaces::WorldSpace);
        if (Aim.IsNearlyZero()) Aim = GetActorForwardVector();
        Aim.Z = 0;
        CommittedDirection = Aim.GetSafeNormal();
    }
    else if (Action == EWardenAction::Dodge)
    {
        CommittedDirection = Aim.IsNearlyZero() ? -GetActorForwardVector() : Aim.GetSafeNormal2D();
    }
    PresentedAction = -1;
    CombatPose(FVector::ZeroVector);
    for(int32 I=0;I<5;++I) PreviousBlade[I]=HitPoint(I);
    return true;
}
void AWardenChallenger::StepFighter(const FVector& Direction, bool SprintRequested)
{
    const FVector Before = GetActorLocation();
    TurnRate=0;
    Fight.UpdateSprint(SprintRequested,!Direction.IsNearlyZero());
    if (Fight.Alive())
    {
        if (Fight.Action == EWardenAction::Ready)
        {
            const FVector Desired=Direction.GetClampedToMaxSize(1.f)*(Fight.Sprinting ? WardenRules::SprintSpeed : bBoss ? 260.f : WardenRules::WalkSpeed);
            MoveVelocity=FMath::VInterpConstantTo(MoveVelocity,Desired,WardenRules::Step,Desired.IsNearlyZero()?3600.f:2400.f);
            MoveSwept(MoveVelocity*WardenRules::Step);
            FVector Facing = Direction;
            if (!bBoss && IsLocked()) Facing = GetTargetPosition()-GetActorLocation();
            // Bosses keep their eyes on the player while walking, backing off or circling;
            // the directional walk clips carry backpedals and strafes.
            if (bBoss && Target.IsValid()) Facing = Target->GetActorLocation()-GetActorLocation();
            const float YawBefore=GetActorRotation().Yaw;
            if (!Facing.IsNearlyZero())
                SetActorRotation(FMath::RInterpConstantTo(GetActorRotation(),FRotator(0,Facing.Rotation().Yaw,0),WardenRules::Step,540.f));
            TurnRate=FMath::FindDeltaAngleDegrees(YawBefore,GetActorRotation().Yaw)/WardenRules::Step;
        }
        else if (Fight.Action == EWardenAction::Dodge)
        {
            MoveVelocity=FVector::ZeroVector;
            MoveSwept(CommittedDirection*(WardenRules::DodgeDistance(Fight.Age+1)-WardenRules::DodgeDistance(Fight.Age)));
        }
        else if (Fight.Action == EWardenAction::Strike)
        {
            const auto& Def = Fight.Definition();
            MoveVelocity=FVector::ZeroVector;
            if(Fight.Age<Def.Windup-8)
                SetActorRotation(FMath::RInterpConstantTo(GetActorRotation(),CommittedDirection.Rotation(),WardenRules::Step,720.f));
            // Authored displacement only during the final anticipation and contact.
            if (Fight.Age >= Def.Windup-8 && Fight.Age < Def.Windup+Def.Active)
                MoveSwept(CommittedDirection*(Def.Advance/(Def.Active+8)));
        }
        else MoveVelocity=FVector::ZeroVector;
    }
    else { MoveVelocity=FVector::ZeroVector; DeathAge=FMath::Min(DeathAge+1,72.f); }
    CombatPose(GetActorLocation()-Before);
}
void AWardenChallenger::CombatPose(const FVector& Travel)
{
    SwordPose(Travel);
}
bool AWardenChallenger::ResolveStrike(AWardenChallenger* Other, bool Debug)
{
    bool Dealt=false;
    const auto& Def=Fight.Definition();
    FCollisionQueryParams Query(SCENE_QUERY_STAT(WardenBlade),false,this);
    for(int32 I=0;I<5;++I)
    {
        const FVector Current=HitPoint(I);
        if(Fight.Active() && !Fight.HitConsumed && Other && Other->Fight.Alive())
        {
            FHitResult Occlusion;
            const bool Blocked=GetWorld()->LineTraceSingleByChannel(Occlusion,HitOrigin(),Current,ECC_Pawn,Query) && Occlusion.GetActor()!=Other;
            FHitResult Hit;
            if(!Blocked && GetWorld()->SweepSingleByChannel(Hit,PreviousBlade[I],Current,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeSphere(Def.Radius*GetActorScale3D().X),Query) && Hit.GetActor()==Other)
            {
                Fight.HitConsumed=true; Dealt=Other->Fight.Damage(Def.Damage);
                if(Dealt) { Other->HitFlash=.18f; Other->PlayCue(1); }
            }
            if(Debug) { DrawDebugSphere(GetWorld(),Current,Def.Radius,8,FColor::Orange,false,.04f); DrawDebugLine(GetWorld(),PreviousBlade[I],Current,FColor::Yellow,false,.04f,0,1); }
        }
        PreviousBlade[I]=Current;
    }
    return Dealt;
}
void AWardenChallenger::Restart()
{
    if (auto* Mode = GetWorld()->GetAuthGameMode<AWardenArenaMode>())
    {
        if (Mode->bTitle || Mode->bPaused || !Fight.Alive() || !Mode->Warden->Fight.Alive())
        { Mode->bDemo=false; Mode->ResetEncounter(); Mode->bTitle=false; }
        else { Mode->SetMenuOpen(true); Mode->LastEvent=TEXT("Restart? Press R again to reset, or P / Esc to resume."); }
    }
}
void AWardenChallenger::StartFight()
{
    if (auto* Mode=GetWorld()->GetAuthGameMode<AWardenArenaMode>(); Mode && Mode->bTitle)
    { Mode->bDemo=false; Mode->ResetEncounter(); Mode->bTitle=false; }
}
void AWardenChallenger::TogglePilot()
{
    if (auto* Mode=GetWorld()->GetAuthGameMode<AWardenArenaMode>())
    {
        if (!Mode->bTitle && !Mode->bPaused && Fight.Alive() && Mode->Warden->Fight.Alive())
        { Mode->SetMenuOpen(true); Mode->LastEvent=TEXT("Switch player mode? F6 again confirms a fresh encounter; P resumes."); return; }
        Mode->ConfigureEncounter(101,!Mode->bScriptedPlayer,1);
    }
}
void AWardenChallenger::PauseGame()
{
    if (auto* Mode = GetWorld()->GetAuthGameMode<AWardenArenaMode>()) { Mode->SetMenuOpen(!Mode->bPaused); }
}
void AWardenChallenger::DebugGeometry()
{
    if (auto* Mode = GetWorld()->GetAuthGameMode<AWardenArenaMode>()) Mode->bDebugGeometry = !Mode->bDebugGeometry;
}
void AWardenChallenger::CaptureEvidence()
{
    auto* Mode=GetWorld()->GetAuthGameMode<AWardenArenaMode>();
    if (!Mode || !Mode->Player || !Mode->Warden) return;
    Mode->SetMenuOpen(true); // A potentially slow capture must not advance a human fight.
    FString Directory=FPaths::Combine(FPaths::ProjectSavedDir(),TEXT("BossLabEvidence"));
#if WITH_EDITOR
    Directory=FPaths::ConvertRelativePathToFull(FPaths::Combine(FPaths::ProjectDir(),TEXT("../../artifacts/unreal")));
#endif
    IFileManager::Get().MakeDirectory(*Directory,true);
    const FString Stem=FPaths::Combine(Directory,FString::Printf(TEXT("combat-%s-%d"),*FDateTime::UtcNow().ToString(TEXT("%Y%m%d-%H%M%S")),Mode->CombatTick));
    const FVector P=GetActorLocation();
    const auto& B=Mode->Warden->Fight;
    const FString Snapshot=FString::Printf(TEXT("{\"tick\":%d,\"player_health\":%g,\"boss_health\":%g,\"stamina\":%g,\"heals\":%d,\"boss_action\":%d,\"boss_age\":%d,\"player_action\":%d,\"x\":%g,\"y\":%g,\"paused\":%s,\"controller\":\"%s\"}"),Mode->CombatTick,Fight.Health,B.Health,Fight.Stamina,Fight.Heals,int32(B.Action),B.Age,int32(Fight.Action),P.X,P.Y,Mode->bPaused?TEXT("true"):TEXT("false"),Mode->bRehearsal?TEXT("fixed-rehearsal"):TEXT("practice-dummy"));
    FFileHelper::SaveStringToFile(Snapshot,*(Stem+TEXT(".json")));
    FScreenshotRequest::RequestScreenshot(Stem+TEXT(".png"),true,false);
    UE_LOG(LogTemp,Display,TEXT("BossLab real gameplay capture: %s"),*Stem);
}
void AWardenArenaMode::ResetEncounter(bool RetainEvidence)
{
    if (!Player || !Warden) return;
    Player->SetActorLocation(FVector(-450,0,95)); Player->SetActorRotation(FRotator::ZeroRotator);
    Warden->SetActorLocation(FVector(300,0,128)); Warden->SetActorRotation(FRotator(0,180,0));
    Player->SetTarget(Warden); Warden->SetTarget(Player);
    Player->ResetFighter(false); Warden->ResetFighter(true);
    CombatTick = 0; CombatAccumulator = 0; VisibleHistory.Reset(); SetMenuOpen(false);
    ++Encounter; Statistics.NewEncounter(Encounter,RetainEvidence); bReportSaved=false;
    RehearsalMove=0; RehearsalWait=100;
    if(bRegent)
    {
        Regent=FWardenRegentState(); Warden->bRegent=true; Warden->SetActorHiddenInGame(false);
        // Testing shortcut: open at the phase threshold, so the transition plays first.
        if(bRegentPhaseTwoStart) Warden->Fight.Health=WardenRegent::PhaseTwoHealth;
    }
    PlayerDamage=BossDamage=0; AcceptedTick=0; AcceptedMove=-1; bDecisionAccepted=false;
    Observation=FWardenObservation(); Decision=FWardenDecision();
    PolicyRandom.Initialize(PolicySeed);
    PlayerScript.LastRespondedInstance=-1;
    for(int32& Count : MoveCounts) Count=0;
    LastPlayerPosition=Player->GetActorLocation();
    LastEvent = bRegent ? TEXT("The Funeral Regent. Read the censer and the skulls; roll late, punish recovery.")
        : TEXT("Tab target. Read the sword. Roll through contact; punish recovery.");
    if (Player->GetController()) Player->GetController()->SetControlRotation(FRotator(-12,0,0));
}
void AWardenArenaMode::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if(bDungeon) AnimateDungeon(Dungeon,GetWorld()->GetTimeSeconds());
    // Regent visuals follow the fixed-step state below; updated after the steps run.
    ON_SCOPE_EXIT { if(bRegent) AnimateRegentView(GetWorld()->GetTimeSeconds()); };
    const double Now=FPlatformTime::Seconds();
    if(LastFrameTime>0 && !bPaused && !bTitle && Player && Warden && Player->Fight.Alive() && Warden->Fight.Alive())
    {
        if(++WarmupFrames>180 && FrameMilliseconds.Num()<10000) FrameMilliseconds.Add((Now-LastFrameTime)*1000);
    }
    LastFrameTime=Now;
    if(bBenchmark && DemoTick>=3600 && !bBenchmarkSaved)
    {
        SaveReport(); bBenchmarkSaved=true;
        if(auto* PC=GetWorld()->GetFirstPlayerController()) PC->ConsoleCommand(TEXT("quit"));
    }
    if (bPaused || bTitle || !Player || !Warden) { CombatAccumulator = 0; return; }
    if(bCaptureFrames)
    {
        ++CaptureFrame;
        if(CaptureFrame>60 && CaptureFrame<=60+CaptureCount)
        {
            const FString Directory=FPaths::Combine(FPaths::ProjectSavedDir(),TEXT("CaptureFrames"));
            IFileManager::Get().MakeDirectory(*Directory,true);
            FScreenshotRequest::RequestScreenshot(FPaths::Combine(Directory,FString::Printf(TEXT("frame-%06d.png"),CaptureFrame-61)),true,false);
        }
        if(CaptureFrame==62+CaptureCount && GetWorld()->GetFirstPlayerController())
        {
            if(bMotionStudy) FFileHelper::SaveStringToFile(MotionStudyTrace,*FPaths::Combine(FPaths::ProjectSavedDir(),TEXT("motion-study.csv")));
            FFileHelper::SaveStringToFile(ReviewTrace,*FPaths::Combine(FPaths::ProjectSavedDir(),TEXT("review-trace.csv")));
            SaveReport();
            GetWorld()->GetFirstPlayerController()->ConsoleCommand(TEXT("quit"));
        }
    }
    CombatAccumulator += DeltaSeconds;
    while (CombatAccumulator >= WardenRules::Step)
    {
        CombatAccumulator -= WardenRules::Step;
        FixedStep();
    }
    const float Alpha=float(CombatAccumulator/WardenRules::Step);
    Player->BlendRenderState(Alpha); Warden->BlendRenderState(Alpha);
}
void AWardenArenaMode::FixedStep()
{
    if (!Player || !Warden) return;
    // Exact step state in, snapshot out; frames blend between snapshots (WardenRenderBlend.cpp).
    Player->RestoreStepState(); Warden->RestoreStepState();
    ON_SCOPE_EXIT { Player->CaptureStepState(); Warden->CaptureStepState(); };
    if(bDemo) ++DemoTick;
    if(!Player->Fight.Alive() || !Warden->Fight.Alive())
    {
        if(!Player->Fight.Alive()) Player->StepFighter(FVector::ZeroVector);
        if(!Warden->Fight.Alive()) Warden->StepFighter(FVector::ZeroVector);
        Statistics.Censor();
        if(bRegent) { Regent.Flying.Reset(); Regent.Hazards.Reset(); }
        if(!bReportSaved) { SaveReport(); bReportSaved=true; }
        if(bDemo && ++DemoResetWait>=120) { ++DemoRounds; ResetEncounter(true); DemoResetWait=0; LastEvent=TEXT("DEMO ROUND RESET | Health restored; evidence retained"); }
        return;
    }
    ++CombatTick;
    FVector BossDirection=FVector::ZeroVector;
    // Temporary rehearsal choreography: fixed 0,1,2 order, no learned policy,
    // response statistics, input reading or hidden resource-dependent selection.
    if(bRegentStudy)
    {
        // The in-action half of RegentDecide (tracking, ash-step teleport) still runs.
        FVector Ignored; Regent.Waiting=1000000; RegentDecide(Ignored); RegentStudyStep();
    }
    else if(bRehearsal && bRegent) RegentDecide(BossDirection);
    else if(bRehearsal && Warden->Fight.Ready())
    {
        const FVector ToPlayer=Player->GetActorLocation()-Warden->GetActorLocation();
        const float Distance=ToPlayer.Size2D();
        if(Distance>225) BossDirection=ToPlayer.GetSafeNormal2D();
        else if(Distance<165) BossDirection=-ToPlayer.GetSafeNormal2D()*.45f;
        if(RehearsalWait>0) --RehearsalWait;
        else if(ToPlayer.Size2D()<260 && Warden->BeginAction(EWardenAction::Strike,RehearsalMove,ToPlayer))
        {
            ++MoveCounts[RehearsalMove]; AcceptedMove=RehearsalMove; AcceptedTick=CombatTick;
            RehearsalMove=(RehearsalMove+1)%3; RehearsalWait=24;
            LastEvent=FString(Warden->Fight.Definition().Name)+TEXT(" | Aim committed.");
        }
    }
    FVector Intent = Player->MoveIntent();
    if(bGaitStudy) GaitStudyStep(Intent,BossDirection);
    if(bScriptedPlayer)
    {
        const auto Command=PlayerScript.Decide(bDemo?DemoTick:CombatTick,Player->GetActorLocation(),Player->Fight,Warden->GetActorLocation(),Warden->Fight.Action,Warden->Fight.Move,Warden->Fight.Age,Warden->Fight.AttackInstance);
        Intent=Command.Movement; Player->PendingAction=Command.Action;
    }
    if(bMotionStudy)
    {
        // Capture-only authored requests use ordinary acceptance/costs, no resets
        // or forced action states. This mode never controls a boss policy.
        Intent=FVector::ZeroVector;
        if(RollStudyGroup>=0)
        {
            const int32 Offset=CombatTick-125;
            if(Offset>=0 && Offset<=270 && Offset%90==0)
            {
                Player->PendingAction=EWardenAction::Dodge;
                Player->PendingDirection=FRotator(0,(Offset/90)*90.f+(RollStudyGroup==1?45.f:0.f),0).Vector();
            }
        }
        else
        {
            if(CombatTick==125 || CombatTick==290) Player->PendingAction=EWardenAction::Strike;
            if(CombatTick==230 || CombatTick==400)
            {
                Player->PendingAction=EWardenAction::Dodge;
                Player->PendingDirection=CombatTick==230 ? FVector::RightVector : -FVector::ForwardVector;
            }
        }
    }
    if (Player->PendingAction != EWardenAction::Ready)
    {
        const auto Action = Player->PendingAction;
        const FVector Aim = Action == EWardenAction::Dodge ? (bScriptedPlayer?Intent:Player->PendingDirection) : (Player->IsLocked() || bScriptedPlayer) ? Warden->GetActorLocation()-Player->GetActorLocation() : Player->GetActorForwardVector();
        const bool Accepted=Player->BeginAction(Action,0,Aim);
        const bool Rejected=Player->Fight.Ready() && !Accepted;
        if(Rejected)
        {
            Player->RejectFlash=.55f;
            LastEvent=Player->Fight.Stamina<(Action==EWardenAction::Dodge?WardenRules::DodgeCost:Action==EWardenAction::Strike?WardenRules::StrikeCost:WardenRules::HealCost)
                ? TEXT("Not enough stamina.") : Action==EWardenAction::Heal ? TEXT("Heal unavailable: full health or no charges.") : TEXT("Still recovering.");
        }
        if(Accepted || Rejected || ++Player->PendingAge>WardenRules::InputBufferTicks)
        { Player->PendingAction=EWardenAction::Ready; Player->PendingAge=0; }
    }
    Player->StepFighter(Intent,!bScriptedPlayer && !bMotionStudy && Player->SprintHeld);
    Warden->StepFighter(BossDirection);
    if(bMotionStudy)
    {
        const FVector P=Player->GetActorLocation();
        MotionStudyTrace+=FString::Printf(TEXT("%d,%d,%d,%.3f,%.4f,%.3f,%.3f,%.3f,%d\n"),CombatTick,int32(Player->Fight.Action),Player->Fight.Age,Player->Fight.Stamina,Player->GripError,P.X,P.Y,P.Z,int32(Player->Fight.Invulnerable()));
    }
    const float PriorPlayerHealth=Player->Fight.Health, PriorBossHealth=Warden->Fight.Health;
    // Explicit boss-first ordering; lethal damage prevents retaliation and healing.
    if (Warden->ResolveStrike(Player,bDebugGeometry)) { BossDamage+=PriorPlayerHealth-Player->Fight.Health; LastEvent = TEXT("You were hit. Recover before committing again."); }
    if (Player->ResolveStrike(Warden,bDebugGeometry)) { PlayerDamage+=PriorBossHealth-Warden->Fight.Health; LastEvent = TEXT("Greatsword connected."); }
    if(bRegent && bRehearsal) RegentResolve();
    Player->Fight.Advance(); Warden->Fight.Advance();
    if(bCaptureFrames) ReviewTrace+=FString::Printf(TEXT("%d,%d,%d,%.1f,%.1f,%d,%d,%.1f,%d,%.2f\n"),CombatTick,int32(Player->Fight.Action),Player->Fight.Age,Player->Fight.Health,Player->Fight.Stamina,int32(Warden->Fight.Action),Warden->Fight.Age,Warden->Fight.Health,Warden->Fight.Poise,FVector::Dist2D(Player->GetActorLocation(),Warden->GetActorLocation()));
}

bool AWardenArenaMode::AcceptBossDecision(const FWardenDecision& Proposed)
{
    if(!Warden || Proposed.Encounter!=Encounter || Proposed.Tick!=CombatTick || !Warden->Fight.Ready()) return false;
    if(Proposed.Choice!=EWardenChoice::Attack) return true;
    if(!Warden->BeginAction(EWardenAction::Strike,Proposed.Move,Proposed.Direction)) return false;
    ++MoveCounts[Proposed.Move]; AcceptedTick=CombatTick; AcceptedMove=Proposed.Move;
    LastEvent=FString(WardenRules::Strike(Proposed.Move).Name)+TEXT(" | Aim committed.");
    return true;
}
void AWardenArenaMode::ConfigureEncounter(int32 Seed,bool Scripted,int32 Style)
{
    PolicySeed=Seed; bScriptedPlayer=Scripted; PlayerScript.Style=Style; PlayerScript.ReactionOffset=0;
    bDemo=false; DemoTick=DemoRounds=DemoResetWait=0;
    ResetEncounter(); bTitle=false;
}
