// Opt-in environment inspection. No boss actor, combat controller or encounter audio.
#include "WardenPrototype.h"
#include "WardenSmelteryLayout.h"
#include "WardenBellbreaker.h"
#include "Engine/World.h"
#include "Engine/GameViewportClient.h"
#include "Camera/CameraComponent.h"
#include "HAL/PlatformTime.h"
#include "Engine/StaticMeshActor.h"
#include "Animation/SkeletalMeshActor.h"
#include "Animation/AnimSequence.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "ReferenceSkeleton.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Engine/DirectionalLight.h"
#include "Engine/PointLight.h"
#include "Engine/SpotLight.h"
#include "Components/SpotLightComponent.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/PostProcessVolume.h"
#include "Components/BrushComponent.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Components/PointLightComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "HAL/FileManager.h"
#include "UnrealClient.h"
#include "Components/StaticMeshComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"


// Bell hammer in the Bellbreaker's right fist (2026-11-18, presentation only). The grip is solved from the
// rig's reference pose instead of hand-tuned numbers: the haft runs through the fist along the knuckle
// line (index -> pinky, bell beyond the pinky) with the bell GripToBell cm from the right hand, leaving
// room for the left hand toward the butt. SM_BellHammerGen: bell at the origin, haft along +Z (3.2 m).
UStaticMeshComponent* WardenAttachBellHammer(AActor* Owner,USkeletalMeshComponent* C,float WorldScale)
{
    UStaticMesh* Mesh=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/BossLab/Bellbreaker/SM_BellHammerGen"),nullptr,LOAD_Quiet|LOAD_NoWarn);
    USkeletalMesh* Rig=C?C->GetSkeletalMeshAsset():nullptr;
    if(!Mesh||!Rig)return nullptr;
    const FReferenceSkeleton& Ref=Rig->GetRefSkeleton();
    TArray<FTransform> CS; CS.SetNum(Ref.GetNum());
    for(int32 i=0;i<Ref.GetNum();++i)
    {
        const int32 P=Ref.GetParentIndex(i);
        CS[i]=P==INDEX_NONE?Ref.GetRefBonePose()[i]:Ref.GetRefBonePose()[i]*CS[P];
    }
    auto At=[&](const TCHAR* Name){const int32 I=Ref.FindBoneIndex(Name);return I==INDEX_NONE?FVector::ZeroVector:CS[I].GetLocation();};
    const int32 HandIndex=Ref.FindBoneIndex(TEXT("hand_r"));
    if(HandIndex==INDEX_NONE)return nullptr;
    const FVector Hand=At(TEXT("hand_r")), Index=At(TEXT("index_01_r")), Pinky=At(TEXT("pinky_01_r")), Middle=At(TEXT("middle_01_r"));
    const FVector Grip=Hand+.55f*(Middle-Hand);
    const FVector ToBell=(Pinky-Index).GetSafeNormal();
    const float GripToBell=230.f/WorldScale;
    const FMatrix R=FRotationMatrix::MakeFromZX(-ToBell,(Middle-Hand).GetSafeNormal());
    const FTransform HammerCS(R.ToQuat(),Grip+ToBell*GripToBell,FVector(1.f/WorldScale));
    auto* H=NewObject<UStaticMeshComponent>(Owner);
    H->SetStaticMesh(Mesh); H->SetCollisionEnabled(ECollisionEnabled::NoCollision); H->SetMobility(EComponentMobility::Movable);
    H->SetupAttachment(C,TEXT("hand_r")); H->RegisterComponent();
    H->SetRelativeTransform(HammerCS.GetRelativeTransform(CS[HandIndex]));
    return H;
}


// Bell Quake preview (BOSSLAB_BELLBREAKER_PREVIEW=quake, 2026-11-18): presentation of the planned move in
// docs/BELLBREAKER_MOVESET_PLAN.md, no combat rules. The boss loops the HY bell-quake slam; at its impact
// a shockwave ring (M_BB_Shockwave) expands along the floor with the generated bell/shockwave sounds, and a
// player-sized mannequin in its path plays the stun clip when the crest reaches it. Times are clip seconds.
namespace BellQuake
{
    constexpr float Impact=1.18f, RingSpeed=850.f, RingStart=120.f, RingEnd=1000.f;
    struct FState
    {
        TWeakObjectPtr<USkeletalMeshComponent> Boss, Victim;
        TWeakObjectPtr<UStaticMeshComponent> Ring, Hammer;
        TWeakObjectPtr<UMaterialInstanceDynamic> Mid;
        TWeakObjectPtr<UAnimSequence> Stun;
        TWeakObjectPtr<USoundBase> Tell, Slam, Wave, Ears;
        FVector Origin=FVector::ZeroVector; float VictimDistance=0, Last=-1; bool bVictimHit=false;
    };
    static FState G;
    static USoundBase* Sound(const TCHAR* Name){return LoadObject<USoundBase>(nullptr,*FString::Printf(TEXT("/Game/BossLab/Bellbreaker/Sound/S_%s"),Name),nullptr,LOAD_Quiet|LOAD_NoWarn);}
    static void Tick(UWorld* World)
    {
        USkeletalMeshComponent* B=G.Boss.Get(); if(!B)return;
        const float T=B->GetPosition(); const float Prev=G.Last; G.Last=T;
        auto Crossed=[&](float At){return Prev>=0 && ((Prev<At && T>=At) || (T<Prev && At<=T));};
        if(Prev>=0 && T<Prev){G.bVictimHit=false;}
        if(Crossed(.05f)&&G.Tell.IsValid())UGameplayStatics::PlaySoundAtLocation(World,G.Tell.Get(),G.Origin);
        if(Crossed(Impact))
        {
            // Centre the shockwave where the bell actually lands (the hammer mesh origin is the bell).
            if(UStaticMeshComponent* H=G.Hammer.Get()){const FVector Bell=H->GetComponentLocation(); G.Origin=FVector(Bell.X,Bell.Y,0);}
            if(UStaticMeshComponent* R=G.Ring.Get())R->SetWorldLocation(G.Origin+FVector(0,0,6));
            if(USkeletalMeshComponent* V=G.Victim.Get())G.VictimDistance=FVector::Dist2D(V->GetComponentLocation(),G.Origin);
            if(G.Slam.IsValid())UGameplayStatics::PlaySoundAtLocation(World,G.Slam.Get(),G.Origin);
        }
        if(Crossed(Impact+.05f)&&G.Wave.IsValid())UGameplayStatics::PlaySoundAtLocation(World,G.Wave.Get(),G.Origin);
        const float Radius=T>=Impact?RingStart+(T-Impact)*RingSpeed:-1;
        if(UStaticMeshComponent* R=G.Ring.Get())
        {
            const bool bOn=Radius>0 && Radius<RingEnd;
            R->SetVisibility(bOn);
            if(bOn){R->SetWorldScale3D(FVector(Radius/50.f,Radius/50.f,1)); if(auto* M=G.Mid.Get())M->SetScalarParameterValue(TEXT("Fade"),FMath::Clamp(1.f-(Radius-RingStart)/(RingEnd-RingStart),0.f,1.f));}
        }
        if(USkeletalMeshComponent* V=G.Victim.Get())
        {
            if(!G.bVictimHit && Radius>=G.VictimDistance){G.bVictimHit=true; if(G.Ears.IsValid())UGameplayStatics::PlaySoundAtLocation(World,G.Ears.Get(),V->GetComponentLocation());}
            const float Into=G.bVictimHit?(T-Impact-(G.VictimDistance-RingStart)/RingSpeed):0.f;
            const float Len=G.Stun.IsValid()?G.Stun->GetPlayLength():1.f;
            V->SetPosition(FMath::Clamp(Into,0.f,Len-.01f),false);
        }
    }
}

