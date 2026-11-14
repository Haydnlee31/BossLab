// Spectacle pass (presentation only; see docs/SPECTACLE_2026-11-14.md). Read from fight state
// every rendered frame, after the fixed steps:
//  - boss weapon trails: a soul-fire ribbon behind the estoc/sword in contact and behind the
//    censer through its sweep;
//  - the Sentence: soul fire gathers on the raised estoc (embers, a growing blue light), then
//    bursts off the point on release;
//  - phase two: an eruption of soul embers and a floor shockwave of grit and dust, a flash,
//    a heavy shake, a short slow-down and a wider view;
//  - the felled moment: slow motion, a flash and the boss's soul streaming up as embers for
//    four seconds (the results panel waits for it, WardenPrototype.cpp);
//  - floor debris: grit and dust kicked up by rolls, landings, boss lunges, slams and the
//    censer dragging on the floor;
//  - critical blows: a quick camera punch-in and a brief slow-down.
// Slow motion only scales how fast real time feeds the fixed step (WardenEncounter.cpp); the
// combat step is unchanged and it is off in automation and with reduced motion.
// BOSSLAB_GRAPHICS=-spectacle (or off) turns the whole pass off.
#include "WardenPrototype.h"
#include "WardenGraphics.h"
#include "WardenRegent.h"
#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "Materials/MaterialInterface.h"

namespace
{
float Hash(int32 I) { return FMath::Frac(FMath::Sin(I*12.9898f+.5f)*43758.5453f); }
float Smooth01(float T) { T=FMath::Clamp(T,0.f,1.f); return T*T*(3-2*T); }
UMaterialInterface* Mat(const TCHAR* Name,const TCHAR* Fallback)
{
    if(auto* M=LoadObject<UMaterialInterface>(nullptr,*(FString(TEXT("/Game/BossLab/Effects/"))+Name),nullptr,LOAD_Quiet|LOAD_NoWarn)) return M;
    if(auto* M=LoadObject<UMaterialInterface>(nullptr,*(FString(TEXT("/Game/BossLab/Effects/"))+Fallback),nullptr,LOAD_Quiet|LOAD_NoWarn)) return M;
    return LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/BossLab/Materials/MI_Amber"));
}
constexpr float FloorZ=2.f;
}

void AWardenArenaMode::BuildSpectacle()
{
    auto& V=Spectacle;
    if(V.Owner.IsValid() || !GetWorld() || !WardenGraphics::Enabled(TEXT("spectacle"))) return;
    auto* Owner=GetWorld()->SpawnActor<AActor>();
    if(!Owner) return;
    V.Owner=Owner;
    auto* Root=NewObject<USceneComponent>(Owner); Owner->SetRootComponent(Root); Root->RegisterComponent();
    auto Set=[&](UMaterialInterface* Material,int32 Count)
    {
        auto* C=NewObject<UInstancedStaticMeshComponent>(Owner);
        C->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Plane"))); C->SetMaterial(0,Material);
        C->SetupAttachment(Root); C->SetCollisionEnabled(ECollisionEnabled::NoCollision); C->SetCanEverAffectNavigation(false);
        C->SetCastShadow(false); C->RegisterComponent(); Owner->AddInstanceComponent(C);
        TArray<FTransform> Hidden; Hidden.Init(FTransform(FRotator::ZeroRotator,FVector::ZeroVector,FVector::ZeroVector),Count);
        C->AddInstances(Hidden,false);
        return C;
    };
    V.BladeTrail=Set(Mat(TEXT("M_BossTrail"),TEXT("M_SwordTrail")),FWardenSpectacle::TrailSamples-1);
    V.CenserTrail=Set(Mat(TEXT("M_BossTrail"),TEXT("M_SwordTrail")),FWardenSpectacle::TrailSamples-1);
    V.Ember=Set(Mat(TEXT("M_SoulEmber"),TEXT("M_HealMote")),FWardenSpectacle::Embers);
    V.Grit_=Set(Mat(TEXT("M_ImpactDust"),TEXT("M_ImpactDust")),FWardenSpectacle::Grit);
    V.Puff=Set(Mat(TEXT("M_ImpactDust"),TEXT("M_ImpactDust")),FWardenSpectacle::Puffs);
    auto Light=[&](float Radius)
    {
        auto* L=NewObject<UPointLightComponent>(Owner);
        L->SetupAttachment(Root); L->SetMobility(EComponentMobility::Movable);
        L->SetIntensity(0); L->SetAttenuationRadius(Radius); L->SetLightColor(FLinearColor(.3f,.55f,1.f));
        L->SetCastShadows(false); L->SetVisibility(false); L->RegisterComponent(); Owner->AddInstanceComponent(L);
        return L;
    };
    V.Charge=Light(420); V.Flash=Light(1600);
    V.bStudy=FParse::Param(FCommandLine::Get(),TEXT("BossLabSpectacleStudy"));   // the launcher passes it only with capture
    for(float& T:V.BladeTime) T=-100;
    for(float& T:V.CenserTime) T=-100;
}

