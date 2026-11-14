// Opt-in dungeon arena (-BossLabArena=dungeon): a fire-lit masonry hall around the
// unchanged fight floor. The floor/wall/pillar actors spawned in BeginPlay keep their
// transforms and collision and only change material; everything added here is
// NoCollision scenery outside the wall line or overhead. See docs/ARENA_DUNGEON.md.
#include "WardenPrototype.h"
#include "WardenGraphics.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SpotLightComponent.h"
#include "Components/SkyLightComponent.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Components/PostProcessComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/PointLight.h"
#include "Engine/SpotLight.h"
#include "Engine/SkyLight.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/PostProcessVolume.h"
#include "Components/BrushComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Materials/MaterialInterface.h"

namespace Dungeon
{
// Existing collision layout (WardenPrototype.cpp): floor R1400 top Z0; 32 wall blocks
// centred R1360, 260 high; 8 pillars centred R1360, radius 55, 540 high.
constexpr float PillarTop=540, OuterWall=1560, Height=1350, Piers=16;
UMaterialInterface* Mat(const TCHAR* Name)
{
    if(FString(Name).StartsWith(TEXT("MI_"))) return LoadObject<UMaterialInterface>(nullptr,*(FString(TEXT("/Game/BossLab/Materials/"))+Name));
    // Stone/flame from ue_import_dungeon.py; banner/fog/shaft/dust from ue_import_props.py.
    for(const TCHAR* Folder:{TEXT("/Game/BossLab/Dungeon/"),TEXT("/Game/BossLab/Dungeon/Props/")})
        if(auto* M=LoadObject<UMaterialInterface>(nullptr,*(FString(Folder)+Name),nullptr,LOAD_Quiet|LOAD_NoWarn)) return M;
    return nullptr;
}
FVector Radial(float A,float R,float Z) { return FVector(FMath::Cos(A)*R,FMath::Sin(A)*R,Z); }
float Hash(int32 I) { return FMath::Frac(FMath::Sin(I*12.9898f)*43758.5453f); }
}

