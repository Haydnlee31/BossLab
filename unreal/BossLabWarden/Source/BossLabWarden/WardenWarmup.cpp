// Shader/PSO warm-up (2026-11-24). Presentation only; no combat rules.
//
// Play runs in the editor binary, where Unreal hard-disables PSO precaching
// (PipelineStateCache::IsPSOPrecachingEnabled() returns false under WITH_EDITOR). Every effect
// material therefore built its graphics pipeline the first time it was drawn, in the middle of the
// fight: the owner's forge session logged 100 PSO creation hitches (each > 20 ms, none precached)
// around the Bellbreaker's phase two. Pooled effects (empty instanced meshes, hidden props, the
// raised dead) are exactly the ones that are never drawn until their move.
//
// The warm-up draws one full-size copy of every distinct mesh/material/component kind in the world
// for a short window before the fight: behind the opaque home/boss-select menu in play, under a
// black camera fade in capture/benchmark (which have no menu). The copies jiggle so the velocity
// pass is built too, and stay until the editor's shader compile queue is empty (materials draw
// with the default material while their shaders compile). The fight starting ends it at once.
// BOSSLAB_WARMUP=0 disables it for A/B evidence; BOSSLAB_PSO_LOG=1 (launcher) names each hitch.
#include "WardenPrototype.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "HAL/FileManager.h"
#include "Materials/MaterialInterface.h"
#include "Misc/Paths.h"
#if WITH_EDITOR
#include "ShaderCompiler.h"
#endif

namespace
{
    int32 RemainingShaderJobs()
    {
#if WITH_EDITOR
        return GShaderCompilingManager ? GShaderCompilingManager->GetNumRemainingJobs() : 0;
#else
        return 0;
#endif
    }
    constexpr int32 CopiesPerFrame=48;      // spreads the first-draw cost over frames (menu stays responsive)
    constexpr int32 MaxCopies=1500;
    constexpr double MaxSeconds=30.;        // cold shader cache: give up rather than hold the menu hostage
    constexpr int32 MaxUncoveredFrames=50;  // capture records from frame 61; benchmark skips 180
}

void AWardenArenaMode::PreloadSoundBank()
{
    // Every layered sound family under /Game/BossLab/Sound is loaded before the fight. SfxVariations
    // used to load a family on its first play, a synchronous package flush mid-fight
    // (FlushAsyncLoading lines in play.log). Same filtering: SfxVariations keeps the roster boundary.
    TArray<FString> Files;
    IFileManager::Get().FindFiles(Files,*FPaths::Combine(FPaths::ProjectContentDir(),TEXT("BossLab/Sound")),TEXT(".uasset"));
    TSet<FString> Families;
    for(const FString& File:Files)
    {
        FString Base=FPaths::GetBaseFilename(File); int32 Under=INDEX_NONE;
        if(Base.FindLastChar(TEXT('_'),Under) && Base.Mid(Under+1).IsNumeric()) Families.Add(Base.Left(Under));
    }
    int32 Loaded=0;
    for(const FString& Name:Families) Loaded+=SfxVariations(Name,nullptr).Num();
    UE_LOG(LogTemp,Display,TEXT("BOSSLAB sound bank preloaded: %d families, %d sounds"),Families.Num(),Loaded);
}

