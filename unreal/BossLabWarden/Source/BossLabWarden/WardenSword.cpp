#include "WardenPrototype.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Animation/BlendSpace.h"
#include "Engine/SkeletalMesh.h"
#include "Materials/MaterialInterface.h"

namespace
{
FVector MeshPoint(FVector V) { return FVector(-V.Y,V.X,V.Z); }
float Smooth(float T) { T=FMath::Clamp(T,0.f,1.f); return T*T*(3-2*T); }
struct FSwordKey { FVector Grip,Axis; float Twist,Lean; };
FSwordKey Blend(const FSwordKey& A,const FSwordKey& B,float T)
{
    T=Smooth(T); return {FMath::Lerp(A.Grip,B.Grip,T),FQuat::Slerp(FQuat::Identity,FQuat::FindBetweenNormals(A.Axis.GetSafeNormal(),B.Axis.GetSafeNormal()),T).RotateVector(A.Axis).GetSafeNormal(),FMath::Lerp(A.Twist,B.Twist,T),FMath::Lerp(A.Lean,B.Lean,T)};
}
}
void AWardenChallenger::CreateSword()
{
    if(FindObject<UStaticMeshComponent>(this,TEXT("SwordBlade"))) return;
    auto Part=[&](const TCHAR* Name,const TCHAR* Mesh,FVector Pos,FVector Scale,const TCHAR* Mat)
    {
        auto* C=NewObject<UStaticMeshComponent>(this,FName(Name));
        C->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,Mesh));
        C->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,*(FString(TEXT("/Game/BossLab/Materials/MI_"))+Mat)));
        C->SetupAttachment(SwordRoot); C->SetRelativeLocation(Pos); C->SetRelativeScale3D(Scale);
        C->SetCollisionEnabled(ECollisionEnabled::NoCollision); C->SetVisibility(bBoss); C->RegisterComponent(); AddInstanceComponent(C);
    };
    Part(TEXT("SwordBlade"),TEXT("/Engine/BasicShapes/Cube"),FVector(0,0,70),FVector(.105,.025,1.22),TEXT("Iron"));
    Part(TEXT("SwordRidge"),TEXT("/Engine/BasicShapes/Cube"),FVector(0,0,70),FVector(.028,.04,1.2),TEXT("Bronze"));
    Part(TEXT("SwordTip"),TEXT("/Engine/BasicShapes/Cone"),FVector(0,0,139),FVector(.105,.025,.18),TEXT("Iron"));
    Part(TEXT("SwordGuard"),TEXT("/Engine/BasicShapes/Cube"),FVector(0,0,8),FVector(.34,.06,.055),TEXT("Bronze"));
    Part(TEXT("SwordGrip"),TEXT("/Engine/BasicShapes/Cylinder"),FVector(0,0,-9),FVector(.045,.045,.32),TEXT("BlackIron"));
    Part(TEXT("SwordPommel"),TEXT("/Engine/BasicShapes/Sphere"),FVector(0,0,-27),FVector(.075,.075,.09),TEXT("Bronze"));
}
FVector AWardenChallenger::BladePoint(float Along) const
{
    return SwordRoot->GetComponentTransform().TransformPosition(FVector(0,0,FMath::Lerp(14.f,148.f,Along)));
}
void AWardenChallenger::SwordPose(const FVector& Travel)
{
    if(GuardBase.IsEmpty() || !VisualBody->GetSkinnedAsset()) return;
    const auto& Ref=VisualBody->GetSkinnedAsset()->GetRefSkeleton();
    TArray<FTransform> Local=GuardBase;
    const float Speed=Travel.Size2D()*60.f;
    // Only locomotion evaluates the installed blendspace. All sword/roll motion below
    // is an original keyed pose with IK; it is not a relabeled punch or dash.
    if(Fight.Action==EWardenAction::Ready && Locomotion)
    {
        if(Body->GetSingleNodeInstance()->GetCurrentAsset()!=Locomotion) Body->PlayAnimation(Locomotion,true);
        auto* Anim=Body->GetSingleNodeInstance();
        const float Angle=FMath::RadiansToDegrees(FMath::Atan2(FVector::DotProduct(Travel,GetActorRightVector()),FVector::DotProduct(Travel,GetActorForwardVector())));
        Anim->SetBlendSpacePosition(FVector(Angle,Speed,0));
        // Blendspace sample weights and marker clocks require a real delta.
        // SetPosition + TickAnimation(0) left the sample cache at idle even while
        // the capsule travelled: measured foot excursion was only 0.052 cm.
        Anim->SetPlayRate(1.f);
        Body->TickAnimation(WardenRules::Step,false); Body->RefreshBoneTransforms(); Local=Body->GetBoneSpaceTransforms();
    }
    // Blend only the unmodified animation base: never feed procedural IK back
    // into itself. This removes the walk/stop/commit snap while keeping contact
    // poses authoritative on the fixed simulation step.
    if(MotionBase.Num()==Local.Num())
        for(int32 I=0;I<Local.Num();++I)
        {
            FTransform Blended; Blended.Blend(MotionBase[I],Local[I],.28f); Local[I]=Blended;
        }
    MotionBase=Local;
    Local[0].SetTranslation(FVector::ZeroVector);
    TArray<FTransform> CS; CS.SetNum(Local.Num());
    auto Rebuild=[&](int32 Start=0) { for(int32 I=Start;I<Local.Num();++I) { const int32 Parent=Ref.GetParentIndex(I); CS[I]=Parent<0?Local[I]:Local[I]*CS[Parent]; } };
    auto Index=[&](const TCHAR* Name) { return Ref.FindBoneIndex(FName(Name)); };
    auto SetRotation=[&](int32 I,FQuat Rotation)
    {
        if(I<0) return; const int32 Parent=Ref.GetParentIndex(I);
        Local[I].SetRotation(Parent<0?Rotation:CS[Parent].GetRotation().Inverse()*Rotation);
        Local[I].NormalizeRotation(); Rebuild(I);
    };
    Rebuild();
    const int32 FootLI=Index(TEXT("foot_l")),FootRI=Index(TEXT("foot_r"));
    const FTransform FootL=CS[FootLI],FootR=CS[FootRI];
    float Plant=0,Recover=0,Load=0,Drive=0,Settle=0;
    FSwordKey Guard{FVector(28,5,114),FVector(.38,-.12,.92).GetSafeNormal(),-7,5};
    FSwordKey Key=Guard;
    float Roll=0, Tuck=0,Landing=0;
    if(Fight.Action==EWardenAction::Strike)
    {
        const auto& D=Fight.Definition();
        Plant=Smooth(float(Fight.Age)/FMath::Max(1,D.Windup-8));
        Recover=Smooth(float(Fight.Age-D.Windup-D.Active)/D.Recovery);
        // Hips load before the blade releases, then lead the chest through contact.
        // These envelopes do not change the engine-owned contact/timing windows.
        Load=Smooth(float(Fight.Age)/FMath::Max(1,D.Windup-10));
        Drive=Smooth(float(Fight.Age-D.Windup+5)/FMath::Max(1,D.Active+5));
        Settle=Smooth(float(Fight.Age-D.Windup-D.Active-5)/FMath::Max(1,D.Recovery-5));
        FSwordKey Wind{FVector(-5,28,148),FVector(-.75,.5,.42).GetSafeNormal(),-52,-10};
        FSwordKey Release{FVector(43,8,123),FVector(.95,.25,.1).GetSafeNormal(),-5,10};
        FSwordKey Follow{FVector(16,-24,118),FVector(.05,-.98,-.12).GetSafeNormal(),58,20};
        if(bBoss && Fight.Move==1)
        {
            Wind={FVector(12,3,178),FVector(-.52,0,.85).GetSafeNormal(),0,-12};
            Release={FVector(45,0,125),FVector(.95,0,.3).GetSafeNormal(),0,16};
            Follow={FVector(32,0,92),FVector(.8,0,-.6).GetSafeNormal(),0,26};
        }
        else if(bBoss && Fight.Move==2)
        {
            Wind={FVector(14,-29,92),FVector(-.25,-.9,-.25).GetSafeNormal(),40,12};
            Release={FVector(43,-3,120),FVector(1,0,.1).GetSafeNormal(),0,7};
            Follow={FVector(12,24,160),FVector(.2,.6,.77).GetSafeNormal(),-45,-6};
        }
        if(Fight.Age<D.Windup) Key=Blend(Guard,Wind,float(Fight.Age)/FMath::Max(1,D.Windup-6));
        else if(Fight.Age<D.Windup+D.Active)
        {
            // One quadratic arc with a single acceleration/deceleration envelope.
            // The old two Smooth() segments halted at Release halfway through
            // contact, making the heavy blade look mechanically repositioned.
            const float U=Smooth(float(Fight.Age-D.Windup)/D.Active), V=1-U;
            auto Arc=[&](FVector A,FVector Mid,FVector B)
            { return A*(V*V)+(2*Mid-(A+B)*.5f)*(2*V*U)+B*(U*U); };
            Key.Grip=Arc(Wind.Grip,Release.Grip,Follow.Grip);
            Key.Axis=Arc(Wind.Axis,Release.Axis,Follow.Axis).GetSafeNormal();
            // Chest finishes after the hips; the head counterbalances below.
            const float Chest=Smooth(float(Fight.Age-D.Windup)/D.Active);
            Key.Twist=FMath::Lerp(Wind.Twist,Follow.Twist,Chest);
            Key.Lean=FMath::Lerp(Wind.Lean,Follow.Lean,Chest);
        }
        else
        {
            // Briefly carry the finished cut before returning to the guard.
            const FSwordKey Carry{Follow.Grip+FVector(-3,0,-4),Follow.Axis,Follow.Twist*.9f,Follow.Lean*.8f};
            const float R=float(Fight.Age-D.Windup-D.Active)/D.Recovery;
            Key=R<.22f?Blend(Follow,Carry,R/.22f):Blend(Carry,Guard,(R-.22f)/.78f);
        }
    }
    else if(Fight.Action==EWardenAction::Dodge)
    {
        const float U=float(Fight.Age)/WardenRules::DodgeTicks;
        Tuck=Smooth(U/.18f)*(1-Smooth((U-.48f)/.46f));
        Roll=360*Smooth((U-.12f)/.62f);
        Landing=Smooth((U-.68f)/.09f)*(1-Smooth((U-.77f)/.20f));
        // Keep the facing continuous. Roll around the axis perpendicular to the
        // committed travel, so backwards rolls do not need a 180-degree yaw whip.
        const FVector LocalDirection=GetActorQuat().UnrotateVector(CommittedDirection);
        const FVector CarryAxis(-LocalDirection.Y,LocalDirection.X,0);
        const float HandTuck=Smooth(U/.14f)*(1-Smooth((U-.78f)/.19f));
        Key=Blend(Guard,{FVector(26,-4,97),CarryAxis,0,68},HandTuck);
        Key.Lean+=6*Landing;
    }
    else if(Fight.Action==EWardenAction::Heal)
        Key=Blend(Guard,{FVector(20,8,105),FVector(.6,.2,.77).GetSafeNormal(),0,8},FMath::Sin(PI*float(Fight.Age)/WardenRules::HealTicks));
    const float Recoil=Fight.ImpactTicks>0 ? FMath::Sin(PI*float(18-Fight.ImpactTicks)/18) : 0;
    // Armored hits still read through the torso, but never alter the sword's
    // active arc. Poise breaks and player flinches get a complete hurt pose.
    if(Fight.Action==EWardenAction::Hurt)
    {
        const float U=float(Fight.Age)/(bBoss?WardenRules::BossHurtTicks:WardenRules::HurtTicks);
        const float Weight=Smooth(U/.17f)*(1-Smooth((U-.32f)/.68f));
        Key=Blend(Guard,{FVector(12,15,100),FVector(.45,.65,.6).GetSafeNormal(),-22,-27},Weight);
    }
    else if(!Fight.Active()) Key.Lean-=Recoil*9;
    if(Fight.Action==EWardenAction::Dead)
    {
        const float U=Smooth(DeathAge/60.f);
        Key=Blend(Guard,{FVector(30,-10,68),FVector(.4,.9,.1).GetSafeNormal(),12,35},U);
        Tuck=U*.7f;
    }
    const int32 Pelvis=Index(TEXT("pelvis"));
    if(Pelvis>=0)
    {
        const float Weight=1-Settle;
        const FVector Shift=Fight.Action==EWardenAction::Strike
            ? FVector(FMath::Lerp(-7.f,9.f,Drive)*Load*Weight,FMath::Lerp(4.f,-3.f,Drive)*Load*Weight,-9*Load*Weight)
            : FVector(-3*Recoil,0,-32*Tuck-6*Landing);
        Local[Pelvis].AddToTranslation(MeshPoint(Shift)); Rebuild(Pelvis);
        const float HipTurn=Fight.Action==EWardenAction::Strike ? FMath::Lerp(-22.f,26.f,Drive)*Load*Weight : Key.Twist*.2f;
        SetRotation(Pelvis,FQuat(FVector::UpVector,FMath::DegreesToRadians(-HipTurn))*CS[Pelvis].GetRotation());
    }
    // Distribute anticipation and follow-through across pelvis/spine, not just wrists.
    for(const TCHAR* Name:{TEXT("spine_01"),TEXT("spine_02"),TEXT("spine_03"),TEXT("spine_04"),TEXT("spine_05")})
    {
        const int32 I=Index(Name); if(I<0) continue;
        const FQuat Delta=FQuat(FVector::UpVector,FMath::DegreesToRadians(-Key.Twist*.8f/5))*FQuat(FVector::ForwardVector,FMath::DegreesToRadians(-Key.Lean/5));
        SetRotation(I,Delta*CS[I].GetRotation());
    }
    // Counterbalance the gaze instead of welding the head to the chest.
    for(const TCHAR* Name:{TEXT("neck_01"),TEXT("neck_02"),TEXT("head")})
    {
        const int32 I=Index(Name); if(I<0) continue;
        SetRotation(I,FQuat(FVector::UpVector,FMath::DegreesToRadians(Key.Twist*.18f))*
            FQuat(FVector::ForwardVector,FMath::DegreesToRadians(Key.Lean*.13f))*CS[I].GetRotation());
    }
    // Shoulder girdle opens under the backswing and reaches across on release.
    // The shared hilt IK below remains responsible for exact palm placement.
    for(int32 Side=0;Side<2;++Side)
    {
        const int32 I=Index(Side?TEXT("clavicle_l"):TEXT("clavicle_r")); if(I<0) continue;
        const float Sign=Side?-1.f:1.f;
        const float Reach=FMath::Clamp((Key.Grip.X-26)*.22f,-6.f,7.f);
        const float Lift=FMath::Clamp((Key.Grip.Z-114)*.18f,-4.f,10.f);
        SetRotation(I,FQuat(FVector::UpVector,FMath::DegreesToRadians(-Key.Twist*.10f+Sign*Reach))*
            FQuat(FVector::RightVector,FMath::DegreesToRadians(Sign*Lift))*CS[I].GetRotation());
    }
    auto IK=[&](const TCHAR* Upper,const TCHAR* Lower,const TCHAR* End,FVector Target,FVector Pole)
    {
        const int32 A=Index(Upper),B=Index(Lower),C=Index(End); if(A<0||B<0||C<0) return;
        const FVector Root=CS[A].GetLocation();
        const float L1=FVector::Distance(Root,CS[B].GetLocation()),L2=FVector::Distance(CS[B].GetLocation(),CS[C].GetLocation());
        const FVector Aim=(Target-Root).GetSafeNormal();
        const float D=FMath::Clamp(FVector::Distance(Root,Target),FMath::Abs(L1-L2)+.1f,L1+L2-.1f);
        const float X=(L1*L1-L2*L2+D*D)/(2*D),H=FMath::Sqrt(FMath::Max(0.f,L1*L1-X*X));
        FVector Side=FVector::VectorPlaneProject(Pole-Root,Aim).GetSafeNormal(); if(Side.IsNearlyZero()) Side=FVector::RightVector;
        const FVector Elbow=Root+Aim*X+Side*H;
        SetRotation(A,FQuat::FindBetweenNormals((CS[B].GetLocation()-Root).GetSafeNormal(),(Elbow-Root).GetSafeNormal())*CS[A].GetRotation());
        SetRotation(B,FQuat::FindBetweenNormals((CS[C].GetLocation()-CS[B].GetLocation()).GetSafeNormal(),(Root+Aim*D-CS[B].GetLocation()).GetSafeNormal())*CS[B].GetRotation());
    };
    if(Fight.Action==EWardenAction::Strike)
    {
        // The support foot stays in world space through the cut. During recovery
        // each foot lifts before repositioning instead of sliding flat on the floor.
        const float LeadReturn=Smooth((Recover-.4f)/.6f),RearReturn=Smooth(Recover/.7f);
        const FTransform MeshWorld=VisualBody->GetComponentTransform();
        const float Scale=GetActorScale3D().X;
        FVector LeadStart=StrikeFootAnchors[0]+(CommittedDirection*36-GetActorRightVector()*3)*Plant*Scale;
        LeadStart.Z=FMath::Lerp(StrikeFootAnchors[0].Z,MeshWorld.TransformPosition(FootL.GetLocation()).Z,Plant);
        FVector RearStart=StrikeFootAnchors[1];
        RearStart.Z=FMath::Lerp(RearStart.Z,MeshWorld.TransformPosition(FootR.GetLocation()).Z,Smooth(float(Fight.Age)/12));
        const FVector LeadWorld=FMath::Lerp(LeadStart,MeshWorld.TransformPosition(FootL.GetLocation()),LeadReturn)
            +FVector::UpVector*(7*FMath::Sin(PI*Plant)+7*FMath::Sin(PI*LeadReturn))*Scale;
        const FVector RearWorld=FMath::Lerp(RearStart,MeshWorld.TransformPosition(FootR.GetLocation()),RearReturn)
            +FVector::UpVector*9*FMath::Sin(PI*RearReturn)*Scale;
        const FVector Lead=MeshWorld.InverseTransformPosition(LeadWorld),Rear=MeshWorld.InverseTransformPosition(RearWorld);
        // A wide stance inherited from walking can exceed leg reach even though
        // the foot targets are grounded. Lower the pelvis enough to keep contact
        // instead of letting the two-bone solver pull the boot up off the floor.
        float SupportDrop=0;
        for(int32 Side=0;Side<2;++Side)
        {
            const int32 A=Index(Side?TEXT("thigh_r"):TEXT("thigh_l"));
            const int32 B=Index(Side?TEXT("calf_r"):TEXT("calf_l"));
            const int32 C=Side?FootRI:FootLI;
            const FVector FootTarget=Side?Rear:Lead, Root=CS[A].GetLocation();
            const float Reach=FVector::Distance(Root,CS[B].GetLocation())+FVector::Distance(CS[B].GetLocation(),CS[C].GetLocation())-.5f;
            const float Horizontal=FVector::DistSquared2D(Root,FootTarget);
            SupportDrop=FMath::Max(SupportDrop,float(Root.Z-FootTarget.Z-FMath::Sqrt(FMath::Max(0.f,Reach*Reach-Horizontal))));
        }
        if(Pelvis>=0 && SupportDrop>0) { Local[Pelvis].AddToTranslation(FVector(0,0,-FMath::Min(SupportDrop,25.f))); Rebuild(Pelvis); }
        IK(TEXT("thigh_l"),TEXT("calf_l"),TEXT("foot_l"),Lead,MeshPoint(FVector(65,-20,55)));
        IK(TEXT("thigh_r"),TEXT("calf_r"),TEXT("foot_r"),Rear,MeshPoint(FVector(65,20,55)));
        SetRotation(FootLI,FootL.GetRotation()); SetRotation(FootRI,FootR.GetRotation());
    }
    if(Fight.Action==EWardenAction::Dodge)
    {
        const FVector Left=FMath::Lerp(FootL.GetLocation(),MeshPoint(FVector(22,-15,64)),Tuck);
        const FVector Right=FMath::Lerp(FootR.GetLocation(),MeshPoint(FVector(4,15,57)),Tuck);
        IK(TEXT("thigh_l"),TEXT("calf_l"),TEXT("foot_l"),Left,MeshPoint(FVector(75,-20,55)));
        IK(TEXT("thigh_r"),TEXT("calf_r"),TEXT("foot_r"),Right,MeshPoint(FVector(75,20,55)));
        SetRotation(FootLI,FootL.GetRotation()); SetRotation(FootRI,FootR.GetRotation());
    }
    const FVector Axis=MeshPoint(Key.Axis).GetSafeNormal();
    SwordFrame=FTransform(FQuat::FindBetweenNormals(FVector::UpVector,Axis),MeshPoint(Key.Grip));
    const FVector Across=SwordFrame.GetRotation().GetAxisX();
    // Project the shared hilt into the intersection of both arms' reachable
    // spheres. The weapon and both hands share this corrected transform; no
    // stretched arm bones or independent floating off-hand.
    FVector SharedGrip=SwordFrame.GetLocation();
    for(int32 Iteration=0;Iteration<12;++Iteration)
        for(int32 Side=0;Side<2;++Side)
        {
            const bool Right=Side==0;
            const int32 U=Index(Right?TEXT("upperarm_r"):TEXT("upperarm_l"));
            const int32 L=Index(Right?TEXT("lowerarm_r"):TEXT("lowerarm_l"));
            const int32 H=Index(Right?TEXT("hand_r"):TEXT("hand_l"));
            if(U<0||L<0||H<0) continue;
            const float Reach=FVector::Distance(CS[U].GetLocation(),CS[L].GetLocation())+FVector::Distance(CS[L].GetLocation(),CS[H].GetLocation())-.25f;
            const FVector Center=CS[U].GetLocation()+(Right?Across*7:Axis*17-Across*7);
            SharedGrip=Center+(SharedGrip-Center).GetClampedToMaxSize(Reach);
        }
    SwordFrame.SetTranslation(SharedGrip);
    GripError=0;
    for(int32 Side=0;Side<2;++Side)
    {
        const bool Right=Side==0;
        const FVector Grip=SwordFrame.TransformPosition(FVector(0,0,Right?0:-17));
        const FVector Finger=Across*(Right?1.f:-1.f);
        const FVector Wrist=Grip-Finger*7;
        IK(Right?TEXT("upperarm_r"):TEXT("upperarm_l"),Right?TEXT("lowerarm_r"):TEXT("lowerarm_l"),Right?TEXT("hand_r"):TEXT("hand_l"),Wrist,MeshPoint(FVector(-10+Key.Grip.X*.25f,(Right?1.f:-1.f)*(45+FMath::Abs(Key.Twist)*.22f),100+(Key.Grip.Z-114)*.45f)));
        const int32 Hand=Index(Right?TEXT("hand_r"):TEXT("hand_l")),Middle=Index(Right?TEXT("middle_01_r"):TEXT("middle_01_l"));
        if(Hand>=0 && Middle>=0)
        {
            SetRotation(Hand,FQuat::FindBetweenNormals((CS[Middle].GetLocation()-CS[Hand].GetLocation()).GetSafeNormal(),Finger)*CS[Hand].GetRotation());
            GripError=FMath::Max(GripError,FVector::Distance(CS[Hand].GetLocation()+Finger*7,Grip));
        }
    }
    VisualBody->BoneSpaceTransforms=Local;
    VisualBody->RefreshBoneTransforms();
    FQuat Rotation=FRotator(0,-90,0).Quaternion(); FVector Origin(0,0,-95);
    if(Fight.Action==EWardenAction::Dodge || Fight.Action==EWardenAction::Dead)
    {
        const FVector LocalDirection=GetActorQuat().UnrotateVector(CommittedDirection);
        const float U=float(Fight.Age)/WardenRules::DodgeTicks;
        const bool Dead=Fight.Action==EWardenAction::Dead;
        const FVector RollAxis=Dead?FVector::RightVector:FVector(-LocalDirection.Y,LocalDirection.X,0).GetSafeNormal();
        const FQuat DirectionalRoll=FQuat(RollAxis,FMath::DegreesToRadians(Dead?85*Smooth(DeathAge/60.f):Roll));
        Rotation=DirectionalRoll*Rotation;
        Origin=FVector(0,0,-25)-DirectionalRoll.RotateVector(FVector(0,0,70));
        // Ground the supporting body envelope, not just a helmet clearance clamp.
        // Blend support into the crouch and out through planted landing. No capsule
        // or iframe changes: this is the flat arena's presentation contact solve.
        float Floor=10000;
        for(const TCHAR* Name:{TEXT("head"),TEXT("spine_03"),TEXT("pelvis"),TEXT("calf_l"),TEXT("calf_r"),TEXT("foot_l"),TEXT("foot_r")})
        {
            const int32 I=Index(Name); if(I<0) continue;
            const float Radius=FCString::Strcmp(Name,TEXT("head"))==0?20.f:FCString::Strncmp(Name,TEXT("foot"),4)==0?3.f:10.f;
            Floor=FMath::Min(Floor,float((Origin+Rotation.RotateVector(CS[I].GetLocation())).Z+95-Radius));
        }
        const float Contact=Dead?Smooth(DeathAge/12.f):Smooth(U/.12f)*(1-Smooth((U-.80f)/.17f));
        Origin.Z-=Floor*Contact;
    }
    VisualBody->SetRelativeLocationAndRotation(Origin,Rotation);
    SwordRoot->SetRelativeTransform(SwordFrame);
    VisualBody->UpdateComponentToWorld(); SwordRoot->UpdateComponentToWorld();
    UpdateAshbound(Travel);
}