void AWardenArenaMode::BuildDungeon(UWorld* World,FWardenDungeon& Out)
{
    using namespace Dungeon;
    Out=FWardenDungeon();
    for(TActorIterator<AStaticMeshActor> It(World);It;++It)
    {
        const bool Pillar=It->GetStaticMeshComponent()->GetStaticMesh() && It->GetStaticMeshComponent()->GetStaticMesh()->GetName()==TEXT("Cylinder");
        const TCHAR* Name=It->GetActorLocation().Z<0?TEXT("M_DungeonFloor"):Pillar?TEXT("M_DungeonColumn"):TEXT("M_DungeonWall");
        It->GetStaticMeshComponent()->SetMaterial(0,Mat(Name));
    }
    // Firelight only: the default sun/fill are switched off and the sky fill is a faint
    // cool fill so dark costumes keep a readable silhouette against the warm flames.
    for(TActorIterator<ADirectionalLight> It(World);It;++It) It->GetLightComponent()->SetVisibility(false);
    for(TActorIterator<ASkyLight> It(World);It;++It) { It->GetLightComponent()->SetIntensity(.5f); It->GetLightComponent()->SetLightColor(FLinearColor(.55,.66,1)); }

    auto Set=[&](const TCHAR* Mesh,const TCHAR* Material)
    {
        auto* Owner=World->SpawnActor<AActor>();
        auto* C=NewObject<UInstancedStaticMeshComponent>(Owner);
        Owner->SetRootComponent(C);
        C->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,Mesh));
        if(Material) C->SetMaterial(0,Mat(Material));
        C->SetCollisionEnabled(ECollisionEnabled::NoCollision); C->SetCanEverAffectNavigation(false);
        // Only the key light casts shadows and no scenery sits in its cone; each set spans
        // the whole hall, so letting it cast would redraw every instance into that map.
        C->SetCastShadow(false);
        C->RegisterComponent(); Owner->AddInstanceComponent(C);
        return C;
    };
    const TCHAR* Cube=TEXT("/Engine/BasicShapes/Cube");
    const TCHAR* Cylinder=TEXT("/Engine/BasicShapes/Cylinder");
    const TCHAR* Sphere=TEXT("/Engine/BasicShapes/Sphere");
    auto* Wall=Set(Cube,TEXT("M_DungeonWall"));
    auto* Pier=Set(Cube,TEXT("M_DungeonPier"));
    auto* Floor=Set(Cylinder,TEXT("M_DungeonFloor"));
    auto* Iron=Set(Cube,TEXT("MI_BlackIron"));
    auto* IronRound=Set(Cylinder,TEXT("MI_BlackIron"));
    auto* Bowl=Set(TEXT("/Engine/BasicShapes/Cone"),TEXT("MI_BlackIron"));
    auto* Coals=Set(Sphere,TEXT("MI_Amber"));
    auto* Inlay=Set(Cube,TEXT("MI_Bronze"));
    auto* Fire=Set(TEXT("/Engine/BasicShapes/Plane"),TEXT("M_DungeonFlame"));
    Out.Fire=Fire;
    auto Box=[](UInstancedStaticMeshComponent* C,FVector Centre,FVector Size,FRotator Rotation)
    { C->AddInstance(FTransform(Rotation,Centre,Size/100),true); };
    // CC0 Poly Haven props (ue_import_props.py): pivot at base centre, front faces +Y, so
    // yaw = bay angle + 90 turns the front toward the arena. One instanced set per mesh.
    TMap<FString,UInstancedStaticMeshComponent*> Props;
    auto Prop=[&](const TCHAR* Name,FVector Base,FRotator Rotation,FVector Scale)
    {
        UInstancedStaticMeshComponent*& C=Props.FindOrAdd(Name);
        if(!C) C=Set(*(FString(TEXT("/Game/BossLab/Dungeon/Props/"))+Name),nullptr);
        C->AddInstance(FTransform(Rotation,Base,Scale),true);
    };
    // Generated props (TRELLIS.2, prep_arena_gen.py / ue_import_arena_gen.py, 2026-11-14),
    // same convention; skipped when the local assets are absent.
    auto Gen=[&](const TCHAR* Name,FVector Base,FRotator Rotation,FVector Scale)
    {
        const FString Path=FString(TEXT("/Game/BossLab/Dungeon/Gen/SM_"))+Name+TEXT("Gen");
        UInstancedStaticMeshComponent*& C=Props.FindOrAdd(Path);
        if(!C)
        {
            if(!LoadObject<UStaticMesh>(nullptr,*Path,nullptr,LOAD_Quiet|LOAD_NoWarn)) return;
            C=Set(*Path,nullptr);
        }
        C->AddInstance(FTransform(Rotation,Base,Scale),true);
    };
    auto* Banner=Set(TEXT("/Engine/BasicShapes/Plane"),TEXT("M_DungeonBanner"));
    auto* FogGate=Set(TEXT("/Engine/BasicShapes/Plane"),TEXT("M_DungeonFogGate"));
    // Crossed vertical cards, base at Base; yaw jitter keeps neighbours from lining up.
    auto Flame=[&](FVector Base,float Width,float Tall,int32 Cards,int32 Seed)
    {
        for(int32 K=0;K<Cards;++K)
            Box(Fire,Base+FVector(0,0,Tall*.5f),FVector(Width,Tall,100),FRotator(0,K*180.f/Cards+Hash(Seed)*90,90));
    };
    auto Light=[&](FVector Position,float Intensity,float Radius,FLinearColor Color,bool Shadows)
    {
        auto* L=World->SpawnActor<APointLight>(Position,FRotator::ZeroRotator);
        auto* C=CastChecked<UPointLightComponent>(L->GetLightComponent());
        C->SetMobility(EComponentMobility::Movable); C->SetIntensity(Intensity); C->SetAttenuationRadius(Radius);
        C->SetLightColor(Color); C->SetCastShadows(Shadows); C->SetSourceRadius(Shadows?25:10);
        Out.Lights.Add(C); Out.Base.Add(Intensity);
    };
    // Warm fire against the cool moonlight and soul fire (BOSSLAB_GRAPHICS warmth): amber,
    // and a little brighter, so blue magic pops off a warm hall as in the reference clip.
    const bool Warm=WardenGraphics::Enabled(TEXT("warmth"));
    const FLinearColor FireColor=Warm ? FLinearColor(1,.5,.17) : FLinearColor(1,.42,.13);
    const float FireBoost=Warm ? 1.35f : 1.f;

    // Fight floor ritual rings (flush inlays, as in the default arena) and the sunken
    // trench floor between the parapet and the outer wall.
    for(float R:{360.f,1210.f})
        for(int32 I=0;I<96;++I)
        {
            const float A=I*2*PI/96;
            Box(Inlay,Radial(A,R,.4f),FVector(2*PI*R/96+2,3,.6f),FRotator(0,FMath::RadiansToDegrees(A)+90,0));
        }
    Box(Floor,FVector(0,0,-60),FVector(2*OuterWall+40,2*OuterWall+40,40),FRotator::ZeroRotator);

    // Outer hall: 48 wall blocks, 16 piers, cornice, pointed arches, ceiling and ribs.
    for(int32 I=0;I<48;++I)
    {
        const float A=I*2*PI/48;
        Box(Wall,Radial(A,OuterWall+40,(Height+300-80)*.5f),FVector(80,2*PI*OuterWall/48+30,Height+380),FRotator(0,FMath::RadiansToDegrees(A),0));
        Box(Pier,Radial(A,OuterWall-30,700),FVector(70,2*PI*OuterWall/48+12,46),FRotator(0,FMath::RadiansToDegrees(A),0));
    }
    for(int32 I=0;I<Piers;++I)
    {
        const float A=I*2*PI/Piers, Yaw=FMath::RadiansToDegrees(A);
        Box(Pier,Radial(A,OuterWall-60,Height*.5f),FVector(150,150,Height),FRotator(0,Yaw,0));
        Box(Pier,Radial(A,OuterWall-100,90),FVector(100,190,180),FRotator(0,Yaw,0));
        // Pointed arch over the bay to the next pier: two struts meeting at the apex.
        const float Mid=A+PI/Piers;
        const FVector Tangent(-FMath::Sin(Mid),FMath::Cos(Mid),0);
        const FVector Centre=Radial(Mid,OuterWall-35,0);
        const float Half=2*OuterWall*FMath::Sin(PI/Piers)*.5f-75;
        for(float Side:{-1.f,1.f})
        {
            const FVector Spring=Centre+Tangent*Side*Half+FVector(0,0,760), Apex=Centre+FVector(0,0,1060);
            Box(Pier,(Spring+Apex)*.5f,FVector(FVector::Dist(Spring,Apex)+40,70,55),(Apex-Spring).Rotation());
        }
        // Ribs from each pier top to the central boss of the vault.
        const FVector From=Radial(A,OuterWall-80,Height-20), To=Radial(A,230,Height+250);
        Box(Pier,(From+To)*.5f,FVector(FVector::Dist(From,To),55,60),(To-From).Rotation());
        // Bays: 0 is the sealed great door behind the boss (+X), 8 the entry door with its
        // fog wall (-X), other even bays barred cells (4 and 12 collapsed into rubble), odd
        // bays guardian statues with candle shrines on the parapet in front.
        const float MidYaw=FMath::RadiansToDegrees(Mid), Face=MidYaw+90;
        const bool Door=I==0 || I==8;
        if(Door)
        {
            // The great door behind the boss (bay 0) stands raised on a stone dais above the
            // parapet, with side steps down into the trench; the entry door stays at floor level.
            const float Raise=I==0 ? 300.f : 0.f;
            if(I==0)
            {
                Box(Pier,Centre-Radial(Mid,85,0)+FVector(0,0,(Raise-40)*.5f-20),FVector(170,600,Raise+40),FRotator(0,MidYaw,0));
                for(float Side:{-1.f,1.f})
                    for(int32 K=0;K<4;++K)
                        Box(Pier,Centre-Radial(Mid,85,0)+Tangent*Side*(330+K*55)+FVector(0,0,(Raise-K*75-40)*.5f-20),FVector(150,55,Raise-K*75+40),FRotator(0,MidYaw,0));
            }
            for(float Side:{-1.f,1.f}) Box(Pier,Centre+Tangent*Side*235+FVector(0,0,290+Raise)-Radial(Mid,30,0),FVector(90,70,660),FRotator(0,MidYaw,0));
            Box(Pier,Centre+FVector(0,0,650+Raise)-Radial(Mid,30,0),FVector(90,560,80),FRotator(0,MidYaw,0));
            Prop(TEXT("SM_CastleDoor"),Centre-Radial(Mid,15,0)+FVector(0,0,-40+Raise),FRotator(0,Face,0),FVector(2.05f,2,2.05f));
            if(I==0)
            {
                // The Regent's funeral throne on the dais before the sealed door, flanked by
                // tall candelabra: the court he holds.
                Gen(TEXT("Throne"),Centre-Radial(Mid,105,0)+FVector(0,0,Raise-20),FRotator(0,Face,0),FVector(1));
                for(float Side:{-1.f,1.f}) Gen(TEXT("Candelabrum"),Centre-Radial(Mid,100,0)+Tangent*Side*190+FVector(0,0,Raise-20),FRotator(0,Face+Side*20,0),FVector(.8f));
            }
            if(I==8) Box(FogGate,Centre-Radial(Mid,75,0)+FVector(0,0,-40+320),FVector(450,640,100),FRotator(0,Face,90));
        }
        else if(I%2==0 && (I==4 || I==12))
        {
            for(int32 K=0;K<4;++K)
                Prop(*FString::Printf(TEXT("SM_Rock0%d"),1+(I+K)%6),Centre-Radial(Mid,40+K*25,0)+Tangent*(K-1.5f)*120+FVector(0,0,-40+K%2*60),
                     FRotator(Hash(I*9+K)*20-10,Hash(I*5+K)*360,Hash(I*3+K)*20-10),FVector(.75f+Hash(I+K)*.35f));
        }
        else if(I%2==0)
        {
            for(float Side:{-1.f,1.f}) Box(Pier,Centre+Tangent*Side*190+FVector(0,0,220)-Radial(Mid,40,0),FVector(80,60,440),FRotator(0,MidYaw,0));
            Box(Pier,Centre+FVector(0,0,470)-Radial(Mid,40,0),FVector(80,440,60),FRotator(0,MidYaw,0));
            Prop(TEXT("SM_IronGate"),Centre-Radial(Mid,45,0)+FVector(0,0,-40),FRotator(0,Face,0),FVector(1.08f,1,1.45f));
        }
        else
        {
            const FVector Plinth=Radial(Mid,1475,0);
            Box(Pier,Plinth+FVector(0,0,80),FVector(230,320,240),FRotator(0,MidYaw,0));
            Prop(TEXT("SM_Statue"),Plinth+FVector(0,0,200),FRotator(0,Face,0),FVector(1.85f));
            Prop(TEXT("SM_KiteShield"),Plinth+Tangent*120-Radial(Mid,70,0)+FVector(0,0,200),FRotator(-18,Face+15,0),FVector(1));
            Prop(I%4==1?TEXT("SM_Mace"):TEXT("SM_WarHammer"),Plinth-Tangent*115-Radial(Mid,85,0)+FVector(0,0,203),FRotator(0,Face+60,-88),FVector(1.1f));
            // Shrine on the parapet top (2.6 m) in front of the statue.
            const FVector Ledge=Radial(Mid,1362,260);
            Prop(TEXT("SM_Candelabra"),Ledge,FRotator(0,Hash(I)*360,0),FVector(1));
            Prop(TEXT("SM_CandleTriple"),Ledge+Tangent*55,FRotator(0,Face+Hash(I+1)*40,0),FVector(1));
            Prop(TEXT("SM_CandleSmall"),Ledge-Tangent*45,FRotator::ZeroRotator,FVector(1));
            Prop(TEXT("SM_CandleSmall"),Ledge-Tangent*70+Radial(Mid,8,0),FRotator::ZeroRotator,FVector(.8f));
        }
        // Upper gallery: a balustraded walkway on carved corbels at ~8 m, between the arches
        // and above the statues; it rings the hall except over the two doors.
        if(!Door)
        {
            const float Chord=2*1450*FMath::Sin(PI/Piers)+20;
            Box(Pier,Radial(Mid,1450,805),FVector(110,Chord,35),FRotator(0,MidYaw,0));
            Box(Pier,Radial(Mid,1398,862),FVector(14,Chord,80),FRotator(0,MidYaw,0));
            Box(Pier,Radial(Mid,1398,906),FVector(24,Chord,10),FRotator(0,MidYaw,0));
            for(int32 K=-1;K<=1;++K)
            {
                Box(Pier,Radial(Mid,1398,862)+Tangent*K*Chord*.33f,FVector(22,22,90),FRotator(0,MidYaw,0));
                Box(Pier,Radial(Mid,1470,745)+Tangent*K*Chord*.33f,FVector(70,36,90),FRotator(-25,MidYaw,0));
            }
        }
        // Generated mourners and the dead on the gallery, looking down on the fight: angels in
        // even bays, sarcophagi, biers and bone heaps in odd bays.
        if(!Door)
        {
            const FVector Walk=Radial(Mid,1462,822);
            if(I%2==0) Gen(TEXT("Angel"),Walk,FRotator(0,Face,0),FVector(.92f));
            else if(I%4==1) Gen(TEXT("Sarcophagus"),Walk,FRotator(0,Face,0),FVector(.9f));
            else if(I==3 || I==11) Gen(TEXT("Bier"),Walk,FRotator(0,Face+Hash(I)*30-15,0),FVector(.85f));
            else Gen(TEXT("Ossuary"),Walk,FRotator(0,Hash(I)*360,0),FVector(.5f));
        }
        // Tattered banner on an iron rod in every bay.
        Box(Banner,Radial(Mid,OuterWall-12,790),FVector(170,440,100),FRotator(0,Face,90));
        Box(IronRound,Radial(Mid,OuterWall-14,1015),FVector(5,5,210),FRotator(90,Face,0));
        const FVector Torch=Radial(A,OuterWall-150,420);
        Box(Iron,Torch-Radial(A,-30,40),FVector(60,10,10),FRotator(-35,Yaw+180,0));
        Box(IronRound,Torch,FVector(22,22,18),FRotator::ZeroRotator);
        Flame(Torch+FVector(0,0,6),48,95,2,I*7+3);
        // Deferred light cost scales with covered pixels: alternate torches lit, short reach.
        if(I%2) Light(Torch+FVector(0,0,70)-Radial(A,60,0),8000*FireBoost,520,FireColor,false);
    }
    Box(Wall,FVector(0,0,Height+300),FVector(2*OuterWall+200,2*OuterWall+200,40),FRotator::ZeroRotator);
    Box(IronRound,FVector(0,0,Height+230),FVector(520,520,60),FRotator::ZeroRotator);

    // Fire trench behind the parapet: a coal bed whose tongues lick over the 2.6 m wall.
    for(int32 I=0;I<52;++I)
    {
        const float A=(I+Hash(I)*.6f)*2*PI/52, R=1450+Hash(I+101)*70;
        Box(Coals,Radial(A,R,-40),FVector(220+Hash(I+7)*80,100,28),FRotator(0,FMath::RadiansToDegrees(A)+90,0));
        // Keep the barred cells (even bays) readable behind embers rather than flames.
        if(FMath::FloorToInt(A/(2*PI/Piers))%2==0) continue;
        Flame(Radial(A,R,-45),220+Hash(I+3)*60,380+Hash(I+5)*140,2,I+11);
    }
    // No trench lights: the flame cards and brazier light read as the fire; each extra
    // deferred light measured ~0.3 ms here.

    // Great braziers on the eight preserved pillars.
    for(int32 I=0;I<8;++I)
    {
        const FVector Top=Radial(I*2*PI/8,1360,PillarTop);
        Box(Bowl,Top+FVector(0,0,32),FVector(150,150,64),FRotator(180,0,0));
        Box(IronRound,Top+FVector(0,0,62),FVector(160,160,8),FRotator::ZeroRotator);
        Box(Coals,Top+FVector(0,0,58),FVector(125,125,26),FRotator::ZeroRotator);
        Flame(Top+FVector(0,0,52),150,250,3,I*13+1);
        // Shadowless: eight cube-shadowed point lights cost 48 shadow views per frame;
        // the overhead key light carries the fighters' shadows instead.
        Light(Top+FVector(0,0,190),60000*FireBoost,2000,FireColor,false);
        Out.EmberSources.Add(Top+FVector(0,0,90));
    }

    // Chandelier: an iron ring of candles over the floor centre, hung on four chains,
    // with a downward key light that pools on the duel.
    const float Ring=Height-350;
    for(int32 I=0;I<24;++I)
    {
        const float A=I*2*PI/24;
        Box(Iron,Radial(A,280,Ring),FVector(16,2*PI*280/24+4,22),FRotator(0,FMath::RadiansToDegrees(A),0));
        if(I%2==0) { Box(IronRound,Radial(A,280,Ring+20),FVector(12,12,22),FRotator::ZeroRotator); Flame(Radial(A,280,Ring+30),16,38,2,I+400); }
        if(I%6==0) Box(IronRound,Radial(A,275,(Ring+Height+230)*.5f),FVector(5,5,Height+230-Ring),FRotator::ZeroRotator);
    }
    // Cool moonlight through a broken oculus is the fighters' key and only shadow caster;
    // the fire supplies warm rims. A soft additive cone and drifting dust mark the shaft.
    const float Oculus=Height+278;
    auto* Key=World->SpawnActor<ASpotLight>(FVector(0,0,Oculus-30),FRotator(-90,0,0));
    auto* KeyC=CastChecked<USpotLightComponent>(Key->GetLightComponent());
    KeyC->SetMobility(EComponentMobility::Movable); KeyC->SetIntensity(2000000); KeyC->SetAttenuationRadius(2600);
    KeyC->SetOuterConeAngle(44); KeyC->SetInnerConeAngle(16); KeyC->SetLightColor(FLinearColor(.62,.74,1)); KeyC->SetCastShadows(true);
    Out.Lights.Add(KeyC); Out.Base.Add(2000000);
    auto* Sky=Set(Cylinder,TEXT("M_DungeonDust"));
    Box(Sky,FVector(0,0,Oculus),FVector(340,340,4),FRotator::ZeroRotator);
    auto* Shaft=Set(TEXT("/Engine/BasicShapes/Cone"),TEXT("M_DungeonShaft"));
    Box(Shaft,FVector(0,0,Oculus*.5f),FVector(1300,1300,Oculus),FRotator::ZeroRotator);
    auto* Dust=Set(Sphere,TEXT("M_DungeonDust"));
    for(int32 I=0;I<90;++I) Dust->AddInstance(FTransform(FRotator::ZeroRotator,FVector(0,0,100),FVector(.006f)),true);
    Out.Dust=Dust;

    // Embers: tiny glowing motes rising from the braziers (animated in AnimateDungeon).
    auto* Embers=Set(Sphere,TEXT("MI_Amber"));
    for(int32 I=0;I<160;++I) Embers->AddInstance(FTransform(FRotator::ZeroRotator,Out.EmberSources[I%8],FVector(.03f)),true);
    Out.Embers=Embers;

    auto* Fog=World->SpawnActor<AExponentialHeightFog>();
    Fog->GetComponent()->SetFogDensity(.015f);
    Fog->GetComponent()->SetFogHeightFalloff(.12f);
    Fog->GetComponent()->SetFogInscatteringColor(FLinearColor(.03,.014,.008));
    Fog->GetComponent()->SetStartDistance(500);
    auto* Post=World->SpawnActor<APostProcessVolume>();
    Post->bUnbound=true;
    Post->GetBrushComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Post->Settings.bOverride_VignetteIntensity=true; Post->Settings.VignetteIntensity=.55f;
    Post->Settings.bOverride_BloomIntensity=true; Post->Settings.BloomIntensity=.75f;
    // Muted, gritty grade: lower saturation, firmer contrast, cool shadows, light grain.
    Post->Settings.bOverride_ColorSaturation=true; Post->Settings.ColorSaturation=FVector4(.86,.84,.82,1);
    Post->Settings.bOverride_ColorContrast=true; Post->Settings.ColorContrast=FVector4(1.12,1.12,1.12,1);
    Post->Settings.bOverride_ColorGainShadows=true; Post->Settings.ColorGainShadows=FVector4(.92,.97,1.08,1);
    Post->Settings.bOverride_FilmGrainIntensity=true; Post->Settings.FilmGrainIntensity=.18f;

    // Overnight 2026-11-14 (BOSSLAB_GRAPHICS, see WardenGraphics.h).
    if(WardenGraphics::Enabled(TEXT("volumetric")))
    {
        // Volumetric fog: the oculus moonlight becomes a real light shaft through the haze
        // and the braziers glow in the air. Only the key light scatters strongly; the
        // shadowless fire lights add a faint warm bloom in the fog.
        auto* FogC=Fog->GetComponent();
        FogC->SetVolumetricFog(true);
        FogC->SetVolumetricFogScatteringDistribution(.55f);
        FogC->SetVolumetricFogAlbedo(FColor(200,205,215));
        FogC->SetVolumetricFogExtinctionScale(2.2f);
        FogC->SetVolumetricFogDistance(4200);
        KeyC->SetVolumetricScatteringIntensity(4.f);
        for(auto& L:Out.Lights) if(L.IsValid() && L.Get()!=KeyC) L->SetVolumetricScatteringIntensity(.35f);
    }
    if(WardenGraphics::Enabled(TEXT("grade")))
    {
        // Filmic grade tuned for soul fire: a firmer toe for deep blacks, a softer shoulder
        // so HDR flame keeps colour, bloom that favours bright fire over lit stone, a fixed
        // exposure (eye adaptation stays off project-wide), warm highlights over the
        // existing cool shadows, a slightly stronger vignette and screen-space contact
        // shadows on the key light so feet and blades sit on the floor.
        auto& S=Post->Settings;
        S.bOverride_FilmToe=true; S.FilmToe=.57f;
        S.bOverride_FilmShoulder=true; S.FilmShoulder=.24f;
        S.bOverride_FilmSlope=true; S.FilmSlope=.9f;
        S.bOverride_BloomIntensity=true; S.BloomIntensity=.95f;
        S.bOverride_BloomThreshold=true; S.BloomThreshold=1.2f;
        S.bOverride_BloomSizeScale=true; S.BloomSizeScale=3.2f;
        S.bOverride_ColorGainHighlights=true; S.ColorGainHighlights=FVector4(1.05,1.0,.94,1);
        S.bOverride_VignetteIntensity=true; S.VignetteIntensity=.68f;
        S.bOverride_SceneFringeIntensity=true; S.SceneFringeIntensity=.35f;
        KeyC->ContactShadowLength=.035f; KeyC->MarkRenderStateDirty();
    }
    if(Warm)
    {
        // Warm midtones and highlights over the existing cool shadows, a touch more saturation.
        auto& S=Post->Settings;
        S.bOverride_ColorSaturation=true; S.ColorSaturation=FVector4(.98,.96,.92,1);
        S.bOverride_ColorGainMidtones=true; S.ColorGainMidtones=FVector4(1.06,1.0,.9,1);
        S.bOverride_ColorGainHighlights=true; S.ColorGainHighlights=FVector4(1.1,1.0,.86,1);
    }
}