void AWardenArenaMode::RecordStartupCamera(const TCHAR* Event,float AxisValue)
{
    if(!bStartupCameraDiagnostic || StartupCameraLogCount>=80 || !Player)return;
    if(FCString::Strncmp(Event,TEXT("raw_"),4)==0)
    {if(StartupCameraAxisLogCount>=48)return;++StartupCameraAxisLogCount;}
    const double Age=FPlatformTime::Seconds()-StartupCameraTime;
    if(Age>10)return;
    auto* PC=GetWorld()->GetFirstPlayerController();if(!PC)return;
    auto* ViewportClient=GetWorld()->GetGameViewport();
    const int32 Focus=(ViewportClient && ViewportClient->Viewport)?int32(ViewportClient->Viewport->HasFocus()):-1;
    ++StartupCameraLogCount;
    UE_LOG(LogTemp,Display,TEXT("BOSSLAB CAMERA STARTUP t=%.3f event=%s raw_axis=%.6f focus=%d control=%s pawn=%s eye=%s eye_rotation=%s arm=%.2f target_offset=%s socket_offset=%s actual_distance=%.2f"),
        Age,Event,AxisValue,Focus,*PC->GetControlRotation().ToString(),*Player->GetActorLocation().ToString(),
        *Player->Camera->GetComponentLocation().ToString(),*Player->Camera->GetComponentRotation().ToString(),
        Player->Arm->TargetArmLength,*Player->Arm->TargetOffset.ToString(),*Player->Arm->SocketOffset.ToString(),
        FVector::Distance(Player->Camera->GetComponentLocation(),Player->GetActorLocation()));
}

