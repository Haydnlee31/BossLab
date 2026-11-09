#include "WardenPrototype.h"
#include "Components/StaticMeshComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Misc/AutomationTest.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRevampTrialTest,"RevampTrial.SkinnedCharactersAndMotion",(EAutomationTestFlags::EditorContext|EAutomationTestFlags::ClientContext)|EAutomationTestFlags::EngineFilter)
bool FRevampTrialTest::RunTest(const FString&)
{
    if(!FParse::Param(FCommandLine::Get(),TEXT("BossLabRevamp"))) { AddError(TEXT("Run this dedicated trial with BOSSLAB_OUTFIT=revamp; baseline BossLab tests are separate.")); return false; }
    auto* W=UWorld::CreateWorld(EWorldType::Game,false); GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
    auto* P=W->SpawnActor<AWardenChallenger>(FVector(0,0,95),FRotator::ZeroRotator); P->DispatchBeginPlay(); P->ResetFighter(false);
    auto Path=[&]{ return P->VisualBody->GetSkinnedAsset()?P->VisualBody->GetSkinnedAsset()->GetPathName():FString(); };
    TestTrue(TEXT("Player wears generated knight, not fallback"),P->bRevampOutfit && Path().Contains(TEXT("SKM_RevampPlayer")));
    TestTrue(TEXT("Skinned costume visible"),P->VisualBody->IsVisible());
    TInlineComponentArray<UStaticMeshComponent*> All(P);
    for(auto* C:All)
    {
        if(C->ComponentHasTag(TEXT("Ashbound")) || C->ComponentHasTag(TEXT("V13Trial"))) TestFalse(TEXT("Older costumes hidden"),C->IsVisible());
        if(C->GetName().StartsWith(TEXT("Sword"))) TestTrue(TEXT("Engine sword shown for player"),C->IsVisible());
    }
    P->ResetFighter(true);
    TestTrue(TEXT("Boss wears generated Regent"),P->bRevampOutfit && Path().Contains(TEXT("SKM_RevampRegent")));
    if(auto* Crown=FindObject<UStaticMeshComponent>(P,TEXT("Crown"))) TestFalse(TEXT("Primitive boss crown hidden"),Crown->IsVisible());
    for(int32 I=0;I<4;++I) P->ResetFighter(I%2==0);
    TInlineComponentArray<UStaticMeshComponent*> Reset(P); TestEqual(TEXT("Reset does not duplicate components"),Reset.Num(),All.Num());

    const TCHAR* Bones[]={TEXT("foot_l"),TEXT("foot_r"),TEXT("hand_l"),TEXT("hand_r"),TEXT("head")};
    float MinFoot=10000,MaxGrip=0,MaxStretch=0,MinCloth=10000,MinTop=10000; bool Finite=true; int32 Chains[2]={0,0};
    auto CheckCloth=[&](bool Boss)
    {
        const auto& Ref=P->VisualBody->GetSkinnedAsset()->GetRefSkeleton();
        Chains[Boss]=P->SwingChains.Num();
        for(const auto& C:P->SwingChains)
        {
            if(C.Bones.Num()) MinTop=FMath::Min(MinTop,float(P->VisualBody->GetBoneLocationByName(Ref.GetBoneName(C.Bones[0]),EBoneSpaces::WorldSpace).Z));
            for(int32 K=1;K<C.Bones.Num();++K)
            {
                const FVector A=P->VisualBody->GetBoneLocationByName(Ref.GetBoneName(C.Bones[K-1]),EBoneSpaces::WorldSpace);
                const FVector B=P->VisualBody->GetBoneLocationByName(Ref.GetBoneName(C.Bones[K]),EBoneSpaces::WorldSpace);
                Finite&=!B.ContainsNaN();
                const float Rest=(Ref.GetRefBonePose()[C.Bones[K]].GetTranslation()).Size();
                MaxStretch=FMath::Max(MaxStretch,FMath::Abs(float(FVector::Dist(A,B))/Rest-1));
                MinCloth=FMath::Min(MinCloth,float(B.Z));
            }
        }
    };
    for(bool Boss:{false,true})
    {
        for(int32 Direction=0;Direction<8;++Direction)
        {
            P->ResetFighter(Boss); const FVector Travel=FRotator(0,Direction*45,0).Vector(); P->BeginAction(EWardenAction::Dodge,0,Travel);
            for(int32 Age:{0,6,12,18,24,30,35})
            {
                P->Fight.Age=Age; P->CombatPose(Travel*8.f);
                for(auto* B:Bones) { const FVector X=P->VisualBody->GetBoneLocationByName(B,EBoneSpaces::WorldSpace); Finite&=!X.ContainsNaN(); }
                for(int32 F=0;F<2;++F) MinFoot=FMath::Min(MinFoot,float(P->VisualBody->GetBoneLocationByName(Bones[F],EBoneSpaces::WorldSpace).Z));
                CheckCloth(Boss);
            }
        }
        P->ResetFighter(Boss); P->BeginAction(EWardenAction::Strike);
        for(int32 Age=0;Age<86;++Age) { P->Fight.Age=Age; P->CombatPose(FVector::ZeroVector); MaxGrip=FMath::Max(MaxGrip,P->GripError); }
    }
    TestTrue(TEXT("Bones finite through sampled rolls"),Finite);
    TestTrue(TEXT("Feet stay above flat floor in sampled rolls"),MinFoot>=-2.f);
    TestTrue(TEXT("Engine hand/hilt constraint unchanged (not glove-fit proof)"),MaxGrip<3.f);
    TestTrue(TEXT("Both costumes carry swing chains"),Chains[0]>0 && Chains[1]>0);
    TestTrue(TEXT("Swing chains keep bone length through rolls"),MaxStretch<.05f);
    TestTrue(TEXT("Swing chains stay above the flat floor"),FMath::Min(MinCloth,MinTop)>=-1.f);
    AddInfo(FString::Printf(TEXT("Revamp: sampled roll foot minZ %.3fcm, engine grip %.3fcm, chains %d/%d, max chain stretch %.4f, chain minZ %.3fcm (top minZ %.3fcm). Presentation test, not cloth/clipping certification."),MinFoot,MaxGrip,Chains[0],Chains[1],MaxStretch,MinCloth,MinTop));
    GEngine->DestroyWorldContext(W); W->DestroyWorld(false); return true;
}
#endif
