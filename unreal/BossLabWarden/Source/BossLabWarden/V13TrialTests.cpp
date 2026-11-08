#include "WardenPrototype.h"
#include "Components/StaticMeshComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "StaticMeshResources.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Misc/AutomationTest.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FV13TrialTest,"V13Trial.ActualTransferAndMotion",(EAutomationTestFlags::EditorContext|EAutomationTestFlags::ClientContext)|EAutomationTestFlags::EngineFilter)
bool FV13TrialTest::RunTest(const FString&)
{
    FString Path;
    if(!FParse::Value(FCommandLine::Get(),TEXT("BossLabV13="),Path)) { AddError(TEXT("Run this dedicated trial with BOSSLAB_OUTFIT=v13; baseline BossLab tests are separate.")); return false; }
    auto* W=UWorld::CreateWorld(EWorldType::Game,false); GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
    auto* P=W->SpawnActor<AWardenChallenger>(FVector(0,0,95),FRotator::ZeroRotator); P->DispatchBeginPlay(); P->ResetFighter(false);
    TestTrue(TEXT("Actual exported V13 selected, not fallback"),P->bV13Outfit);
    TestEqual(TEXT("Frozen Blender source identity"),P->V13SourceHash,FString(TEXT("2457b527d43ceea7bf94f16d3fb15fcda230a302253956c36d9c2cbd4ed00839")));
    TInlineComponentArray<UStaticMeshComponent*> All(P); TArray<UStaticMeshComponent*> Parts;
    int32 Triangles=0,Sections=0; bool Sword=false;
    for(auto* C:All) if(C->ComponentHasTag(TEXT("V13Trial")))
    {
        Parts.Add(C); TestTrue(TEXT("Imported part visible/noncolliding"),C->IsVisible() && C->GetCollisionEnabled()==ECollisionEnabled::NoCollision);
        const UStaticMesh* Mesh=C->GetStaticMesh();
        if(!TestNotNull(TEXT("Real transferred render mesh"),Mesh) || !Mesh->GetRenderData()) continue;
        const auto& LOD=Mesh->GetRenderData()->LODResources[0];
        for(const auto& S:LOD.Sections) { Triangles+=S.NumTriangles; ++Sections; TestTrue(TEXT("Material slot and UV metadata initialized"),Mesh->GetStaticMaterials().IsValidIndex(S.MaterialIndex) && Mesh->GetStaticMaterials()[S.MaterialIndex].UVChannelData.bInitialized); }
        if(C->GetName().EndsWith(TEXT("_sword"))) { Sword=true; TestTrue(TEXT("Imported sword tip stays within 2mm of engine reach (decorative tip relief)"),FMath::IsNearlyEqual(float(Mesh->GetBoundingBox().Max.Z),148.f,.2f)); }
    }
    TestTrue(TEXT("Actual whole costume geometry imported within test budget"),Triangles>50000 && Triangles<=120000 && Parts.Num()>=17 && Parts.Num()<=40);
    TestTrue(TEXT("Actual sword group imported"),Sword); TestFalse(TEXT("Studio body replaces visible mannequin without hiding attachments"),P->VisualBody->IsVisible());
    for(int32 I=0;I<4;++I) P->ResetFighter(I%2==0);
    TInlineComponentArray<UStaticMeshComponent*> Reset(P); TestEqual(TEXT("Reset does not duplicate imported meshes"),Reset.Num(),All.Num());
    P->ResetFighter(true); for(auto* C:Parts) TestFalse(TEXT("Boss does not wear player trial"),C->IsVisible());
    P->ResetFighter(false); for(auto* C:Parts) TestTrue(TEXT("Player trial restored after reset"),C->IsVisible());
    float MinZ=10000,MaxGrip=0; bool Finite=true;
    // Sample all actual imported vertices at representative roll phases in eight directions.
    for(int32 Direction=0;Direction<8;++Direction)
    {
        P->ResetFighter(false); const FVector Travel=FRotator(0,Direction*45,0).Vector(); P->BeginAction(EWardenAction::Dodge,0,Travel);
        for(int32 Age:{0,6,12,18,24,30,35})
        {
            P->Fight.Age=Age; P->CombatPose(Travel*8.f);
            for(auto* C:Parts)
            {
                C->UpdateComponentToWorld(); const auto& V=C->GetStaticMesh()->GetRenderData()->LODResources[0].VertexBuffers.PositionVertexBuffer;
                for(uint32 I=0;I<V.GetNumVertices();++I) { const FVector X=C->GetComponentTransform().TransformPosition(FVector(V.VertexPosition(I))); Finite &= !X.ContainsNaN(); MinZ=FMath::Min(MinZ,float(X.Z)); }
            }
        }
    }
    P->ResetFighter(false); P->BeginAction(EWardenAction::Strike);
    for(int32 Age=0;Age<86;++Age) { P->Fight.Age=Age; P->CombatPose(FVector::ZeroVector); MaxGrip=FMath::Max(MaxGrip,P->GripError); }
    TestTrue(TEXT("Imported geometry finite through sampled motion"),Finite); TestTrue(TEXT("Imported geometry clears flat floor in sampled eight-direction rolls"),MinZ>=-2.f);
    TestTrue(TEXT("Engine shared hand/hilt constraint unchanged (not imported glove fit proof)"),MaxGrip<3.f);
    P->Fight.Health=0; P->Fight.Action=EWardenAction::Dead; P->DeathAge=1.5f; P->CombatPose(FVector::ZeroVector);
    float DeathMin=10000; bool DeathFinite=true;
    for(auto* C:Parts)
    {
        C->UpdateComponentToWorld(); const auto& V=C->GetStaticMesh()->GetRenderData()->LODResources[0].VertexBuffers.PositionVertexBuffer;
        for(uint32 I=0;I<V.GetNumVertices();++I) { const FVector X=C->GetComponentTransform().TransformPosition(FVector(V.VertexPosition(I))); DeathFinite &= !X.ContainsNaN(); DeathMin=FMath::Min(DeathMin,float(X.Z)); }
    }
    TestTrue(TEXT("Imported geometry finite and above flat floor in sampled death pose"),DeathFinite && DeathMin>=-2.f);
    AddInfo(FString::Printf(TEXT("Sampled death minimum %.3fcm"),DeathMin));
    AddInfo(FString::Printf(TEXT("Actual V13: %d parts, %d triangles, %d sections; sampled roll minZ %.3fcm; engine grip %.3fcm. Rigid test, not cloth/skin/collision certification."),Parts.Num(),Triangles,Sections,MinZ,MaxGrip));
    GEngine->DestroyWorldContext(W); W->DestroyWorld(false); return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FV13FailureFallbackTest,"V13Trial.AssetFailureFallback",(EAutomationTestFlags::EditorContext|EAutomationTestFlags::ClientContext)|EAutomationTestFlags::EngineFilter)
