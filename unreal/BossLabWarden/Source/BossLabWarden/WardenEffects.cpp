// Presentation-only player effects, read from fighter state every rendered frame:
// the crimson flask in the left hand while healing, the rising crimson motes and light
// flash when the heal lands (Elden Ring's flask feel), and dust with a camera kick when
// a jump or jump attack lands. Materials: ue_import_effects.py (/Game/BossLab/Effects).
#include "WardenPrototype.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "GameFramework/PlayerController.h"
#include "Materials/MaterialInterface.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"

namespace
{
float Hash(int32 I) { return FMath::Frac(FMath::Sin(I*12.9898f)*43758.5453f); }
UMaterialInterface* Effect(const TCHAR* Name,const TCHAR* Fallback)
{
    if(auto* M=LoadObject<UMaterialInterface>(nullptr,*(FString(TEXT("/Game/BossLab/Effects/"))+Name),nullptr,LOAD_Quiet|LOAD_NoWarn)) return M;
    return LoadObject<UMaterialInterface>(nullptr,*(FString(TEXT("/Game/BossLab/Materials/MI_"))+Fallback));
}
}

void AWardenArenaMode::BuildEffects()
{
    auto& V=Effects;
    if(V.Owner.IsValid()) return;
    auto* Owner=GetWorld()->SpawnActor<AActor>();
    V.Owner=Owner;
    auto* Root=NewObject<USceneComponent>(Owner); Owner->SetRootComponent(Root); Root->RegisterComponent();
    auto Prepare=[&](UPrimitiveComponent* C)
    {
        C->SetupAttachment(Root); C->SetCollisionEnabled(ECollisionEnabled::NoCollision); C->SetCanEverAffectNavigation(false);
        C->SetCastShadow(false); C->RegisterComponent(); Owner->AddInstanceComponent(C);
    };
    auto Set=[&](const TCHAR* Mesh,UMaterialInterface* Material,int32 Count)
    {
        auto* C=NewObject<UInstancedStaticMeshComponent>(Owner);
        C->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,Mesh)); C->SetMaterial(0,Material); Prepare(C);
        TArray<FTransform> Hidden; Hidden.Init(FTransform(FRotator::ZeroRotator,FVector::ZeroVector,FVector::ZeroVector),Count);
        C->AddInstances(Hidden,false);
        return C;
    };
    V.Motes=Set(TEXT("/Engine/BasicShapes/Plane"),Effect(TEXT("M_HealMote"),TEXT("Amber")),FWardenEffects::MoteCount);
    V.Dust=Set(TEXT("/Engine/BasicShapes/Plane"),Effect(TEXT("M_ImpactDust"),TEXT("Stone")),FWardenEffects::DustCount);
    V.Blood=Set(TEXT("/Engine/BasicShapes/Plane"),Effect(TEXT("M_BloodDrop"),TEXT("BlackIron")),FWardenEffects::Bursts*FWardenEffects::Drops);
    V.Splat=Set(TEXT("/Engine/BasicShapes/Plane"),Effect(TEXT("M_BloodSplat"),TEXT("BlackIron")),FWardenEffects::Splats);
    V.Trail=Set(TEXT("/Engine/BasicShapes/Plane"),Effect(TEXT("M_SwordTrail"),TEXT("Amber")),FWardenEffects::TrailSamples-1);
    for(float& T:V.TrailTime) T=-100;
    // Flask: a glowing crimson bulb with a dark iron neck and stopper.
    V.Flask=Set(TEXT("/Engine/BasicShapes/Sphere"),Effect(TEXT("M_FlaskGlass"),TEXT("Amber")),1);
    V.FlaskNeck=Set(TEXT("/Engine/BasicShapes/Cylinder"),LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/BossLab/Materials/MI_BlackIron")),2);
    auto* Light=NewObject<UPointLightComponent>(Owner);
    Light->SetupAttachment(Root); Light->SetMobility(EComponentMobility::Movable);
    Light->SetIntensity(0); Light->SetAttenuationRadius(380); Light->SetLightColor(FLinearColor(1,.18,.08));
    Light->SetCastShadows(false); Light->RegisterComponent(); Owner->AddInstanceComponent(Light);
    V.Glow=Light;
    auto* Blade=NewObject<UPointLightComponent>(Owner);
    Blade->SetupAttachment(Root); Blade->SetMobility(EComponentMobility::Movable);
    Blade->SetIntensity(0); Blade->SetAttenuationRadius(260); Blade->SetLightColor(FLinearColor(1,.5,.15));
    Blade->SetCastShadows(false); Blade->RegisterComponent(); Owner->AddInstanceComponent(Blade);
    V.SwordLight=Blade;
}