void AWardenArenaMode::BeginSmelteryWalkthrough()
{
    bSmelteryWalkthrough=true; bFrontendSession=true; bTitle=false; bPaused=false;
    bRehearsal=false; bAdaptive=false; bScriptedPlayer=false; bRegent=false;
    bHearthA2=bHearthA2 || FParse::Param(FCommandLine::Get(),TEXT("BossLabHearthA2"));
    bHearthA=bHearthA2 || bHearthA || FParse::Param(FCommandLine::Get(),TEXT("BossLabHearthA"));
    bStartupCameraDiagnostic=FParse::Param(FCommandLine::Get(),TEXT("BossLabCameraDiagnostic"));
    bStartupEntryCapture=FParse::Param(FCommandLine::Get(),TEXT("BossLabEntryCapture"));
    StartupCameraTime=FPlatformTime::Seconds();StartupCameraNextSample=0;StartupCameraLogCount=StartupCameraAxisLogCount=0;bStartupEntryCaptured=false;
    bSmelteryTiming=FParse::Param(FCommandLine::Get(),TEXT("BossLabSmelteryTiming"));
    SmelteryStudyDistance=0;SmelteryWaypointArrivals=SmelteryLastMovementTick=0;SmelteryStudyStops.Reset();
    MotionStudyTrace.Empty(); FrameMilliseconds.Reset(); DemoTick=0; DemoRounds=0; DemoResetWait=0;
    const FString Folder=bHearthA2?TEXT("HearthA2"):(bHearthA?TEXT("HearthA"):TEXT("Smeltery"));
    const FString AssetRoot=TEXT("/Game/BossLab/")+Folder+TEXT("/");
    const FString Layout=FPaths::ProjectContentDir()/TEXT("BossLab")/Folder/TEXT("layout.json");
    FString Json;TSharedPtr<FJsonObject> Root;
    const bool Parsed=FFileHelper::LoadFileToString(Json,*Layout) && FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Json),Root) && Root.IsValid();
    SmelteryHalfSize=bHearthA?FVector2D(1000,1200):FVector2D(1400,1800);
    SmelterySpawn=bHearthA?FVector(600,-800,95):FVector(0,-1200,95);
    SmelteryEntry=FRotator(-12,bHearthA?110.55605f:90.f,0);
    bool OuterCamera=false;
    if(bHearthA2)
    {
        WardenSmelteryLayout::FLayout Validated;FString Error;
        if(!Parsed || !WardenSmelteryLayout::Validate(Root,Validated,Error))
        {
            UE_LOG(LogTemp,Error,TEXT("A2 layout rejected before world construction: %s"),*Error);
            bPaused=true;FPlatformMisc::RequestExit(false);return;
        }
        // Resolve all required meshes before creating even the floor.
        for(const auto& Value:Root->GetArrayField(TEXT("instances")))
            if(!LoadObject<UStaticMesh>(nullptr,*Value->AsObject()->GetStringField(TEXT("asset"))))
            {UE_LOG(LogTemp,Error,TEXT("A2 required mesh missing; import the complete A2 scene first"));bPaused=true;FPlatformMisc::RequestExit(false);return;}
        SmelteryHalfSize=Validated.HalfSize;SmelterySpawn=Validated.Spawn;SmelteryEntry=Validated.Entry;OuterCamera=Validated.bOuterCamera;SmelteryStudyStops=Validated.StudyStops;
    }
    const float HalfWidth=SmelteryHalfSize.X,HalfLength=SmelteryHalfSize.Y;
    UWorld* World=GetWorld();
    auto Box=[&](FVector Position,FVector Scale,const TCHAR* Tag)
    {
        auto* A=World->SpawnActor<AStaticMeshActor>(Position,FRotator::ZeroRotator);
        A->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube")));
        A->SetActorScale3D(Scale); A->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
        A->SetActorHiddenInGame(true); A->Tags.Add(Tag);
        // The walkthrough can survey the outer bays. During combat the longer
        // lock-on boom must retract before the opaque racks behind the field.
        if(OuterCamera && !bForgeArena && FCString::Strcmp(Tag,TEXT("SmelteryBoundary"))==0)
            A->GetStaticMeshComponent()->SetCollisionResponseToChannel(ECC_Camera,ECR_Ignore);
        return A;
    };
    // Fixed floor: current locomotion assumes a level surface. Art is outside this
    // rectangle in older variants; A2 also has authored prop islands. Field
    // walls block pawn; explicit outer-camera mode uses separate enclosing proxies.
    Box(FVector(0,0,-50),FVector(HalfWidth*.02f,HalfLength*.02f,1),TEXT("SmelteryFloor"));
    for(int32 Sign : {-1,1})
    {
        Box(FVector(Sign*(HalfWidth+50),0,850),FVector(1,HalfLength*.02f+2,18),TEXT("SmelteryBoundary"));
        Box(FVector(0,Sign*(HalfLength+50),850),FVector(HalfWidth*.02f,1,18),TEXT("SmelteryBoundary"));
    }
    int32 Loaded=0;
    if(Parsed)
    {
        if(Root.IsValid())
        {
            const TArray<TSharedPtr<FJsonValue>>* Lights=nullptr;
            if(Root->TryGetArrayField(TEXT("lights"),Lights))for(int32 I=0;I<FMath::Min(bHearthA?6:4,Lights->Num());++I)
            {
                const auto O=(*Lights)[I]->AsObject(); if(!O.IsValid())continue;
                const TArray<TSharedPtr<FJsonValue>> *P=nullptr,*C=nullptr;
                if(!O->TryGetArrayField(TEXT("location_cm"),P) || P->Num()!=3 || !O->TryGetArrayField(TEXT("color_rgb"),C) || C->Num()!=3)continue;
                const FVector Position((*P)[0]->AsNumber(),(*P)[1]->AsNumber(),(*P)[2]->AsNumber());
                if(Position.ContainsNaN())continue;
                double Power=10000,Radius=1500;
                O->TryGetNumberField(TEXT("intensity_lumens"),Power);O->TryGetNumberField(TEXT("attenuation_radius_cm"),Radius);
                FString Type; O->TryGetStringField(TEXT("type"),Type);
                ALight* L=nullptr;
                if(bHearthA && Type==TEXT("spot"))
                {
                    const TArray<TSharedPtr<FJsonValue>>* Target=nullptr;
                    if(!O->TryGetArrayField(TEXT("target_cm"),Target) || Target->Num()!=3)continue;
                    const FVector Aim((*Target)[0]->AsNumber(),(*Target)[1]->AsNumber(),(*Target)[2]->AsNumber());
                    if(Aim.ContainsNaN())continue;
                    auto* Spot=World->SpawnActor<ASpotLight>(Position,(Aim-Position).Rotation());
                    auto* SC=CastChecked<USpotLightComponent>(Spot->GetLightComponent());
                    double Inner=16,Outer=27;
                    O->TryGetNumberField(TEXT("inner_angle_deg"),Inner);O->TryGetNumberField(TEXT("outer_angle_deg"),Outer);
                    SC->SetOuterConeAngle(FMath::Clamp(float(Outer),1.f,80.f));
                    SC->SetInnerConeAngle(FMath::Clamp(float(Inner),0.f,SC->OuterConeAngle));
                    SC->SetVolumetricScatteringIntensity(bHearthA2?2.2f:4.f);   // A2 concept pass: a visible cool shaft through the haze
                    L=Spot;
                }
                else L=World->SpawnActor<APointLight>(Position,FRotator::ZeroRotator);
                auto* Light=CastChecked<UPointLightComponent>(L->GetLightComponent());
                bool Shadows=false; O->TryGetBoolField(TEXT("casts_shadows"),Shadows);
                Light->SetMobility(EComponentMobility::Movable);Light->SetCastShadows(bHearthA && Type==TEXT("spot") && Shadows);
                Light->SetIntensityUnits(ELightUnits::Lumens);Light->SetIntensity(FMath::Clamp(float(Power),0.f,80000.f));
                Light->SetAttenuationRadius(FMath::Clamp(float(Radius),100.f,4000.f));
                if(bHearthA2)
                {
                    double Source=0,Soft=0;O->TryGetNumberField(TEXT("source_radius_cm"),Source);O->TryGetNumberField(TEXT("soft_source_radius_cm"),Soft);
                    Light->SetSourceRadius(Source);Light->SetSoftSourceRadius(Soft);
                }
                Light->SetLightColor(FLinearColor((*C)[0]->AsNumber(),(*C)[1]->AsNumber(),(*C)[2]->AsNumber()));
                L->Tags.Add(TEXT("SmelteryLight"));
            }
            const TArray<TSharedPtr<FJsonValue>>* CameraBoxes=nullptr;
            if(bHearthA && Root->TryGetArrayField(TEXT("camera_collision"),CameraBoxes))for(const auto& Value:*CameraBoxes)
            {
                const auto O=Value->AsObject(); if(!O.IsValid())continue;
                const TArray<TSharedPtr<FJsonValue>> *P=nullptr,*E=nullptr;
                if(!O->TryGetArrayField(TEXT("location_cm"),P)||P->Num()!=3||!O->TryGetArrayField(TEXT("extent_cm"),E)||E->Num()!=3)continue;
                const FVector Position((*P)[0]->AsNumber(),(*P)[1]->AsNumber(),(*P)[2]->AsNumber());
                const FVector Extent((*E)[0]->AsNumber(),(*E)[1]->AsNumber(),(*E)[2]->AsNumber());
                if(Position.ContainsNaN()||Extent.ContainsNaN()||Extent.GetMin()<=0)continue;
                auto* A=Box(Position,Extent*.02f,TEXT("SmelteryCameraBoundary"));
                A->GetStaticMeshComponent()->SetCollisionResponseToAllChannels(ECR_Ignore);
                A->GetStaticMeshComponent()->SetCollisionResponseToChannel(ECC_Camera,ECR_Block);
            }
            if(bHearthA2)for(const auto& Value:Root->GetArrayField(TEXT("prop_collision")))
            {
                const auto O=Value->AsObject();FVector Position,Extent;
                WardenSmelteryLayout::Vector(O,TEXT("location_cm"),Position);
                WardenSmelteryLayout::Vector(O,TEXT("extent_cm"),Extent);
                auto* A=Box(Position,Extent*.02f,TEXT("SmelteryPropBoundary"));
                A->SetActorRotation(FRotator(0,O->GetNumberField(TEXT("yaw_deg")),0));
                A->GetStaticMeshComponent()->SetCollisionResponseToAllChannels(ECR_Ignore);
                A->GetStaticMeshComponent()->SetCollisionResponseToChannel(ECC_Pawn,ECR_Block);
                A->GetStaticMeshComponent()->SetCollisionResponseToChannel(ECC_Camera,ECR_Block);
            }
            const TArray<TSharedPtr<FJsonValue>>* Instances=nullptr;
            if(Root->TryGetArrayField(TEXT("instances"),Instances))for(const auto& Value:*Instances)
            {
                const auto O=Value->AsObject(); if(!O.IsValid())continue;
                FString Path; if(!O->TryGetStringField(TEXT("asset"),Path) || !Path.StartsWith(AssetRoot) || Path.Contains(TEXT("..")))continue;
                auto Vector=[&](const TCHAR* Key,FVector Default)
                {
                    const TArray<TSharedPtr<FJsonValue>>* V=nullptr;
                    if(!O->TryGetArrayField(Key,V) || V->Num()!=3)return Default;
                    const FVector Out((*V)[0]->AsNumber(),(*V)[1]->AsNumber(),(*V)[2]->AsNumber());
                    return Out.ContainsNaN()?Default:Out;
                };
                if(auto* Mesh=LoadObject<UStaticMesh>(nullptr,*Path))
                {
                    const FVector R=Vector(TEXT("rotation_deg"),FVector::ZeroVector);
                    auto* A=World->SpawnActor<AStaticMeshActor>(Vector(TEXT("location_cm"),FVector::ZeroVector),FRotator(R.X,R.Y,R.Z));
                    A->GetStaticMeshComponent()->SetStaticMesh(Mesh); A->SetActorScale3D(Vector(TEXT("scale"),FVector::OneVector));
                    A->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
                    A->Tags.Add(TEXT("SmelteryDressing")); ++Loaded;
                }
            }
        }
    }
    // A2 forge fire: a looping flipbook from a generated fire video (M_A2_ForgeFlipbook,
    // ue_forge_fire.py) on three crossed vertical planes in each furnace mouth
    // (layout hearth_effect_anchors_cm), plus a dim inner glow. NoCollision presentation only.
    if(bHearthA2 && Parsed && Root.IsValid())
    {
        auto* FlameMat=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/BossLab/HearthA2/Fire/M_A2_ForgeFlipbook"),nullptr,LOAD_Quiet|LOAD_NoWarn);
        auto* GlowMat=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/BossLab/HearthA2/M_A2_ForgeFire"),nullptr,LOAD_Quiet|LOAD_NoWarn);
        const TArray<TSharedPtr<FJsonValue>>* Anchors=nullptr;
        if(Root->TryGetArrayField(TEXT("hearth_effect_anchors_cm"),Anchors))for(const auto& Value:*Anchors)
        {
            const TArray<TSharedPtr<FJsonValue>>* A=nullptr;
            if(!Value->TryGetArray(A) || A->Num()!=3)continue;
            const FVector At((*A)[0]->AsNumber(),(*A)[1]->AsNumber(),(*A)[2]->AsNumber());
            if(At.ContainsNaN())continue;
            auto Spawn=[&](const TCHAR* Shape,UMaterialInterface* M,FVector Loc,FRotator Rot,FVector Scale)
            {
                auto* X=World->SpawnActor<AStaticMeshActor>(Loc,Rot);
                X->SetMobility(EComponentMobility::Movable);
                X->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,Shape));
                X->GetStaticMeshComponent()->SetMaterial(0,M);
                X->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
                X->GetStaticMeshComponent()->SetCastShadow(false);
                X->SetActorScale3D(Scale); X->Tags.Add(TEXT("SmelteryDressing"));
            };
            if(FlameMat)
                for(const float Yaw:{0.f,55.f,-55.f})
                    Spawn(TEXT("/Engine/BasicShapes/Plane"),FlameMat,At+FVector(0,-8,22),FRotator(0,Yaw,90),FVector(.95f,1.15f,1));
            else if(GlowMat)
                Spawn(TEXT("/Engine/BasicShapes/Sphere"),GlowMat,At+FVector(0,0,20),FRotator::ZeroRotator,FVector(1.05f,.45f,.95f));
            if(GlowMat && FlameMat)   // embers' bed glow, low and flattened behind the flames
                Spawn(TEXT("/Engine/BasicShapes/Sphere"),GlowMat,At+FVector(0,12,-25),FRotator::ZeroRotator,FVector(.8f,.35f,.18f));
        }
    }
    // A2 concept pass: the board's molten channel along the left wall, beside the coal (the
    // imported hot-metal plate sits inside the furnace footprint and never shows). Outside the
    // walkable field (x > 800 cm), NoCollision, one shadowless orange light.
    if(bHearthA2)
        if(auto* Molten=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/BossLab/HearthA2/M_A2_contained_molten_metal"),nullptr,LOAD_Quiet|LOAD_NoWarn))
        {
            auto* Rim=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/BossLab/HearthA2/M_A2_cut_stone_value_1"),nullptr,LOAD_Quiet|LOAD_NoWarn);
            auto Slab=[&](FVector At,FVector Scale,UMaterialInterface* M)
            {
                auto* A=World->SpawnActor<AStaticMeshActor>(At,FRotator::ZeroRotator);
                A->SetMobility(EComponentMobility::Movable);
                A->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube")));
                if(M)A->GetStaticMeshComponent()->SetMaterial(0,M);
                A->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
                A->SetActorScale3D(Scale); A->Tags.Add(TEXT("SmelteryDressing"));
            };
            // Above the flagstone tops (below them it only glowed through the joints); ends short
            // of the gallery post at y -470.
            Slab(FVector(915,15,7),FVector(.9f,8.3f,.04f),Molten);
            for(const float X:{858.f,972.f}) Slab(FVector(X,15,10),FVector(.16f,8.6f,.16f),Rim);
            auto* Glow=World->SpawnActor<APointLight>(FVector(915,15,70),FRotator(0,90,0));   // source length runs along local X: turned onto the channel
            auto* GC=CastChecked<UPointLightComponent>(Glow->GetLightComponent());
            GC->SetMobility(EComponentMobility::Movable); GC->SetCastShadows(false);
            GC->SetIntensityUnits(ELightUnits::Lumens); GC->SetIntensity(1800); GC->SetAttenuationRadius(800);
            GC->SetSourceLength(800); GC->SetSourceRadius(20); GC->SetLightColor(FLinearColor(1,.38,.08));
            Glow->Tags.Add(TEXT("SmelteryLight"));
        }
    // A2 detail pass: warm light under each chain-hung lantern (layout concept_lanterns_cm) and
    // rising steam over the quench cistern (quench_steam_cm): three crossed translucent planes.
    if(bHearthA2 && Parsed && Root.IsValid())
    {
        auto Vec=[](const TSharedPtr<FJsonValue>& V,FVector& Out)
        {
            const TArray<TSharedPtr<FJsonValue>>* A=nullptr;
            if(!V.IsValid() || !V->TryGetArray(A) || A->Num()!=3)return false;
            Out=FVector((*A)[0]->AsNumber(),(*A)[1]->AsNumber(),(*A)[2]->AsNumber()); return !Out.ContainsNaN();
        };
        const TArray<TSharedPtr<FJsonValue>>* Hung=nullptr;
        if(Root->TryGetArrayField(TEXT("concept_lanterns_cm"),Hung))for(int32 I=0;I<FMath::Min(4,Hung->Num());++I)
        {
            FVector At; if(!Vec((*Hung)[I],At))continue;
            auto* L=World->SpawnActor<APointLight>(At-FVector(0,0,40),FRotator::ZeroRotator);
            auto* C=CastChecked<UPointLightComponent>(L->GetLightComponent());
            C->SetMobility(EComponentMobility::Movable); C->SetCastShadows(false);
            C->SetIntensityUnits(ELightUnits::Lumens); C->SetIntensity(520); C->SetAttenuationRadius(700);
            C->SetSourceRadius(12); C->SetLightColor(FLinearColor(1,.62,.32)); L->Tags.Add(TEXT("SmelteryLight"));
        }
        const TArray<TSharedPtr<FJsonValue>>* SteamAt=nullptr; FVector Quench;
        if(Root->TryGetArrayField(TEXT("quench_steam_cm"),SteamAt) && SteamAt->Num()==3)
        {
            Quench=FVector((*SteamAt)[0]->AsNumber(),(*SteamAt)[1]->AsNumber(),(*SteamAt)[2]->AsNumber());
            if(auto* SteamMat=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/BossLab/HearthA2/Kit/M_A2_Steam"),nullptr,LOAD_Quiet|LOAD_NoWarn))
                for(const float Yaw:{0.f,36.f,72.f,108.f,144.f})
                {
                    auto* P=World->SpawnActor<AStaticMeshActor>(Quench+FVector(25,0,180),FRotator(0,Yaw,90));
                    P->SetMobility(EComponentMobility::Movable);
                    P->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Plane")));
                    P->GetStaticMeshComponent()->SetMaterial(0,SteamMat);
                    P->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
                    P->GetStaticMeshComponent()->SetCastShadow(false);
                    P->SetActorScale3D(FVector(2.8f,3.6f,1)); P->Tags.Add(TEXT("SmelteryDressing"));
                    UE_LOG(LogTemp,Display,TEXT("BOSSLAB A2 steam plane at %s"),*P->GetActorLocation().ToString());
                }
        }
    }
    // Opt-in scale preview (BOSSLAB_BELLBREAKER_PREVIEW=1): the static, unrigged Bellbreaker study
    // mesh (4.6 m, ~2.5x the player) standing before the furnace, facing the entry. No collision,
    // no moves or AI; presentation only.
    // Retarget review (BOSSLAB_BELLBREAKER_PREVIEW=anim, 2026-11-18): three rigged Bellbreakers at game
    // scale (2.55x the 180 cm rig = 4.6 m), each looping a clip retargeted by ue_retarget_bellbreaker.py.
    // BOSSLAB_BELLBREAKER_CLIPS picks them (comma list of BB_* suffixes). Presentation only: no collision,
    // no moves, AI or encounter.
    if(bHearthA2 && FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_BELLBREAKER_PREVIEW"))==TEXT("anim"))
        if(auto* Rig=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/BossLab/Bellbreaker/Rig/SKM_BellbreakerRig"),nullptr,LOAD_Quiet|LOAD_NoWarn))
        {
            FString List=FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_BELLBREAKER_CLIPS"));
            if(List.IsEmpty())List=TEXT("HY_Anims_root_HY_idle_hammer_s0,HY_Anims_root_HY_hammer_overhead_s0,HY_Anims_root_HY_sweep_rl_s0");
            TArray<FString> Clips; List.ParseIntoArray(Clips,TEXT(","));
            for(int32 i=0;i<Clips.Num() && i<3;++i)
            {
                auto* Anim=LoadObject<UAnimSequence>(nullptr,*(TEXT("/Game/BossLab/Bellbreaker/Anim/BB_")+Clips[i]),nullptr,LOAD_Quiet|LOAD_NoWarn);
                auto* Boss=World->SpawnActor<ASkeletalMeshActor>(FVector((i-1)*450.f,350,0),FRotator(0,180,0));   // rig faces +Y; yaw 180 faces the entry
                if(!Boss)continue;
                Boss->SetActorScale3D(FVector(2.55f));
                auto* C=Boss->GetSkeletalMeshComponent();
                C->SetMobility(EComponentMobility::Movable);
                C->SetSkeletalMesh(Rig);
                C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
                C->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
                if(Anim)C->PlayAnimation(Anim,true);
                if(FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_BELLBREAKER_HAMMER"))!=TEXT("off"))WardenAttachBellHammer(Boss,C,2.55f);
                Boss->Tags.Add(TEXT("SmelteryDressing"));
                UE_LOG(LogTemp,Display,TEXT("BOSSLAB BELLBREAKER lineup %d %s anim=%d"),i,*Clips[i],Anim!=nullptr);
            }
        }
    if(bHearthA2 && FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_BELLBREAKER_PREVIEW"))==TEXT("quake"))
        if(auto* Rig=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/BossLab/Bellbreaker/Rig/SKM_BellbreakerRig"),nullptr,LOAD_Quiet|LOAD_NoWarn))
        {
            const FString Seed=FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_BELLBREAKER_QUAKE_SEED")).IsEmpty()?TEXT("0"):FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_BELLBREAKER_QUAKE_SEED"));
            auto* Quake=LoadObject<UAnimSequence>(nullptr,*(TEXT("/Game/BossLab/Bellbreaker/Anim/BB_HY_Anims_root_HY_bell_quake_s")+Seed),nullptr,LOAD_Quiet|LOAD_NoWarn);
            const FVector BossAt(0,450,0);
            auto* Boss=World->SpawnActor<ASkeletalMeshActor>(BossAt,FRotator(0,180,0));
            Boss->SetActorScale3D(FVector(2.55f));
            auto* C=Boss->GetSkeletalMeshComponent();
            C->SetMobility(EComponentMobility::Movable); C->SetSkeletalMesh(Rig); C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
            C->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
            if(Quake)C->PlayAnimation(Quake,true);
            UStaticMeshComponent* QuakeHammer=WardenAttachBellHammer(Boss,C,2.55f);
            Boss->Tags.Add(TEXT("SmelteryDressing"));
            BellQuake::G=BellQuake::FState();
            BellQuake::G.Boss=C; BellQuake::G.Hammer=QuakeHammer; BellQuake::G.Origin=BossAt+FVector(0,-320,0);
            if(auto* Plane=LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Plane"),nullptr,LOAD_Quiet|LOAD_NoWarn))
                if(auto* Mat=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/BossLab/Bellbreaker/FX/M_BB_Shockwave"),nullptr,LOAD_Quiet|LOAD_NoWarn))
                {
                    auto* RingActor=World->SpawnActor<AStaticMeshActor>(BellQuake::G.Origin+FVector(0,0,6),FRotator::ZeroRotator);
                    RingActor->SetMobility(EComponentMobility::Movable);
                    auto* R=RingActor->GetStaticMeshComponent(); R->SetStaticMesh(Plane); R->SetCollisionEnabled(ECollisionEnabled::NoCollision);
                    R->SetCastShadow(false); auto* Mid=UMaterialInstanceDynamic::Create(Mat,RingActor); R->SetMaterial(0,Mid); R->SetVisibility(false);
                    BellQuake::G.Ring=R; BellQuake::G.Mid=Mid; RingActor->Tags.Add(TEXT("SmelteryDressing"));
                }
            auto* Manny=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"),nullptr,LOAD_Quiet|LOAD_NoWarn);
            auto* Stun=LoadObject<UAnimSequence>(nullptr,TEXT("/Game/BossLab/Bellbreaker/HYSource/HY_Anims_root_HY_stun_s0"),nullptr,LOAD_Quiet|LOAD_NoWarn);
            if(Manny&&Stun)
            {
                const FVector VictimAt(-330,-40,0);
                auto* Victim=World->SpawnActor<ASkeletalMeshActor>(VictimAt,FRotator(0,(BellQuake::G.Origin-VictimAt).Rotation().Yaw-90,0));   // mannequin faces +Y: turn it toward the impact
                auto* VC=Victim->GetSkeletalMeshComponent();
                VC->SetMobility(EComponentMobility::Movable); VC->SetSkeletalMesh(Manny); VC->SetCollisionEnabled(ECollisionEnabled::NoCollision);
                VC->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
                VC->PlayAnimation(Stun,false); VC->SetPlayRate(0.f);
                Victim->Tags.Add(TEXT("SmelteryDressing"));
                BellQuake::G.Victim=VC; BellQuake::G.Stun=Stun; BellQuake::G.VictimDistance=FVector::Dist2D(VictimAt,BellQuake::G.Origin);
            }
            BellQuake::G.Tell=BellQuake::Sound(TEXT("clapper_tell_v0")); BellQuake::G.Slam=BellQuake::Sound(TEXT("bell_slam_ground_v0"));
            BellQuake::G.Wave=BellQuake::Sound(TEXT("shockwave_v0")); BellQuake::G.Ears=BellQuake::Sound(TEXT("stun_ring_v0"));
            UE_LOG(LogTemp,Display,TEXT("BOSSLAB BELLBREAKER quake preview anim=%d ring=%d victim=%d sounds=%d%d%d%d"),Quake!=nullptr,BellQuake::G.Ring.IsValid(),BellQuake::G.Victim.IsValid(),
                BellQuake::G.Tell.IsValid(),BellQuake::G.Slam.IsValid(),BellQuake::G.Wave.IsValid(),BellQuake::G.Ears.IsValid());
        }
    if(bHearthA2 && FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_BELLBREAKER_PREVIEW"))==TEXT("1"))
        if(auto* BossMesh=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/BossLab/Bellbreaker/SM_BellbreakerGen"),nullptr,LOAD_Quiet|LOAD_NoWarn))
        {
            auto* Boss=World->SpawnActor<AStaticMeshActor>(FVector(0,650,0),FRotator(0,180,0));
            Boss->SetMobility(EComponentMobility::Movable);
            Boss->GetStaticMeshComponent()->SetStaticMesh(BossMesh);
            Boss->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
            Boss->Tags.Add(TEXT("SmelteryDressing"));
            if(auto* HammerMesh=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/BossLab/Bellbreaker/SM_BellHammerGen"),nullptr,LOAD_Quiet|LOAD_NoWarn))
            {
                auto* Hammer=World->SpawnActor<AStaticMeshActor>(FVector(-230,560,0),FRotator(-18,200,0));   // bell on the floor, haft leaning toward the boss
                Hammer->SetMobility(EComponentMobility::Movable);
                Hammer->GetStaticMeshComponent()->SetStaticMesh(HammerMesh);
                Hammer->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
                Hammer->Tags.Add(TEXT("SmelteryDressing"));
            }
        }
    UE_LOG(LogTemp,Display,TEXT("BOSSLAB SMELTERY walkthrough: %d art instances, no boss, no encounter audio; clear floor %.0fx%.0fcm; Hearth A=%d"),Loaded,HalfWidth*2,HalfLength*2,bHearthA);
    auto* Sun=World->SpawnActor<ADirectionalLight>(FVector(0,0,1000),FRotator(-55,-35,0));
    Sun->GetLightComponent()->SetMobility(EComponentMobility::Movable);
    CastChecked<UDirectionalLightComponent>(Sun->GetLightComponent())->SetForwardShadingPriority(1);
    // A2 concept pass (2026-11-17): the two shadowless directionals lit every face evenly and
    // flattened the room; the concept is dark between pools of forge, lantern and window light.
    Sun->GetLightComponent()->SetIntensity(bHearthA2?.07f:(bHearthA?.22f:.7f));
    Sun->GetLightComponent()->SetCastShadows(!bHearthA);
    Sun->GetLightComponent()->SetLightColor(bHearthA?FLinearColor(.8,.75,.65):FLinearColor(1,.67,.36));
    auto* Fill=World->SpawnActor<ADirectionalLight>(FVector(0,0,1000),FRotator(-25,140,0));
    Fill->GetLightComponent()->SetMobility(EComponentMobility::Movable);
    Fill->GetLightComponent()->SetIntensity(bHearthA2?.13f:(bHearthA?.35f:.7f)); Fill->GetLightComponent()->SetLightColor(FLinearColor(.45,.55,.7));
    Fill->GetLightComponent()->SetCastShadows(false);
    if(bHearthA)
    {
        auto* Fog=World->SpawnActor<AExponentialHeightFog>();
        auto* FC=Fog->GetComponent(); FC->SetFogDensity(.008f);
        FC->SetVolumetricFog(true); FC->SetVolumetricFogScatteringDistribution(.35f);
        FC->SetVolumetricFogAlbedo(FColor(195,205,220));
        FC->SetVolumetricFogExtinctionScale(.7f); FC->SetVolumetricFogDistance(4200);
        if(bHearthA2)
        {
            // Smoky forge air: denser low haze, warm inscatter; the window spot scatters cool.
            FC->SetFogDensity(.02f); FC->SetFogHeightFalloff(.18f);
            FC->SetFogInscatteringColor(FLinearColor(.035,.018,.009));
            FC->SetVolumetricFogExtinctionScale(1.6f);
            auto* Post=World->SpawnActor<APostProcessVolume>();
            Post->bUnbound=true; Post->GetBrushComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
            Post->Settings.bOverride_VignetteIntensity=true; Post->Settings.VignetteIntensity=.6f;
            Post->Settings.bOverride_BloomIntensity=true; Post->Settings.BloomIntensity=.9f;
            Post->Settings.bOverride_ColorSaturation=true; Post->Settings.ColorSaturation=FVector4(1.05,.98,.9,1);
            Post->Settings.bOverride_ColorContrast=true; Post->Settings.ColorContrast=FVector4(1.15,1.15,1.15,1);
            Post->Settings.bOverride_ColorGainShadows=true; Post->Settings.ColorGainShadows=FVector4(.9,.97,1.1,1);
            Post->Settings.bOverride_ColorGainHighlights=true; Post->Settings.ColorGainHighlights=FVector4(1.08,1.,.9,1);
            Post->Tags.Add(TEXT("SmelteryGrade"));
        }
    }
    if(auto* PC=World->GetFirstPlayerController())
    {
        Player=Cast<AWardenChallenger>(PC->GetPawn());
        RecordStartupCamera(TEXT("before_entry_init"));
        PC->SetControlRotation(SmelteryEntry);
        PC->SetInputMode(FInputModeGameOnly()); PC->bShowMouseCursor=false;
    }
    if(Player)
    {
        Player->SetActorLocation(SmelterySpawn); Player->SetActorRotation(FRotator(0,SmelteryEntry.Yaw,0));
        Player->ResetFighter(false); Player->SetLocked(false); Player->SetTarget(nullptr);
    }
    bScriptedPlayer=bSmelteryTiming || FParse::Param(FCommandLine::Get(),TEXT("BossLabSmelteryStudy"));
    LoadSettings();
    RecordStartupCamera(TEXT("after_entry_and_settings"));
    LastEvent=TEXT("SMELTERY WALKTHROUGH | WASD move / Shift sprint / Mouse camera / Esc pause / Q quit while paused");
}

void AWardenArenaMode::TickSmelteryWalkthrough(float DeltaSeconds)
{
    // Wall-clock diagnostic only: no synthetic camera, movement, focus or input.
    const double StartupAge=FPlatformTime::Seconds()-StartupCameraTime;
    if(bStartupCameraDiagnostic && StartupAge<=10 && StartupAge>=StartupCameraNextSample)
    {RecordStartupCamera(TEXT("tick_sample"));StartupCameraNextSample=StartupAge+.5;}
    if(bStartupEntryCapture && !bStartupEntryCaptured && !bScriptedPlayer && StartupAge>=8)
    {
        bStartupEntryCaptured=true;
        const FString Dir=FPaths::ProjectSavedDir()/TEXT("NormalEntryDiagnostic");
        IFileManager::Get().MakeDirectory(*Dir,true);
        const FString Name=Dir/(FDateTime::UtcNow().ToString(TEXT("%Y%m%d-%H%M%S"))+TEXT("-entry.png"));
        FScreenshotRequest::RequestScreenshot(Name,true,false);
        UE_LOG(LogTemp,Display,TEXT("BOSSLAB normal entry screenshot requested without camera/input override: %s"),*Name);
        RecordStartupCamera(TEXT("normal_entry_screenshot"));
    }
    if(bPaused || !Player) { CombatAccumulator=0; return; }
    BellQuake::Tick(GetWorld());
    // BeginPlay camera settings can be overwritten by initial possession.
    // Apply once after startup; ordinary human look input remains unrestricted.
    if(bHearthA && DemoResetWait==0)
        if(auto* PC=GetWorld()->GetFirstPlayerController()) { PC->SetControlRotation(SmelteryEntry); DemoResetWait=1;RecordStartupCamera(TEXT("post_possession_entry_init")); }
    if(bScriptedPlayer && DemoTick>(bSmelteryTiming?300:120) && FrameMilliseconds.Num()<10000)FrameMilliseconds.Add(DeltaSeconds*1000);
    CombatAccumulator+=FMath::Min(DeltaSeconds,.1f);
    while(CombatAccumulator>=WardenRules::Step)
    {
        CombatAccumulator-=WardenRules::Step; Player->RestoreStepState();
        FVector Intent=Player->MoveIntent();
        if(bScriptedPlayer)
        {
            ++DemoTick;
            const int32 RouteTick=bHearthA?(FMath::Max(1,DemoTick-300)-1)%1800+1:(DemoTick-1)%1800+1;
            Intent=RouteTick<400?FVector(0,1,0):RouteTick<650?FVector(1,0,0):RouteTick<1100?FVector(0,-1,0):RouteTick<1550?FVector(-1,0,0):FVector(0,1,0);
            if(bHearthA)
            {
                // Position-driven loop remains inside the compact room; unlike
                // a timed leg, it does not spend seconds pushing into a wall.
                const FVector Stops[]={FVector(450,1000,0),FVector(-800,800,0),FVector(-800,-800,0),FVector(800,-800,0),FVector(800,800,0),FVector(0,0,0)};
                const int32 StopCount=bHearthA2?SmelteryStudyStops.Num():6;
                auto Stop=[&](int32 I){return bHearthA2?SmelteryStudyStops[I]:Stops[I];};
                FVector Delta=Stop(DemoRounds%StopCount)-Player->GetActorLocation(); Delta.Z=0;
                if(DemoTick>300 && Delta.Size2D()<60){++SmelteryWaypointArrivals;DemoRounds=(DemoRounds+1)%StopCount;Delta=Stop(DemoRounds)-Player->GetActorLocation();Delta.Z=0;}
                Intent=Delta.GetSafeNormal();
                Player->SprintHeld=RouteTick>=700 && RouteTick<780;
            }
            // Capture-only review (BOSSLAB_HEARTH_VIEWS=1 with `study`): the player stands at fixed
            // spots facing each wall so dressing outside the route's view is inspected too.
            static const bool bViews=FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_HEARTH_VIEWS"))==TEXT("1");
            if(bHearthA2 && bViews && DemoTick>300)
            {
                struct FView{FVector At;float Yaw;};
                const FView Views[]={{FVector(250,-300,95),10},{FVector(300,200,95),35},{FVector(-300,300,95),150},{FVector(-200,-200,95),200},
                                     {FVector(-300,500,95),120},{FVector(400,-500,95),-20},{FVector(-200,-400,95),-120},{FVector(0,-500,95),-90}};
                const int32 V=FMath::Min((DemoTick-301)/120,7);
                // Retarget lineup review: hold one wide view of the three bosses instead.
                static const FString PreviewMode=FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_BELLBREAKER_PREVIEW"));
                static const bool bLineup=PreviewMode==TEXT("anim")||PreviewMode==TEXT("quake");
                const FView Lineup={FVector(0,-250,95),90};
                const FView& Use=bLineup?Lineup:Views[V];
                Player->SetActorLocation(Use.At); Intent=FVector::ZeroVector;
                if(auto* PC=GetWorld()->GetFirstPlayerController())PC->SetControlRotation(FRotator(bLineup?2:-14,Use.Yaw,0));
                Player->SetActorRotation(FRotator(0,Use.Yaw,0));
                if(bLineup)Player->SetActorHiddenInGame(true);   // the camera keeps its follow distance; the player no longer blocks the middle boss
            }
            else if(bHearthA && DemoTick<=300)
            {
                Intent=FVector::ZeroVector;
                if(auto* PC=GetWorld()->GetFirstPlayerController())PC->SetControlRotation(SmelteryEntry);
            }
            else if(auto* PC=GetWorld()->GetFirstPlayerController())PC->SetControlRotation(FRotator(-12,Intent.Rotation().Yaw,0));
            if(!(bHearthA2 && bViews) && (RouteTick==180 || RouteTick==840))Player->PendingAction=EWardenAction::Dodge;
            if(!(bHearthA2 && bViews) && RouteTick==480)Player->PendingAction=EWardenAction::Jump;
            const FString Dir=FPaths::ProjectSavedDir()/(bHearthA2?(bSmelteryTiming?TEXT("HearthA2Timing"):TEXT("HearthA2Study")):(bHearthA?(bSmelteryTiming?TEXT("HearthATiming"):TEXT("HearthAStudy")):(bSmelteryTiming?TEXT("SmelteryTiming"):TEXT("SmelteryStudy"))));
            static const bool bLineupFrames=bHearthA2 && bViews && (FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_BELLBREAKER_PREVIEW"))==TEXT("anim")||FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_BELLBREAKER_PREVIEW"))==TEXT("quake"));
            static const bool bQuakeFrames=bLineupFrames && FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_BELLBREAKER_PREVIEW"))==TEXT("quake");
            if(bLineupFrames ? (bQuakeFrames ? (DemoTick>=320 && DemoTick<=560 && DemoTick%5==0) : (DemoTick>=320 && DemoTick<=800 && DemoTick%15==0))
                             : (bHearthA ? (DemoTick>=300 && (DemoTick%120==0 || DemoTick==300)) : DemoTick%120==0))
            {
                if(!bSmelteryTiming)
                {
                    IFileManager::Get().MakeDirectory(*Dir,true);
                    FScreenshotRequest::RequestScreenshot(Dir/FString::Printf(TEXT("frame-%04d.png"),DemoTick),true,false);
                }
                const FVector P=Player->GetActorLocation();
                MotionStudyTrace+=FString::Printf(TEXT("%d,%.3f,%.3f,%.3f\n"),DemoTick,P.X,P.Y,P.Z);
            }
            if(DemoTick>=(bSmelteryTiming?3900:1860))
            {
                IFileManager::Get().MakeDirectory(*Dir,true);
                FFileHelper::SaveStringToFile(TEXT("tick,x_cm,y_cm,z_cm\n")+MotionStudyTrace,*(Dir/TEXT("path.csv")));
                TSharedRef<FJsonObject> Report=MakeShared<FJsonObject>();
                Report->SetStringField(TEXT("kind"),TEXT("scripted actual player walkthrough, native frame timing, not human play"));
                Report->SetBoolField(TEXT("screenshots_enabled"),!bSmelteryTiming);
                Report->SetNumberField(TEXT("warmup_simulation_ticks"),bSmelteryTiming?300:120);
                Report->SetStringField(TEXT("arena"),bHearthA2?TEXT("Hearth A2"):(bHearthA?TEXT("Hearth A"):TEXT("Smeltery original")));
                if(bHearthA2)
                {
                    Report->SetNumberField(TEXT("actual_travel_cm"),SmelteryStudyDistance);
                    Report->SetNumberField(TEXT("waypoint_arrivals"),SmelteryWaypointArrivals);
                    Report->SetNumberField(TEXT("waypoint_count"),SmelteryStudyStops.Num());
                    Report->SetBoolField(TEXT("route_coverage_complete"),SmelteryWaypointArrivals>=SmelteryStudyStops.Num());
                    Report->SetNumberField(TEXT("ticks_since_last_actual_motion"),DemoTick-SmelteryLastMovementTick);
                }
                Report->SetBoolField(TEXT("boss_present"),Warden!=nullptr);Report->SetNumberField(TEXT("combat_ticks"),CombatTick);
                TArray<TSharedPtr<FJsonValue>> Times;for(float T:FrameMilliseconds)Times.Add(MakeShared<FJsonValueNumber>(T));
                Report->SetArrayField(TEXT("frame_ms"),Times);FString Out;FJsonSerializer::Serialize(Report,TJsonWriterFactory<>::Create(&Out));
                FFileHelper::SaveStringToFile(Out,*(Dir/TEXT("report.json")));
                bPaused=true;if(auto* PC=GetWorld()->GetFirstPlayerController())PC->ConsoleCommand(TEXT("quit"));return;
            }
        }
        const auto Action=Player->PendingAction;
        if(Action==EWardenAction::Jump || Action==EWardenAction::Dodge)
            Player->BeginAction(Action,0,Intent);
        Player->PendingAction=EWardenAction::Ready; Player->FollowAction=EWardenAction::Ready;
        const FVector BeforeStep=Player->GetActorLocation();
        Player->StepFighter(Intent,Player->SprintHeld); Player->Fight.Advance();
        if(bHearthA2 && bScriptedPlayer && DemoTick>300)
        {
            const double Travel=FVector::Dist2D(BeforeStep,Player->GetActorLocation());
            SmelteryStudyDistance+=Travel;if(Travel>.1)SmelteryLastMovementTick=DemoTick;
        }
        Player->CaptureStepState();
    }
    Player->BlendRenderState(float(CombatAccumulator/WardenRules::Step));
}
