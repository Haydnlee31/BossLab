#include "WardenPrototype.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SkyLightComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/PlayerController.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Animation/BlendSpace.h"
#include "Animation/AnimSequence.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/SkeletalMeshActor.h"
#include "Engine/DirectionalLight.h"
#include "Engine/SkyLight.h"
#include "Engine/TextureCube.h"
#include "Engine/Canvas.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "UObject/ConstructorHelpers.h"
#include "DrawDebugHelpers.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Camera/CameraActor.h"

AWardenChallenger::AWardenChallenger()
{
    PrimaryActorTick.bCanEverTick = true;
    Capsule = CreateDefaultSubobject<UCapsuleComponent>(TEXT("Collision"));
    SetRootComponent(Capsule);
    Capsule->InitCapsuleSize(34, 90);
    Capsule->SetCollisionProfileName(TEXT("Pawn"));
    // Fighters must not retract the orbit camera into their own silhouettes.
    // Arena geometry still blocks Camera; pawn/blade collision is unchanged.
    Capsule->SetCollisionResponseToChannel(ECC_Camera,ECR_Ignore);
    Body = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Challenger"));
    Body->SetupAttachment(Capsule);
    // Flat-arena capsule clears the floor by 5 cm; the rendered feet remain on it.
    Body->SetRelativeLocation(FVector(0,0,-95));
    Body->SetRelativeRotation(FRotator(0,-90,0));
    Body->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    static ConstructorHelpers::FObjectFinder<USkeletalMesh> Mesh(TEXT("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"));
    if (Mesh.Succeeded()) Body->SetSkeletalMesh(Mesh.Object);
    Body->SetHiddenInGame(true);
    Body->SetCastShadow(false);
    Body->SetDisablePostProcessBlueprint(true);
    VisualBody=CreateDefaultSubobject<UPoseableMeshComponent>(TEXT("SwordFighter"));
    VisualBody->SetupAttachment(Capsule);
    VisualBody->SetRelativeLocation(FVector(0,0,-95));
    VisualBody->SetRelativeRotation(FRotator(0,-90,0));
    VisualBody->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    if(Mesh.Succeeded()) VisualBody->SetSkinnedAssetAndUpdate(Mesh.Object);
    VisualBody->SetComponentTickEnabled(false);
    SwordRoot=CreateDefaultSubobject<USceneComponent>(TEXT("Greatsword"));
    SwordRoot->SetupAttachment(VisualBody);
    Arm = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraArm"));
    Arm->SetupAttachment(Capsule);
    Arm->TargetArmLength = 500;
    Arm->SocketOffset = FVector(0,45,100);
    Arm->bUsePawnControlRotation = true;
    Arm->bDoCollisionTest = true;
    Arm->ProbeSize = 16;
    Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
    Camera->SetupAttachment(Arm);
    Camera->FieldOfView = 75;
}