void AWardenArenaMode::AnimateSpectacle(float Seconds)
{
    auto& V=Spectacle;
    if(!V.Owner.IsValid() || !Player || !Warden || !Player->Camera) return;
    const float Dt=V.LastSeconds<0 ? 0.f : FMath::Clamp(Seconds-V.LastSeconds,0.f,.05f);
    V.LastSeconds=Seconds;
    FVector Eye=Player->GetActorLocation()+FVector(-500,0,200);
    if(auto* PC=GetWorld()->GetFirstPlayerController(); PC && PC->PlayerCameraManager) Eye=PC->PlayerCameraManager->GetCameraLocation();
    const FTransform Hidden(FRotator::ZeroRotator,Warden->GetActorLocation(),FVector::ZeroVector);
    auto Card=[&](const FVector& At,float Size) { return FTransform(FRotationMatrix::MakeFromZ((Eye-At).GetSafeNormal()).ToQuat(),At,FVector(Size/100)); };
    auto Emit=[&](FWardenSpectacle::FMote* Pool,int32 Count,int32& Next,const FVector& At,const FVector& Vel,float Life,float Size,float Drag,float Gravity)
    {
        auto& M=Pool[Next]; Next=(Next+1)%Count;
        M.At=At; M.Vel=Vel; M.Start=Seconds; M.Life=Life; M.Size=Size; M.Drag=Drag; M.Gravity=Gravity;
    };
    int32 Seed=int32(Seconds*977);
    auto Rand=[&](float Lo,float Hi) { return FMath::Lerp(Lo,Hi,Hash(++Seed)); };
    auto Ember=[&](const FVector& At,const FVector& Vel,float Life,float Size) { Emit(V.EmberMote,FWardenSpectacle::Embers,V.NextEmber,At,Vel,Life,Size,1.2f,-60.f); };
    // Floor debris: chips thrown out low and falling back, plus a few soft dust puffs.
    auto Kick=[&](const FVector& Where,const FVector& Push,int32 Chips,int32 Puffs,float Scale)
    {
        const FVector Base(Where.X,Where.Y,FloorZ+3);
        for(int32 I=0;I<Chips;++I)
        {
            const float A=Rand(0,2*PI);
            const FVector Out=FVector(FMath::Cos(A),FMath::Sin(A),0)*Rand(80,260)*Scale+Push*.6f;
            Emit(V.GritMote,FWardenSpectacle::Grit,V.NextGrit,Base+FVector(Out.X,Out.Y,0)*.05f,Out+FVector(0,0,Rand(160,420)*Scale),Rand(.5f,.9f),Rand(2.5f,5.5f),.4f,-1400.f);
        }
        for(int32 I=0;I<Puffs;++I)
        {
            const float A=Rand(0,2*PI);
            Emit(V.PuffMote,FWardenSpectacle::Puffs,V.NextPuff,Base+FVector(FMath::Cos(A),FMath::Sin(A),0)*Rand(10,40)*Scale+FVector(0,0,12),
                 FVector(FMath::Cos(A),FMath::Sin(A),0)*Rand(40,120)*Scale+Push*.3f+FVector(0,0,Rand(20,60)),Rand(.7f,1.1f),Rand(40,70)*Scale,2.5f,0.f);
        }
    };
    if(V.bStudy)
    {
        // Capture-only review (scripts/bosslab-unreal capture spectacle): the fight's three big
        // moments on a fixed schedule; the player cannot fall.
        Player->Fight.Health=Player->Fight.MaxHealth;
        if(bRegent && CombatTick>=60 && !Regent.PhaseTwo && Warden->Fight.Health>WardenRegent::PhaseTwoHealth) Warden->Fight.Health=WardenRegent::PhaseTwoHealth;
        if(CombatTick>=420 && V.SeenCritical==0 && CriticalCount==0) ++CriticalCount;
        if(CombatTick>=600 && Warden->Fight.Alive()) Warden->Fight.Health=0;
    }
    const auto& P=Player->Fight;
    const auto& B=Warden->Fight;
    const bool BossStriking=B.Action==EWardenAction::Strike;
    const auto& BD=B.Definition();
    const int32 Since=BossStriking ? B.Age-BD.Windup : -999;
    const bool IsRegentMove=bRegent && WardenRegent::IsRegent(B.Move);
    const WardenRegent::EKind Kind=IsRegentMove ? WardenRegent::Kind(B.Move) : WardenRegent::EKind::Blade;

    // --- Boss weapon trails ------------------------------------------------------------
    const bool BladeSwing=BossStriking && (Kind==WardenRegent::EKind::Blade || Kind==WardenRegent::EKind::Vanish || !IsRegentMove)
        && Since>=-2 && Since<BD.Active+2 && !(IsRegentMove && WardenRegent::Vanished(B.Move,B.Age));
    // A fast blade can jump half a metre between frames (the Sentence covers its arc in three
    // ticks): fill in chord samples so the ribbon follows the sweep instead of one wide slab.
    auto Sample=[&](FVector* Base,FVector* Tip,float* Time,int32& Next,const FVector& NewBase,const FVector& NewTip)
    {
        const int32 N=FWardenSpectacle::TrailSamples, Last=(Next-1+N)%N;
        const bool Fresh=Seconds-Time[Last]<.06f;
        const int32 Steps=Fresh ? FMath::Clamp(FMath::CeilToInt(FVector::Dist(Tip[Last],NewTip)/35.f),1,5) : 1;
        const FVector FromBase=Base[Last], FromTip=Tip[Last]; const float FromTime=Time[Last];
        for(int32 K=1;K<=Steps;++K)
        {
            const float U=float(K)/Steps;
            Base[Next]=Fresh ? FMath::Lerp(FromBase,NewBase,U) : NewBase; Tip[Next]=Fresh ? FMath::Lerp(FromTip,NewTip,U) : NewTip;
            Time[Next]=Fresh ? FMath::Lerp(FromTime,Seconds,U) : Seconds; Next=(Next+1)%N;
        }
    };
    if(BladeSwing) Sample(V.BladeBase,V.BladeTip,V.BladeTime,V.BladeNext,Warden->BladePoint(.3f),Warden->BladePoint(1.02f));
    const bool CenserSwing=BossStriking && IsRegentMove && Kind==WardenRegent::EKind::Censer && Since>=-4 && Since<BD.Active+4;
    if(CenserSwing)
    {
        const FVector Head=Warden->CenserWorld();
        Sample(V.CenserA,V.CenserB,V.CenserTime,V.CenserNext,Head,Head-FVector(0,0,58));
    }
    auto Ribbon=[&](UInstancedStaticMeshComponent* C,const FVector* Base,const FVector* Tip,const float* Time,int32 Next,float Keep,float Width)
    {
        TArray<FTransform> Out; Out.Reserve(FWardenSpectacle::TrailSamples-1);
        const int32 N=FWardenSpectacle::TrailSamples;
        for(int32 K=0;K<N-1;++K)
        {
            const int32 A=(Next-1-K+2*N)%N, Bk=(A-1+N)%N;
            const float Age=Seconds-Time[A];
            if(Age>Keep || Seconds-Time[Bk]>Keep+.05f) { Out.Add(Hidden); continue; }
            const FVector MidA=(Base[A]+Tip[A])*.5f, MidB=(Base[Bk]+Tip[Bk])*.5f;
            const FVector Along=MidA-MidB, Span=(Tip[A]-Base[A]+Tip[Bk]-Base[Bk])*.5f;
            if(Along.Size()<1) { Out.Add(Hidden); continue; }
            const FVector X=Along.GetSafeNormal(), Toward=(Eye-(MidA+MidB)*.5f).GetSafeNormal();
            const FVector Y=FVector::CrossProduct(Toward,X).GetSafeNormal(), Z=FVector::CrossProduct(X,Y);
            const float Fade=1-Age/Keep;
            const FVector Centre=((MidA+MidB)*.5f+(Tip[A]+Tip[Bk])*.5f)*.5f;
            Out.Add(FTransform(FMatrix(X,Y,Z,FVector::ZeroVector).ToQuat(),Centre,FVector(Along.Size()/100,Span.Size()/100*Width*Fade,1)));
        }
        C->BatchUpdateInstancesTransforms(0,Out,true,true);
    };
    Ribbon(V.BladeTrail.Get(),V.BladeBase,V.BladeTip,V.BladeTime,V.BladeNext,.16f,.4f);
    Ribbon(V.CenserTrail.Get(),V.CenserA,V.CenserB,V.CenserTime,V.CenserNext,.22f,.6f);

    // --- The Sentence: soul fire gathers on the raised estoc, bursts on release -----------
    float ChargeLight=0;
    if(IsRegentMove && B.Move==WardenRegent::Sentence && BossStriking)
    {
        if(Since<0)
        {
            const float Charge=Smooth01((B.Age-24)/float(BD.Windup-24));
            V.EmberCarry+=Dt*(20+110*Charge);
            while(V.EmberCarry>=1)
            {
                V.EmberCarry-=1;
                const FVector On=Warden->BladePoint(Rand(.25f,1.f));
                Ember(On+FVector(Rand(-4,4),Rand(-4,4),Rand(-4,4)),FVector(Rand(-25,25),Rand(-25,25),Rand(40,120)),Rand(.4f,.8f),Rand(3,6)+5*Charge);
            }
            ChargeLight=Charge;
        }
        else if(V.SeenRelease!=B.AttackInstance)
        {
            V.SeenRelease=B.AttackInstance;
            const FVector Tip=Warden->BladePoint(1), Dir=Warden->CommittedDirection.GetSafeNormal2D();
            for(int32 I=0;I<36;++I) Ember(Tip,Dir*Rand(300,900)+FVector(Rand(-200,200),Rand(-200,200),Rand(-80,260)),Rand(.35f,.7f),Rand(4,9));
            V.FlashAt=Seconds; V.FlashPeak=9000; V.Flash->SetWorldLocation(Tip);
            Kick(Warden->GetActorLocation(),Dir*500,18,4,1.2f);
        }
    }
    if(auto* L=V.Charge.Get())
    {
        L->SetVisibility(ChargeLight>0);
        if(ChargeLight>0) { L->SetWorldLocation(Warden->BladePoint(.75f)); L->SetIntensity(9000*ChargeLight*(.85f+.15f*FMath::Sin(Seconds*31))); }
    }

    // --- Floor debris -------------------------------------------------------------------
    const FVector PlayerFeet=Player->GetActorLocation();
    if(P.Action==EWardenAction::Dodge && P.Age<=3)
    {
        const int32 Start=CombatTick-P.Age;
        if(V.SeenDodge!=Start) { V.SeenDodge=Start; Kick(PlayerFeet,Player->MoveVelocity*.3f,10,2,.8f); }
    }
    if(V.LastPlayerAction==int32(EWardenAction::Jump) && P.Action!=EWardenAction::Jump) Kick(PlayerFeet,FVector::ZeroVector,14,4,1.f);
    V.LastPlayerAction=int32(P.Action);
    if(BossStriking && Since==0 && V.SeenRelease!=B.AttackInstance+1000000)
    {
        // Lunges and slams throw grit; the bigger the move, the bigger the kick.
        const bool Lunge=BD.Advance>=100, Slam=IsRegentMove && (B.Move==WardenRegent::Bell || B.Move==WardenRegent::Pyre);
        if(Lunge || Slam || !IsRegentMove)
        {
            V.SeenRelease=B.AttackInstance+1000000;
            const FVector At=Slam ? Warden->CenserWorld() : Warden->GetActorLocation();
            Kick(At,Warden->CommittedDirection.GetSafeNormal2D()*(Lunge ? 400.f : 0.f),Slam ? 26 : 12,Slam ? 6 : 3,Slam ? 1.4f : 1.f);
        }
    }
    if(bRegent && Regent.CenserGrounded && Hash(int32(Seconds*60))<.5f) Kick(Warden->CenserWorld(),FVector::ZeroVector,2,Hash(int32(Seconds*60)+7)<.25f ? 1 : 0,.6f);

    // --- Critical blow: punch in and a brief slow-down ----------------------------------
    if(CriticalCount!=V.SeenCritical)
    {
        V.SeenCritical=CriticalCount;
        V.PunchAt=Seconds; V.PunchDepth=13; V.SlowUntil=Seconds+.32f; V.SlowScale=.35f;
    }

    // --- Phase two: eruption, shockwave, flash, slow-down, wider view -------------------
    if(bRegent && Regent.PhaseTwo && !V.bWasPhaseTwo)
    {
        V.PhaseAt=Seconds;
        const FVector At=Warden->GetActorLocation();
        for(int32 I=0;I<120;++I)
        {
            const float A=Rand(0,2*PI), Up=Rand(.2f,1);
            Ember(At+FVector(0,0,Rand(-60,80)),FVector(FMath::Cos(A),FMath::Sin(A),0)*Rand(250,900)*(1.2f-Up)+FVector(0,0,Up*Rand(300,1100)),Rand(.8f,1.8f),Rand(5,12));
        }
        for(int32 I=0;I<40;++I)
        {
            const float A=I*2*PI/40;
            Emit(V.GritMote,FWardenSpectacle::Grit,V.NextGrit,FVector(At.X,At.Y,FloorZ+5)+FVector(FMath::Cos(A),FMath::Sin(A),0)*60,
                 FVector(FMath::Cos(A),FMath::Sin(A),0)*Rand(900,1300)+FVector(0,0,Rand(120,300)),Rand(.6f,.9f),Rand(4,7),.3f,-1200.f);
        }
        for(int32 I=0;I<16;++I)
        {
            const float A=I*2*PI/16;
            Emit(V.PuffMote,FWardenSpectacle::Puffs,V.NextPuff,FVector(At.X,At.Y,FloorZ+20)+FVector(FMath::Cos(A),FMath::Sin(A),0)*120,
                 FVector(FMath::Cos(A),FMath::Sin(A),0)*Rand(500,700),Rand(.8f,1.2f),Rand(80,130),2.2f,0.f);
        }
        V.FlashAt=Seconds; V.FlashPeak=60000; V.Flash->SetWorldLocation(At+FVector(0,0,120));
        V.SlowUntil=Seconds+.7f; V.SlowScale=.35f; V.PunchAt=Seconds; V.PunchDepth=-9;
        Impact(0,1.f);
    }
    V.bWasPhaseTwo=bRegent && Regent.PhaseTwo;

    // --- Felled: slow motion, flash, the boss's soul streams away -----------------------
    if(!B.Alive() && V.bBossWasAlive && P.Alive())
    {
        V.FelledAt=Seconds;
        V.SlowUntil=Seconds+1.6f; V.SlowScale=.3f; V.PunchAt=Seconds; V.PunchDepth=10;
        V.FlashAt=Seconds; V.FlashPeak=40000; V.Flash->SetWorldLocation(Warden->GetActorLocation()+FVector(0,0,100));
    }
    if(B.Alive()) V.FelledAt=-100;
    V.bBossWasAlive=B.Alive();
    if(V.FelledAt>0 && Seconds-V.FelledAt<4.5f && Warden->VisualBody)
    {
        static const TCHAR* Bones[]={TEXT("pelvis"),TEXT("spine_03"),TEXT("spine_05"),TEXT("head"),TEXT("hand_l"),TEXT("hand_r"),TEXT("calf_l"),TEXT("calf_r")};
        const float Rate=Seconds-V.FelledAt<3.2f ? 90.f : 30.f;
        V.EmberCarry+=Dt*Rate;
        while(V.EmberCarry>=1)
        {
            V.EmberCarry-=1;
            const FVector From=Warden->VisualBody->GetBoneLocationByName(Bones[int32(Rand(0,7.99f))],EBoneSpaces::WorldSpace);
            Ember(From+FVector(Rand(-15,15),Rand(-15,15),Rand(-10,10)),FVector(Rand(-40,40),Rand(-40,40),Rand(90,260)),Rand(1.2f,2.4f),Rand(4,9));
        }
    }

    // --- Lights, camera ------------------------------------------------------------------
    if(auto* L=V.Flash.Get())
    {
        const float Age=Seconds-V.FlashAt, Glow=Age<0 ? 0.f : V.FlashPeak*FMath::Exp(-Age*4.5f);
        L->SetVisibility(Glow>50); if(Glow>50) L->SetIntensity(Glow);
    }
    {
        const float Age=Seconds-V.PunchAt;
        const float Env=Age<0 || bReducedMotion ? 0.f : Smooth01(Age/.08f)*(1-Smooth01((Age-.25f)/.6f));
        Player->Camera->SetFieldOfView(75-V.PunchDepth*Env);
    }

    // --- Integrate and draw the motes ----------------------------------------------------
    auto Draw=[&](UInstancedStaticMeshComponent* C,FWardenSpectacle::FMote* Pool,int32 Count,bool Puff,bool Bounce)
    {
        TArray<FTransform> Out; Out.Reserve(Count);
        for(int32 I=0;I<Count;++I)
        {
            auto& M=Pool[I];
            const float Age=Seconds-M.Start;
            if(Age<0 || Age>M.Life) { Out.Add(Hidden); continue; }
            M.Vel.Z+=M.Gravity*Dt; M.Vel*=FMath::Max(0.f,1-M.Drag*Dt); M.At+=M.Vel*Dt;
            if(Bounce && M.At.Z<FloorZ+1) { M.At.Z=FloorZ+1; M.Vel.Z=-M.Vel.Z*.3f; M.Vel.X*=.6f; M.Vel.Y*=.6f; }
            const float U=Age/M.Life;
            const float Size=Puff ? M.Size*(.5f+.9f*U)*(1-Smooth01((U-.6f)/.4f)) : M.Size*(1-Smooth01((U-.7f)/.3f));
            Out.Add(Card(M.At,Size));
        }
        C->BatchUpdateInstancesTransforms(0,Out,true,true);
    };
    Draw(V.Ember.Get(),V.EmberMote,FWardenSpectacle::Embers,false,false);
    Draw(V.Grit_.Get(),V.GritMote,FWardenSpectacle::Grit,false,true);
    Draw(V.Puff.Get(),V.PuffMote,FWardenSpectacle::Puffs,true,false);
}
