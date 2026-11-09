#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/HUD.h"
#include "WardenCombat.h"
#include "WardenPolicy.h"
#include "WardenScript.h"
#include "WardenStatistics.h"
#include "WardenRegent.h"
#include "WardenPrototype.generated.h"

class UCapsuleComponent;
class USkeletalMeshComponent;
class USpringArmComponent;
class UCameraComponent;
class UAnimationAsset;
class UPoseableMeshComponent;
class UStaticMeshComponent;

struct FWardenOutfitSupport
{
    TWeakObjectPtr<UStaticMeshComponent> Part;
    TArray<FVector> Vertices;
};

// Presentation-only cape/robe chain on the revamp costumes (see WardenRevamp.cpp).
struct FWardenSwingChain
{
    TArray<int32> Bones;
    int32 Anchor=INDEX_NONE;
    TArray<FVector> Pos,Prev;
};

UCLASS()
class BOSSLABWARDEN_API AWardenChallenger : public APawn
{
    GENERATED_BODY()
public:
    AWardenChallenger();
    virtual void BeginPlay() override;
    virtual void PossessedBy(AController* NewController) override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
    bool IsLocked() const { return bLocked && Target.IsValid(); }
    FVector GetTargetPosition() const;
    void SetTarget(AActor* Actor) { Target = Actor; }
    void SetLocked(bool Value) { bLocked=Value; }
    void SimulateMovement(const FVector& Direction, float DeltaSeconds);
    void MoveSwept(const FVector& Step);
    FVector MoveIntent() const;
    void CombatPose(const FVector& Travel);
    void SwordPose(const FVector& Travel);
    void CreateSword();
    FVector BladePoint(float Along) const;
    FTransform SwordFrame;
    FVector PreviousBlade[5];
    float GripError = 0;
    TArray<FTransform> GuardBase;
    TArray<FTransform> MotionBase;
    EWardenAction PosedAction=EWardenAction::Ready;
    int32 PoseSettle=0;
    static inline float GaitRate=1.1f;
    // Per-direction play-rate trims (forward / sideways / backward clips walk at different
    // natural speeds); blended by travel angle. Tuned by AnimationTests.
    static inline float GaitTrim[3]={1.f,1.f,1.f};
    float TurnRate=0;
    // Walking foot locks (WardenSword.cpp); reset with the fighter.
    bool FootLocked[2]={false,false};
    FVector FootLock[2], FootReleaseFrom[2], FootAnimPrev[2];
    float FootRelease[2]={1,1}, FootLow[2]={1e9f,1e9f};
    int32 FootForcedReleases=0;   // locks broken by the stretch limit (should stay rare)   // yaw deg/s this step while ready; drives turn-in-place stepping
    // Render interpolation between fixed steps (WardenRenderBlend.cpp); presentation only.
    struct FStepPose { FVector Location=FVector::ZeroVector; float Yaw=0; FTransform Visual, Sword; TArray<FTransform> Bones; };
    FStepPose RenderPrev, RenderCurr;
    bool bRenderValid=false, bRenderBlended=false;
    void CaptureStepState();
    void RestoreStepState();
    void BlendRenderState(float Alpha);   // locomotion clip play rate (tuned by AnimationTests)
    UPROPERTY() TObjectPtr<UPoseableMeshComponent> VisualBody;
    UPROPERTY() TObjectPtr<USceneComponent> SwordRoot;
    void StepFighter(const FVector& Direction, bool SprintRequested=false);
    bool SprintHeld=false;
    bool AllowsGameplayInput() const;
    void ClearGameplayInput();
    void QueueAction(EWardenAction Action);
    bool SuppressMouseAttack=false;
    bool BeginAction(EWardenAction Action, int32 Move = 0, FVector Aim = FVector::ZeroVector);
    bool ResolveStrike(AWardenChallenger* Other, bool Debug);
    void ResetFighter(bool Boss);
    void DressFighter();
    void DressAshbound();
    bool DressV13();
    bool bV13Outfit=false;
    bool DressRevamp();
    bool bRevampOutfit=false;
    TArray<FWardenSwingChain> SwingChains;
    void SwingCloth(const TArray<FTransform>& CS);
    FString V13SourceHash;
    // Funeral Regent (-BossLabRegent): one-handed estoc, censer chain from the left arm.
    bool bRegent=false;
    void DressRegentWeapon();
    FVector CenserWorld() const;
    bool CenserStrike() const;
    FVector HitPoint(int32 Sample) const;
    FVector HitOrigin() const;
    void UpdateAshbound(const FVector& Travel);
    int32 OutfitTriangles=0;
    float OutfitClock=0;
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> CapePanels;
    TArray<FTransform> CapeRest;
    TArray<FWardenOutfitSupport> OutfitSupport;
    void PlayCue(int32 Cue);
    FWardenFighterState Fight;
    bool bBoss = false;
    EWardenAction PendingAction = EWardenAction::Ready;
    int32 PendingAge=0;
    FVector PendingDirection=FVector::ZeroVector;
    FVector CommittedDirection = FVector::ForwardVector;
    FVector StrikeOrigin = FVector::ZeroVector;
    FVector StrikeFootAnchors[2];
    FVector MoveVelocity=FVector::ZeroVector;
    float DeathAge=0, RejectFlash=0, LockYawOffset=0, LockPitchOffset=0;
    float HitFlash = 0;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UCapsuleComponent> Capsule;
    UPROPERTY(VisibleAnywhere) TObjectPtr<USkeletalMeshComponent> Body;
    UPROPERTY(VisibleAnywhere) TObjectPtr<USpringArmComponent> Arm;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UCameraComponent> Camera;
private:
    void Forward(float Value) { ForwardInput = AllowsGameplayInput()?Value:0; }
    void Right(float Value) { RightInput = AllowsGameplayInput()?Value:0; }
    void Turn(float Value);
    void Look(float Value);
    void ToggleLock();
    void Attack() { QueueAction(EWardenAction::Strike); }
    void MouseAttack() { if(!SuppressMouseAttack) Attack(); }
    void MouseAttackReleased() { SuppressMouseAttack=false; }
    void StartSprint() { SprintHeld=AllowsGameplayInput(); }
    void StopSprint() { SprintHeld=false; }
    void QuitMenu();
    void Dodge() { QueueAction(EWardenAction::Dodge); }
    void Heal() { QueueAction(EWardenAction::Heal); }
    void Restart();
    void PauseGame();
    void DebugGeometry();
    void CaptureEvidence();
    void StartFight();
    void TogglePilot();
    void ToggleMute();
    void ToggleMotion();
    void CycleSensitivity();
    void ToggleInspector();
    void ToggleRecording();
    void ToggleEvents();
    void ToggleController();
    void StartDemo();
    void ExportReport();
    float Sensitivity = 1.f;
    float ForwardInput = 0, RightInput = 0;
    double Accumulator = 0;
    bool bLocked = false;
    bool bCloseCameraHidden = false;
    TWeakObjectPtr<AActor> Target;
    UPROPERTY() TObjectPtr<UAnimationAsset> Locomotion;
    UPROPERTY() TArray<TObjectPtr<UAnimationAsset>> AttackAnimations;
    UPROPERTY() TObjectPtr<UAnimationAsset> DashAnimation;
    UPROPERTY() TObjectPtr<UAnimationAsset> IdleAnimation;
    int32 PresentedAction = -1;
};

