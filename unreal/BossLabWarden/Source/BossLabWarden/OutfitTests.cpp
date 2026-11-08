#include "WardenPrototype.h"
#include "Components/StaticMeshComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "StaticMeshResources.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "PhysicsEngine/BodySetup.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAshboundAssemblyTest,"BossLab.Outfit.AssemblyMaterialsAndContact",(EAutomationTestFlags::EditorContext|EAutomationTestFlags::ClientContext)|EAutomationTestFlags::EngineFilter)
bool FAshboundAssemblyTest::RunTest(const FString&)
{
    auto* W=UWorld::CreateWorld(EWorldType::Game,false); GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
    auto* P=W->SpawnActor<AWardenChallenger>(FVector(0,0,95),FRotator::ZeroRotator); P->DispatchBeginPlay(); P->ResetFighter(false);
    auto* Early=W->SpawnActor<AWardenChallenger>(FVector(500,0,95),FRotator::ZeroRotator);
    Early->ResetFighter(false); Early->DispatchBeginPlay();
    TestFalse(TEXT("Late BeginPlay cannot reveal the obsolete player sword"),FindObject<UStaticMeshComponent>(Early,TEXT("SwordBlade"))->IsVisible());
    TInlineComponentArray<UStaticMeshComponent*> All(P); TArray<UStaticMeshComponent*> Parts;
    int32 Triangles=0,Sections=0;
    for(auto* C:All) if(C->ComponentHasTag(TEXT("Ashbound")))
    {
        Parts.Add(C); TestTrue(TEXT("Outfit part visible and non-colliding"),C->IsVisible() && C->GetCollisionEnabled()==ECollisionEnabled::NoCollision);
        UStaticMesh* Mesh=C->GetStaticMesh(); TestNotNull(TEXT("Real render mesh"),Mesh);
        const auto& LOD=Mesh->GetRenderData()->LODResources[0];
        for(const auto& Section:LOD.Sections)
        {
            Triangles+=Section.NumTriangles; ++Sections;
            TestTrue(TEXT("Every rendered section resolves its material"),Mesh->GetStaticMaterials().IsValidIndex(Section.MaterialIndex));
            TestTrue(TEXT("Runtime material has initialized UV streaming metadata"),Mesh->GetStaticMaterials()[Section.MaterialIndex].UVChannelData.bInitialized);
            TestNotNull(TEXT("Original material instance is bound"),Cast<UMaterialInstanceDynamic>(Mesh->GetMaterial(Section.MaterialIndex)));
        }
        TestTrue(TEXT("Decorative geometry never cooks physics"),Mesh->GetBodySetup()->bNeverNeedsCookedCollisionData);
    }
    TestTrue(TEXT("Outfit geometric budget"),Triangles>5000 && Triangles<=25000);
    auto* Cape=FindObject<UStaticMeshComponent>(P,TEXT("AshCapeL"));
    const auto& CapeLOD=Cape->GetStaticMesh()->GetRenderData()->LODResources[0];
    const auto* Red=Cast<UMaterialInstanceDynamic>(Cape->GetMaterial(CapeLOD.Sections[0].MaterialIndex));
    FLinearColor Actual; TestTrue(TEXT("Cape color parameter exists"),Red && Red->GetVectorParameterValue(FMaterialParameterInfo(TEXT("Color")),Actual));
    AddInfo(FString::Printf(TEXT("Cape section%d material%s actualRGBA %s"),CapeLOD.Sections[0].MaterialIndex,*Red->GetName(),*Actual.ToString()));
    TestTrue(TEXT("Cape is oxblood, not default grey"),Actual.R>Actual.G*3 && Actual.R>Actual.B*3);
    auto* Blade=FindObject<UStaticMeshComponent>(P,TEXT("OathwakeBlade"));
    const auto Bounds=Blade->GetStaticMesh()->GetBoundingBox();
    TestTrue(TEXT("Visible blade endpoints match engine contact extent"),FMath::IsNearlyEqual(float(Bounds.Min.Z),14.f,.001f) && FMath::IsNearlyEqual(float(Bounds.Max.Z),148.f,.001f));
    for(int32 I=0;I<6;++I) P->ResetFighter(I%2==0);
    TInlineComponentArray<UStaticMeshComponent*> After(P); TestEqual(TEXT("Resets do not duplicate meshes"),After.Num(),All.Num());
    P->ResetFighter(true); for(auto* C:Parts) TestFalse(TEXT("Boss retains its own design"),C->IsVisible());
    P->ResetFighter(false); for(auto* C:Parts) TestTrue(TEXT("Player outfit restored"),C->IsVisible());
    float MinZ=10000; FString Lowest; TMap<FString,float> Minima;
    for(int32 Direction=0;Direction<8;++Direction)
    {
        P->ResetFighter(false); const FVector Travel=FRotator(0,Direction*45,0).Vector(); P->BeginAction(EWardenAction::Dodge,0,Travel);
        for(int32 Tick=0;Tick<36;++Tick)
        {
            P->Fight.Age=Tick; P->CombatPose(Travel*8.f);
            for(auto* C:Parts)
            {
                C->UpdateComponentToWorld();
                const auto& Vertices=C->GetStaticMesh()->GetRenderData()->LODResources[0].VertexBuffers.PositionVertexBuffer;
                for(uint32 V=0;V<Vertices.GetNumVertices();++V)
                {
                    const FVector Position=C->GetComponentTransform().TransformPosition(FVector(Vertices.VertexPosition(V)));
                    if(Position.ContainsNaN()) { AddError(TEXT("Nonfinite outfit vertex")); break; }
                    float& PartMin=Minima.FindOrAdd(C->GetName(),10000.f); PartMin=FMath::Min(PartMin,float(Position.Z));
                    if(Position.Z<MinZ) { MinZ=Position.Z; Lowest=C->GetName(); }
                }
            }
        }
    }
    AddInfo(FString::Printf(TEXT("%d parts, %d rendered triangles, %d sections; eight-direction roll minimum vertex Z %.3fcm (%s)"),Parts.Num(),Triangles,Sections,MinZ,*Lowest));
    for(auto Pair:Minima) if(Pair.Value<0) AddInfo(FString::Printf(TEXT("%s minimum %.3f"),*Pair.Key,Pair.Value));
    TestTrue(TEXT("Outfit clears flat floor through eight-direction roll"),MinZ>=-2.f);
    GEngine->DestroyWorldContext(W); W->DestroyWorld(false); return true;
}
#endif
