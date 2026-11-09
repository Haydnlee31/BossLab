#include "WardenPrototype.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Animation/BlendSpace.h"
#include "Engine/SkeletalMesh.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"

namespace
{
FVector MeshPoint(FVector V) { return FVector(-V.Y,V.X,V.Z); }
float Smooth(float T) { T=FMath::Clamp(T,0.f,1.f); return T*T*(3-2*T); }
struct FSwordKey { FVector Grip,Axis; float Twist,Lean; };
FSwordKey Blend(const FSwordKey& A,const FSwordKey& B,float T)
{
    T=Smooth(T); return {FMath::Lerp(A.Grip,B.Grip,T),FQuat::Slerp(FQuat::Identity,FQuat::FindBetweenNormals(A.Axis.GetSafeNormal(),B.Axis.GetSafeNormal()),T).RotateVector(A.Axis).GetSafeNormal(),FMath::Lerp(A.Twist,B.Twist,T),FMath::Lerp(A.Lean,B.Lean,T)};
}
// Funeral Regent: one-handed estoc in the right hand. Blade moves thrust from a high
// en-garde; censer and cast moves carry the estoc low while the body and left arm work.
// Greybox keys on the engine-owned phases; they never change contact timing.
FSwordKey RegentGuard() { return {FVector(30,22,112),FVector(.9f,-.15f,.4f).GetSafeNormal(),-10,2}; }
FSwordKey RegentKey(const FWardenFighterState& F)
{
    using namespace WardenRegent;
    const FSwordKey Guard=RegentGuard();
    const FSwordKey Wind{FVector(2,26,130),FVector(.97f,-.05f,.2f).GetSafeNormal(),-28,-6};
    const FSwordKey Lunge{FVector(60,8,124),FVector(1,-.05f,.02f).GetSafeNormal(),18,14};
    const FSwordKey Low{FVector(16,30,92),FVector(.45f,.2f,-.87f).GetSafeNormal(),0,0};
    const auto& D=F.Definition();
    const int32 A=F.Age, R=A-D.Windup;
    const float In=Smooth(float(A)/FMath::Max(1,D.Windup)), Hit=Smooth(float(R+2)/FMath::Max(2,D.Active)), Out=Smooth(float(R-D.Active)/D.Recovery);
    auto Phased=[&](const FSwordKey& Base,float WindLean,float WindTwist,float HitLean,float HitTwist)
    {
        FSwordKey K=Blend(Guard,Blend(Base,Guard,Out),float(A)/12);
        K.Lean=FMath::Lerp(FMath::Lerp(0.f,WindLean,In),HitLean,Hit)*(1-Out);
        K.Twist=FMath::Lerp(FMath::Lerp(0.f,WindTwist,In),HitTwist,Hit)*(1-Out);
        return K;
    };
    switch(Kind(F.Move))
    {
    case EKind::Blade: case EKind::Vanish:
    {
        if(A<D.Windup)
        {
            const int32 From=F.Move==AshStep ? AshAppear : 0;
            // Held Thrust winds as fast as the plain thrust, then holds coiled and drawn back.
            const int32 Wound=F.Move==HeldThrust ? 30 : D.Windup-6;
            FSwordKey K=Blend(Guard,Wind,float(A-From)/FMath::Max(1,Wound-From));
            if(F.Move==Dash) K.Lean+=18*In;   // crouched before the procession dash
            if(F.Move==HeldThrust && A>30)
            {
                const float Coil=Smooth((A-30)/16.f);
                K.Grip+=FVector(-8,4,4)*Coil; K.Twist-=10*Coil; K.Lean-=5*Coil;
            }
            return K;
        }
        if(F.Move==Rite)
        {
            // Extend over four ticks into each contact window, hold, retract over eight.
            float E=0;
            for(const int32 S:{0,20,56}) E=FMath::Max(E,Smooth(float(R-S+4)/4)*(1-Smooth(float(R-S-(S==56?10:8))/8)));
            return Blend(Wind,Lunge,E);
        }
        if(R<D.Active) { FSwordKey K=Blend(Wind,Lunge,float(R+3)/4); if(F.Move==Dash) K.Lean+=20; return K; }
        const float U=float(R-D.Active)/D.Recovery;
        return U<.25f ? Lunge : Blend(Lunge,Guard,(U-.25f)/.75f);
    }
    case EKind::Censer: return F.Move==Arc ? Phased(Low,-4,35,6,-40) : Phased(Low,-14,8,24,0);
    case EKind::Cast: return F.Move==Volley || F.Move==Circle ? Phased(Low,-9,10,4,0) : Phased(Low,-6,0,18,0);
    case EKind::Move: return Phased(Guard,-8,0,-8,0);
    case EKind::Ring:
    {
        const FSwordKey Raised{FVector(10,18,170),FVector(.1f,0,1).GetSafeNormal(),0,-16};
        const FSwordKey Slam{FVector(26,14,86),FVector(.25f,0,-1).GetSafeNormal(),0,26};
        if(A<D.Windup) return Blend(Guard,Raised,float(A)/(D.Windup*.6f));
        if(R<D.Active) return Blend(Raised,Slam,float(R+1)/3);
        return Blend(Slam,Guard,float(R-D.Active)/D.Recovery);
    }
    default: return Phased({FVector(8,40,118),FVector(.2f,.7f,.68f).GetSafeNormal(),0,0},-20,0,-10,0);
    }
}
// Left hand of the Regent in the same key space, for moves that cast with it. Other moves
// aim the arm at the censer instead (see SwordPose).
bool RegentLeftKey(const FWardenFighterState& F,FVector& Out)
{
    using namespace WardenRegent;
    if(F.Action!=EWardenAction::Strike || !IsRegent(F.Move)) return false;
    const auto& D=F.Definition();
    const float In=Smooth(float(F.Age)/FMath::Max(1,D.Windup)), Hit=Smooth(float(F.Age-D.Windup+2)/FMath::Max(2,D.Active)), Back=Smooth(float(F.Age-D.Windup-D.Active)/D.Recovery);
    const FVector Low(14,-34,96);
    auto Path=[&](FVector Wind,FVector Release) { return FMath::Lerp(FMath::Lerp(FMath::Lerp(Low,Wind,In),Release,Hit),Low,Back); };
    switch(F.Move)
    {
        case Volley: case Circle: Out=Path(FVector(34,-28,178),FVector(52,-20,162)); return true;
        case Furrow: Out=Path(FVector(0,-40,170),FVector(58,-18,70)); return true;
        case Pyre: Out=Path(FVector(8,-34,200),FVector(30,-20,80)); return true;
        case Wakes: Out=Path(FVector(4,-62,165),FVector(4,-66,175)); return true;
        default: return false;
    }
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
        C->SetCollisionEnabled(ECollisionEnabled::NoCollision); C->SetVisibility(bBoss || bRevampOutfit); C->RegisterComponent(); AddInstanceComponent(C);
    };
    Part(TEXT("SwordBlade"),TEXT("/Engine/BasicShapes/Cube"),FVector(0,0,70),FVector(.105,.025,1.22),TEXT("Iron"));
    Part(TEXT("SwordRidge"),TEXT("/Engine/BasicShapes/Cube"),FVector(0,0,70),FVector(.028,.04,1.2),TEXT("Bronze"));
    Part(TEXT("SwordTip"),TEXT("/Engine/BasicShapes/Cone"),FVector(0,0,139),FVector(.105,.025,.18),TEXT("Iron"));
    Part(TEXT("SwordGuard"),TEXT("/Engine/BasicShapes/Cube"),FVector(0,0,8),FVector(.34,.06,.055),TEXT("Bronze"));
    Part(TEXT("SwordGrip"),TEXT("/Engine/BasicShapes/Cylinder"),FVector(0,0,-9),FVector(.045,.045,.32),TEXT("BlackIron"));
    Part(TEXT("SwordPommel"),TEXT("/Engine/BasicShapes/Sphere"),FVector(0,0,-27),FVector(.075,.075,.09),TEXT("Bronze"));
}
void AWardenChallenger::DressGreatsword()
{
    // The modelled enchanted greatsword (prep_greatsword.py / ue_import_greatsword.py) in
    // the sword root's frame: grip at the origin, point at the existing 148 cm reach, so
    // contact sweeps are unchanged. Falls back to the primitive blade when absent.
    auto* Mesh=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/BossLab/Sword/SM_Greatsword"),nullptr,LOAD_Quiet|LOAD_NoWarn);
    if(!Mesh) return;
    for(const TCHAR* Name:{TEXT("SwordBlade"),TEXT("SwordRidge"),TEXT("SwordTip"),TEXT("SwordGuard"),TEXT("SwordGrip"),TEXT("SwordPommel")})
        if(auto* C=FindObject<UStaticMeshComponent>(this,Name)) C->SetVisibility(false);
    UStaticMeshComponent* Blade=FindObject<UStaticMeshComponent>(this,TEXT("PlayerGreatsword"));
    if(!Blade)
    {
        Blade=NewObject<UStaticMeshComponent>(this,TEXT("PlayerGreatsword"));
        Blade->SetStaticMesh(Mesh); Blade->SetupAttachment(SwordRoot);
        Blade->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Blade->RegisterComponent(); AddInstanceComponent(Blade);
        const int32 Slot=Blade->GetMaterialIndex(TEXT("sword_rune"));
        if(Slot!=INDEX_NONE) SwordRunes=Blade->CreateDynamicMaterialInstance(Slot);
    }
    Greatsword=Blade;
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
    // The blendspace's speed axis is in the unscaled mannequin's cm/s; the boss is drawn
    // at 1.35x, so the same ground speed needs a proportionally slower gait.
    const float StepSpeed=Travel.Size2D()*60.f/FMath::Max(.1f,float(GetActorScale3D().X));
    // Only locomotion evaluates the installed blendspace. All sword/roll motion below
    // is an original keyed pose with IK; it is not a relabeled punch or dash.
    const bool DrinkWalk=!bBoss && Fight.Action==EWardenAction::Heal;
    if((Fight.Action==EWardenAction::Ready || DrinkWalk) && Locomotion)
    {
        if(Body->GetSingleNodeInstance()->GetCurrentAsset()!=Locomotion) Body->PlayAnimation(Locomotion,true);
        auto* Anim=Body->GetSingleNodeInstance();
        float Angle=FMath::RadiansToDegrees(FMath::Atan2(FVector::DotProduct(Travel,GetActorRightVector()),FVector::DotProduct(Travel,GetActorForwardVector())));
        // Turning on the spot steps the feet round (side-step clips) instead of spinning
        // the idle pose like a turntable. Travel still wins when the body is moving.
        float Speed=StepSpeed;
        // Feet ~15 cm from the turning axis travel about 0.26 cm/s per deg/s; 0.5 gives a
        // visible shuffle without a full walking stride.
        const float Turn=FMath::Min(FMath::Abs(TurnRate)*.5f,150.f);
        if(Turn>20 && Turn>Speed) { Speed=Turn; Angle=TurnRate>0 ? 90.f : -90.f; }
        // Speed warping: below the walk samples (300) keep the full walk stride and slow
        // its clock, instead of mixing in idle (a short shuffling stride at full cadence).
        // The last 60 cm/s still fade into idle at a fixed slow clock, so stops settle.
        const float Side=FMath::Abs(Angle)<=90 ? FMath::Abs(Angle)/90 : 0, Back=FMath::Abs(Angle)>90 ? (FMath::Abs(Angle)-90)/90 : 0;
        const float Trim=FMath::Abs(Angle)<=90 ? FMath::Lerp(GaitTrim[0],GaitTrim[1],Side) : FMath::Lerp(GaitTrim[1],GaitTrim[2],Back);
        float Param=Speed, Rate=GaitRate*Trim;
        if(Speed>60 && Speed<300) { Param=300; Rate*=Speed/300; }
        else if(Speed<=60) { Param=Speed*5; Rate*=.2f; }
        Anim->SetBlendSpacePosition(FVector(Angle,Param,0));
        // Blendspace sample weights and marker clocks require a real delta.
        // SetPosition + TickAnimation(0) left the sample cache at idle even while
        // the capsule travelled: measured foot excursion was only 0.052 cm.
        Anim->SetPlayRate(Rate);
        Body->TickAnimation(WardenRules::Step,false); Body->RefreshBoneTransforms(); Local=Body->GetBoneSpaceTransforms();
    }
    // Blend only the unmodified animation base: never feed procedural IK back
    // into itself. This removes the walk/stop/commit snap while keeping contact
    // poses authoritative on the fixed simulation step.
    // Only around a change of action (walk/stop/commit): a permanent low-pass also damped
    // every stride, so planted feet skated at ~65% of body speed (AnimationTests).
    if(Fight.Action!=PosedAction) { PosedAction=Fight.Action; PoseSettle=10; }
    const float Catch=PoseSettle>0 ? FMath::Lerp(1.f,.28f,PoseSettle/10.f) : 1.f;
    if(PoseSettle>0) --PoseSettle;
    if(MotionBase.Num()==Local.Num() && Catch<1)
        for(int32 I=0;I<Local.Num();++I)
        {
            FTransform Blended; Blended.Blend(MotionBase[I],Local[I],Catch); Local[I]=Blended;
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
    FSwordKey Guard=bRegent ? RegentGuard() : FSwordKey{FVector(28,5,114),FVector(.38,-.12,.92).GetSafeNormal(),-7,5};
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
        else if(!bBoss)
        {
            // Player moveset: cut I (right-to-left diagonal, the keys above), cut II
            // backhand, cut III overhead finisher, jump slam, rolling thrust, running cut.
            switch(Fight.Move)
            {
            case WardenRules::CutTwo:
                Wind={FVector(10,-26,140),FVector(-.45,-.75,.5).GetSafeNormal(),45,-8};
                Release={FVector(44,-4,122),FVector(.95,-.2,.15).GetSafeNormal(),0,10};
                Follow={FVector(18,26,112),FVector(.1,.98,-.15).GetSafeNormal(),-50,18}; break;
            case WardenRules::CutThree:
                Wind={FVector(12,3,178),FVector(-.52,0,.85).GetSafeNormal(),0,-12};
                Release={FVector(45,0,125),FVector(.95,0,.3).GetSafeNormal(),0,16};
                Follow={FVector(32,0,88),FVector(.8,0,-.6).GetSafeNormal(),0,28}; break;
            case WardenRules::JumpAttack:
                Wind={FVector(8,3,182),FVector(-.6,0,.8).GetSafeNormal(),0,-16};
                Release={FVector(46,0,120),FVector(.9,0,.2).GetSafeNormal(),0,20};
                Follow={FVector(36,0,74),FVector(.7,0,-.72).GetSafeNormal(),0,32}; break;
            case WardenRules::RollAttack:
                Wind={FVector(4,16,112),FVector(.97,.05,.2).GetSafeNormal(),-18,-4};
                Release={FVector(58,4,118),FVector(1,0,0),10,14};
                Follow={FVector(52,4,116),FVector(1,0,-.05).GetSafeNormal(),8,12}; break;
            case WardenRules::RunAttack:
                Wind={FVector(-2,30,132),FVector(-.6,.75,.25).GetSafeNormal(),-58,-6};
                Release={FVector(46,6,120),FVector(.97,.2,.05).GetSafeNormal(),-4,14};
                Follow={FVector(14,-28,112),FVector(.05,-.98,-.1).GetSafeNormal(),62,24}; break;
            default: break;
            }
        }
        // Cancels (chain cuts, rolling thrust, jump attack) wind up from the interrupted pose.
        const FSwordKey Start=bPoseFromLast ? FSwordKey{LastGrip,LastAxis,LastTwist,LastLean} : Guard;
        if(bRegent && WardenRegent::IsRegent(Fight.Move)) Key=RegentKey(Fight);
        else if(Fight.Age<D.Windup) Key=Blend(Start,Wind,float(Fight.Age)/FMath::Max(1,D.Windup-6));
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
    else if(Fight.Action==EWardenAction::Jump)
    {
        // Gather, rise with the blade held high, tuck the legs at the top, reach for the floor.
        const float U=float(Fight.Age)/WardenRules::JumpTicks;
        Key=Blend(Guard,{Guard.Grip+FVector(0,0,16),Guard.Axis,0,-10},FMath::Sin(PI*U));
        Tuck=.5f*FMath::Sin(PI*U);
    }
    else if(Fight.Action==EWardenAction::Heal)
    {
        // Drinking the flask: the blade drops to the right hand alone, low and pointing down,
        // while the left hand brings the flask to the mouth (below).
        const float Hold=Smooth(Fight.Age/12.f)*(1-Smooth((Fight.Age-64)/14.f));
        Key=Blend(Guard,{FVector(22,26,96),FVector(.5,.3,-.8).GetSafeNormal(),-8,4},Hold);
    }
    if(Fight.Action==EWardenAction::Ready && PoseEase>0)
    {
        Key=Blend({EaseGrip,EaseAxis,EaseTwist,EaseLean},Key,1-PoseEase/8.f);
        --PoseEase;
    }
    const float Recoil=Fight.ImpactTicks>0 ? FMath::Sin(PI*float(18-Fight.ImpactTicks)/18) : 0;
    // Armored hits still read through the torso, but never alter the sword's
    // active arc. Poise breaks and player flinches get a complete hurt pose.
    if(Fight.Action==EWardenAction::Hurt)
    {
        const float U=float(Fight.Age)/(bBoss?WardenRules::BossHurtTicks:WardenRules::HurtTicks);
        const float Weight=Smooth(U/.17f)*(1-Smooth((U-.32f)/.68f));
        Key=Blend(Guard,{FVector(12,15,100),FVector(.45,.65,.6).GetSafeNormal(),-22,-27},Weight);
    }
    // Directional recoil from the blow: lean away from the hit and twist off it. Never
    // during an armoured swing's contact (the blade path stays authoritative); the head
    // still snaps then (below).
    const float HitFront=ImpactDir.IsNearlyZero() ? -1.f : float(FVector::DotProduct(ImpactDir,GetActorForwardVector()));
    const float HitSide=ImpactDir.IsNearlyZero() ? 0.f : float(FVector::DotProduct(ImpactDir,GetActorRightVector()));
    if(Fight.Action!=EWardenAction::Hurt && !Fight.Active())
    { Key.Lean+=HitFront*13*Recoil; Key.Twist-=HitSide*18*Recoil; }
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
            : FVector(6*HitFront*Recoil,6*HitSide*Recoil,-32*Tuck-6*Landing-4*Recoil);
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
    // The head snaps with the blow, even mid-swing.
    if(Recoil>0)
        for(const TCHAR* Name:{TEXT("neck_01"),TEXT("head")})
            if(const int32 I=Index(Name); I>=0)
                SetRotation(I,FQuat(FVector::UpVector,FMath::DegreesToRadians(HitSide*9*Recoil))*FQuat(FVector::ForwardVector,FMath::DegreesToRadians(HitFront*10*Recoil))*CS[I].GetRotation());
    // Head tips back to drink while the flask is at the mouth.
    const float Drink=Fight.Action==EWardenAction::Heal && !bBoss ? Smooth((Fight.Age-14)/10.f)*(1-Smooth((Fight.Age-54)/10.f)) : 0;
    if(Drink>0)
        for(const TCHAR* Name:{TEXT("neck_02"),TEXT("head")})
            if(const int32 I=Index(Name); I>=0) SetRotation(I,FQuat(FVector::ForwardVector,FMath::DegreesToRadians(13*Drink))*CS[I].GetRotation());
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
    // The Regent glides under its robe on every long lunge (>= 1 m), dash, drift and ash
    // step: feet planted at the start would stretch the rear leg across the travel and drag
    // the long robe into a backward slope (seen in the 2026-11-09 study capture).
    const bool Glide=(bRegent && WardenRegent::IsRegent(Fight.Move) && (FMath::Abs(Fight.Definition().Advance)>=100 || Fight.Move==WardenRegent::AshStep))
        || (!bBoss && (Fight.Move==WardenRules::JumpAttack || FMath::Abs(Fight.Definition().Advance)>=60));
    if(Fight.Action==EWardenAction::Strike && !Glide)
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
    if(Fight.Action==EWardenAction::Dodge || Fight.Action==EWardenAction::Jump)
    {
        const FVector Left=FMath::Lerp(FootL.GetLocation(),MeshPoint(FVector(22,-15,64)),Tuck);
        const FVector Right=FMath::Lerp(FootR.GetLocation(),MeshPoint(FVector(4,15,57)),Tuck);
        IK(TEXT("thigh_l"),TEXT("calf_l"),TEXT("foot_l"),Left,MeshPoint(FVector(75,-20,55)));
        IK(TEXT("thigh_r"),TEXT("calf_r"),TEXT("foot_r"),Right,MeshPoint(FVector(75,20,55)));
        SetRotation(FootLI,FootL.GetRotation()); SetRotation(FootRI,FootR.GetRotation());
    }
    // Foot locking while ready: a foot that plants stays pinned to the floor (leg IK) until
    // the clip lifts it, then eases back onto the clip over six ticks. Removes the residual
    // skate the clips carry, most visible on strafes. Presentation only; no capsule change.
    if((Fight.Action==EWardenAction::Ready || DrinkWalk) && Fight.Alive())
    {
        const FTransform MeshWorld=VisualBody->GetComponentTransform();
        const float Scale=GetActorScale3D().X;
        for(int32 Side=0;Side<2;++Side)
        {
            const FTransform& Anim=Side?FootR:FootL;
            const FVector AnimWorld=MeshWorld.TransformPosition(Anim.GetLocation());
            FootLow[Side]=FMath::Min(FootLow[Side],float(Anim.GetLocation().Z));
            // Planted = the clip's own foot is nearly still over the floor and low; a height
            // test alone kept slowed full strides "planted" into the swing (forced releases).
            const float AnimMove=FVector::Dist2D(AnimWorld,FootAnimPrev[Side]);
            FootAnimPrev[Side]=AnimWorld;
            const bool Planted=Anim.GetLocation().Z<FootLow[Side]+4.f && AnimMove<FMath::Max(1.2f,.6f*float(Travel.Size2D()));
            if(Planted && !FootLocked[Side] && FootRelease[Side]>=1) { FootLocked[Side]=true; FootLock[Side]=AnimWorld; }
            if(FootLocked[Side] && (!Planted || FVector::Dist2D(FootLock[Side],AnimWorld)>28*Scale))
            { if(Planted) ++FootForcedReleases; FootLocked[Side]=false; FootReleaseFrom[Side]=FootLock[Side]; FootRelease[Side]=0; }
            FVector Pin=AnimWorld;
            if(FootLocked[Side]) Pin=FVector(FootLock[Side].X,FootLock[Side].Y,AnimWorld.Z);
            else if(FootRelease[Side]<1)
            {
                FootRelease[Side]=FMath::Min(1.f,FootRelease[Side]+1/6.f);
                Pin=FMath::Lerp(FVector(FootReleaseFrom[Side].X,FootReleaseFrom[Side].Y,AnimWorld.Z),AnimWorld,Smooth(FootRelease[Side]));
            }
            if(Pin.Equals(AnimWorld,.01)) continue;
            IK(Side?TEXT("thigh_r"):TEXT("thigh_l"),Side?TEXT("calf_r"):TEXT("calf_l"),Side?TEXT("foot_r"):TEXT("foot_l"),MeshWorld.InverseTransformPosition(Pin),MeshPoint(FVector(65,Side?20.f:-20.f,55)));
            SetRotation(Side?FootRI:FootLI,Anim.GetRotation());
        }
    }
    else { FootLocked[0]=FootLocked[1]=false; FootRelease[0]=FootRelease[1]=1; }
    const FVector Axis=MeshPoint(Key.Axis).GetSafeNormal();
    LastGrip=Key.Grip; LastAxis=Key.Axis; LastTwist=Key.Twist; LastLean=Key.Lean;
    SwordFrame=FTransform(FQuat::FindBetweenNormals(FVector::UpVector,Axis),MeshPoint(Key.Grip));
    const FVector Across=SwordFrame.GetRotation().GetAxisX();
    // Project the shared hilt into the intersection of both arms' reachable
    // spheres. The weapon and both hands share this corrected transform; no
    // stretched arm bones or independent floating off-hand.
    FVector SharedGrip=SwordFrame.GetLocation();
    // The Regent holds the estoc in the right hand only; the left arm carries the chain.
    // One hand on the hilt for the Regent (chain arm) and for the player while drinking.
    const bool Drinking=!bBoss && Fight.Action==EWardenAction::Heal;
    const int32 Hands=bRegent || Drinking ? 1 : 2;
    for(int32 Iteration=0;Iteration<12;++Iteration)
        for(int32 Side=0;Side<Hands;++Side)
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
    if(bRegent)
    {
        const int32 U=Index(TEXT("upperarm_l")),L=Index(TEXT("lowerarm_l")),H=Index(TEXT("hand_l")),Middle=Index(TEXT("middle_01_l"));
        if(U>=0 && L>=0 && H>=0)
        {
            const FVector Shoulder=CS[U].GetLocation();
            const float Reach=FVector::Distance(Shoulder,CS[L].GetLocation())+FVector::Distance(CS[L].GetLocation(),CS[H].GetLocation());
            FVector Cast;
            const FVector Aim=RegentLeftKey(Fight,Cast) ? MeshPoint(Cast)-Shoulder
                : VisualBody->GetComponentTransform().InverseTransformPosition(CenserWorld())-Shoulder;
            const FVector HandTarget=Shoulder+Aim.GetClampedToMaxSize(Reach*.95f);
            IK(TEXT("upperarm_l"),TEXT("lowerarm_l"),TEXT("hand_l"),HandTarget,MeshPoint(FVector(-10,-55,100)));
            if(Middle>=0) SetRotation(H,FQuat::FindBetweenNormals((CS[Middle].GetLocation()-CS[H].GetLocation()).GetSafeNormal(),Aim.GetSafeNormal())*CS[H].GetRotation());
        }
    }
    else if(Drinking)
    {
        // Flask from the hip to just below the mouth (following the tipped head), held, lowered.
        const int32 Head=Index(TEXT("head")),Middle=Index(TEXT("middle_01_l")),H=Index(TEXT("hand_l"));
        if(Head>=0 && H>=0)
        {
            const float Raise=Smooth(Fight.Age/16.f)*(1-Smooth((Fight.Age-58)/14.f));
            const FVector Mouth=CS[Head].GetLocation()+MeshPoint(FVector(13,-3,-9));
            const FVector Hip=MeshPoint(FVector(14,-28,98));
            const FVector FlaskAt=FMath::Lerp(Hip,Mouth,Raise);
            IK(TEXT("upperarm_l"),TEXT("lowerarm_l"),TEXT("hand_l"),FlaskAt,MeshPoint(FVector(-10,-60,95)));
            // Palm turned in toward the face.
            if(Middle>=0) SetRotation(H,FQuat::FindBetweenNormals((CS[Middle].GetLocation()-CS[H].GetLocation()).GetSafeNormal(),FMath::Lerp(MeshPoint(FVector(.3f,.2f,-1)),MeshPoint(FVector(.2f,.9f,.4f)),Raise).GetSafeNormal())*CS[H].GetRotation());
        }
    }
    for(int32 Side=0;Side<Hands;++Side)
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
    if(Local.Num()<Ref.GetNum())
    {
        // Revamp swing-chain bones follow the mannequin's; SwingCloth sets them below.
        TArray<FTransform> Full=Local;
        for(int32 I=Local.Num();I<Ref.GetNum();++I) Full.Add(VisualBody->BoneSpaceTransforms.IsValidIndex(I)?VisualBody->BoneSpaceTransforms[I]:Ref.GetRefBonePose()[I]);
        VisualBody->BoneSpaceTransforms=MoveTemp(Full);
    }
    else VisualBody->BoneSpaceTransforms=Local;
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
    SwingCloth(CS);
}