bool FV13FailureFallbackTest::RunTest(const FString&)
{
    FString Path;
    if(!FParse::Value(FCommandLine::Get(),TEXT("BossLabV13="),Path)) { AddError(TEXT("Fallback test requires an explicitly invalid V13 asset path.")); return false; }
    AddExpectedMessage(TEXT("V13 trial unavailable"),ELogVerbosity::Warning,EAutomationExpectedMessageFlags::Contains,0,false);
    auto* W=UWorld::CreateWorld(EWorldType::Game,false); GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
    auto* P=W->SpawnActor<AWardenChallenger>(FVector(0,0,95),FRotator::ZeroRotator); P->DispatchBeginPlay(); P->ResetFighter(false);
    TestFalse(TEXT("Invalid asset does not enable trial"),P->bV13Outfit);
    auto* Original=FindObject<UStaticMeshComponent>(P,TEXT("AshHelmet"));
    TestTrue(TEXT("Usable original outfit retained"),Original && Original->IsVisible() && P->OutfitTriangles==15448 && P->VisualBody->IsVisible());
    TInlineComponentArray<UStaticMeshComponent*> Parts(P); int32 TrialCount=0;
    for(auto* Part:Parts) if(Part->ComponentHasTag(TEXT("V13Trial"))) ++TrialCount;
    TestEqual(TEXT("Invalid data leaves no partial imported components"),TrialCount,0);
    AddInfo(FString::Printf(TEXT("Fallback verified for deliberately invalid fixture %s"),*Path));
    GEngine->DestroyWorldContext(W); W->DestroyWorld(false); return true;
}
#endif
