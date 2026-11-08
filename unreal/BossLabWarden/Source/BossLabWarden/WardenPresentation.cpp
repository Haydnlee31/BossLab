#include "WardenPrototype.h"
#include "Components/StaticMeshComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/PointLight.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Materials/MaterialInterface.h"
#include "Sound/SoundWave.h"
#include "Sound/SoundAttenuation.h"
#include "Kismet/GameplayStatics.h"

static UMaterialInterface* Surface(const TCHAR* Name)
{
    return LoadObject<UMaterialInterface>(nullptr,*(FString(TEXT("/Game/BossLab/Materials/MI_"))+Name));
}
void AWardenArenaMode::DressArena()
{
    for(TActorIterator<AStaticMeshActor> It(GetWorld());It;++It)
        It->GetStaticMeshComponent()->SetMaterial(0,Surface(It->GetActorLocation().Z<0?TEXT("Stone"):TEXT("DarkStone")));
    auto Instances=[&](const TCHAR* Mesh,const TCHAR* Material)
    {
        auto* Owner=GetWorld()->SpawnActor<AActor>();
        auto* C=NewObject<UInstancedStaticMeshComponent>(Owner);
        Owner->SetRootComponent(C);
        C->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,Mesh)); C->SetMaterial(0,Surface(Material));
        C->SetCollisionEnabled(ECollisionEnabled::NoCollision); C->RegisterComponent(); Owner->AddInstanceComponent(C);
        return C;
    };
    auto* Inlay=Instances(TEXT("/Engine/BasicShapes/Cube"),TEXT("Bronze"));
    auto* Ribs=Instances(TEXT("/Engine/BasicShapes/Cube"),TEXT("Iron"));
    auto* Stone=Instances(TEXT("/Engine/BasicShapes/Cube"),TEXT("DarkStone"));
    auto* Flame=Instances(TEXT("/Engine/BasicShapes/Sphere"),TEXT("Amber"));
    for(float Radius : {360.f,780.f,1210.f})
        for(int32 I=0;I<96;++I)
        {
            const float A=I*2*PI/96;
            Inlay->AddInstance(FTransform(FRotator(0,FMath::RadiansToDegrees(A)+90,0),FVector(FMath::Cos(A)*Radius,FMath::Sin(A)*Radius,.4f),FVector(2*PI*Radius/9600,.025,.006)),true);
        }
    for(int32 I=0;I<16;++I)
    {
        const float A=I*2*PI/16, Yaw=FMath::RadiansToDegrees(A);
        const FVector Radial(FMath::Cos(A),FMath::Sin(A),0);
        Inlay->AddInstance(FTransform(FRotator(0,Yaw,0),Radial*995+FVector(0,0,.5),FVector(4.2,.035,.008)),true);
        Stone->AddInstance(FTransform(FRotator(0,Yaw,0),Radial*1420+FVector(0,0,350),FVector(1.6,1.35,7)),true);
        Ribs->AddInstance(FTransform(FRotator(0,Yaw,0),Radial*1330+FVector(0,0,330),FVector(.1,1.45,6)),true);
        Inlay->AddInstance(FTransform(FRotator(0,Yaw,0),Radial*1330+FVector(0,0,270),FVector(.16,1.5,.16)),true);
        if(I%2==0)
        {
            const FVector Pos=Radial*1290+FVector(0,0,295);
            Flame->AddInstance(FTransform(FRotator::ZeroRotator,Pos,FVector(.2,.2,.45)),true);
            auto* L=GetWorld()->SpawnActor<APointLight>(Pos,FRotator::ZeroRotator);
            auto* C=CastChecked<UPointLightComponent>(L->GetLightComponent());
            C->SetMobility(EComponentMobility::Movable); C->SetIntensity(1800); C->SetAttenuationRadius(600);
            C->SetLightColor(FLinearColor(1,.4,.09)); C->SetCastShadows(false);
        }
    }
    auto* Fog=GetWorld()->SpawnActor<AExponentialHeightFog>();
    Fog->GetComponent()->SetFogDensity(.012f);
    Fog->GetComponent()->SetFogInscatteringColor(FLinearColor(.025,.04,.055));
    Fog->GetComponent()->SetStartDistance(700);
}
void AWardenChallenger::DressFighter()
{
    auto* Main=Surface(TEXT("Iron"));
    for(int32 I=0;I<VisualBody->GetNumMaterials();++I) VisualBody->SetMaterial(I,Main);
    TInlineComponentArray<UStaticMeshComponent*> Existing(this);
    for(auto* C:Existing) if(C->GetFName()==TEXT("IronGauntlet")) C->SetMaterial(0,Surface(TEXT("Bronze")));
    // Create once; subsequent resets recolor without duplicating geometry.
    if(!FindObject<UStaticMeshComponent>(this,TEXT("Crown")))
    {
    auto Piece=[&](const TCHAR* Name,const TCHAR* Bone,FVector Offset,FVector Scale,const TCHAR* Mat,const TCHAR* Mesh=TEXT("/Engine/BasicShapes/Cube"))
    {
        auto* C=NewObject<UStaticMeshComponent>(this,FName(Name));
        C->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,Mesh)); C->SetMaterial(0,Surface(Mat));
        C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        C->RegisterComponent(); AddInstanceComponent(C);
        C->SetWorldLocation(VisualBody->GetSocketLocation(FName(Bone))+GetActorQuat().RotateVector(Offset*GetActorScale3D()));
        C->SetWorldRotation(GetActorRotation()); C->SetWorldScale3D(Scale*GetActorScale3D());
        C->AttachToComponent(VisualBody,FAttachmentTransformRules::KeepWorldTransform,FName(Bone));
    };
    Piece(TEXT("Crown"),TEXT("head"),FVector(0,0,5),FVector(.24,.25,.28),TEXT("BlackIron"),TEXT("/Engine/BasicShapes/Sphere"));
    Piece(TEXT("Crest"),TEXT("head"),FVector(0,0,20),FVector(.23,.035,.12),TEXT("Bronze"));
    Piece(TEXT("ShoulderL"),TEXT("upperarm_l"),FVector(0,0,0),FVector(.27,.34,.22),TEXT("Bronze"),TEXT("/Engine/BasicShapes/Sphere"));
    Piece(TEXT("ShoulderR"),TEXT("upperarm_r"),FVector(0,0,0),FVector(.27,.34,.22),TEXT("Bronze"),TEXT("/Engine/BasicShapes/Sphere"));
    Piece(TEXT("Mantle"),TEXT("spine_03"),FVector(-15,0,-17),FVector(.055,.37,.52),bBoss?TEXT("BlackIron"):TEXT("Cloth"));
    Piece(TEXT("Seal"),TEXT("spine_03"),FVector(15,0,-4),FVector(.04,.08,.16),bBoss?TEXT("Amber"):TEXT("Jade"));
    }
    if(!bBoss && !DressV13()) DressAshbound();
    VisualBody->SetVisibility(bBoss || !bV13Outfit,false);
    TInlineComponentArray<UStaticMeshComponent*> Parts(this);
    for(auto* C:Parts)
    {
        const FString N=C->GetName();
        if(C->ComponentHasTag(TEXT("V13Trial"))) C->SetVisibility(!bBoss && bV13Outfit);
        else if(C->ComponentHasTag(TEXT("Ashbound"))) C->SetVisibility(!bBoss && !bV13Outfit);
        else if(N.StartsWith(TEXT("Sword")) || N==TEXT("Crown") || N==TEXT("Crest") || N.StartsWith(TEXT("Shoulder")) || N==TEXT("Mantle") || N==TEXT("Seal")) C->SetVisibility(bBoss);
    }

}
void AWardenChallenger::PlayCue(int32 Cue)
{
    auto* Mode=GetWorld()->GetAuthGameMode<AWardenArenaMode>();
    if(!Mode || Mode->bMuted || !GetWorld()->GetFirstPlayerController()) return;
    const TCHAR* Names[]={TEXT("Cue"),TEXT("Impact"),TEXT("Heal"),TEXT("Step")};
    auto* Sound=LoadObject<USoundWave>(nullptr,*(FString(TEXT("/Game/BossLab/Audio/"))+Names[FMath::Clamp(Cue,0,3)]));
    if(!Sound) return;
    auto* Attenuation=NewObject<USoundAttenuation>(this);
    Attenuation->Attenuation.bAttenuate=true; Attenuation->Attenuation.bSpatialize=true;
    Attenuation->Attenuation.AttenuationShapeExtents=FVector(150);
    Attenuation->Attenuation.FalloffDistance=1800;
    UGameplayStatics::PlaySoundAtLocation(this,Sound,GetActorLocation(),Cue==3?.18f:.35f,1.f,0.f,Attenuation);
}
void AWardenChallenger::ToggleMute()
{ if(auto* M=GetWorld()->GetAuthGameMode<AWardenArenaMode>()) { M->bMuted=!M->bMuted; M->LastEvent=M->bMuted?TEXT("Audio muted"):TEXT("Audio enabled"); } }
void AWardenChallenger::ToggleMotion()
{ if(auto* M=GetWorld()->GetAuthGameMode<AWardenArenaMode>()) { M->bReducedMotion=!M->bReducedMotion; M->LastEvent=M->bReducedMotion?TEXT("Reduced motion: hit flash disabled"):TEXT("Hit flash enabled"); } }
void AWardenChallenger::CycleSensitivity()
{ Sensitivity=Sensitivity<.75f?1.f:Sensitivity<1.25f?1.5f:.5f; if(auto* M=GetWorld()->GetAuthGameMode<AWardenArenaMode>()) M->LastEvent=FString::Printf(TEXT("Mouse sensitivity %.1fx"),Sensitivity); }