void AWardenArenaMode::BeginShaderWarmup()
{
    if(GIsAutomationTesting || FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_WARMUP"))==TEXT("0")) return;
    ShaderWarmupFrame=0; ShaderWarmupStart=FPlatformTime::Seconds(); bShaderWarmup=true;
}

void AWardenArenaMode::GatherShaderWarmupSources()
{
    // One source per distinct (kind, mesh, materials, shadow, custom data): that is what selects
    // the vertex factory, material shaders and render state of each pass.
    TSet<uint32> Seen;
    for(TActorIterator<AActor> It(GetWorld());It;++It)
    {
        if(*It==ShaderWarmupActor) continue;
        TInlineComponentArray<UPrimitiveComponent*> Prims(*It);
        for(UPrimitiveComponent* C:Prims)
        {
            if(!C || !C->IsRegistered()) continue;
            uint32 Key=0; const UObject* Asset=nullptr;
            if(const auto* S=Cast<UStaticMeshComponent>(C)) { Asset=S->GetStaticMesh(); Key=C->IsA<UInstancedStaticMeshComponent>() ? 1 : 0; }
            else if(const auto* K=Cast<USkinnedMeshComponent>(C)) { Asset=Cast<USkeletalMesh>(K->GetSkinnedAsset()); Key=2; }
            if(!Asset) continue;
            Key=HashCombine(Key,PointerHash(Asset));
            for(int32 M=0;M<C->GetNumMaterials();++M) Key=HashCombine(Key,PointerHash(C->GetMaterial(M)));
            Key=HashCombine(Key,GetTypeHash(C->CastShadow));
            if(const auto* I=Cast<UInstancedStaticMeshComponent>(C)) Key=HashCombine(Key,GetTypeHash(I->NumCustomDataFloats>0));
            bool Already=false; Seen.Add(Key,&Already);
            if(!Already && ShaderWarmupSources.Num()<MaxCopies) ShaderWarmupSources.Add(C);
        }
    }
}

void AWardenArenaMode::AddShaderWarmupCopy(UPrimitiveComponent* Src)
{
    USceneComponent* Root=ShaderWarmupActor->GetRootComponent();
    UPrimitiveComponent* Copy=nullptr; float Radius=0;
    if(auto* I=Cast<UInstancedStaticMeshComponent>(Src))
    {
        auto* C=NewObject<UInstancedStaticMeshComponent>(ShaderWarmupActor,Src->IsA<UHierarchicalInstancedStaticMeshComponent>() ? UHierarchicalInstancedStaticMeshComponent::StaticClass() : UInstancedStaticMeshComponent::StaticClass());
        C->SetStaticMesh(I->GetStaticMesh()); C->NumCustomDataFloats=I->NumCustomDataFloats;
        Radius=I->GetStaticMesh()->GetBounds().SphereRadius; Copy=C;
    }
    else if(auto* S=Cast<UStaticMeshComponent>(Src))
    {
        auto* C=NewObject<UStaticMeshComponent>(ShaderWarmupActor);
        C->SetStaticMesh(S->GetStaticMesh()); Radius=S->GetStaticMesh()->GetBounds().SphereRadius; Copy=C;
    }
    else if(auto* K=Cast<USkinnedMeshComponent>(Src))
    {
        auto* Mesh=Cast<USkeletalMesh>(K->GetSkinnedAsset());
        auto* C=NewObject<USkeletalMeshComponent>(ShaderWarmupActor);
        C->SetSkeletalMeshAsset(Mesh); Radius=Mesh->GetBounds().SphereRadius; Copy=C;
    }
    if(!Copy) return;
    for(int32 M=0;M<Src->GetNumMaterials();++M) Copy->SetMaterial(M,Src->GetMaterial(M));
    Copy->SetMobility(EComponentMobility::Movable);
    Copy->SetCollisionEnabled(ECollisionEnabled::NoCollision); Copy->SetGenerateOverlapEvents(false);
    Copy->SetCanEverAffectNavigation(false);
    Copy->CastShadow=Src->CastShadow; Copy->bCastDynamicShadow=Src->bCastDynamicShadow;
    Copy->bReceivesDecals=Src->bReceivesDecals; Copy->bRenderCustomDepth=Src->bRenderCustomDepth;
    Copy->LightingChannels=Src->LightingChannels;
    // A grid across the middle of the view, each copy ~16 cm across at 1.2 m: large enough that
    // the depth prepass and shadow depth draw it (both skip tiny screen radii).
    const int32 Index=ShaderWarmupCopies.Num(), Col=Index%9, Row=(Index/9)%7;
    Copy->SetupAttachment(Root);
    Copy->SetRelativeLocation(FVector(0,(Col-4)*9.f,(Row-3)*9.f));
    Copy->SetRelativeScale3D(FVector(8.f/FMath::Max(Radius,1.f)));
    Copy->RegisterComponent();
    if(auto* I=Cast<UInstancedStaticMeshComponent>(Copy)) I->AddInstance(FTransform::Identity);   // custom data 0 = faded out
    ShaderWarmupCopies.Add(Copy);
}

void AWardenArenaMode::TickShaderWarmup()
{
    if(!bShaderWarmup) return;
    APlayerController* PC=GetWorld()->GetFirstPlayerController();
    if(!PC || !PC->PlayerCameraManager) return;
    const bool MenuCovers=bFrontendSession && (bTitle || bPaused);
    const bool Uncovered=bCaptureFrames || bBenchmark;
    if(!MenuCovers && !Uncovered) { EndShaderWarmup(TEXT("fight started")); return; }
    ++ShaderWarmupFrame;
    // Frame 3: after the first presentation passes have swapped in their real materials (forge fire).
    if(ShaderWarmupFrame==3)
    {
        ShaderWarmupActor=GetWorld()->SpawnActor<AActor>();
        auto* Root=NewObject<USceneComponent>(ShaderWarmupActor); ShaderWarmupActor->SetRootComponent(Root); Root->RegisterComponent();
        GatherShaderWarmupSources();
    }
    if(ShaderWarmupFrame<3) return;
    for(int32 N=0;N<CopiesPerFrame && ShaderWarmupCopies.Num()<ShaderWarmupSources.Num();++N)
        if(UPrimitiveComponent* Src=ShaderWarmupSources[ShaderWarmupCopies.Num()].Get()) AddShaderWarmupCopy(Src); else ShaderWarmupCopies.Add(nullptr);
    // Follow the camera 1.2 m ahead, jiggling 1 cm so the velocity pass draws as well.
    const FRotator R=PC->PlayerCameraManager->GetCameraRotation();
    const FVector At=PC->PlayerCameraManager->GetCameraLocation()+R.Vector()*120.f+FVector(0,0,(ShaderWarmupFrame&1)?.5f:-.5f);
    ShaderWarmupActor->SetActorLocationAndRotation(At,R);
    if(Uncovered && !MenuCovers) PC->PlayerCameraManager->SetManualCameraFade(1.f,FLinearColor::Black,false);
    const int32 Jobs=RemainingShaderJobs();
    ShaderWarmupIdle=Jobs>0 ? 0 : ShaderWarmupIdle+1;
    const bool AllCopied=ShaderWarmupCopies.Num()>=ShaderWarmupSources.Num();
    if(AllCopied && ShaderWarmupIdle>=10) EndShaderWarmup(TEXT("complete"));
    else if(Uncovered && !MenuCovers && ShaderWarmupFrame>=MaxUncoveredFrames) EndShaderWarmup(TEXT("frame cap (no menu)"));
    else if(FPlatformTime::Seconds()-ShaderWarmupStart>MaxSeconds) EndShaderWarmup(TEXT("time cap"));
}

void AWardenArenaMode::EndShaderWarmup(const TCHAR* Why)
{
    if(!bShaderWarmup) return;
    bShaderWarmup=false;
    int32 Drawn=0;
    for(auto& C:ShaderWarmupCopies) if(C) { ++Drawn; C->DestroyComponent(); }
    if(ShaderWarmupActor) ShaderWarmupActor->Destroy();
    if((bCaptureFrames || bBenchmark) && GetWorld()->GetFirstPlayerController() && GetWorld()->GetFirstPlayerController()->PlayerCameraManager)
        GetWorld()->GetFirstPlayerController()->PlayerCameraManager->StopCameraFade();
    UE_LOG(LogTemp,Display,TEXT("BOSSLAB shader warmup %s: %d sources, %d copies drawn, %d frames, %.2f s, %d shader jobs left"),
        Why,ShaderWarmupSources.Num(),Drawn,ShaderWarmupFrame,FPlatformTime::Seconds()-ShaderWarmupStart,RemainingShaderJobs());
    ShaderWarmupActor=nullptr; ShaderWarmupCopies.Reset(); ShaderWarmupSources.Reset();
}
