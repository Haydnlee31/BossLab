// Opt-in generated characters (TRELLIS.2 from the approved concepts), skinned to the
// mannequin skeleton with distance-based weights, plus cape/robe swing chains.
// Presentation only: combat timing, reach and collision stay engine-owned.
// See docs/CLAUDE_REVAMP.md.
#include "WardenPrototype.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "WardenCombat.h"

namespace RevampTrial
{
const TCHAR* PlayerPath=TEXT("/Game/BossLab/Revamp/SKM_RevampPlayer");
const TCHAR* BossPath=TEXT("/Game/BossLab/Revamp/SKM_RevampRegent");

// Poses are copied from the hidden mannequin by bone index, so a costume must share
// the mannequin's exact bone order and local translations; only rest rotations may differ.
// Any further bones must be swing chains (cape_*) appended after the mannequin's.
bool Compatible(const USkinnedAsset* Costume,const USkinnedAsset* Mannequin,FString& Error)
{
    if(!Costume || !Mannequin) { Error=TEXT("missing asset"); return false; }
    const auto& A=Costume->GetRefSkeleton(); const auto& B=Mannequin->GetRefSkeleton();
    if(A.GetNum()<B.GetNum()) { Error=FString::Printf(TEXT("bone count %d vs %d"),A.GetNum(),B.GetNum()); return false; }
    for(int32 I=B.GetNum();I<A.GetNum();++I)
        if(!A.GetBoneName(I).ToString().StartsWith(TEXT("cape_")) || A.GetParentIndex(I)>=I)
        { Error=FString::Printf(TEXT("extra bone %s is not an appended swing chain"),*A.GetBoneName(I).ToString()); return false; }
    for(int32 I=0;I<B.GetNum();++I)
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
    SwingChains.Empty();
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

// Verlet chains on the fixed presentation step: each particle is pulled toward where
// the rigid (unsimulated) cape would be, more loosely further down, then kept at bone
// length, outside body spheres and above the arena floor. Bone rotations then aim each
// segment at its simulated child. No cloth asset, no physics scene, no gameplay effect.
void AWardenChallenger::SwingCloth(const TArray<FTransform>& CS)
{
    if(!bRevampOutfit || !VisualBody->GetSkinnedAsset()) return;
    const auto& Ref=VisualBody->GetSkinnedAsset()->GetRefSkeleton();
    const int32 First=CS.Num();
    if(Ref.GetNum()<=First || VisualBody->BoneSpaceTransforms.Num()!=Ref.GetNum()) return;
    TArray<FTransform> Rest; Rest.SetNum(Ref.GetNum());
    for(int32 I=0;I<Ref.GetNum();++I) { const int32 P=Ref.GetParentIndex(I); Rest[I]=P<0?Ref.GetRefBonePose()[I]:Ref.GetRefBonePose()[I]*Rest[P]; }
    if(SwingChains.IsEmpty())
    {
        for(int32 I=First;I<Ref.GetNum();++I)
        {
            const int32 P=Ref.GetParentIndex(I);
            FWardenSwingChain* Chain=P<First?nullptr:SwingChains.FindByPredicate([P](const FWardenSwingChain& C){ return C.Bones.Last()==P; });
            if(!Chain) Chain=&SwingChains.AddDefaulted_GetRef();
            Chain->Bones.Add(I);
        }
        for(auto& Chain:SwingChains)
        {
            float Best=MAX_flt;
            for(const TCHAR* Name:{TEXT("pelvis"),TEXT("spine_01"),TEXT("spine_02"),TEXT("spine_03"),TEXT("spine_04"),TEXT("spine_05")})
            {
                const int32 I=Ref.FindBoneIndex(Name);
                const float D=I<0?MAX_flt:FVector::Dist(Rest[I].GetLocation(),Rest[Chain.Bones[0]].GetLocation());
                if(D<Best) { Best=D; Chain.Anchor=I; }
            }
        }
    }
    const FTransform World=VisualBody->GetComponentTransform();
    const float Scale=World.GetScale3D().X;
    const float Floor=GetActorLocation().Z-95*GetActorScale3D().Z+2*Scale;
    struct FSwingSphere { FVector Rest,Now; float Radius; };
    TArray<FSwingSphere> Spheres;
    auto AddSphere=[&](const TCHAR* A,const TCHAR* B,float Radius)
    {
        const int32 I=Ref.FindBoneIndex(A),J=B?Ref.FindBoneIndex(B):I;
        if(I<0 || J<0 || I>=First || J>=First) return;
        Spheres.Add({(Rest[I].GetLocation()+Rest[J].GetLocation())*.5f,World.TransformPosition((CS[I].GetLocation()+CS[J].GetLocation())*.5f),Radius});
    };
    AddSphere(TEXT("pelvis"),nullptr,16); AddSphere(TEXT("spine_02"),nullptr,15); AddSphere(TEXT("spine_04"),nullptr,16);
    AddSphere(TEXT("thigh_l"),TEXT("calf_l"),11); AddSphere(TEXT("thigh_r"),TEXT("calf_r"),11);
    AddSphere(TEXT("calf_l"),TEXT("foot_l"),9); AddSphere(TEXT("calf_r"),TEXT("foot_r"),9);
    const FVector Gravity(0,0,-980*WardenRules::Step*WardenRules::Step);
    // Rolls and death spin the anchor a full turn; hold the cloth close so it wraps
    // the body instead of sheeting out (cf. the Ashbound panels' roll tuck).
    const bool Tumbling=Fight.Action==EWardenAction::Dodge || !Fight.Alive();
    const float TopFollow=Tumbling?.55f:.3f,HemFollow=Tumbling?.3f:.07f;
    for(auto& Chain:SwingChains)
    {
        const int32 N=Chain.Bones.Num();
        if(Chain.Anchor<0 || N<2) continue;
        const FTransform Follow=Rest[Chain.Anchor].Inverse()*CS[Chain.Anchor]*World;
        TArray<FTransform> Rigid; Rigid.SetNum(N);
        for(int32 K=0;K<N;++K) Rigid[K]=Rest[Chain.Bones[K]]*Follow;
        // Reset on first use and after teleports (fighter reset, test pose jumps).
        if(Chain.Pos.Num()!=N || FVector::Dist(Chain.Pos[0],Rigid[0].GetLocation())>60*Scale)
        {
            Chain.Pos.SetNum(N); Chain.Prev.SetNum(N);
            for(int32 K=0;K<N;++K) Chain.Pos[K]=Chain.Prev[K]=Rigid[K].GetLocation();
        }
        // The pin rides the skinned back, which the roll's floor solve does not cover
        // (it sits behind the spine envelope), so keep it on the floor too.
        Chain.Pos[0]=Chain.Prev[0]=Rigid[0].GetLocation();
        Chain.Pos[0].Z=Chain.Prev[0].Z=FMath::Max(float(Chain.Pos[0].Z),Floor);
        for(int32 K=1;K<N;++K)
        {
            const FVector Velocity=(Chain.Pos[K]-Chain.Prev[K])*.85f;
            Chain.Prev[K]=Chain.Pos[K];
            Chain.Pos[K]=FMath::Lerp(Chain.Pos[K]+Velocity+Gravity,Rigid[K].GetLocation(),FMath::Lerp(TopFollow,HemFollow,float(K-1)/FMath::Max(1,N-2)));
        }
        for(int32 Pass=0;Pass<3;++Pass)
            for(int32 K=1;K<N;++K)
            {
                const float Length=FVector::Dist(Rest[Chain.Bones[K]].GetLocation(),Rest[Chain.Bones[K-1]].GetLocation())*Scale;
                FVector& X=Chain.Pos[K];
                const FVector& P=Chain.Pos[K-1];
                for(const FSwingSphere& S:Spheres)
                {
                    // Never push further out than the cloth sat at rest.
                    const float Radius=FMath::Min(S.Radius,.9f*FVector::Dist(S.Rest,Rest[Chain.Bones[K]].GetLocation()))*Scale;
                    const FVector D=X-S.Now;
                    if(D.SizeSquared()<Radius*Radius) X=S.Now+D.GetSafeNormal()*Radius;
                }
                // Bone length is exact; floor contact slides the segment along the floor.
                X=P+(X-P).GetSafeNormal()*Length;
                const float Ground=FMath::Min(Floor,float(P.Z));
                if(X.Z<Ground)
                {
                    FVector Flat=(X-P).GetSafeNormal2D();
                    if(Flat.IsNearlyZero()) Flat=(Rigid[K].GetLocation()-Rigid[K-1].GetLocation()).GetSafeNormal2D();
                    if(Flat.IsNearlyZero()) Flat=GetActorForwardVector()*-1;
                    X=P+Flat*FMath::Sqrt(FMath::Max(0.f,Length*Length-FMath::Square(float(P.Z-Ground))));
                    X.Z=Ground;
                }
            }
        const int32 Root=Ref.GetParentIndex(Chain.Bones[0]);
        FTransform Parent=Root<0?World:CS[Root]*World;
        FQuat Correction=FQuat::Identity;
        for(int32 K=0;K<N;++K)
        {
            if(K+1<N) Correction=FQuat::FindBetweenNormals((Rigid[K+1].GetLocation()-Rigid[K].GetLocation()).GetSafeNormal(),(Chain.Pos[K+1]-Chain.Pos[K]).GetSafeNormal());
            const FTransform Bone(Correction*Rigid[K].GetRotation(),Chain.Pos[K],Rigid[K].GetScale3D());
            FTransform Local=Bone.GetRelativeTransform(Parent); Local.NormalizeRotation();
            if(!Local.ContainsNaN()) VisualBody->BoneSpaceTransforms[Chain.Bones[K]]=Local;
            Parent=Bone;
        }
    }
    VisualBody->RefreshBoneTransforms();
}