// Opt-in dungeon dressing (-BossLabArena=dungeon). Presentation only: every added
// component is NoCollision, so the floor/wall/pillar collision actors stay authoritative.
struct FWardenDungeon
{
    TArray<TWeakObjectPtr<class ULightComponent>> Lights;
    TArray<float> Base;
    TWeakObjectPtr<class UInstancedStaticMeshComponent> Embers;
    TWeakObjectPtr<class UInstancedStaticMeshComponent> Dust;
    TArray<FVector> EmberSources;
    TWeakObjectPtr<class UInstancedStaticMeshComponent> Fire;
};

// Greybox visuals for the Regent's censer, chain, skulls and floor fire. Read-only view
// of FWardenRegentState; rebuilt from it every rendered frame.
struct FWardenRegentView
{
    static constexpr int32 Links=72, Flames=220, Discs=14;
    TWeakObjectPtr<AActor> Owner;
    TWeakObjectPtr<class UInstancedStaticMeshComponent> Censer, Chain, Bones, Eyes, Fire, Glint;
    bool bLantern=false, bLinks=false, bSkull=false;   // local props found (else primitives)
    TArray<TWeakObjectPtr<class UStaticMeshComponent>> Disc;
    TArray<TWeakObjectPtr<class UMaterialInstanceDynamic>> DiscMaterial;
    TWeakObjectPtr<class UPointLightComponent> Glow;
    TArray<FLinearColor> HallColors;
    bool bBlueHall=false;
};

