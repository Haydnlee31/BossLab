// Render interpolation (presentation only). The fixed 60 Hz step owns every transform;
// rendered frames rarely line up with it, so a frame could show 0 or 2 steps of motion
// and the body, blade and follow camera juddered. Between steps the visible state is
// blended from the previous to the current step by the leftover accumulator time, and
// the exact step state is restored before the next step, so combat, hit sweeps and the
// frame-partition determinism are unchanged.
#include "WardenPrototype.h"
#include "Components/PoseableMeshComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Camera/CameraActor.h"

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

void AWardenArenaMode::GaitStudyStep(FVector& PlayerIntent,FVector& BossDirection)
{
    // Capture-only locomotion review, side-on: 0-4 s boss walks in, 4-7 s backpedals,
    // 7-11 s circles; 11-15 s player walks in and strafes locked on while the boss turns
    // on the spot; 15-19 s player backs off; then both stand. Ticks offset by the 2 s
    // capture warm-up. No attacks or damage.
    const int32 T=CombatTick-120;
    const FVector ToPlayer=(Player->GetActorLocation()-Warden->GetActorLocation()).GetSafeNormal2D();
    const FVector Around(-ToPlayer.Y,ToPlayer.X,0);
    PlayerIntent=FVector::ZeroVector; BossDirection=FVector::ZeroVector;
    const float Distance=FVector::Dist2D(Player->GetActorLocation(),Warden->GetActorLocation());
    if(T<240) BossDirection=Distance>260 ? ToPlayer : FVector::ZeroVector;
    else if(T<420) BossDirection=-ToPlayer;
    else if(T<660) BossDirection=Around;
    else if(T<900)
    {
        Player->SetLocked(true);
        PlayerIntent=T<760 ? (Distance>300 ? -ToPlayer : FVector::ZeroVector) : FVector(ToPlayer.Y,-ToPlayer.X,0);
    }
    else if(T<1140) PlayerIntent=ToPlayer*.8f;
    else Player->SetLocked(false);
    // Camera stays side-on to the line between the fighters, framing both at mid range.
    if(RegentStudyCamera.IsValid())
    {
        const FVector Mid=(Player->GetActorLocation()+Warden->GetActorLocation())*.5f;
        const FVector Eye=FVector(Mid.X,Mid.Y,0)+Around*(320+Distance*.55f)+FVector(0,0,190);
        const FVector Look=FVector(Mid.X,Mid.Y,105);
        const FRotator Want=(Look-Eye).Rotation();
        RegentStudyCamera->SetActorLocationAndRotation(FMath::VInterpTo(RegentStudyCamera->GetActorLocation(),Eye,WardenRules::Step,3.f),
            FMath::RInterpTo(RegentStudyCamera->GetActorRotation(),Want,WardenRules::Step,4.f));
    }
}