void AWardenArenaMode::RecentDamageAdd(float Amount,float Seconds)
{
    auto& V=Effects;
    V.RecentDamage=Seconds-V.LastBossHit<2.5f ? V.RecentDamage+Amount : Amount;
}
void AWardenArenaMode::AnimateEffects(float Seconds)
{
    auto& V=Effects;
    if(!Player || !V.Motes.IsValid()) return;
    const auto& F=Player->Fight;
    FVector Eye=Player->GetActorLocation()+FVector(-500,0,200);
    if(auto* PC=GetWorld()->GetFirstPlayerController(); PC && PC->PlayerCameraManager) Eye=PC->PlayerCameraManager->GetCameraLocation();
    auto Card=[&](const FVector& At,float Size)
    {
        // Plane faces +Z: turn its normal to the camera so motes and puffs never show an edge.
        return FTransform(FRotationMatrix::MakeFromZ((Eye-At).GetSafeNormal()).ToQuat(),At,FVector(Size/100));
    };
    const FTransform Hidden(FRotator::ZeroRotator,Player->GetActorLocation(),FVector::ZeroVector);
    const FVector Feet=Player->GetActorLocation()-FVector(0,0,Player->AirLift+90);

    // Flask: visible while drinking, in the left palm, tipping toward the mouth.
    const bool Drinking=F.Action==EWardenAction::Heal && F.Age>2 && F.Age<74;
    const FVector Hand=Player->VisualBody->GetBoneLocationByName(TEXT("hand_l"),EBoneSpaces::WorldSpace);
    const FVector Finger=Player->VisualBody->GetBoneLocationByName(TEXT("middle_01_l"),EBoneSpaces::WorldSpace);
    const FVector Head=Player->VisualBody->GetBoneLocationByName(TEXT("head"),EBoneSpaces::WorldSpace);
    const FVector Palm=(Hand+Finger)*.5f;
    const float Tip=Drinking ? FMath::Clamp((F.Age-14)/12.f,0.f,1.f)*(1-FMath::Clamp((F.Age-54)/10.f,0.f,1.f)) : 0;
    const FVector Neck=FMath::Lerp(FVector::UpVector,((Head-Palm).GetSafeNormal()+FVector::UpVector*.3f).GetSafeNormal(),Tip).GetSafeNormal();
    const FQuat Upright=FQuat::FindBetweenNormals(FVector::UpVector,Neck);
    auto Place=[&](UInstancedStaticMeshComponent* C,int32 I,const FTransform& X) { C->UpdateInstanceTransform(I,X,true,false,true); };
    Place(V.Flask.Get(),0,Drinking ? FTransform(Upright,Palm,FVector(.085f,.085f,.1f)) : Hidden);
    Place(V.FlaskNeck.Get(),0,Drinking ? FTransform(Upright,Palm+Neck*8.5f,FVector(.028f,.028f,.07f)) : Hidden);
    Place(V.FlaskNeck.Get(),1,Drinking ? FTransform(Upright,Palm+Neck*12.5f,FVector(.036f,.036f,.025f)) : Hidden);

    // Heal burst: when the heal lands (commit tick), crimson motes swirl up the body and a
    // red light flashes; a few motes already gather around the flask while drinking.
    const int32 HealKey=Encounter*10+F.Heals;
    if(F.Action==EWardenAction::Heal && F.Age>=WardenRules::HealCommit && V.HealFor!=HealKey) { V.HealFor=HealKey; V.HealAt=Seconds; }
    const float Since=Seconds-V.HealAt;
    TArray<FTransform> Motes; Motes.Reserve(FWardenEffects::MoteCount);
    for(int32 I=0;I<FWardenEffects::MoteCount;++I)
    {
        const float Life=1.f+.6f*Hash(I+3), Delay=.25f*Hash(I+7), U=(Since-Delay)/Life;
        if(U>=0 && U<1)
        {
            const float A=Hash(I)*2*PI+U*(2.5f+2*Hash(I+11)), R=(22+28*Hash(I+5))*(1-.35f*U);
            const FVector At=Feet+FVector(FMath::Cos(A)*R,FMath::Sin(A)*R,15+130*Hash(I+9)+(70+80*Hash(I+13))*U);
            Motes.Add(Card(At,(5+5*Hash(I+17))*FMath::Sin(PI*FMath::Min(1.f,U*1.6f))));
        }
        else if(Drinking && I<10)
        {
            const float A=Seconds*3+I*.63f;
            Motes.Add(Card(Palm+FVector(FMath::Cos(A)*9,FMath::Sin(A)*9,FMath::Frac(Seconds*.8f+I*.1f)*22),2.5f+1.5f*Hash(I)));
        }
        else Motes.Add(Hidden);
    }
    V.Motes->BatchUpdateInstancesTransforms(0,Motes,true,true);
    if(auto* L=V.Glow.Get())
    {
        const float Flash=Since>=0 && Since<.9f ? FMath::Sin(PI*FMath::Min(1.f,Since/.9f))*(1-Since/.9f*.4f) : 0;
        L->SetWorldLocation(Player->GetActorLocation()+FVector(0,0,20));
        const float Intensity=(Drinking ? 600.f : 0.f)+5000.f*Flash;
        // A dark light still costs a lighting pass: hide it between drinks.
        L->SetVisibility(Intensity>0); L->SetIntensity(Intensity);
    }

    // Landing dust and camera kick: a jump attack's impact at the blade, a plain jump at the feet.
    const bool Slam=F.Action==EWardenAction::Strike && F.Move==WardenRules::JumpAttack && F.Age>=F.Definition().Windup;
    if(Slam && V.DustFor!=F.AttackInstance)
    {
        V.DustFor=F.AttackInstance; V.DustAt=Player->BladePoint(.9f); V.DustAt.Z=Feet.Z; V.DustAt+=FVector(0,0,2);
        V.DustTime=Seconds; V.DustScale=1; Shake=FMath::Max(Shake,.65f);
    }
    if(V.bAirborne && Player->AirLift<1 && F.Action!=EWardenAction::Strike)
    { V.DustAt=Feet+FVector(0,0,2); V.DustTime=Seconds; V.DustScale=.45f; Shake=FMath::Max(Shake,.15f); }
    V.bAirborne=Player->AirLift>5;
    TArray<FTransform> Dust; Dust.Reserve(FWardenEffects::DustCount);
    const float D=(Seconds-V.DustTime)/.9f;
    for(int32 I=0;I<FWardenEffects::DustCount;++I)
    {
        if(D<0 || D>=1) { Dust.Add(Hidden); continue; }
        const float A=I*2*PI/FWardenEffects::DustCount+Hash(I+50)*.4f;
        const float R=(20+150*FMath::Sqrt(D)*(.7f+.6f*Hash(I+51)))*V.DustScale;
        Dust.Add(Card(V.DustAt+FVector(FMath::Cos(A)*R,FMath::Sin(A)*R,(12+28*D)*V.DustScale),(35+55*D)*V.DustScale*(1-D*D)));
    }
    V.Dust->BatchUpdateInstancesTransforms(0,Dust,true,true);

    // Blood: a burst at each landed blow, sprayed along the blade's travel and away from
    // the attacker, falling under gravity; the drops that reach the floor leave splats.
    AWardenChallenger* Bleeders[2]={Player.Get(),Warden.Get()};
    for(int32 K=0;K<2;++K)
    {
        AWardenChallenger* Who=Bleeders[K];
        if(!Who || Who->BleedCount==V.SeenBleed[K]) continue;
        V.SeenBleed[K]=Who->BleedCount;
        auto& B=V.Burst[V.NextBurst]; V.NextBurst=(V.NextBurst+1)%FWardenEffects::Bursts;
        B.Start=Seconds; B.At=Who->BleedAt; B.Seed=Who->BleedCount*31+K*7;
        B.Dir=(Who->BleedDir*.6f+Who->ImpactDir*.8f).GetSafeNormal(); B.Scale=Who->GetActorScale3D().X;
        // Splats where some drops will land (floor top at z 0).
        for(int32 I=0;I<5;++I)
        {
            const float Speed=(160+200*Hash(B.Seed+I*3))*B.Scale, Up=80+120*Hash(B.Seed+I*5);
            const float T=(Up+FMath::Sqrt(Up*Up+2*980*FMath::Max(1.f,float(B.At.Z))))/980;
            auto& S=V.Splat_[V.NextSplat]; V.NextSplat=(V.NextSplat+1)%FWardenEffects::Splats;
            const FVector Side=FVector(-B.Dir.Y,B.Dir.X,0)*(Hash(B.Seed+I*7)-.5f)*120;
            S.At=FVector(B.At.X,B.At.Y,1.2f)+(FVector(B.Dir.X,B.Dir.Y,0)*Speed+Side)*T*.55f;
            S.Start=Seconds+T; S.Size=(14+26*Hash(B.Seed+I*11))*B.Scale; S.Yaw=360*Hash(B.Seed+I*13);
        }
    }
    TArray<FTransform> Drops; Drops.Reserve(FWardenEffects::Bursts*FWardenEffects::Drops);
    for(const auto& B:V.Burst)
        for(int32 I=0;I<FWardenEffects::Drops;++I)
        {
            const float T=Seconds-B.Start, Life=.55f+.35f*Hash(B.Seed+I);
            if(T<0 || T>Life) { Drops.Add(Hidden); continue; }
            // The first few drops are a short blood mist at the wound (big, soft, quick);
            // the rest spray over a wide hemisphere, biased along the blow, so some always
            // fly out past the bodies toward the camera.
            if(I<6)
            {
                const float U=T/.3f;
                if(U>=1) { Drops.Add(Hidden); continue; }
                const FVector Puff=FVector(Hash(B.Seed+I*9)-.5f,Hash(B.Seed+I*10)-.5f,Hash(B.Seed+I*11)*.6f)*60*U*B.Scale;
                Drops.Add(Card(B.At+Puff,(18+30*Hash(B.Seed+I*12))*B.Scale*FMath::Sin(PI*FMath::Min(1.f,U*1.4f)))); continue;
            }
            const FVector Random=FVector(Hash(B.Seed+I*2)-.5f,Hash(B.Seed+I*3)-.5f,Hash(B.Seed+I*4)*.8f).GetSafeNormal();
            const FVector Velocity=((B.Dir*.55f+Random).GetSafeNormal()*(220+300*Hash(B.Seed+I*5))+FVector(0,0,120+180*Hash(B.Seed+I*6)))*B.Scale;
            FVector At=B.At+Velocity*T+FVector(0,0,-490*T*T);
            if(At.Z<1) { Drops.Add(Hidden); continue; }
            Drops.Add(Card(At,(4+6*Hash(B.Seed+I*7))*B.Scale*(1-T/Life*.5f)));
        }
    V.Blood->BatchUpdateInstancesTransforms(0,Drops,true,true);
    TArray<FTransform> Splats; Splats.Reserve(FWardenEffects::Splats);
    for(const auto& S:V.Splat_)
    {
        const float T=Seconds-S.Start;
        // Spreads in over a fifth of a second, lingers, then shrinks away after 12 s.
        const float Size=T<0 ? 0 : S.Size*FMath::Min(1.f,T/.2f)*(1-FMath::Clamp((T-12)/3,0.f,1.f));
        Splats.Add(Size>.5f ? FTransform(FRotator(0,S.Yaw,0),S.At,FVector(Size/100,Size/100,1)) : Hidden);
    }
    V.Splat->BatchUpdateInstancesTransforms(0,Splats,true,true);

    // Enchanted greatsword: runes breathe at rest, brighten through the wind-up, blaze on
    // contact (more on heavy moves) and flash when a blow lands; an amber trail follows the
    // blade only during contact.
    const bool Swinging=F.Action==EWardenAction::Strike;
    float Glow=1+.25f*FMath::Sin(Seconds*2.2f);
    if(Swinging)
    {
        const auto& Def=F.Definition();
        const float Wind=FMath::Clamp(float(F.Age)/FMath::Max(1,Def.Windup),0.f,1.f);
        Glow=FMath::Lerp(Glow,Def.Stance>=2 ? 3.2f : 2.2f,Wind);
        if(F.Active()) Glow=Def.Stance>=2 ? 5.f : 3.6f;
    }
    if(Warden && Warden->BleedCount!=V.FlashFor) { V.FlashFor=Warden->BleedCount; V.RuneFlash=1; }
    V.RuneFlash=FMath::Max(0.f,V.RuneFlash-GetWorld()->GetDeltaSeconds()*3);
    Glow+=4*V.RuneFlash;
    if(auto* Runes=Player->SwordRunes.Get()) Runes->SetScalarParameterValue(TEXT("Glow"),Glow);
    if(auto* L=V.SwordLight.Get())
    {
        const bool Has=Player->Greatsword.IsValid();
        L->SetVisibility(Has);
        if(Has) { L->SetWorldLocation(Player->BladePoint(.45f)); L->SetIntensity(140*Glow); }
    }
    if(Swinging && (F.Active() || F.Age==F.Definition().Windup-1) && Player->Greatsword.IsValid())
    {
        V.TrailBase[V.TrailNext]=Player->BladePoint(.35f); V.TrailTip[V.TrailNext]=Player->BladePoint(1);
        V.TrailTime[V.TrailNext]=Seconds; V.TrailNext=(V.TrailNext+1)%FWardenEffects::TrailSamples;
    }
    TArray<FTransform> Ribbon; Ribbon.Reserve(FWardenEffects::TrailSamples-1);
    for(int32 K=0;K<FWardenEffects::TrailSamples-1;++K)
    {
        // Newest first: segment between consecutive samples, as a camera-facing card.
        const int32 A=(V.TrailNext-1-K+2*FWardenEffects::TrailSamples)%FWardenEffects::TrailSamples, B=(A-1+FWardenEffects::TrailSamples)%FWardenEffects::TrailSamples;
        const float Age=Seconds-V.TrailTime[A];
        if(Age>.14f || Seconds-V.TrailTime[B]>.18f) { Ribbon.Add(Hidden); continue; }
        const FVector MidA=(V.TrailBase[A]+V.TrailTip[A])*.5f, MidB=(V.TrailBase[B]+V.TrailTip[B])*.5f;
        const FVector Along=(MidA-MidB), Span=(V.TrailTip[A]-V.TrailBase[A]+V.TrailTip[B]-V.TrailBase[B])*.5f;
        if(Along.Size()<1) { Ribbon.Add(Hidden); continue; }
        const FVector X=Along.GetSafeNormal(), Toward=(Eye-(MidA+MidB)*.5f).GetSafeNormal();
        const FVector Y=FVector::CrossProduct(Toward,X).GetSafeNormal(), Z=FVector::CrossProduct(X,Y);
        const float Fade=1-Age/.14f;
        // Placed on the blade's outer half (where the tip sweeps), narrower than the blade.
        const FVector Centre=((MidA+MidB)*.5f+(V.TrailTip[A]+V.TrailTip[B])*.5f)*.5f;
        Ribbon.Add(FTransform(FMatrix(X,Y,Z,FVector::ZeroVector).ToQuat(),Centre,FVector(Along.Size()/100,Span.Size()/100*.45f*Fade,1)));
    }
    V.Trail->BatchUpdateInstancesTransforms(0,Ribbon,true,true);

    // Health-bar trails: hold 0.7 s after a hit, then drain; the boss damage number sums
    // hits landed within 2.5 s of each other.
    auto Trail=[&](float& TrailValue,float& Shown,float& LastHit,float Health,bool Boss)
    {
        if(Shown<0 || Health>Shown) { TrailValue=Health; Shown=Health; return; }
        if(Health<Shown)
        {
            if(Boss) RecentDamageAdd(Shown-Health,Seconds);
            LastHit=Seconds; Shown=Health;
        }
        if(Seconds-LastHit>.7f) TrailValue=FMath::Max(Health,TrailValue-200*(GetWorld()->GetDeltaSeconds()));
    };
    if(Warden) Trail(V.BossTrail,V.BossShown,V.LastBossHit,Warden->Fight.Health,true);
    Trail(V.PlayerTrail,V.PlayerShown,V.LastPlayerHit,Player->Fight.Health,false);
    for(auto* C:{V.Flask.Get(),V.FlaskNeck.Get()}) C->MarkRenderStateDirty();
}
