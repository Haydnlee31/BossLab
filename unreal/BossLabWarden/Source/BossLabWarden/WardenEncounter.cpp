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
#include "Camera/CameraComponent.h"
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
    GroundZ=GetActorLocation().Z; AirLift=JumpAttackLift=0; bPoseFromLast=false; PoseEase=0;
    FootLocked[0]=FootLocked[1]=false; FootRelease[0]=FootRelease[1]=1; FootLow[0]=FootLow[1]=1e9f;
    FeelPrevVel=FeelAccel=FeelSway=FeelSwayVel=FVector::ZeroVector; FeelCarry=FeelLean=FeelBank=FeelLook=0; FeelHold=0; FeelFree=0; FeelLand=FeelAbsorb=FeelIdle=0;
    Fight.IsBoss = Boss;
    Fight.Health = Fight.MaxHealth = Boss ? 240.f : 100.f;
    PendingAction = EWardenAction::Ready; PendingAge=0; PendingHeld=0; PendingDirection=FVector::ZeroVector; PresentedAction = -1;
    HitFlash = RejectFlash = DeathAge = 0; MoveVelocity=FVector::ZeroVector;
    Accumulator = 0; MotionBase.Empty();
    if(Locomotion) Body->PlayAnimation(Locomotion,true);
    DressFighter();
    CombatPose(FVector::ZeroVector);
}
bool AWardenChallenger::BeginAction(EWardenAction Action, int32 Move, FVector Aim)
{
    const EWardenAction Before=Fight.Action;
    if (!Fight.Request(Action,Move)) return false;
    // A cancel (chain cut, rolling thrust, jump attack) starts its pose from the pose it
    // interrupted, not from the guard.
    // The player also starts from the drawn ready pose: it carries the sword lower and
    // further back at speed (locomotion carry), so a swing from a sprint winds from there.
    bPoseFromLast=Before!=EWardenAction::Ready || !bBoss;
    if (Action==EWardenAction::Strike && !bBoss && Move==WardenRules::JumpAttack) JumpAttackLift=AirLift;
    StrikeOrigin=GetActorLocation();
    PlayCue(Action==EWardenAction::Strike ? 0 : Action==EWardenAction::Heal ? 2 : Action==EWardenAction::Jump ? 4 : 3);
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
    else if (Action == EWardenAction::Jump)
    {
        // Jumps carry the run's momentum; standing jumps go straight up.
        CommittedDirection = MoveVelocity.IsNearlyZero() ? GetActorForwardVector() : MoveVelocity.GetSafeNormal2D();
        JumpMomentum = MoveVelocity;
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
        // Moving out of a late recovery hands control straight back (no stiff full stop).
        if (!bBoss && !Direction.IsNearlyZero() && Fight.CancelIntoMove())
        {
            PoseEase=8; EaseGrip=LastGrip; EaseAxis=LastAxis; EaseTwist=LastTwist; EaseLean=LastLean;
        }
        if (Fight.Action == EWardenAction::Heal && !bBoss)
        {
            // Walk while drinking, slowly; the legs walk (SwordPose) while the arm drinks.
            const FVector Desired=Direction.GetClampedToMaxSize(1.f)*WardenRules::HealWalkSpeed;
            MoveVelocity=FMath::VInterpConstantTo(MoveVelocity,Desired,WardenRules::Step,Desired.IsNearlyZero()?3600.f:2400.f);
            MoveSwept(MoveVelocity*WardenRules::Step);
            const FVector Facing=IsLocked() ? GetTargetPosition()-GetActorLocation() : Direction;
            if (!Facing.IsNearlyZero())
                SetActorRotation(FMath::RInterpConstantTo(GetActorRotation(),FRotator(0,Facing.Rotation().Yaw,0),WardenRules::Step,360.f));
        }
        else if (Fight.Action == EWardenAction::Ready)
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
            {
                // Same 540 deg/s top speed; the player's turn eases into the last ~40 degrees
                // (70 ms time constant) instead of stopping dead on the target angle.
                const float Gap=FMath::Abs(FMath::FindDeltaAngleDegrees(YawBefore,Facing.Rotation().Yaw));
                const float Rate=bBoss ? 540.f : FMath::Clamp(Gap*14.f,60.f,540.f);
                SetActorRotation(FMath::RInterpConstantTo(GetActorRotation(),FRotator(0,Facing.Rotation().Yaw,0),WardenRules::Step,Rate));
            }
            TurnRate=FMath::FindDeltaAngleDegrees(YawBefore,GetActorRotation().Yaw)/WardenRules::Step;
        }
        else if (Fight.Action == EWardenAction::Jump)
        {
            // Some air control: the stick nudges the jump's momentum.
            const FVector Desired=JumpMomentum+Direction.GetClampedToMaxSize(1.f)*WardenRules::WalkSpeed*WardenRules::AirControl;
            MoveVelocity=FMath::VInterpConstantTo(MoveVelocity,Desired,WardenRules::Step,1200.f);
            MoveSwept(MoveVelocity*WardenRules::Step);
        }
        else if (Fight.Action == EWardenAction::Dodge)
        {
            MoveVelocity=FVector::ZeroVector;
            MoveSwept(CommittedDirection*(WardenRules::DodgeDistance(Fight.Age+1)-WardenRules::DodgeDistance(Fight.Age)));
        }
        else if (Fight.Action == EWardenAction::Strike)
        {
            const auto& Def = Fight.Definition();
            if(!bBoss && Fight.Move==WardenRules::JumpAttack)
            {
                // A jump attack keeps flying with the jump's momentum until it lands.
                if(Fight.Age<Def.Windup) MoveSwept(MoveVelocity*WardenRules::Step);
                else MoveVelocity=FVector::ZeroVector;
            }
            else if(!bBoss)
            {
                // Run momentum carries into the swing and brakes; the feet skid with it.
                MoveVelocity=FMath::VInterpConstantTo(MoveVelocity,FVector::ZeroVector,WardenRules::Step,WardenRules::EntryBrake);
                const FVector Skid=MoveVelocity*WardenRules::Step;
                if(!Skid.IsNearlyZero()) { MoveSwept(Skid); StrikeFootAnchors[0]+=Skid; StrikeFootAnchors[1]+=Skid; }
                // Steer the swing during its wind-up toward the lock target or the stick.
                const FVector Want=IsLocked() ? GetTargetPosition()-GetActorLocation() : Direction;
                if(Fight.Age<Def.Windup-6 && !Want.IsNearlyZero())
                    CommittedDirection=FMath::RInterpConstantTo(CommittedDirection.Rotation(),FRotator(0,Want.Rotation().Yaw,0),WardenRules::Step,WardenRules::SteerDegreesPerSecond).Vector();
            }
            else MoveVelocity=FVector::ZeroVector;
            if(Fight.Age<Def.Windup-8)
                SetActorRotation(FMath::RInterpConstantTo(GetActorRotation(),CommittedDirection.Rotation(),WardenRules::Step,720.f));
            // Authored displacement only during the final anticipation and contact.
            if (Fight.Age >= Def.Windup-8 && Fight.Age < Def.Windup+Def.Active)
                MoveSwept(CommittedDirection*(Def.Advance/(Def.Active+8)));
        }
        else MoveVelocity=FVector::ZeroVector;
    }
    else { MoveVelocity=FVector::ZeroVector; DeathAge=FMath::Min(DeathAge+1,72.f); }
    // Height above the floor: the jump arc, then the jump attack's descent to landing at
    // contact. The capsule really rises (low sweeps and fire pools can pass beneath).
    float Lift=0;
    if (Fight.Action==EWardenAction::Jump) Lift=WardenRules::JumpLift(Fight.Age);
    else if (Fight.Action==EWardenAction::Strike && !bBoss && Fight.Move==WardenRules::JumpAttack)
    {
        const float U=FMath::Clamp(float(Fight.Age-WardenRules::JumpAttackHang)/(Fight.Definition().Windup-WardenRules::JumpAttackHang),0.f,1.f);
        Lift=JumpAttackLift*(1-U*U);
    }
    if (!FMath::IsNearlyEqual(Lift,AirLift) || Lift>0)
    {
        AirLift=Lift;
        SetActorLocation(FVector(GetActorLocation().X,GetActorLocation().Y,GroundZ+AirLift));
    }
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
                // A staggered (stance-broken) boss takes a critical blow.
                const bool Critical=!bBoss && Other->bBoss && Other->Fight.Action==EWardenAction::Hurt;
                Fight.HitConsumed=true; Dealt=Other->Fight.Damage(Def.Damage*(Critical ? WardenRules::StaggerCritical : 1.f),true,Def.Stance);
                if(Dealt && Critical)
                    if(auto* Mode=GetWorld()->GetAuthGameMode<AWardenArenaMode>()) { Mode->Impact(9,.8f); ++Mode->CriticalCount; Mode->LastEvent=TEXT("CRITICAL BLOW | The staggered boss takes heavy damage."); }
                if(Dealt)
                {
                    Other->HitFlash=.18f; Other->PlayCue(1);
                    Other->ImpactDir=(Other->GetActorLocation()-GetActorLocation()).GetSafeNormal2D();
                    Other->BleedAt=Hit.ImpactPoint; Other->BleedDir=(Current-PreviousBlade[I]).GetSafeNormal(); ++Other->BleedCount;
                    // Hit-stop: both fighters freeze a few ticks so the blow lands with weight.
                    if(auto* Mode=GetWorld()->GetAuthGameMode<AWardenArenaMode>()) Mode->Impact(Def.Stance>=2 ? 6 : 4, bBoss ? .35f : .15f+.1f*Def.Stance);
                }
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
        if(Mode->bFrontendSession) { if(Mode->bTitle) return; if(Mode->FrontScreen==EWardenFrontScreen::Pause || Mode->FrontScreen==EWardenFrontScreen::Result) Mode->RetrySession(); else if(!Mode->bPaused) Mode->ShowFrontPage(EWardenFrontScreen::Pause); return; }
        if (Mode->bTitle || Mode->bPaused || !Fight.Alive() || !Mode->Warden->Fight.Alive())
        { Mode->bDemo=false; Mode->ResetEncounter(); Mode->bTitle=false; }
        else { Mode->SetMenuOpen(true); Mode->LastEvent=TEXT("Restart? Press R again to reset, or P / Esc to resume."); }
    }
}
void AWardenChallenger::StartFight()
{
    if (auto* Mode=GetWorld()->GetAuthGameMode<AWardenArenaMode>(); Mode && Mode->bTitle)
    { if(Mode->bFrontendSession) { if(Mode->FrontScreen==EWardenFrontScreen::Home) Mode->OpenBossSelect(); return; } Mode->bDemo=false; Mode->ResetEncounter(); Mode->bTitle=false; }
}
void AWardenChallenger::TogglePilot()
{
    if (auto* Mode=GetWorld()->GetAuthGameMode<AWardenArenaMode>())
    {
        if(Mode->bFrontendSession) return;
        if (!Mode->bTitle && !Mode->bPaused && Fight.Alive() && Mode->Warden->Fight.Alive())
        { Mode->SetMenuOpen(true); Mode->LastEvent=TEXT("Switch player mode? F6 again confirms a fresh encounter; P resumes."); return; }
        Mode->ConfigureEncounter(101,!Mode->bScriptedPlayer,1);
    }
}
void AWardenChallenger::PauseGame()
{
    if (auto* Mode = GetWorld()->GetAuthGameMode<AWardenArenaMode>())
    {
        if(Mode->bFrontendSession)
        {
            if(Mode->FrontScreen==EWardenFrontScreen::Result) return;
            if(Mode->bTitle) { if(Mode->FrontScreen!=EWardenFrontScreen::Home) Mode->OpenHome(); return; }
            if(Mode->FrontScreen==EWardenFrontScreen::Settings || Mode->FrontScreen==EWardenFrontScreen::CreativeSetup)
            { Mode->ShowFrontPage(EWardenFrontScreen::Pause); return; }
        }
        Mode->SetMenuOpen(!Mode->bPaused);
    }
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
    Warden->SetActorLocation(FVector(300,0,95*Warden->GetActorScale3D().Z)); Warden->SetActorRotation(FRotator(0,180,0));
    Player->SetTarget(Warden); Warden->SetTarget(Player);
    Player->ResetFighter(false); Warden->ResetFighter(true);
    CombatTick = 0; CombatAccumulator = 0; VisibleHistory.Reset(); SetMenuOpen(false);
    ++Encounter; Statistics.NewEncounter(Encounter,RetainEvidence); bReportSaved=false;
    RehearsalMove=0; RehearsalWait=100; HitStop=0; Shake=0;
    if(bRegent)
    {
        Regent=FWardenRegentState(); Warden->bRegent=true; Warden->SetActorHiddenInGame(false);
        Warden->Fight.Health=Warden->Fight.MaxHealth=WardenRegent::Health;
        Warden->Fight.Poise=Warden->Fight.MaxPoise=WardenRegent::Poise;
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
    UpdateAudio();
    // Regent visuals follow the fixed-step state below; updated after the steps run.
    ON_SCOPE_EXIT { if(bRegent) AnimateRegentView(GetWorld()->GetTimeSeconds()); AnimateEffects(GetWorld()->GetTimeSeconds()); AnimateSpectacle(GetWorld()->GetTimeSeconds()); };
    const double Now=FPlatformTime::Seconds();
    if(LastFrameTime>0 && !bPaused && !bTitle && Player && Warden && Player->Fight.Alive() && Warden->Fight.Alive())
    {
        if(++WarmupFrames>180 && FrameMilliseconds.Num()<10000) FrameMilliseconds.Add((Now-LastFrameTime)*1000);
    }
    LastFrameTime=Now;
    if(bBenchmark && DemoTick>=3600 && !bBenchmarkSaved)
    {
        SaveReport(); bBenchmarkSaved=true; StopAudioRecording();
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
    // Slow motion for the big moments (phase change, felled boss, critical blow): real time feeds
    // the fixed step more slowly; the step itself is unchanged. Off in automation and with
    // reduced motion, so tests and determinism checks never see it.
    CombatAccumulator += DeltaSeconds*(GIsAutomationTesting || bReducedMotion ? 1.f : Spectacle.TimeScale(GetWorld()->GetTimeSeconds()));
    while (CombatAccumulator >= WardenRules::Step)
    {
        CombatAccumulator -= WardenRules::Step;
        FixedStep();
    }
    const float Alpha=float(CombatAccumulator/WardenRules::Step);
    Player->BlendRenderState(Alpha); Warden->BlendRenderState(Alpha);
    // Camera shake after landed blows (off with reduced motion); presentation only.
    Shake=FMath::Max(0.f,Shake-DeltaSeconds*2.2f);
    if(Player->Camera)
    {
        const float S=bReducedMotion ? 0.f : Shake, Time=GetWorld()->GetTimeSeconds();
        Player->Camera->SetRelativeLocation(FVector(0,FMath::Sin(Time*83)*S*7,FMath::Sin(Time*71+1)*S*5));
    }
}
void AWardenArenaMode::FixedStep()
{
    if (!Player || !Warden) return;
    // Exact step state in, snapshot out; frames blend between snapshots (WardenRenderBlend.cpp).
    Player->RestoreStepState(); Warden->RestoreStepState();
    ON_SCOPE_EXIT { Player->CaptureStepState(); Warden->CaptureStepState(); };
    // Hit-stop freezes the whole fight (both fighters, hazards, skulls) for a few ticks.
    if(bFrontendSession && (bTitle || bPaused)) return;
    if(HitStop>0) { --HitStop; return; }
    if(bDemo) ++DemoTick;
    if(!Player->Fight.Alive() || !Warden->Fight.Alive())
    {
        if(!Player->Fight.Alive()) Player->StepFighter(FVector::ZeroVector);
        if(!Warden->Fight.Alive()) Warden->StepFighter(FVector::ZeroVector);
        Statistics.Censor();
        if(bRegent) { Regent.Flying.Reset(); Regent.Hazards.Reset(); }
        if(!bReportSaved) { SaveReport(); bReportSaved=true; }
        RunEnded();
        if(bDemo && ++DemoResetWait>=120) { ++DemoRounds; ResetEncounter(true); DemoResetWait=0; LastEvent=TEXT("DEMO ROUND RESET | Health restored; evidence retained"); }
        return;
    }
    ++CombatTick;
    if(CombatTick==1) RunStarted();
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
    if(bFeelStudy) FeelStudyStep(Intent);
    if(TestPilot) TestPilot(*this,Intent);
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
            // The player kit in one take: three-cut chain (buffered presses), a side roll,
            // jump + jump attack, then a back roll into the rolling thrust.
            if(CombatTick==125 || CombatTick==150 || CombatTick==192 || CombatTick==355 || CombatTick==455) Player->PendingAction=EWardenAction::Strike;
            if(CombatTick==270 || CombatTick==420)
            {
                Player->PendingAction=EWardenAction::Dodge;
                Player->PendingDirection=CombatTick==270 ? FVector::RightVector : -FVector::ForwardVector;
            }
            if(CombatTick==340 || CombatTick==760) Player->PendingAction=EWardenAction::Jump;
            // Then a flask (health lowered first: healing is refused at full health).
            if(CombatTick==560) Player->Fight.Health=55;
            if(CombatTick==580) Player->PendingAction=EWardenAction::Heal;
            // Walk while drinking (toward the camera's left), then stop.
            if(CombatTick>=600 && CombatTick<650) Intent=FVector(0,-1,0);
            // Turn the study camera to the knight's front for the drink, then back.
            if(CombatTick==570 || CombatTick==700) MotionStudyView=CombatTick==570 ? FRotator(-8,160,0) : FRotator(-12,-40,0);
        }
    }
    if (Player->PendingAction != EWardenAction::Ready)
    {
        const auto Action = Player->PendingAction;
        // A buffered roll goes where the stick points when it comes out (as in Elden Ring),
        // falling back to the direction held at the press.
        const FVector Live = bScriptedPlayer ? Intent : Player->MoveIntent();
        const FVector Aim = Action == EWardenAction::Dodge ? (bScriptedPlayer||!Live.IsNearlyZero()?Live:Player->PendingDirection) : (Player->IsLocked() || bScriptedPlayer) ? Warden->GetActorLocation()-Player->GetActorLocation() : Player->GetActorForwardVector();
        const bool Accepted=Player->BeginAction(Action,Action==EWardenAction::Strike ? Player->Fight.NextPlayerMove() : 0,Action==EWardenAction::Jump ? Intent : Aim);
        const bool Rejected=Player->Fight.Ready() && !Accepted;
        if(Rejected)
        {
            Player->RejectFlash=.55f;
            LastEvent=Player->Fight.Stamina<(Action==EWardenAction::Dodge?WardenRules::DodgeCost:Action==EWardenAction::Strike?Player->Fight.StrikeCostOf(Player->Fight.NextPlayerMove()):Action==EWardenAction::Jump?WardenRules::JumpCost:WardenRules::HealCost)
                ? TEXT("Not enough stamina.") : Action==EWardenAction::Heal ? TEXT("Heal unavailable: full health or no charges.") : TEXT("Still recovering.");
        }
        // While the current action cannot yet be cancelled into this one, the press is held
        // (bounded) rather than aged out, so it fires on the first allowed tick.
        const int32 Index=Action==EWardenAction::Strike ? Player->Fight.NextPlayerMove() : 0;
        const bool Held=!Accepted && !Rejected && !Player->Fight.Ready() && !Player->Fight.CancelOpen(Action,Index);
        const bool Expired=Held ? ++Player->PendingHeld>WardenRules::HeldInputTicks : ++Player->PendingAge>WardenRules::InputBufferTicks;
        if(Accepted || Rejected || Expired)
        {
            Player->PendingAction=EWardenAction::Ready; Player->PendingAge=0; Player->PendingHeld=0;
            // The queued follow-up (an attack pressed right after a jump or roll) becomes
            // the buffered input once its lead action has started.
            if(Accepted && Player->FollowAction!=EWardenAction::Ready) Player->PendingAction=Player->FollowAction;
            Player->FollowAction=EWardenAction::Ready;
        }
    }
    Player->StepFighter(Intent,!bScriptedPlayer && !bMotionStudy && Player->SprintHeld);
    Warden->StepFighter(BossDirection);
    if(bMotionStudy)
    {
        const FVector P=Player->GetActorLocation();
        MotionStudyTrace+=FString::Printf(TEXT("%d,%d,%d,%.3f,%.4f,%.3f,%.3f,%.3f,%d\n"),CombatTick,int32(Player->Fight.Action),Player->Fight.Age,Player->Fight.Stamina,Player->GripError,P.X,P.Y,P.Z,int32(Player->Fight.Invulnerable()));
    }
    // Practice (opt-in, labelled): the player is refilled before each step resolves.
    if(bFrontendSession && !bCreativeMode) { if(bPracticeInfiniteHealth || bPracticeInfiniteStamina) Run.bChallengeEligible=false; bPracticeInfiniteHealth=false; bPracticeInfiniteStamina=false; }
    if(bPracticeInfiniteHealth) { Player->Fight.Health=Player->Fight.MaxHealth; Run.bPractice=true; }
    if(bPracticeInfiniteStamina && bCreativeMode) { Player->Fight.Stamina=100; Run.bPractice=true; }
    const float PriorPlayerHealth=Player->Fight.Health, PriorBossHealth=Warden->Fight.Health;
    // Explicit boss-first ordering; lethal damage prevents retaliation and healing.
    if (Warden->ResolveStrike(Player,bDebugGeometry)) { BossDamage+=PriorPlayerHealth-Player->Fight.Health; LastEvent = TEXT("You were hit. Recover before committing again."); }
    if (Player->ResolveStrike(Warden,bDebugGeometry)) { PlayerDamage+=PriorBossHealth-Warden->Fight.Health; LastEvent = TEXT("Greatsword connected."); }
    if(bRegent && bRehearsal) RegentResolve();
    if(bFrontendSession && bCreativeMode && bPracticeInfiniteHealth)
    {
        Player->Fight.Health=Player->Fight.MaxHealth;
        if(Player->Fight.Action==EWardenAction::Dead) { Player->Fight.Action=EWardenAction::Ready; Player->Fight.Age=0; }
    }
    if(PriorPlayerHealth>0 && !Player->Fight.Alive()) RunKilled();
    UpdateRunStats();
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
