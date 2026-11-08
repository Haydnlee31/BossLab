// Opt-in generated characters (TRELLIS.2 from the approved concepts), skinned to the
// mannequin skeleton with distance-based weights. Presentation only: combat timing,
// reach and collision stay engine-owned. See docs/CLAUDE_REVAMP.md.
#include "WardenPrototype.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

namespace RevampTrial
{
const TCHAR* PlayerPath=TEXT("/Game/BossLab/Revamp/SKM_RevampPlayer");
const TCHAR* BossPath=TEXT("/Game/BossLab/Revamp/SKM_RevampRegent");

// Poses are copied from the hidden mannequin by bone index, so a costume must share
// the mannequin's exact bone order and local translations; only rest rotations may differ.
bool Compatible(const USkinnedAsset* Costume,const USkinnedAsset* Mannequin,FString& Error)
{
    if(!Costume || !Mannequin) { Error=TEXT("missing asset"); return false; }
    const auto& A=Costume->GetRefSkeleton(); const auto& B=Mannequin->GetRefSkeleton();
    if(A.GetNum()!=B.GetNum()) { Error=FString::Printf(TEXT("bone count %d vs %d"),A.GetNum(),B.GetNum()); return false; }
    for(int32 I=0;I<A.GetNum();++I)
    {
        if(A.GetBoneName(I)!=B.GetBoneName(I) || A.GetParentIndex(I)!=B.GetParentIndex(I))
        { Error=FString::Printf(TEXT("bone %d is %s, mannequin has %s"),I,*A.GetBoneName(I).ToString(),*B.GetBoneName(I).ToString()); return false; }
        if(!A.GetRefBonePose()[I].GetTranslation().Equals(B.GetRefBonePose()[I].GetTranslation(),.1))
        { Error=FString::Printf(TEXT("bone %s offset differs"),*A.GetBoneName(I).ToString()); return false; }
    }
    return true;
}
}

bool AWardenChallenger::DressRevamp()
{
    using namespace RevampTrial;
    bRevampOutfit=false;
    USkinnedAsset* Mannequin=Body->GetSkeletalMeshAsset();
    if(FParse::Param(FCommandLine::Get(),TEXT("BossLabRevamp")))
    {
        FString Error;
        auto* Costume=LoadObject<USkeletalMesh>(nullptr,bBoss?BossPath:PlayerPath);
        if(Compatible(Costume,Mannequin,Error))
        {
            if(VisualBody->GetSkinnedAsset()!=Costume) VisualBody->SetSkinnedAssetAndUpdate(Costume);
            VisualBody->EmptyOverrideMaterials();
            bRevampOutfit=true;
            return true;
        }
        UE_LOG(LogTemp,Warning,TEXT("Revamp %s unavailable (%s); original outfit retained"),bBoss?TEXT("boss"):TEXT("player"),*Error);
    }
    if(Mannequin && VisualBody->GetSkinnedAsset()!=Mannequin) VisualBody->SetSkinnedAssetAndUpdate(Mannequin);
    return false;
}
