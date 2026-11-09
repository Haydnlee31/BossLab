#include "WardenPrototype.h"
#include "Components/PrimitiveComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/LightComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "EngineUtils.h"
#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonArenaTest,"BossLab.Arena.DungeonIsPresentationOnly",(EAutomationTestFlags::EditorContext|EAutomationTestFlags::ClientContext)|EAutomationTestFlags::EngineFilter)
bool FDungeonArenaTest::RunTest(const FString&)
{
    auto* W=UWorld::CreateWorld(EWorldType::Game,false); GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
    // Stand-in for one existing collision block; it must keep transform and collision.
    auto* Block=W->SpawnActor<AStaticMeshActor>(FVector(1360,0,130),FRotator::ZeroRotator);
    Block->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube")));
    Block->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
    const FTransform Before=Block->GetActorTransform();
    TSet<AActor*> Existing; for(TActorIterator<AActor> It(W);It;++It) Existing.Add(*It);
    FWardenDungeon D; AWardenArenaMode::BuildDungeon(W,D);
    int32 Colliding=0,Instances=0,Inside=0,Lights=0;
    for(TActorIterator<AActor> It(W);It;++It)
    {
        if(Existing.Contains(*It)) continue;
        TInlineComponentArray<UPrimitiveComponent*> Parts(*It);
        for(auto* C:Parts)
        {
            if(C->GetCollisionEnabled()!=ECollisionEnabled::NoCollision) ++Colliding;
            if(auto* I=Cast<UInstancedStaticMeshComponent>(C))
                for(int32 K=0;K<I->GetInstanceCount();++K)
                {
                    FTransform T; I->GetInstanceTransform(K,T,true); ++Instances;
                    // Nothing raised may stand on the fight floor: inside the wall line
                    // only flush inlays (<1 cm) and overhead pieces (>4 m) are allowed.
                    const FBox B=I->GetStaticMesh()->GetBounds().GetBox().TransformBy(T);
                    if(FVector2D(T.GetLocation()).Size()<1330 && B.Max.Z>1 && B.Min.Z<400) ++Inside;
                }
        }
        TInlineComponentArray<ULightComponent*> L(*It); Lights+=L.Num();
    }
    AWardenArenaMode::AnimateDungeon(D,1.5f);
    TestEqual(TEXT("Dungeon dressing adds no collision"),Colliding,0);
    TestEqual(TEXT("No raised dungeon geometry inside the wall line below 4 m"),Inside,0);
    TestTrue(TEXT("Collision block keeps its transform"),Before.Equals(Block->GetActorTransform()));
    TestTrue(TEXT("Collision block keeps BlockAll"),Block->GetStaticMeshComponent()->GetCollisionProfileName()==TEXT("BlockAll"));
    TestTrue(TEXT("Dungeon materials load"),Block->GetStaticMeshComponent()->GetMaterial(0) && Block->GetStaticMeshComponent()->GetMaterial(0)->GetName()==TEXT("M_DungeonWall"));
    TestTrue(TEXT("Fire lights and embers present"),D.Lights.Num()>=15 && D.Embers.IsValid());
    AddInfo(FString::Printf(TEXT("Dungeon: %d instances, %d lights (%d flickering), %d colliding, %d inside wall line."),Instances,Lights,D.Lights.Num(),Colliding,Inside));
    GEngine->DestroyWorldContext(W); W->DestroyWorld(false); return true;
}
#endif
