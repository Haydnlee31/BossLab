#include "WardenPrototype.h"
#include "WardenSmelteryLayout.h"
#include "Misc/AutomationTest.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "Engine/World.h"
#include "Engine/OverlapResult.h"
#include "Engine/Engine.h"
#include "Engine/StaticMeshActor.h"
#include "EngineUtils.h"
#include "Components/StaticMeshComponent.h"
#if WITH_DEV_AUTOMATION_TESTS
// Explicit asset-trial filter: default BossLab tests do not require optional A2 imports.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FHearthA2RuntimeCollision,"WardenAssetTrial.HearthA2.RuntimeCollision",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FHearthA2RuntimeCollision::RunTest(const FString&)
{
    FString Text,Error;TSharedPtr<FJsonObject> Root;WardenSmelteryLayout::FLayout Layout;
    if(!FFileHelper::LoadFileToString(Text,*(FPaths::ProjectContentDir()/TEXT("BossLab/HearthA2/layout.json"))) ||
       !FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text),Root) || !WardenSmelteryLayout::Validate(Root,Layout,Error))
    {AddError(TEXT("Explicit A2 asset trial requires a valid imported manifest: ")+Error);return false;}
    for(const auto& V:Root->GetArrayField(TEXT("instances")))
        if(!LoadObject<UStaticMesh>(nullptr,*V->AsObject()->GetStringField(TEXT("asset"))))
        {AddError(TEXT("Explicit A2 trial requires all imported meshes"));return false;}
    UWorld* World=UWorld::CreateWorld(EWorldType::Game,false);
    GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
    auto* Mode=World->SpawnActor<AWardenArenaMode>();Mode->bSmelteryWalkthrough=true;Mode->bHearthA2=true;
    Mode->Player=World->SpawnActor<AWardenChallenger>();Mode->Player->DispatchBeginPlay();Mode->DispatchBeginPlay();
    auto* Pawn=Mode->Player.Get();
    TestNull(TEXT("A2 never spawns a boss"),Mode->Warden.Get());
    TestEqual(TEXT("No encounter ticks"),Mode->CombatTick,0);
    TestTrue(TEXT("Actual spawn comes from manifest"),Pawn->GetActorLocation().Equals(Layout.Spawn,.01));
    int32 Props=0;
    for(TActorIterator<AStaticMeshActor> It(World);It;++It)
    {
        if(!It->ActorHasTag(TEXT("SmelteryPropBoundary")))continue;++Props;
        auto* Box=*It;const FVector C=Box->GetActorLocation(),E=Box->GetActorScale3D()*50;
        const FRotator R=Box->GetActorRotation();
        // Choose the face most oriented toward the centre of the walkable room.
        FVector LocalNormal(1,0,0);double Score=-1.e30;
        for(const FVector N:{FVector(1,0,0),FVector(-1,0,0),FVector(0,1,0),FVector(0,-1,0)})
        {const double S=FVector::DotProduct(R.RotateVector(N),-C);if(S>Score){Score=S;LocalNormal=N;}}
        const FVector Normal=R.RotateVector(LocalNormal);
        const double Edge=FMath::Abs(LocalNormal.X)>0?E.X:E.Y;
        FVector Start=C+Normal*(Edge+130);Start.Z=95;
        Pawn->SetActorLocation(Start);Pawn->ResetFighter(false);Pawn->MoveSwept(-Normal*(Edge*2+500));
        const FVector Local=R.UnrotateVector(Pawn->GetActorLocation()-C);
        TestTrue(TEXT("Actual pawn sweep stops outside work island"),FVector::DotProduct(Local,LocalNormal)>=Edge+32);
        FHitResult Hit;FCollisionQueryParams Query;Query.AddIgnoredActor(Pawn);
        const FVector CameraStart=C+Normal*(Edge+200),CameraEnd=C-Normal*(Edge+200);
        const bool Blocked=World->SweepSingleByChannel(Hit,CameraStart,CameraEnd,FQuat::Identity,ECC_Camera,FCollisionShape::MakeSphere(16),Query);
        TestTrue(TEXT("Actual camera sphere sweep hits intended work island"),Blocked && Hit.GetActor()==Box);
        for(const EWardenAction Action:{EWardenAction::Dodge,EWardenAction::Jump})
        {
            Pawn->SetActorLocation(Start);Pawn->ResetFighter(false);Pawn->BeginAction(Action,0,-Normal);
            bool Penetrated=false;
            for(int32 Tick=0;Tick<100;++Tick)
            {
                Pawn->StepFighter(-Normal);Pawn->Fight.Advance();
                TArray<FOverlapResult> Overlaps;
                World->OverlapMultiByChannel(Overlaps,Pawn->GetActorLocation(),FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(33,89),Query);
                for(const auto& O:Overlaps)if(O.GetActor()==Box)Penetrated=true;
            }
            TestFalse(Action==EWardenAction::Jump?TEXT("Jump/landing never penetrates work island"):TEXT("Roll never penetrates work island"),Penetrated);
        }
    }
    TestTrue(TEXT("Actual foreground collision was exercised"),Props>0);
    for(const FVector Direction:{FVector(1,0,0),FVector(-1,0,0),FVector(0,1,0),FVector(0,-1,0),FVector(1,1,0).GetSafeNormal(),FVector(-1,-1,0).GetSafeNormal()})
    {
        Pawn->SetActorLocation(FVector(0,0,95));Pawn->ResetFighter(false);Pawn->MoveSwept(Direction*5000);
        const FVector P=Pawn->GetActorLocation();TestTrue(TEXT("Outer pawn envelope remains closed"),FMath::Abs(P.X)<=Layout.HalfSize.X-33 && FMath::Abs(P.Y)<=Layout.HalfSize.Y-33);
    }
    Pawn->SetActorLocation(Layout.Spawn);Pawn->ResetFighter(false);
    Mode->ShowFrontPage(EWardenFrontScreen::Pause);Mode->ShowFrontPage(EWardenFrontScreen::Settings);
    TestTrue(TEXT("Settings pauses no-boss scene"),Mode->bPaused && !Mode->bTitle);
    Mode->ShowFrontPage(EWardenFrontScreen::Pause);Mode->SetMenuOpen(false);
    Mode->bPaused=true;const FVector Before=Pawn->GetActorLocation();Mode->TickSmelteryWalkthrough(.1f);
    TestTrue(TEXT("Pause freezes actual pawn"),Before.Equals(Pawn->GetActorLocation()));
    GEngine->DestroyWorldContext(World);World->DestroyWorld(false);return true;
}
#endif
