#include "WardenPrototype.h"
#include "WardenSmelteryLayout.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "EngineUtils.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSmelteryWalkthroughTest,"BossLab.Arena.SmelteryWalkthroughIsolation",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FSmelteryWalkthroughTest::RunTest(const FString&)
{
    UWorld* World=UWorld::CreateWorld(EWorldType::Game,false);
    GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
    auto* Mode=World->SpawnActor<AWardenArenaMode>();
    Mode->bSmelteryWalkthrough=true;
    Mode->Player=World->SpawnActor<AWardenChallenger>();
    Mode->Player->DispatchBeginPlay(); Mode->DispatchBeginPlay();
    TestNull(TEXT("No boss is spawned"),Mode->Warden.Get());
    Mode->SaveReport(); // F9 must be harmless with no encounter/boss.
    TestFalse(TEXT("No fixed boss controller"),Mode->bRehearsal);
    TestFalse(TEXT("No Regent"),Mode->bRegent);
    TestFalse(TEXT("No title or combat session"),Mode->bTitle);
    TestEqual(TEXT("No combat ticks"),Mode->CombatTick,0);
    int32 Boundaries=0, Floors=0;
    for(TActorIterator<AStaticMeshActor> It(World);It;++It)
    {
        if(It->ActorHasTag(TEXT("SmelteryBoundary")))
        {++Boundaries;TestEqual(TEXT("Boundary blocks camera"),It->GetStaticMeshComponent()->GetCollisionResponseToChannel(ECC_Camera),ECR_Block);}
        if(It->ActorHasTag(TEXT("SmelteryFloor")))++Floors;
        if(It->ActorHasTag(TEXT("SmelteryDressing")))TestEqual(TEXT("Dressing has no collision"),It->GetStaticMeshComponent()->GetCollisionEnabled(),ECollisionEnabled::NoCollision);
    }
    TestEqual(TEXT("Four closed sides"),Boundaries,4); TestEqual(TEXT("One level floor"),Floors,1);
    const FVector Start=Mode->Player->GetActorLocation();
    for(int32 I=0;I<60;++I) {Mode->Player->StepFighter(FVector::ForwardVector,true);Mode->Player->Fight.Advance();}
    TestTrue(TEXT("Player can move and sprint without target"),Mode->Player->GetActorLocation().X>Start.X+300);
    TestFalse(TEXT("No lock target"),Mode->Player->IsLocked());
    // Sweep actual pawn against all cardinal edges and diagonal corners, then
    // repeat from elevated jump height and through a full committed roll.
    for(const FVector Direction : {FVector(1,0,0),FVector(-1,0,0),FVector(0,1,0),FVector(0,-1,0),FVector(1,1,0).GetSafeNormal(),FVector(-1,1,0).GetSafeNormal(),FVector(1,-1,0).GetSafeNormal(),FVector(-1,-1,0).GetSafeNormal()})
    {
        auto Inside=[&](){const FVector P=Mode->Player->GetActorLocation();return FMath::Abs(P.X)<=1367 && FMath::Abs(P.Y)<=1767;};
        for(float Z : {95.f,220.f})
        {
            Mode->Player->SetActorLocation(FVector(0,0,Z));
            Mode->Player->MoveSwept(Direction*5000);
            TestTrue(TEXT("Actual cardinal/corner sweep blocked at floor/jump height"),Inside());
        }
        const FVector Edge(Direction.X*1310,Direction.Y*1710,95);
        Mode->Player->SetActorLocation(Edge);Mode->Player->ResetFighter(false);
        Mode->Player->BeginAction(EWardenAction::Dodge,0,Direction);
        for(int32 I=0;I<WardenRules::DodgeTicks;++I){Mode->Player->StepFighter(FVector::ZeroVector);Mode->Player->Fight.Advance();}
        TestTrue(TEXT("Committed roll cannot cross perimeter"),Inside());
    }
    Mode->Player->SetActorLocation(FVector(0,1500,95)); Mode->Player->ResetFighter(false);
    Mode->Player->PendingAction=EWardenAction::Jump;Mode->TickSmelteryWalkthrough(WardenRules::Step*2);
    TestTrue(TEXT("Walkthrough tick consumes jump input"),Mode->Player->Fight.Action==EWardenAction::Jump);
    TestTrue(TEXT("No old circular radius clamp at Y15m"),Mode->Player->GetActorLocation().Y>1499);
    Mode->Player->ResetFighter(false);Mode->Player->PendingAction=EWardenAction::Dodge;
    Mode->TickSmelteryWalkthrough(WardenRules::Step*2);
    TestTrue(TEXT("Walkthrough tick consumes roll input"),Mode->Player->Fight.Action==EWardenAction::Dodge);
    Mode->ShowFrontPage(EWardenFrontScreen::Pause);Mode->ShowFrontPage(EWardenFrontScreen::Settings);
    TestTrue(TEXT("Settings remains paused without title"),Mode->bPaused && !Mode->bTitle);
    Mode->ShowFrontPage(EWardenFrontScreen::Pause);Mode->SetMenuOpen(false);
    TestTrue(TEXT("Resume returns to walkthrough"),!Mode->bPaused && Mode->bSmelteryWalkthrough && !Mode->Warden);
    Mode->bPaused=true; const FVector Before=Mode->Player->GetActorLocation();
    Mode->TickSmelteryWalkthrough(.1f);
    TestTrue(TEXT("Pause freezes movement"),Before.Equals(Mode->Player->GetActorLocation()));
    TestEqual(TEXT("Movement never advances combat stats"),Mode->CombatTick,0);
    GEngine->DestroyWorldContext(World);World->DestroyWorld(false);return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FHearthAWalkthroughTest,"BossLab.Arena.HearthAWalkthroughIsolation",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FHearthAWalkthroughTest::RunTest(const FString&)
{
    UWorld* World=UWorld::CreateWorld(EWorldType::Game,false);
    GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
    auto* Mode=World->SpawnActor<AWardenArenaMode>();
    Mode->bSmelteryWalkthrough=true;Mode->bHearthA=true;
    Mode->Player=World->SpawnActor<AWardenChallenger>();
    Mode->Player->DispatchBeginPlay(); Mode->DispatchBeginPlay();
    TestNull(TEXT("No boss is spawned"),Mode->Warden.Get());
    Mode->SaveReport(); // F9 must be harmless with no encounter/boss.
    TestFalse(TEXT("No fixed boss controller"),Mode->bRehearsal);
    TestFalse(TEXT("No Regent"),Mode->bRegent);
    TestFalse(TEXT("No title or combat session"),Mode->bTitle);
    TestEqual(TEXT("No combat ticks"),Mode->CombatTick,0);
    int32 Boundaries=0, Floors=0;
    for(TActorIterator<AStaticMeshActor> It(World);It;++It)
    {
        if(It->ActorHasTag(TEXT("SmelteryBoundary")))
        {++Boundaries;TestTrue(TEXT("Boundary is invisible"),It->IsHidden());TestEqual(TEXT("Boundary blocks camera"),It->GetStaticMeshComponent()->GetCollisionResponseToChannel(ECC_Camera),ECR_Block);}
        if(It->ActorHasTag(TEXT("SmelteryFloor")))++Floors;
        if(It->ActorHasTag(TEXT("SmelteryDressing")))TestEqual(TEXT("Dressing has no collision"),It->GetStaticMeshComponent()->GetCollisionEnabled(),ECollisionEnabled::NoCollision);
    }
    TestTrue(TEXT("New arena fixture selected"),Mode->bHearthA);
    TestEqual(TEXT("Four closed sides"),Boundaries,4); TestEqual(TEXT("One level floor"),Floors,1);
    const FVector Start=Mode->Player->GetActorLocation();
    for(int32 I=0;I<60;++I) {Mode->Player->StepFighter(FVector::ForwardVector,true);Mode->Player->Fight.Advance();}
    TestTrue(TEXT("Player can move and sprint without target"),Mode->Player->GetActorLocation().X>Start.X+300);
    TestFalse(TEXT("No lock target"),Mode->Player->IsLocked());
    // Sweep actual pawn against all cardinal edges and diagonal corners, then
    // repeat from elevated jump height and through a full committed roll.
    for(const FVector Direction : {FVector(1,0,0),FVector(-1,0,0),FVector(0,1,0),FVector(0,-1,0),FVector(1,1,0).GetSafeNormal(),FVector(-1,1,0).GetSafeNormal(),FVector(1,-1,0).GetSafeNormal(),FVector(-1,-1,0).GetSafeNormal()})
    {
        auto Inside=[&](){const FVector P=Mode->Player->GetActorLocation();return FMath::Abs(P.X)<=967 && FMath::Abs(P.Y)<=1167;};
        for(float Z : {95.f,220.f})
        {
            Mode->Player->SetActorLocation(FVector(0,0,Z));
            Mode->Player->MoveSwept(Direction*5000);
            TestTrue(TEXT("Actual cardinal/corner sweep blocked at floor/jump height"),Inside());
        }
        const FVector Edge(Direction.X*910,Direction.Y*1110,95);
        Mode->Player->SetActorLocation(Edge);Mode->Player->ResetFighter(false);
        Mode->Player->BeginAction(EWardenAction::Dodge,0,Direction);
        for(int32 I=0;I<WardenRules::DodgeTicks;++I){Mode->Player->StepFighter(FVector::ZeroVector);Mode->Player->Fight.Advance();}
        TestTrue(TEXT("Committed roll cannot cross perimeter"),Inside());
    }
    Mode->Player->SetActorLocation(FVector(900,1100,95)); Mode->Player->ResetFighter(false);
    Mode->Player->PendingAction=EWardenAction::Jump;Mode->TickSmelteryWalkthrough(WardenRules::Step*2);
    TestTrue(TEXT("Walkthrough tick consumes jump input"),Mode->Player->Fight.Action==EWardenAction::Jump);
    TestTrue(TEXT("No old circular radius clamp at diagonal corner"),Mode->Player->GetActorLocation().Y>1099);
    Mode->Player->ResetFighter(false);Mode->Player->PendingAction=EWardenAction::Dodge;
    Mode->TickSmelteryWalkthrough(WardenRules::Step*2);
    TestTrue(TEXT("Walkthrough tick consumes roll input"),Mode->Player->Fight.Action==EWardenAction::Dodge);
    Mode->ShowFrontPage(EWardenFrontScreen::Pause);Mode->ShowFrontPage(EWardenFrontScreen::Settings);
    TestTrue(TEXT("Settings remains paused without title"),Mode->bPaused && !Mode->bTitle);
    Mode->ShowFrontPage(EWardenFrontScreen::Pause);Mode->SetMenuOpen(false);
    TestTrue(TEXT("Resume returns to walkthrough"),!Mode->bPaused && Mode->bSmelteryWalkthrough && !Mode->Warden);
    Mode->bPaused=true; const FVector Before=Mode->Player->GetActorLocation();
    Mode->TickSmelteryWalkthrough(.1f);
    TestTrue(TEXT("Pause freezes movement"),Before.Equals(Mode->Player->GetActorLocation()));
    TestEqual(TEXT("Movement never advances combat stats"),Mode->CombatTick,0);
    // A stationary evidence warmup must never enqueue a backstep/roll.
    Mode->bPaused=false;Mode->bScriptedPlayer=true;Mode->bSmelteryTiming=true;
    Mode->DemoTick=Mode->DemoRounds=0;Mode->Player->ResetFighter(false);
    const FVector WarmupStart=Mode->Player->GetActorLocation();
    for(int32 I=0;I<300;++I)Mode->TickSmelteryWalkthrough(WardenRules::Step);
    TestTrue(TEXT("Study warmup leaves actual pawn stationary"),WarmupStart.Equals(Mode->Player->GetActorLocation(),.1f));
    TestTrue(TEXT("Study warmup never rolls or jumps"),Mode->Player->Fight.Action==EWardenAction::Ready);
    GEngine->DestroyWorldContext(World);World->DestroyWorld(false);return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FHearthA2ManifestTest,"BossLab.Arena.HearthA2ManifestValidation",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FHearthA2ManifestTest::RunTest(const FString&)
{
    // Asset-independent: checks the future manifest contract without importing
    // or pretending to validate A2 geometry/lighting in the existing game.
    const FString Valid=TEXT(R"({"schema_version":2,"scene_id":"hearth-a2","coordinate_space":"unreal_cm",
      "walkable_cm":[1600,1800],"spawn_cm":[400,-400,95],"entry_target_cm":[0,500,95],"entry_pitch_deg":-12,
      "instances":[{"asset":"/Game/BossLab/HearthA2/SM_Floor","location_cm":[0,0,0],"rotation_deg":[0,0,0],"scale":[1,1,1]}],
      "lights":[{"fixture_id":"window","type":"spot","location_cm":[-500,1000,600],"target_cm":[0,0,0],"color_rgb":[0.6,0.7,1],"intensity_lumens":16000,"attenuation_radius_cm":4000,"inner_angle_deg":16,"outer_angle_deg":27,"casts_shadows":true}],"camera_collision":[],"study_waypoints_cm":[[0,600,95],[-500,0,95],[0,-500,95]],"prop_collision":[{"cluster_id":"anvil","location_cm":[550,-100,80],"extent_cm":[80,100,80],"yaw_deg":20}]})");
    auto Parse=[&](const FString& Text){TSharedPtr<FJsonObject> O;FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text),O);return O;};
    WardenSmelteryLayout::FLayout L;FString Error;
    TestTrue(TEXT("Complete explicit contract accepted"),WardenSmelteryLayout::Validate(Parse(Valid),L,Error));
    TestTrue(TEXT("Collision consumes manifest centimetres"),L.HalfSize.Equals(FVector2D(800,900)));
    TestTrue(TEXT("Spawn is already converted, never mirrored twice"),L.Spawn.Equals(FVector(400,-400,95)));
    TestTrue(TEXT("Entry direction follows manifest target"),FMath::IsNearlyEqual(L.Entry.Yaw,113.96249f,.01f));
    for(const auto& Pair:TArray<TPair<FString,FString>>{
        {TEXT("[1600,1800]"),TEXT("[2000,2400]")},
        {TEXT("unreal_cm"),TEXT("blender_m")},
        {TEXT("/HearthA2/"),TEXT("/HearthA/")},
        {TEXT("[1,1,1]"),TEXT("[-1,1,1]")},
        {TEXT("[400,-400,95]"),TEXT("[400,-880,95]")},
        {TEXT("16000"),TEXT("90000")},
        {TEXT("[80,100,80]"),TEXT("[80,-100,80]")},
        {TEXT("[550,-100,80]"),TEXT("[400,-400,95]")},
        {TEXT("\"spot\""),TEXT("\"point\"")},
        {TEXT("\"fixture_id\""),TEXT("\"missing_fixture\"")}})
        TestFalse(TEXT("Malformed contract fails without fallback"),WardenSmelteryLayout::Validate(Parse(Valid.Replace(*Pair.Key,*Pair.Value)),L,Error));
    auto TooMany=Parse(Valid);auto Lights=TooMany->GetArrayField(TEXT("lights"));
    const auto FirstLight=Lights[0];while(Lights.Num()<7)Lights.Add(FirstLight);TooMany->SetArrayField(TEXT("lights"),Lights);
    TestFalse(TEXT("Excess lights rejected instead of silently truncated"),WardenSmelteryLayout::Validate(TooMany,L,Error));
    auto NoEnclosure=Parse(Valid);NoEnclosure->SetStringField(TEXT("camera_boundary_mode"),TEXT("outer_proxies"));
    TestFalse(TEXT("Outer camera cannot disable field collision without enclosing proxies"),WardenSmelteryLayout::Validate(NoEnclosure,L,Error));
    auto BlockedRoute=Parse(Valid);auto Prop=BlockedRoute->GetArrayField(TEXT("prop_collision"))[0]->AsObject();
    TArray<TSharedPtr<FJsonValue>> Position;for(double V:{0.,600.,80.})Position.Add(MakeShared<FJsonValueNumber>(V));Prop->SetArrayField(TEXT("location_cm"),Position);
    TestFalse(TEXT("Route through a work island rejected before tour"),WardenSmelteryLayout::Validate(BlockedRoute,L,Error));
    TestTrue(TEXT("Rotated proxy sweep detects crossing"),WardenSmelteryLayout::SegmentHitsProxy(FVector(-500,0,95),FVector(500,0,95),FVector(0,0,80),FVector(80,100,80),35,FVector(50,50,90)));
    TestFalse(TEXT("Clear route passes rotated proxy"),WardenSmelteryLayout::SegmentHitsProxy(FVector(-500,500,95),FVector(500,500,95),FVector(0,0,80),FVector(80,100,80),35,FVector(50,50,90)));
    TestFalse(TEXT("Absent manifest rejected"),WardenSmelteryLayout::Validate(nullptr,L,Error));
    return true;
}
#endif
