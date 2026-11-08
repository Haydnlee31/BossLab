#include "Misc/AutomationTest.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "GameFramework/Actor.h"
#include "Components/BoxComponent.h"
#include "WardenPrototype.h"
#if WITH_EDITOR
#include "Editor.h"
#include "LevelEditorSubsystem.h"
#endif

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossLabMovement,
    "BossLab.Movement.FramePartitionAndWallCollision",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FBossLabMovement::RunTest(const FString& Parameters)
{
    UWorld* World = UWorld::CreateWorld(EWorldType::Game, false);
    GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
    auto* Player = World->SpawnActor<AWardenChallenger>(FVector(0,0,95), FRotator::ZeroRotator);
    if (!TestNotNull(TEXT("Real pawn spawned"), Player))
    { GEngine->DestroyWorldContext(World); World->DestroyWorld(false); return false; }
    auto* Floor = World->SpawnActor<AActor>();
    auto* FloorBox = NewObject<UBoxComponent>(Floor);
    Floor->SetRootComponent(FloorBox);
    FloorBox->SetBoxExtent(FVector(2000,2000,50));
    FloorBox->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    FloorBox->SetCollisionResponseToAllChannels(ECR_Block);
    FloorBox->RegisterComponent();
    Floor->SetActorLocation(FVector(0,0,-50));
    for (int32 I=0;I<60;++I) Player->SimulateMovement(FVector::ForwardVector,1.f/60.f);
    const float At60 = Player->GetActorLocation().X;
    TestTrue(TEXT("One second advances 360 cm"), FMath::IsNearlyEqual(At60,360.f,.1f));
    Player->SetActorLocation(FVector(0,0,95));
    for (int32 I=0;I<30;++I) Player->SimulateMovement(FVector::ForwardVector,1.f/30.f);
    TestTrue(TEXT("30 Hz and 60 Hz rendering yield the same movement"), FMath::IsNearlyEqual(Player->GetActorLocation().X,At60,.1f));
    auto* Wall = World->SpawnActor<AActor>();
    auto* Box = NewObject<UBoxComponent>(Wall);
    Wall->SetRootComponent(Box);
    Box->SetBoxExtent(FVector(50,500,200));
    Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Box->SetCollisionResponseToAllChannels(ECR_Block);
    Box->RegisterComponent();
    Wall->SetActorLocation(FVector(500,0,95));
    Player->SetActorLocation(FVector(0,0,95));
    for (int32 I=0;I<120;++I) Player->SimulateMovement(FVector::ForwardVector,1.f/60.f);
    TestTrue(TEXT("Capsule sweep stops at the actual wall surface"), FMath::IsNearlyEqual(Player->GetActorLocation().X,416.f,2.f));
    World->DestroyActor(Player); World->DestroyActor(Wall); World->DestroyActor(Floor);
    GEngine->DestroyWorldContext(World); World->DestroyWorld(false);
    return true;
}
#if WITH_EDITOR
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossLabEditorSubsystems,
    "BossLab.Preflight.EditorSubsystems",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FBossLabEditorSubsystems::RunTest(const FString& Parameters)
{
    return TestNotNull(TEXT("Native level editor subsystem exists"), GEditor->GetEditorSubsystem<ULevelEditorSubsystem>());
}
#endif
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossLabWorldPreflight,
    "BossLab.Preflight.ActorCollisionLifecycle",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FBossLabWorldPreflight::RunTest(const FString& Parameters)
{
    UWorld* World = UWorld::CreateWorld(EWorldType::Game, false);
    if (!TestNotNull(TEXT("Isolated test world exists"), World)) return false;
    GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
    AActor* Actor = World->SpawnActor<AActor>();
    if (!TestNotNull(TEXT("Actor spawned"), Actor)) { GEngine->DestroyWorldContext(World); World->DestroyWorld(false); return false; }
    UBoxComponent* Box = NewObject<UBoxComponent>(Actor);
    Actor->SetRootComponent(Box);
    Box->SetBoxExtent(FVector(50.f));
    Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Box->SetCollisionResponseToAllChannels(ECR_Block);
    Box->RegisterComponent();
    Actor->SetActorLocation(FVector(250.f, 0.f, 100.f));
    FHitResult Hit;
    const bool bHit = World->LineTraceSingleByChannel(Hit,
        FVector(0.f, 0.f, 100.f), FVector(500.f, 0.f, 100.f), ECC_Visibility);
    TestTrue(TEXT("Actual Unreal collision query hits the spawned box"), bHit);
    TestEqual(TEXT("Query identifies the expected actor"), Hit.GetActor(), Actor);
    Actor->SetActorLocation(FVector(250.f, 300.f, 100.f));
    TestFalse(TEXT("Moving actor clears the original query path"),
        World->LineTraceSingleByChannel(Hit, FVector(0.f, 0.f, 100.f),
            FVector(500.f, 0.f, 100.f), ECC_Visibility));
    TestTrue(TEXT("Test actor can be destroyed"), World->DestroyActor(Actor));
    GEngine->DestroyWorldContext(World);
    World->DestroyWorld(false);
    return true;
}
#endif