void AWardenChallenger::BeginPlay()
{
    Super::BeginPlay();
    Locomotion = LoadObject<UBlendSpace>(nullptr,TEXT("/Game/Characters/Mannequins/Anims/Unarmed/BS_Idle_Walk_Run"));
    IdleAnimation = LoadObject<UAnimSequence>(nullptr,TEXT("/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle"));
    auto Ual=[](const TCHAR* Clip)->UAnimSequence*
    {
        for(const FString& Name:{FString::Printf(TEXT("UAL_Anims_root_UAL_%s"),Clip),FString::Printf(TEXT("UAL_Anims_UAL_%s"),Clip),FString::Printf(TEXT("UAL_%s"),Clip),FString(Clip)})
            if(auto* A=LoadObject<UAnimSequence>(nullptr,*(TEXT("/Game/BossLab/Anim/UAL/")+Name),nullptr,LOAD_Quiet|LOAD_NoWarn)) return A;
        return nullptr;
    };
    auto Hy=[](const TCHAR* Clip)->UAnimSequence*
    {
        return LoadObject<UAnimSequence>(nullptr,*FString::Printf(TEXT("/Game/BossLab/Anim/HY/HY_Anims_root_HY_%s"),Clip),nullptr,LOAD_Quiet|LOAD_NoWarn);
    };
    // Roll: the HY-Motion tucked ground roll by default; BOSSLAB_ANIM_ROLL=ual for the UAL dive
    // roll, =procedural for the keyed shoulder roll. The sprint loop (UAL) is on by default.
    ClipSprint=Ual(TEXT("Sprint_Loop"));
    const FString RollMode=FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_ANIM_ROLL")).ToLower();
    if(RollMode==TEXT("ual") || RollMode==TEXT("clip")) { ClipRoll=Ual(TEXT("Roll")); ClipRollFrom=.1f; ClipRollTo=1.f; }
    else if(RollMode!=TEXT("procedural") && (ClipRoll=Hy(TEXT("roll_s0")))!=nullptr) { ClipRollFrom=.15f; ClipRollTo=.75f; }   // the tumble, at ~1.25x (the whole clip moved joints ~50 cm a tick)
    // Cuts I-III: authored body (BOSSLAB_ANIM_CUTS=off keeps the keyed body).
    if(FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_ANIM_CUTS")).ToLower()!=TEXT("off"))
    {
        ClipCut0=Hy(TEXT("cut_a_s0")); ClipCut1=Hy(TEXT("cut_b_s1")); ClipCut2=Hy(TEXT("cut_heavy_s1"));
        ClipCutPeak[0]=.433f; ClipCutPeak[1]=.2f; ClipCutPeak[2]=.933f;   // retarget report: peak hand speed
    }
    Body->SetComponentTickEnabled(false);
    Body->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    Body->PlayAnimation(IdleAnimation,false);
    if(auto* A=Body->GetSingleNodeInstance()) A->SetPosition(0,false);
    Body->TickAnimation(0,false); Body->RefreshBoneTransforms();
    GuardBase=Body->GetBoneSpaceTransforms();
    CreateSword();
    CombatPose(FVector::ZeroVector);
    if (Controller) Controller->SetControlRotation(FRotator(-12,0,0));
}

void AWardenChallenger::PossessedBy(AController* NewController)
{
    Super::PossessedBy(NewController);
    NewController->SetControlRotation(FRotator(-12,0,0));
}

void AWardenChallenger::SetupPlayerInputComponent(UInputComponent* Input)
{
    Super::SetupPlayerInputComponent(Input);
    Input->BindAxis(TEXT("MoveForward"),this,&AWardenChallenger::Forward);
    Input->BindAxis(TEXT("MoveRight"),this,&AWardenChallenger::Right);
    Input->BindAxis(TEXT("Turn"),this,&AWardenChallenger::Turn);
    Input->BindAxis(TEXT("Look"),this,&AWardenChallenger::Look);
    Input->BindAction(TEXT("Lock"),IE_Pressed,this,&AWardenChallenger::ToggleLock);
    Input->BindAction(TEXT("Attack"),IE_Pressed,this,&AWardenChallenger::Attack);
    Input->BindAction(TEXT("MouseAttack"),IE_Pressed,this,&AWardenChallenger::MouseAttack);
    Input->BindAction(TEXT("MouseAttack"),IE_Released,this,&AWardenChallenger::MouseAttackReleased);
    Input->BindAction(TEXT("Sprint"),IE_Pressed,this,&AWardenChallenger::StartSprint);
    Input->BindAction(TEXT("Sprint"),IE_Released,this,&AWardenChallenger::StopSprint);
    Input->BindAction(TEXT("QuitMenu"),IE_Pressed,this,&AWardenChallenger::QuitMenu);
    Input->BindAction(TEXT("Dodge"),IE_Pressed,this,&AWardenChallenger::Dodge);
    Input->BindAction(TEXT("Jump"),IE_Pressed,this,&AWardenChallenger::JumpPressed);
    Input->BindAction(TEXT("Heal"),IE_Pressed,this,&AWardenChallenger::Heal);
    Input->BindAction(TEXT("Restart"),IE_Pressed,this,&AWardenChallenger::Restart);
    Input->BindAction(TEXT("Pause"),IE_Pressed,this,&AWardenChallenger::PauseGame);
    Input->BindAction(TEXT("Hints"),IE_Pressed,this,&AWardenChallenger::ToggleHints);
    Input->BindAction(TEXT("Debug"),IE_Pressed,this,&AWardenChallenger::DebugGeometry);
    Input->BindAction(TEXT("Capture"),IE_Pressed,this,&AWardenChallenger::CaptureEvidence);
    Input->BindAction(TEXT("Start"),IE_Pressed,this,&AWardenChallenger::StartFight);
    Input->BindAction(TEXT("Pilot"),IE_Pressed,this,&AWardenChallenger::TogglePilot);
    Input->BindAction(TEXT("Mute"),IE_Pressed,this,&AWardenChallenger::ToggleMute);
    Input->BindAction(TEXT("Motion"),IE_Pressed,this,&AWardenChallenger::ToggleMotion);
    Input->BindAction(TEXT("Sensitivity"),IE_Pressed,this,&AWardenChallenger::CycleSensitivity);
    Input->BindAction(TEXT("Inspector"),IE_Pressed,this,&AWardenChallenger::ToggleInspector);
    Input->BindAction(TEXT("Recording"),IE_Pressed,this,&AWardenChallenger::ToggleRecording);
    Input->BindAction(TEXT("Events"),IE_Pressed,this,&AWardenChallenger::ToggleEvents);
    Input->BindAction(TEXT("Controller"),IE_Pressed,this,&AWardenChallenger::ToggleController);

    Input->BindAction(TEXT("Export"),IE_Pressed,this,&AWardenChallenger::ExportReport);
}
void AWardenChallenger::Turn(float Value) { if(FMath::Abs(Value)>.01f) LookIdle=0; if(!AllowsGameplayInput()) return; if (!IsLocked()) AddControllerYawInput(Value*Sensitivity); else LockYawOffset=FMath::Clamp(LockYawOffset+Value*Sensitivity*.8f,-40.f,40.f); }
void AWardenChallenger::Look(float Value) { if(FMath::Abs(Value)>.01f) LookIdle=0; if(!AllowsGameplayInput()) return; if (!IsLocked()) AddControllerPitchInput(-Value*Sensitivity*(bInvertLook?-1.f:1.f)); else LockPitchOffset=FMath::Clamp(LockPitchOffset-Value*Sensitivity*.8f*(bInvertLook?-1.f:1.f),-18.f,14.f); }
void AWardenChallenger::ToggleLock() { if(!AllowsGameplayInput()) return; bLocked = !bLocked && Target.IsValid(); LockYawOffset=LockPitchOffset=0; }
FVector AWardenChallenger::GetTargetPosition() const { return Target.IsValid() ? Target->GetActorLocation()+FVector(0,0,45) : FVector::ZeroVector; }

void AWardenChallenger::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    HitFlash = FMath::Max(0.f,HitFlash-DeltaSeconds);
    RejectFlash = FMath::Max(0.f,RejectFlash-DeltaSeconds);
    if (!Controller) return;
    if(const auto* M=GetWorld()->GetAuthGameMode<AWardenArenaMode>(); M && M->bPaused) return;
    if(const auto* M=GetWorld()->GetAuthGameMode<AWardenArenaMode>(); M && M->bOutfitStudy)
    {
        // Explicit inspection-only camera. Combat camera and inputs remain unchanged.
        const int32 View=FMath::Clamp((M->CaptureFrame-61)/45,0,3);
        const float Angles[]={180,90,0,135};
        Arm->SocketOffset=FVector(0,0,0); Arm->TargetOffset=FVector(0,0,40); Arm->TargetArmLength=380;
        Controller->SetControlRotation(FRotator(-3,Angles[View],0));
        return;
    }

    const float CameraDistance = FVector::Distance(Camera->GetComponentLocation(), GetActorLocation());
    const bool HideBody = CameraDistance < (bCloseCameraHidden ? 200.f : 160.f);
    if (HideBody != bCloseCameraHidden)
    {
        bCloseCameraHidden = HideBody;
        VisualBody->SetOwnerNoSee(HideBody);
        TInlineComponentArray<UStaticMeshComponent*> Attachments(this);
        for (auto* Attachment : Attachments) Attachment->SetOwnerNoSee(HideBody);
    }
    if (!Target.IsValid())
        for (TActorIterator<AWardenChallenger> It(GetWorld()); It; ++It)
            if (It->ActorHasTag(TEXT("BossLabTarget"))) { Target = *It; break; }
    if (IsLocked() && FVector::DistSquared2D(GetActorLocation(), Target->GetActorLocation()) > FMath::Square(2400.f)) bLocked = false;
    FRotator View = Controller->GetControlRotation();
    const auto* CameraMode=GetWorld()->GetAuthGameMode<AWardenArenaMode>();
    const float Separation=IsLocked() && !(CameraMode && CameraMode->bMotionStudy)
        ? FMath::Clamp((500-FVector::Dist2D(GetActorLocation(),Target->GetActorLocation()))/300.f,0.f,1.f):0.f;
    // At contact, frame the pair around their midpoint rather than pushing the
    // player's feet below the viewport with an increasingly high shoulder socket.
    FVector PairOffset=FVector::ZeroVector;
    if(IsLocked()) { PairOffset=(Target->GetActorLocation()-GetActorLocation())*.5f; PairOffset.Z=30; }
    Arm->TargetOffset=FMath::VInterpTo(Arm->TargetOffset,PairOffset*Separation,DeltaSeconds,5.f);
    // Locked on (Elden Ring style): a raised camera looking down over the shoulder at the boss,
    // a little further back from the towering Regent so the pair stays in frame.
    const bool Towering=IsLocked() && CameraMode && CameraMode->bRegent;
    const float SocketZ=IsLocked() ? (Towering ? 150.f : 125.f) : 100.f;
    Arm->SocketOffset=FMath::VInterpTo(Arm->SocketOffset,FVector(0,45,SocketZ)*(1-Separation),DeltaSeconds,4.f);
    Arm->TargetArmLength=FMath::FInterpTo(Arm->TargetArmLength,((Towering ? 560.f : 500.f)+120*Separation)*CameraDistanceScale,DeltaSeconds,4.f);
    if (IsLocked())
    {
        // Aim at the boss's body (not its head, which towers over the camera) and always look down
        // a little, so the floor between the two reads and attacks are seen coming.
        FVector Aim = GetTargetPosition() - (GetActorLocation()+FVector(0,0,80));
        if(Towering) Aim.Z-=60;
        FRotator Desired = Aim.Rotation();
        Desired.Pitch = FMath::Clamp(FMath::Lerp(FMath::Min(Desired.Pitch-14.f,-12.f),-20.f,Separation)+LockPitchOffset,-38.f,4.f);
        Desired.Yaw+=35*Separation+LockYawOffset;
        // Mouse nudges hold while the mouse moves, then relax back over ~1.5 s.
        if(LookIdle>.8f)
        {
            LockYawOffset=FMath::FInterpTo(LockYawOffset,0.f,DeltaSeconds,1.6f);
            LockPitchOffset=FMath::FInterpTo(LockPitchOffset,0.f,DeltaSeconds,1.6f);
        }
        // Softer follow than a snap: the camera trails the boss's sidesteps slightly.
        View = FMath::RInterpTo(View,Desired,DeltaSeconds,4.5f);
    }
    // Option (default on): after ~1 s without look input, an unlocked moving camera eases back
    // behind the player's heading. Never swings round when running toward the camera.
    LookIdle+=DeltaSeconds;
    if(bCameraRecentre && !IsLocked() && LookIdle>1.f && MoveVelocity.SizeSquared2D()>FMath::Square(60.f))
    {
        const float Heading=GetActorRotation().Yaw;
        if(FMath::Abs(FRotator::NormalizeAxis(Heading-View.Yaw))<100.f)
            View.Yaw=FMath::FixedTurn(View.Yaw,Heading,DeltaSeconds*FMath::Clamp((LookIdle-1.f)*60.f,0.f,60.f));
    }
    View.Pitch = FMath::Clamp(FRotator::NormalizeAxis(View.Pitch),-55.f,25.f);
    if(auto* Mode=GetWorld()->GetAuthGameMode<AWardenArenaMode>(); Mode && Mode->bTitle) View=FRotator(-12,0,0);
    if(auto* Mode=GetWorld()->GetAuthGameMode<AWardenArenaMode>(); Mode && Mode->bMotionStudy) View=Mode->bArenaTour?FRotator(10,Mode->CaptureFrame*1.6f,0):Mode->MotionStudyView;
    View.Roll = 0;
    Controller->SetControlRotation(View);
}

