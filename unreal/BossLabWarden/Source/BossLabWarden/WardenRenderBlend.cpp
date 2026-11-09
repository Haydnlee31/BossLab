// Render interpolation (presentation only). The fixed 60 Hz step owns every transform;
// rendered frames rarely line up with it, so a frame could show 0 or 2 steps of motion
// and the body, blade and follow camera juddered. Between steps the visible state is
// blended from the previous to the current step by the leftover accumulator time, and
// the exact step state is restored before the next step, so combat, hit sweeps and the
// frame-partition determinism are unchanged.
#include "WardenPrototype.h"
#include "Components/PoseableMeshComponent.h"
#include "GameFramework/SpringArmComponent.h"

void AWardenChallenger::CaptureStepState()
{
    RestoreStepState();
    RenderPrev=RenderCurr;
    RenderCurr.Location=GetActorLocation(); RenderCurr.Yaw=GetActorRotation().Yaw;
    RenderCurr.Visual=VisualBody->GetRelativeTransform(); RenderCurr.Sword=SwordRoot->GetRelativeTransform();
    RenderCurr.Bones=VisualBody->BoneSpaceTransforms;
    // Never blend across a teleport (reset, ash step) or a skeleton swap.
    if(!bRenderValid || FVector::Dist(RenderPrev.Location,RenderCurr.Location)>150 || RenderPrev.Bones.Num()!=RenderCurr.Bones.Num())
        RenderPrev=RenderCurr;
    bRenderValid=true;
}
void AWardenChallenger::RestoreStepState()
{
    if(!bRenderBlended) return;
    VisualBody->SetRelativeTransform(RenderCurr.Visual); SwordRoot->SetRelativeTransform(RenderCurr.Sword);
    VisualBody->BoneSpaceTransforms=RenderCurr.Bones; VisualBody->RefreshBoneTransforms();
    Arm->SetRelativeLocation(FVector::ZeroVector);
    bRenderBlended=false;
}
void AWardenChallenger::BlendRenderState(float Alpha)
{
    if(!bRenderValid || RenderCurr.Bones.Num()!=VisualBody->BoneSpaceTransforms.Num()) return;
    Alpha=FMath::Clamp(Alpha,0.f,1.f);
    const FTransform Actor=GetActorTransform();
    const FVector Location=FMath::Lerp(RenderPrev.Location,RenderCurr.Location,Alpha);
    const float Yaw=RenderCurr.Yaw+FMath::FindDeltaAngleDegrees(RenderCurr.Yaw,RenderPrev.Yaw)*(1-Alpha);
    const FTransform Shown(FRotator(0,Yaw,0),Location,Actor.GetScale3D());
    FTransform Visual; Visual.Blend(RenderPrev.Visual,RenderCurr.Visual,Alpha);
    // Place the mesh as if the actor stood at the blended transform.
    VisualBody->SetRelativeTransform(Visual*Shown*Actor.Inverse());
    FTransform Sword; Sword.Blend(RenderPrev.Sword,RenderCurr.Sword,Alpha);
    SwordRoot->SetRelativeTransform(Sword);
    TArray<FTransform> Bones; Bones.SetNum(RenderCurr.Bones.Num());
    for(int32 I=0;I<Bones.Num();++I) Bones[I].Blend(RenderPrev.Bones[I],RenderCurr.Bones[I],Alpha);
    VisualBody->BoneSpaceTransforms=MoveTemp(Bones); VisualBody->RefreshBoneTransforms();
    // The follow camera rides the blended position too.
    Arm->SetRelativeLocation(Actor.InverseTransformVector(Location-Actor.GetLocation()));
    bRenderBlended=true;
}