UCLASS()
class BOSSLABWARDEN_API AWardenArenaMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    AWardenArenaMode();
    static void BuildDungeon(UWorld* World,FWardenDungeon& Out);
    static void AnimateDungeon(FWardenDungeon& Dungeon,float Seconds);
    bool bDungeon=false;
    FWardenDungeon Dungeon;
    bool bRegent=false, bRegentPhaseTwoStart=false;
    FWardenRegentState Regent;
    FWardenRegentView RegentView;
    void EnableRegent();
    void RegentDecide(FVector& BossDirection);
    void RegentResolve();
    FVector RegentAshTarget() const;
    void RegentSound(const TCHAR* Name,const FVector& At,float Volume);
    // Capture-only side-on review of every Regent move (-BossLabRegentStudy).
    bool bRegentStudy=false;
    int32 RegentStudyMove=WardenRegent::First, RegentStudyWait=90;
    TWeakObjectPtr<class ACameraActor> RegentStudyCamera;
    // Capture-only side-on locomotion review (-BossLabGaitStudy): scripted walking, no attacks.
    bool bGaitStudy=false;
    void GaitStudyStep(FVector& PlayerIntent,FVector& BossDirection);
    void RegentStudyStep();
    void BuildRegentView();
    void AnimateRegentView(float Seconds);
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void Tick(float DeltaSeconds) override;
    void FixedStep();
    void SetMenuOpen(bool Open);
    void QuitFromMenu();
    void DressArena();
    void ResetEncounter(bool RetainEvidence=false);
    void SaveReport();
    TArray<double> FrameMilliseconds;
    double LastFrameTime=0;
    int32 WarmupFrames=0;
    bool bBenchmark=false, bBenchmarkSaved=false, bCaptureFrames=false;
    int32 CaptureFrame=0, CaptureCount=180;
    FString ReviewTrace=TEXT("tick,player_action,player_age,player_health,stamina,boss_action,boss_age,boss_health,boss_poise,distance_cm\n");
    bool bMotionStudy=false;
    bool bArenaTour=false;  // capture-only slow 360° look around the arena
    bool bOutfitStudy=false;
    int32 RollStudyGroup=-1;
    FString MotionStudyTrace=TEXT("tick,action,age,stamina,grip_error_cm,x,y,z,protected\n");
    bool AcceptBossDecision(const FWardenDecision& Proposed);
    void ConfigureEncounter(int32 Seed, bool Scripted, int32 Style);
    UPROPERTY() TObjectPtr<AWardenChallenger> Player;
    UPROPERTY() TObjectPtr<AWardenChallenger> Warden;
    bool bPaused = false, bDebugGeometry = false, bTitle = true;
    int32 CombatTick = 0;
    int32 Encounter = 0;
    FWardenObservation Observation;
    FWardenDecision Decision;
    int32 MoveCounts[3] = {0,0,0};
    bool bScriptedPlayer = false;
    bool bMuted = false, bReducedMotion = false;
    bool bAdaptive=false, bInspector=false, bRecording=false, bEvents=false;
    bool bRehearsal=true;
    int32 RehearsalMove=0, RehearsalWait=100;
    bool bDemo=false, bReportSaved=false, bDecisionAccepted=false;
    int32 DemoTick=0, DemoRounds=0, DemoResetWait=0;
    int32 AcceptedTick=0, AcceptedMove=-1;
    float PlayerDamage=0, BossDamage=0;
    FWardenStatistics Statistics;
    FWardenPlayerScript PlayerScript;
    FString LastEvent = TEXT("Approach the Warden. Read the raised gauntlet.");
private:
    TSharedPtr<class SWidget> PauseMenuWidget;
    double CombatAccumulator = 0;
    TArray<FWardenObservation> VisibleHistory;
    FRandomStream PolicyRandom{101};
    int32 PolicySeed = 101;
    FVector LastPlayerPosition = FVector::ZeroVector;
};

UCLASS()
class BOSSLABWARDEN_API AWardenPrototypeHUD : public AHUD
{
    GENERATED_BODY()
public:
    virtual void DrawHUD() override;
    void DrawInspector(AWardenArenaMode* Mode);
};