void AWardenChallenger::SimulateMovement(const FVector& Direction, float DeltaSeconds)
{
    Accumulator += DeltaSeconds;
    // No dropped simulation time. This is the initial flat-arena kinematic authority.
    while (Accumulator >= 1.0/60.0)
    {
        Accumulator -= 1.0/60.0;
        MoveSwept(Direction.GetClampedToMaxSize(1.f) * (360.f/60.f));
    }
}

AWardenArenaMode::AWardenArenaMode()
{
    PrimaryActorTick.bCanEverTick = true;
    DefaultPawnClass = AWardenChallenger::StaticClass();
    HUDClass = AWardenPrototypeHUD::StaticClass();
}

void AWardenArenaMode::BeginPlay()
{
    Super::BeginPlay();
    UWorld* World = GetWorld();
    auto* Cube = LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube"));
    auto* Cylinder = LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cylinder"));
    auto Shape = [&](UStaticMesh* Mesh, FVector Position, FVector Scale, FRotator Rotation = FRotator::ZeroRotator)
    {
        auto* Actor = World->SpawnActor<AStaticMeshActor>(Position,Rotation);
        Actor->GetStaticMeshComponent()->SetStaticMesh(Mesh);
        Actor->SetActorScale3D(Scale);
        Actor->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
        return Actor;
    };
    Shape(Cylinder,FVector(0,0,-50),FVector(28,28,1));
    for(int32 Index=0;Index<32;++Index)
    {
        float Angle=Index*2.f*PI/32.f;
        FVector Position(FMath::Cos(Angle)*1360,FMath::Sin(Angle)*1360,130);
        Shape(Cube,Position,FVector(.55,2.8,2.6),FRotator(0,FMath::RadiansToDegrees(Angle),0));
        if (Index%4==0) Shape(Cylinder,Position+FVector(0,0,140),FVector(1.1,1.1,5.4));
    }
    auto* Sun = World->SpawnActor<ADirectionalLight>(FVector(0,0,700),FRotator(-45,-30,0));
    Sun->GetLightComponent()->SetMobility(EComponentMobility::Movable);
    Sun->GetLightComponent()->SetIntensity(3.f);
    Sun->GetLightComponent()->SetLightColor(FLinearColor(1,.78,.55));
    CastChecked<UDirectionalLightComponent>(Sun->GetLightComponent())->SetForwardShadingPriority(1);
    auto* Sky = World->SpawnActor<ASkyLight>();
    Sky->GetLightComponent()->SetMobility(EComponentMobility::Movable);
    // Original tiny ambient environment supplies broad reflections for the steel.
    // A captured empty sky supplied almost no fill with GI/reflection tracing off.
    auto* Ambient=UTextureCube::CreateTransient(16,16,PF_B8G8R8A8);
    Ambient->SRGB=true; Ambient->NeverStream=true;
    auto& Mip=Ambient->GetPlatformData()->Mips[0];
    auto* Pixels=static_cast<FColor*>(Mip.BulkData.Lock(LOCK_READ_WRITE));
    for(int32 Face=0;Face<6;++Face) for(int32 I=0;I<256;++I)
        Pixels[Face*256+I]=Face==4?FColor(140,148,160):Face==5?FColor(45,40,35):FColor(94,100,110);
    Mip.BulkData.Unlock(); Ambient->UpdateResource();
    Sky->GetLightComponent()->SourceType=SLS_SpecifiedCubemap;
    Sky->GetLightComponent()->bLowerHemisphereIsBlack=false;
    Sky->GetLightComponent()->SetCubemap(Ambient);
    Sky->GetLightComponent()->SetIntensity(.65f);
    Sky->GetLightComponent()->SetLightColor(FLinearColor(1,1,1));
    auto* Fill = World->SpawnActor<ADirectionalLight>(FVector(0,0,700),FRotator(-35,150,0));
    Fill->GetLightComponent()->SetMobility(EComponentMobility::Movable);
    Fill->GetLightComponent()->SetIntensity(2.f);
    Fill->GetLightComponent()->SetLightColor(FLinearColor(.55,.7,1));
    Fill->GetLightComponent()->SetCastShadows(false);
    Warden = World->SpawnActor<AWardenChallenger>(FVector(300,0,128),FRotator(0,180,0));
    Warden->SetActorScale3D(FVector(1.35));
    Warden->Tags.Add(TEXT("BossLabTarget"));
    if (auto* PC = World->GetFirstPlayerController())
    {
        Player = Cast<AWardenChallenger>(PC->GetPawn());
        PC->SetInputMode(FInputModeGameOnly());
        PC->bShowMouseCursor = false;
    }
    DressArena();
    BuildEffects();
    BuildSpectacle();
    if(FParse::Param(FCommandLine::Get(),TEXT("BossLabRegent"))) EnableRegent();
    bRegentPhaseTwoStart=bRegent && FParse::Param(FCommandLine::Get(),TEXT("BossLabRegentPhaseTwo"));
    SetupAudio();
    LoadSettings();
    ResetEncounter();
    bTitle=true;
    if(FParse::Param(FCommandLine::Get(),TEXT("BossLabCapture")))
    {
        ConfigureEncounter(202,true,1); bAdaptive=false; bCaptureFrames=true; bInspector=false; Player->SetLocked(true);
        int32 Seconds=6;
        if(FParse::Value(FCommandLine::Get(),TEXT("BossLabCaptureSeconds="),Seconds)) CaptureCount=30*FMath::Clamp(Seconds,6,30);
    }
    if(bCaptureFrames && (FParse::Param(FCommandLine::Get(),TEXT("BossLabMotionStudy")) || FParse::Value(FCommandLine::Get(),TEXT("BossLabRollStudy="),RollStudyGroup)))
    {
        bMotionStudy=true; bRehearsal=false; bScriptedPlayer=false; Player->SetLocked(false);
        bArenaTour=FParse::Param(FCommandLine::Get(),TEXT("BossLabArenaTour"));
        if(auto* PC=World->GetFirstPlayerController()) PC->SetControlRotation(FRotator(-12,-40,0));
    }
    if(bCaptureFrames && bRegent && FParse::Param(FCommandLine::Get(),TEXT("BossLabRegentStudy")))
    {
        bRegentStudy=true; bScriptedPlayer=false; Player->SetLocked(false);
        // Optional: start the review at one move (BOSSLAB_STUDY_FROM=<move index>).
        int32 From=0;
        if(FParse::Value(FCommandLine::Get(),TEXT("BossLabRegentStudyFrom="),From) && WardenRegent::IsRegent(From)) RegentStudyMove=From;
        auto* Camera=World->SpawnActor<ACameraActor>(FVector(150,-820,240),FRotator(-8,90,0));
        RegentStudyCamera=Camera;
        if(auto* PC=World->GetFirstPlayerController()) PC->SetViewTarget(Camera);
    }
    if(bCaptureFrames && FParse::Param(FCommandLine::Get(),TEXT("BossLabGaitStudy")))
    {
        bGaitStudy=true; bScriptedPlayer=false; bRehearsal=false; Player->SetLocked(false);
        Player->SetActorLocation(FVector(-350,0,95)); Warden->SetActorLocation(FVector(350,0,95*Warden->GetActorScale3D().Z));
        auto* Camera=World->SpawnActor<ACameraActor>(FVector(0,-1050,260),(FVector(0,0,110)-FVector(0,-1050,260)).Rotation());
        RegentStudyCamera=Camera;
        if(auto* PC=World->GetFirstPlayerController()) PC->SetViewTarget(Camera);
    }
    if(bCaptureFrames && FParse::Param(FCommandLine::Get(),TEXT("BossLabFeelStudy")))
    {
        bFeelStudy=true; bScriptedPlayer=false; bRehearsal=false; Player->SetLocked(false);
        Player->SetActorLocation(FVector(-350,0,95)); Warden->SetActorLocation(FVector(0,900,95*Warden->GetActorScale3D().Z));
        auto* Camera=World->SpawnActor<ACameraActor>(FVector(-350,-700,230),FRotator(-10,90,0));
        RegentStudyCamera=Camera;
        if(auto* PC=World->GetFirstPlayerController()) PC->SetViewTarget(Camera);
    }
    if(bCaptureFrames && FParse::Param(FCommandLine::Get(),TEXT("BossLabOutfitStudy")))
    {
        bOutfitStudy=true; bScriptedPlayer=false; bRehearsal=false; bMotionStudy=false; bTitle=false;
        Player->SetLocked(false); Warden->SetActorHiddenInGame(true);
        Player->Arm->SocketOffset=FVector(0,0,0); Player->Arm->TargetOffset=FVector(0,0,0); Player->Arm->TargetArmLength=300;
    }
    if(FParse::Param(FCommandLine::Get(),TEXT("BossLabBenchmark")))
    {
        ConfigureEncounter(202,true,3); bDemo=true; bAdaptive=false; bInspector=false; bBenchmark=true;
        Player->SetLocked(true);
    }
}