// Presentation-time flicker and embers; the fixed combat step never reads these.
void AWardenArenaMode::AnimateDungeon(FWardenDungeon& D,float T)
{
    using namespace Dungeon;
    for(int32 I=0;I<D.Lights.Num();++I)
        if(auto* L=D.Lights[I].Get())
        {
            const float P=Hash(I+31)*20;
            const float Flicker=1+.10f*FMath::Sin(T*7.3f+P)+.07f*FMath::Sin(T*13.1f+P*1.7f)+.05f*FMath::Sin(T*23.f+P*.3f);
            L->SetIntensity(D.Base[I]*(L->IsA<USpotLightComponent>()?1+(Flicker-1)*.3f:Flicker));
        }
    if(auto* Dust=D.Dust.Get())
    {
        TArray<FTransform> Motes; Motes.SetNum(Dust->GetInstanceCount());
        for(int32 I=0;I<Motes.Num();++I)
        {
            const float Z=FMath::Frac(Hash(I+40)+T*.012f*(.5f+Hash(I+41)))*1500+80;
            const float R=FMath::Sqrt(Hash(I+42))*(120+Z*.32f), A=Hash(I+43)*2*PI+T*.05f;
            Motes[I]=FTransform(FRotator::ZeroRotator,FVector(FMath::Cos(A)*R,FMath::Sin(A)*R,Z)+FVector(FMath::Sin(T*.4f+I),FMath::Cos(T*.3f+I*.5f),0)*25,FVector(.006f));
        }
        Dust->BatchUpdateInstancesTransforms(0,Motes,true,true);
    }
    auto* E=D.Embers.Get();
    if(!E || D.EmberSources.IsEmpty()) return;
    TArray<FTransform> Motes; Motes.SetNum(E->GetInstanceCount());
    for(int32 I=0;I<Motes.Num();++I)
    {
        const float Life=2.4f+Hash(I)*2, Age=FMath::Frac(T/Life+Hash(I+500));
        const float A=Hash(I+900)*2*PI+T*.6f*(Hash(I+77)-.5f);
        const FVector Drift(FMath::Cos(A)*(20+Age*90),FMath::Sin(A)*(20+Age*90),Age*520);
        const FVector Sway(FMath::Sin(T*2.1f+I)*12,FMath::Cos(T*1.7f+I*.7f)*12,0);
        Motes[I]=FTransform(FRotator::ZeroRotator,D.EmberSources[I%D.EmberSources.Num()]+Drift+Sway*Age,FVector(.035f*(1-Age)+.004f));
    }
    E->BatchUpdateInstancesTransforms(0,Motes,true,true);
}