void AWardenPrototypeHUD::DrawHUD()
{
    Super::DrawHUD();
    if (!Canvas) return;
    auto* Mode = GetWorld()->GetAuthGameMode<AWardenArenaMode>();
    if (!Mode || !Mode->Player || !Mode->Warden) return;
    const auto& P = Mode->Player->Fight;
    const auto& B = Mode->Warden->Fight;
    const float W = Canvas->SizeX, H = Canvas->SizeY;
    auto Bar = [&](float X,float Y,float Width,float Value,FLinearColor Color)
    {
        DrawRect(FLinearColor(.025,.03,.035,.9),X-2,Y-2,Width+4,15);
        DrawRect(Color,X,Y,Width*FMath::Clamp(Value,0.f,1.f),11);
    };
    DrawRect(FLinearColor(.008,.014,.02,.75),20,18,300,110);
    DrawText(TEXT("BOSSLAB / THE WARDEN"),FColor(230,192,125),32,24,nullptr,1.3f);
    // Elden Ring style: a pale trail shows the health just lost before it drains away.
    const auto& Fx=Mode->Effects;
    Bar(32,58,260,(Fx.PlayerTrail>=0?Fx.PlayerTrail:P.Health)/P.MaxHealth,FLinearColor(.85,.72,.42));
    DrawRect(FLinearColor(.65,.13,.12),32,58,260*FMath::Clamp(P.Health/P.MaxHealth,0.f,1.f),11);
    Bar(32,78,260,P.Stamina/100,FLinearColor(.3,.6,.45));
    if(Mode->Player->RejectFlash>0) DrawRect(FLinearColor(1,.3,.12,Mode->Player->RejectFlash),30,76,264,15);
    DrawText(FString::Printf(TEXT("HP %.0f   STAMINA %.0f   HEALS %d"),P.Health,P.Stamina,P.Heals),FColor::White,32,100);
    if(!Mode->bRecording && Mode->Settings.bControlHints) DrawText(TEXT("WASD move | Shift sprint | Tab target | LMB cut (chain x3) | Space roll | F jump | E heal | Esc menu"),FColor(200,205,210),32,H-62);
    if(!Mode->bRecording && Mode->Settings.bControlHints) DrawText(TEXT("I controls | F5 boss rehearsal | F6 test pilot | F9 export | F1 clean | H hide hints"),FColor(170,180,190),32,H-42);
    if(!Mode->bRecording && (Mode->Player->RejectFlash>0 || (!Mode->LastEvent.StartsWith(TEXT("Not enough stamina")) && !Mode->LastEvent.StartsWith(TEXT("Heal unavailable"))))) DrawText(Mode->LastEvent,FColor(230,192,125),32,132);
    if(!Mode->bRecording)
    {
        const TCHAR* State=!P.Alive()?TEXT("FALLEN"):P.Action==EWardenAction::Heal?TEXT("HEAL / committed"):P.Action==EWardenAction::Hurt?TEXT("HIT / recovering"):P.Action==EWardenAction::Dodge?P.Invulnerable()?TEXT("ROLL / protected"):TEXT("ROLL / vulnerable"):P.Action==EWardenAction::Jump?TEXT("JUMP / attack to slam"):P.Action==EWardenAction::Strike?P.Active()?TEXT("CUT / contact"):P.Age<P.Definition().Windup?TEXT("CUT / wind-up"):TEXT("CUT / recovery"):P.Gap>0?TEXT("RECOVERING"):P.Sprinting?TEXT("SPRINTING"):TEXT("READY");
        DrawText(State,FColor(190,210,210),32,116);
    }
    if (Mode->bDemo) DrawText(FString::Printf(TEXT("PERFORMANCE / %s | Round %d | %.1fs | Resets disclosed"),TEXT("FIXED REHEARSAL"),Mode->DemoRounds+1,Mode->DemoTick/60.f),FColor(130,210,215),32,158);
    else if (Mode->bScriptedPlayer) DrawText(TEXT("SCRIPTED TEST PLAYER | Fixed rehearsal, real damage"),FColor(130,210,215),32,158);
    if(Mode->bOutfitStudy) DrawText(Mode->Player->bRevampOutfit?TEXT("REVAMP KNIGHT | Generated from approved concept / inspection camera"):Mode->Player->bV13Outfit?TEXT("LAST VIGIL V13 | Blender transfer test / rigid attachments"):TEXT("ASHBOUND KNIGHT | Authored 3D outfit study / inspection camera"),FColor(230,192,125),32,158);
    if(!Mode->bMotionStudy && !Mode->bOutfitStudy)
    {
        Bar(W*.25f,H-110,W*.5f,(Fx.BossTrail>=0?Fx.BossTrail:B.Health)/B.MaxHealth,FLinearColor(.85,.72,.42));
        DrawRect(FLinearColor(.62,.1,.07),W*.25f,H-110,W*.5f*FMath::Clamp(B.Health/B.MaxHealth,0.f,1.f),11);
        // Damage dealt by the latest flurry, beside the bar.
        if(Mode->Settings.bDamageNumbers && GetWorld()->GetTimeSeconds()-Fx.LastBossHit<2.5f && Fx.RecentDamage>0)
            DrawText(FString::Printf(TEXT("%.0f"),Fx.RecentDamage),FColor(240,225,200),W*.75f+12,H-114,nullptr,1.15f);
        DrawText(Mode->bRegent?TEXT("THE FUNERAL REGENT"):TEXT("THE WARDEN"),FColor(230,192,125),W*.25f,H-137,nullptr,1.2f);
        DrawText(FString::Printf(TEXT("STANCE %d / %d%s"),B.Poise,B.MaxPoise,B.Action==EWardenAction::Hurt?TEXT(" / BROKEN"):TEXT("")),FColor(190,205,210),W*.65f,H-137);
        if(Mode->bRegent) DrawText(FString::Printf(TEXT("SKULLS %d / 3%s"),Mode->Regent.ReadySkulls(),Mode->Regent.PhaseTwo?TEXT("   |   SECOND PHASE"):TEXT("")),FColor(150,190,255),W*.48f,H-137);
    }
    if (P.Alive() && B.Alive() && B.Action == EWardenAction::Strike)
    {
        const auto& Def = WardenRules::Strike(B.Move);
        const TCHAR* Phase = B.Age < Def.Windup ? TEXT("ANTICIPATION") : B.Active() ? TEXT("CONTACT") : TEXT("RECOVERY");
        DrawText(FString::Printf(TEXT("%s / %s"),Def.Name,Phase),FColor(240,190,110),W*.25f,H-88);
    }
    // A felled boss gets its moment (slow motion, the soul streaming away, the golden banner)
    // before the results panel opens over it (WardenSpectacle.cpp).
    const bool Moment=!B.Alive() && P.Alive() && Mode->Spectacle.FelledAt>0 && GetWorld()->GetTimeSeconds()-Mode->Spectacle.FelledAt<3.4f;
    if ((!P.Alive() || !B.Alive()) && !Mode->bPaused && !Moment)
    {
        DrawRect(FLinearColor(.015,.02,.025,.85),W*.25f,H*.35f,W*.5f,FMath::Max(190.f,H*.12f+150));
        DrawText(!P.Alive() ? TEXT("YOU FELL") : !B.Alive() ? (Mode->bRegent?TEXT("REGENT FALLEN"):TEXT("WARDEN FALLEN")) : TEXT("PAUSED"),FColor(230,192,125),W*.3f,H*.4f,nullptr,2.f);
        DrawText(P.Alive() && B.Alive() ? TEXT("P resume / R restart | M mute | F2 motion | F4 sensitivity") : TEXT("R to begin a fresh encounter"),FColor::White,W*.3f,H*.47f);
        if(!P.Alive() || !B.Alive())
        {
            DrawText(FString::Printf(TEXT("%.1fs | Damage dealt %.0f / taken %.0f"),Mode->CombatTick/60.f,Mode->PlayerDamage,Mode->BossDamage),FColor(185,205,211),W*.3f,H*.47f+28);
            DrawText(FString::Printf(TEXT("Warden moves %d / %d / %d | Observed exchanges %d"),Mode->MoveCounts[0],Mode->MoveCounts[1],Mode->MoveCounts[2],Mode->Statistics.Pooled.Samples),FColor(185,205,211),W*.3f,H*.47f+50);
            // Death recap and session record (WardenQoL.cpp); human attempts only.
            const auto& Run=Mode->Run;
            if(!P.Alive() && !Run.KilledBy.IsEmpty()) DrawText(FString::Printf(TEXT("Killed by: %s   |   Boss left at %.0f%%"),*Run.KilledBy,100*FMath::Max(B.Health,0.f)/B.MaxHealth),FColor(240,170,140),W*.3f,H*.47f+76,nullptr,1.1f);
            if(Run.Attempts>0) DrawText(FString::Printf(TEXT("Attempt %d | Deaths %d | Victories %d | Best: boss at %.0f%%%s%s"),Run.Attempts,Run.Deaths,Run.Victories,100*Run.BestBossFraction,
                Run.BestVictorySeconds>0?*FString::Printf(TEXT(" | Fastest win %.1fs"),Run.BestVictorySeconds):TEXT(""),Run.bPractice?TEXT(" | PRACTICE (not recorded)"):TEXT("")),FColor(185,205,211),W*.3f,H*.47f+100);
        }
    }
    if(Mode->Player->bV13Outfit) DrawText(TEXT("V13 TEST | Approximate rigid fitting / simplified materials"),FColor(230,192,125),32,258);
    if(Mode->Player->bRevampOutfit) DrawText(TEXT("REVAMP TEST | Generated characters / distance-weighted skin, no cloth sim"),FColor(230,192,125),32,258);
    if(Mode->bCaptureFrames) DrawText(TEXT("ENGINE FRAME CAPTURE / fixed 30 fps / not a real-time benchmark"),FColor(230,192,125),32,184);
    // The boss's name as the fight opens (fades in and out over four seconds) and an Elden
    // Ring-style golden banner when it falls.
    auto Banner=[&](const TCHAR* Text,const TCHAR* Sub,float Alpha,FColor Colour,float Top)
    {
        if(Alpha<=0) return;
        float TW=0,TH=0; GetTextSize(Text,TW,TH,nullptr,2.6f);
        DrawRect(FLinearColor(0,0,0,.45f*Alpha),0,H*Top,W,H*.14f);
        DrawText(Text,FColor(Colour.R,Colour.G,Colour.B,uint8(255*Alpha)),(W-TW)*.5f,H*(Top+.02f),nullptr,2.6f);
        if(Sub) { float SW=0,SH=0; GetTextSize(Sub,SW,SH,nullptr,1.1f); DrawText(Sub,FColor(200,205,210,uint8(220*Alpha)),(W-SW)*.5f,H*(Top+.02f)+TH+4,nullptr,1.1f); }
    };
    if(!Mode->bMotionStudy && !Mode->bOutfitStudy && !Mode->bRegentStudy && !Mode->bGaitStudy && !Mode->bFeelStudy && B.Alive() && P.Alive())
    {
        const float T=Mode->CombatTick/60.f;
        Banner(Mode->bRegent?TEXT("THE FUNERAL REGENT"):TEXT("THE WARDEN"),Mode->bRegent?TEXT("Keeper of the Last Rites"):TEXT("Gaoler of the Ring"),FMath::Clamp(T/.6f,0.f,1.f)*FMath::Clamp((4-T)/.8f,0.f,1.f),FColor(230,200,140),.42f);
    }
    // Above the results panel, which opens in the middle of the screen.
    if(!B.Alive() && P.Alive()) Banner(TEXT("GREAT ENEMY FELLED"),nullptr,FMath::Clamp(Mode->Warden->DeathAge/24.f,0.f,1.f),FColor(235,190,95),.14f);
    if(Mode->bMotionStudy)
    {
        DrawText(Mode->RollStudyGroup<0?TEXT("SCRIPTED MOTION STUDY / normal stamina and commitment"):
            Mode->RollStudyGroup==0?TEXT("SCRIPTED ROLLS / world forward, right, back, left / normal costs"):
            TEXT("SCRIPTED ROLLS / four world diagonals / normal costs"),FColor(110,220,220),32,208);
        const bool Protected=Mode->Player->Fight.Invulnerable();
        DrawText(FString::Printf(TEXT("ROLL WINDOW: %s | age %d / 36 | protection ages 4-17"),Protected?TEXT("PROTECTED"):TEXT("VULNERABLE"),Mode->Player->Fight.Age),Protected?FColor(100,240,170):FColor(230,190,140),32,232);
    }
    DrawInspector(Mode);
    if (Mode->Player->HitFlash > 0 && !Mode->bReducedMotion) DrawRect(FLinearColor(.7,.03,.01,Mode->Player->HitFlash),0,0,W,H);
    DrawText(Mode->bRehearsal?(Mode->bRegent?TEXT("REGENT GREYBOX / FIXED SEQUENCE"):TEXT("FIXED ATTACK REHEARSAL")):TEXT("PRACTICE DUMMY"),FColor(180,195,200),W-285,28);
    // Fight clock and attempt number (WardenQoL.cpp), human attempts only.
    if(!Mode->bTitle && !Mode->bRecording && Mode->Run.bCounted)
    {
        const int32 Secs=Mode->CombatTick/60;
        DrawText(FString::Printf(TEXT("TIME %d:%02d   |   ATTEMPT %d"),Secs/60,Secs%60,Mode->Run.Attempts),FColor(180,195,200),W-285,48);
    }
    if(!Mode->bTitle && Mode->bPracticeInfiniteHealth) DrawText(TEXT("PRACTICE / INFINITE HEALTH"),FColor(255,140,110),W-285,68);
    if (Mode->bTitle)
    {
        DrawRect(FLinearColor(.01,.015,.02,.93),W*.18f,H*.2f,W*.64f,H*.55f);
        DrawText(TEXT("THE WARDEN"),FColor(230,192,125),W*.24f,H*.28f,nullptr,3.f);
        DrawText(TEXT("Combat fundamentals / temporary character rigs"),FColor::White,W*.24f,H*.4f,nullptr,1.2f);
        DrawText(TEXT("ENTER to challenge"),FColor(230,192,125),W*.24f,H*.5f,nullptr,1.5f);
        DrawText(TEXT("Two-handed greatsword. Fixed attack rehearsal. AI deferred."),FColor(180,195,200),W*.24f,H*.59f);
        DrawText(TEXT("Tab target / Space roll / Shift sprint / Esc menu."),FColor(180,195,200),W*.24f,H*.64f);
        DrawText(TEXT("F6: watch a labeled development player"),FColor(130,210,215),W*.24f,H*.69f);
        // CC BY attribution for the sounds in use (see CREDITS.md).
        DrawText(TEXT("Sound: \"Ghost Manifestation 1\" by OGsoundFX, \"Scattered Ghost\" by qubodup (CC BY); belarathbone, Kenney (CC0)"),FColor(120,130,135),W*.24f,H*.72f,nullptr,.8f);
    }
    if (auto* Player = Cast<AWardenChallenger>(GetOwningPawn()); Player && Player->IsLocked() && !Mode->bPaused)
    {
        FVector2D Screen;
        if (GetOwningPlayerController()->ProjectWorldLocationToScreen(Player->GetTargetPosition(),Screen))
        {
            DrawLine(Screen.X-7,Screen.Y,Screen.X+7,Screen.Y,FLinearColor(1,.75,.3),2);
            DrawLine(Screen.X,Screen.Y-7,Screen.X,Screen.Y+7,FLinearColor(1,.75,.3),2);
        }
    }
}
