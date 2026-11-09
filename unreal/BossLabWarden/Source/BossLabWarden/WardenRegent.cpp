// Opt-in Funeral Regent moveset (-BossLabRegent): estoc in the right hand, a soul-fire
// censer on a chain from the left forearm, three floating witness skulls, and a second
// phase below half health. Greybox for feel testing; see docs/REGENT_MOVESET.md.
// Rules and the fixed-step resolution below are engine-owned and deterministic; the
// view at the end only reads that state.
#include "WardenRegent.h"
#include "WardenPrototype.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SpotLightComponent.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundWave.h"
#include "Sound/SoundAttenuation.h"
#include "Camera/CameraActor.h"
#include "Camera/PlayerCameraManager.h"
#include "GameFramework/PlayerController.h"

namespace
{
float Smooth(float T) { T=FMath::Clamp(T,0.f,1.f); return T*T*(3-2*T); }
FVector Ring(float Degrees,float Radius,float Z) { const float A=FMath::DegreesToRadians(Degrees); return FVector(FMath::Cos(A)*Radius,FMath::Sin(A)*Radius,Z); }
}

const FWardenStrike& WardenRegent::Strike(int32 Index)
{
    // Name, pose family, bone, windup, active, recovery, (unused animation times),
    // damage, radius, advance. Radius is the hit-sample radius for melee, the eruption
    // radius for Furrow and the blast radius for Pyre. Negative advance glides backwards.
    static const FWardenStrike Moves[Count]={
        {TEXT("MOURNER'S THRUST"),TEXT("RegentBlade"),TEXT("hand_r"),36,10,40,0,0,1,22,7,120},
        {TEXT("TRIPLE RITE"),TEXT("RegentBlade"),TEXT("hand_r"),30,66,44,0,0,1,12,7,150},
        {TEXT("CENSER ARC"),TEXT("RegentCenser"),TEXT("hand_l"),54,22,48,0,0,1,24,30,30},
        {TEXT("GRAVE BELL"),TEXT("RegentCenser"),TEXT("hand_l"),66,10,66,0,0,1,30,45,40},
        {TEXT("WITNESS VOLLEY"),TEXT("RegentCast"),TEXT("hand_l"),40,30,40,0,0,1,SkullDamage,0,0},
        {TEXT("DRIFT STEP"),TEXT("RegentMove"),TEXT("pelvis"),8,22,14,0,0,1,0,0,-320},
        {TEXT("PROCESSION DASH"),TEXT("RegentBlade"),TEXT("hand_r"),48,22,52,0,0,1,26,8,760},
        {TEXT("ASHEN FURROW"),TEXT("RegentCast"),TEXT("hand_l"),44,40,50,0,0,1,20,95,0},
        {TEXT("ASH STEP"),TEXT("RegentBlade"),TEXT("hand_r"),68,10,50,0,0,1,24,7,80},
        {TEXT("FUNERAL PYRE"),TEXT("RegentCast"),TEXT("hand_l"),72,8,70,0,0,1,28,480,0},
        {TEXT("THE PYRE WAKES"),TEXT("RegentCast"),TEXT("head"),30,30,40,0,0,1,0,0,0},
        // Same thrust, held cocked for an extra beat: punishes rolling on the usual rhythm.
        {TEXT("HELD THRUST"),TEXT("RegentBlade"),TEXT("hand_r"),58,10,44,0,0,1,22,7,120},
    };
    check(IsRegent(Index));
    return Moves[Index-First];
}
WardenRegent::EKind WardenRegent::Kind(int32 Move)
{
    switch(Move)
    {
        case Thrust: case Rite: case Dash: case HeldThrust: return EKind::Blade;
        case Arc: case Bell: return EKind::Censer;
        case Volley: case Furrow: return EKind::Cast;
        case Drift: return EKind::Move;
        case AshStep: return EKind::Vanish;
        case Pyre: return EKind::Ring;
        default: return EKind::Transition;
    }
}
bool WardenRegent::Contact(int32 Move,int32 Age)
{
    if(!IsRegent(Move)) return false;
    const EKind K=Kind(Move);
    if(K!=EKind::Blade && K!=EKind::Censer && K!=EKind::Vanish) return false;
    const auto& D=Strike(Move);
    const int32 R=Age-D.Windup;
    // Rite: two quick thrusts, then a held beat before the third. Rolling on rhythm loses.
    if(Move==Rite) return (R>=0 && R<8) || (R>=20 && R<28) || (R>=56 && R<66);
    return R>=0 && R<D.Active;
}
bool WardenRegent::Rearm(int32 Move,int32 Age)
{
    return Move==Rite && (Age-Strike(Rite).Windup==20 || Age-Strike(Rite).Windup==56);
}
bool WardenRegent::Vanished(int32 Move,int32 Age)
{
    return Move==AshStep && Age>=AshVanish && Age<AshAppear;
}
FVector WardenRegent::CenserOffset(int32 Move,int32 Age,bool Striking)
{
    // Hangs out to the left, clear of the mantle; the lantern body hangs ~36 cm below this point.
    const FVector Rest(10,-74,-58);
    if(!Striking || !IsRegent(Move)) return Rest;
    const auto& D=Strike(Move);
    if(Move==Dash)
    {
        const float U=Smooth(float(Age-D.Windup+8)/10)*(1-Smooth(float(Age-D.Windup-D.Active)/20));
        return FMath::Lerp(Rest,FVector(-90,-55,-30),U);
    }
    if(Move==Arc)
    {
        const FVector Start=Ring(-100,400,-30), Finish=Ring(95,400,-30);
        if(Age<D.Windup)
        {
            // Whirl overhead, widening, then drop to the sweep start behind the left side.
            const float U=float(Age)/D.Windup;
            const FVector Whirl=FVector(0,-20,150)+Ring(-Age*14.f,40+90*U,0);
            return FMath::Lerp(FMath::Lerp(Rest,Whirl,Smooth(U/.25f)),Start,Smooth((U-.75f)/.25f));
        }
        if(Age<D.Windup+D.Active) return Ring(FMath::Lerp(-100.f,95.f,Smooth(float(Age-D.Windup)/D.Active)),400,-30);
        return FMath::Lerp(Finish,Rest,Smooth(float(Age-D.Windup-D.Active)/D.Recovery));
    }
    if(Move==Bell)
    {
        // Raised high behind the head, slammed ahead, then dragged back along the floor.
        const FVector High(-35,-30,235), Mid(180,-20,230), Impact(360,0,-84);
        if(Age<D.Windup) { const float U=float(Age)/D.Windup; return FMath::Lerp(Rest,High,Smooth(U/.7f))+FVector(0,FMath::Sin(Age*.3f)*10*U,0); }
        if(Age<D.Windup+D.Active)
        {
            const float U=Smooth(float(Age-D.Windup+1)/4);
            return High*FMath::Square(1-U)+Mid*2*U*(1-U)+Impact*U*U;
        }
        return FMath::Lerp(Impact,Rest,Smooth((float(Age-D.Windup-D.Active)/D.Recovery-.35f)/.65f));
    }
    return Rest;
}
FVector WardenRegent::SkullOrbit(int32 Slot,int32 Tick)
{
    return Ring(Slot*120.f+Tick*1.1f,85,150);
}
FVector2D WardenRegent::Band(int32 Move)
{
    switch(Move)
    {
        case Thrust: case HeldThrust: return {0,330};
        case Rite: return {0,300};
        case Arc: return {0,440};
        case Bell: return {160,430};
        case Volley: return {250,5000};
        case Drift: return {0,320};
        case Dash: return {400,1300};
        case Furrow: return {280,1300};
        case Pyre: return {0,400};
        default: return {0,5000};
    }
}
int32 WardenRegent::Pause(int32 Move)
{
    switch(Move)
    {
        case Drift: return 0;
        case Volley: case AshStep: return 8;
        case Thrust: case HeldThrust: return 18;
        case Arc: case Furrow: case Wakes: return 24;
        case Bell: case Dash: return 32;
        default: return 40;   // Rite, Pyre: the long recoveries are the main punish windows
    }
}
float FWardenRegentState::PoolArea(int32 Tick) const
{
    float Area=0;
    for(const auto& H:Hazards) if(H.Kind==ERegentHazard::Pool && H.Live(Tick)) Area+=PI*H.Radius*H.Radius;
    return Area;
}

FVector AWardenChallenger::CenserWorld() const
{
    const bool Striking=Fight.Action==EWardenAction::Strike;
    return GetActorLocation()+FRotator(0,GetActorRotation().Yaw,0).RotateVector(WardenRegent::CenserOffset(Fight.Move,Fight.Age,Striking));
}
bool AWardenChallenger::CenserStrike() const
{
    return bRegent && Fight.Action==EWardenAction::Strike && WardenRegent::IsRegent(Fight.Move) && WardenRegent::Kind(Fight.Move)==WardenRegent::EKind::Censer;
}
FVector AWardenChallenger::HitPoint(int32 Sample) const
{
    if(!CenserStrike()) return BladePoint(Sample/4.f);
    // The chain from the shoulder to the censer head is the weapon.
    const FVector Anchor=WardenRegent::ChainAnchor();
    return GetActorLocation()+FRotator(0,GetActorRotation().Yaw,0).RotateVector(FMath::Lerp(Anchor,WardenRegent::CenserOffset(Fight.Move,Fight.Age,true),Sample/4.f));
}
FVector AWardenChallenger::HitOrigin() const
{
    if(!CenserStrike()) return SwordRoot->GetComponentLocation();
    return GetActorLocation()+FRotator(0,GetActorRotation().Yaw,0).RotateVector(WardenRegent::ChainAnchor());
}
void AWardenChallenger::DressRegentWeapon()
{
    // Estoc: the CC0 antique_estoc prop (pommel at its origin, guard 35 cm up, 149 cm long),
    // scaled so the grip sits on the existing hilt and the point ends at the existing reach.
    for(const TCHAR* Name:{TEXT("SwordBlade"),TEXT("SwordRidge"),TEXT("SwordTip"),TEXT("SwordGuard"),TEXT("SwordGrip"),TEXT("SwordPommel")})
        if(auto* C=FindObject<UStaticMeshComponent>(this,Name)) C->SetVisibility(false);
    if(FindObject<UStaticMeshComponent>(this,TEXT("RegentEstoc"))) return;
    auto* Estoc=NewObject<UStaticMeshComponent>(this,TEXT("RegentEstoc"));
    if(auto* Mesh=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/BossLab/Dungeon/Props/SM_Estoc"),nullptr,LOAD_Quiet|LOAD_NoWarn))
    { Estoc->SetStaticMesh(Mesh); Estoc->SetRelativeLocation(FVector(0,0,-22)); Estoc->SetRelativeScale3D(FVector(1.12f)); }
    else
    {
        // Fallback when the local prop is absent: a thin primitive blade at the same reach.
        Estoc->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube")));
        Estoc->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/BossLab/Materials/MI_Iron")));
        Estoc->SetRelativeLocation(FVector(0,0,78)); Estoc->SetRelativeScale3D(FVector(.035,.02,1.38));
    }
    Estoc->SetupAttachment(SwordRoot); Estoc->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Estoc->RegisterComponent(); AddInstanceComponent(Estoc);
}

void AWardenArenaMode::EnableRegent()
{
    bRegent=true;
    if(!Warden) return;
    Warden->bRegent=true;
    Warden->DressRegentWeapon();
    BuildRegentView();
    Regent=FWardenRegentState();
}
FVector AWardenArenaMode::RegentAshTarget() const
{
    // Reappear past the player and to one side (alternating), never outside the fight
    // floor or inside a pillar/pawn. Falls back to the other side, then to staying put.
    const FVector P=Player->GetActorLocation(), B=Warden->GetActorLocation();
    const FVector Away=(P-B).GetSafeNormal2D();
    const float Side=Warden->Fight.AttackInstance%2 ? 1.f : -1.f;
    FCollisionQueryParams Query(SCENE_QUERY_STAT(RegentAsh),false,Warden);
    for(const float S:{Side,-Side})
    {
        const FVector C=P+Away.RotateAngleAxis(S*55,FVector::UpVector)*230;
        const FVector Spot(C.X,C.Y,B.Z);
        if(FVector2D(Spot).Size()>WardenRegent::ArenaRadius) continue;
        if(!GetWorld()->OverlapAnyTestByChannel(Spot,FQuat::Identity,ECC_Pawn,Warden->Capsule->GetCollisionShape(),Query)) return Spot;
    }
    return B;
}
void AWardenArenaMode::RegentDecide(FVector& BossDirection)
{
    using namespace WardenRegent;
    auto& R=Regent; auto& F=Warden->Fight;
    const FVector ToPlayer=Player->GetActorLocation()-Warden->GetActorLocation();
    const float Distance=ToPlayer.Size2D();
    for(int32& Grow:R.Regrow) if(Grow>0) --Grow;
    if(F.Action==EWardenAction::Strike && IsRegent(F.Move))
    {
        const auto& D=F.Definition();
        // Telegraphed actions track the player until shortly before contact; then the
        // aim locks, so a late sidestep or roll beats them.
        const int32 Lock=F.Move==Dash ? 12 : 14;
        if(F.Move==AshStep)
        {
            if(F.Age==AshVanish)
            {
                R.AshTarget=RegentAshTarget();
                FRegentHazard Mark; Mark.Kind=ERegentHazard::Mark; Mark.Center=FVector(R.AshTarget.X,R.AshTarget.Y,0);
                Mark.Radius=110; Mark.Start=Mark.Arm=CombatTick; Mark.End=CombatTick+AshAppear-AshVanish; R.Hazards.Add(Mark);
            }
            if(F.Age==AshAppear)
            {
                Warden->SetActorLocation(R.AshTarget);
                const FVector Face=(Player->GetActorLocation()-R.AshTarget).GetSafeNormal2D();
                Warden->SetActorRotation(Face.Rotation()); Warden->CommittedDirection=Face;
            }
            if(F.Age>AshAppear && F.Age<D.Windup-Lock) Warden->CommittedDirection=ToPlayer.GetSafeNormal2D();
        }
        else if(F.Age<D.Windup-Lock) Warden->CommittedDirection=ToPlayer.GetSafeNormal2D();
        return;
    }
    if(!F.Ready()) return;
    auto Commit=[&](int32 Move)
    {
        if(!Warden->BeginAction(EWardenAction::Strike,Move,ToPlayer)) return false;
        AcceptedMove=Move; AcceptedTick=CombatTick;
        LastEvent=FString(F.Definition().Name)+TEXT(" | Aim committed.");
        if(Move==Pyre)
        {
            FRegentHazard Mark; Mark.Kind=ERegentHazard::Mark; Mark.Center=FVector(Warden->GetActorLocation().X,Warden->GetActorLocation().Y,0);
            Mark.Radius=F.Definition().Radius; Mark.Start=Mark.Arm=CombatTick; Mark.End=CombatTick+F.Definition().Windup; R.Hazards.Add(Mark);
        }
        return true;
    };
    if(!R.PhaseTwo && F.Health<=PhaseTwoHealth) { Commit(Wakes); return; }
    // Fixed rehearsal sequence, labelled as such: no learning, no input reading. Each
    // step walks into its distance band, commits, or is skipped after four seconds.
    static const int32 One[]={Thrust,Arc,Volley,Rite,HeldThrust,Drift,Dash,Bell,Furrow};
    static const int32 Two[]={AshStep,Rite,Pyre,HeldThrust,Volley,Dash,Arc,Furrow,Bell,Thrust,Drift};
    const int32 Next=R.PhaseTwo ? Two[R.Step%UE_ARRAY_COUNT(Two)] : One[R.Step%UE_ARRAY_COUNT(One)];
    if(Next==Volley && R.ReadySkulls()==0) { ++R.Step; R.Seeking=0; return; }
    const FVector2D B=Band(Next);
    // A player who stays close cannot lock out the ranged rites: after backing off for
    // three quarters of a second the Regent commits from where it stands.
    const bool TooClose=Distance<B.X && R.Seeking<45;
    if(Distance>B.Y) BossDirection=ToPlayer.GetSafeNormal2D();
    else if(TooClose) BossDirection=-ToPlayer.GetSafeNormal2D()*.8f;
    if(R.Waiting>0) { --R.Waiting; return; }
    if(TooClose || Distance>B.Y)
    {
        if(++R.Seeking>240) { ++R.Step; R.Seeking=0; }
        return;
    }
    // Phase two presses harder: shorter pauses between rites.
    if(Commit(Next)) { ++R.Step; R.Seeking=0; R.Waiting=R.PhaseTwo ? Pause(Next)*3/5 : Pause(Next); }
}
void AWardenArenaMode::RegentResolve()
{
    using namespace WardenRegent;
    auto& R=Regent; auto& F=Warden->Fight;
    const int32 T=CombatTick;
    const FVector BossAt=Warden->GetActorLocation();
    const FRotator Yaw(0,Warden->GetActorRotation().Yaw,0);
    auto Hurt=[&](float Amount,bool Flinch,const TCHAR* Event)
    {
        const float Before=Player->Fight.Health;
        if(!Player->Fight.Damage(Amount,Flinch)) return false;
        BossDamage+=Before-Player->Fight.Health; Player->HitFlash=.18f;
        if(Flinch) { Player->PlayCue(1); Impact(4,.35f); }
        LastEvent=Event; return true;
    };
    auto AddPool=[&](const FVector& Centre,float Radius,int32 Ticks)
    {
        // Keep the floor fightable: the oldest pool burns out before a fifth appears.
        int32 Pools=0, Oldest=INDEX_NONE;
        for(int32 I=0;I<R.Hazards.Num();++I)
            if(R.Hazards[I].Kind==ERegentHazard::Pool && R.Hazards[I].Live(T))
            { ++Pools; if(Oldest==INDEX_NONE || R.Hazards[I].Start<R.Hazards[Oldest].Start) Oldest=I; }
        if(Pools>=MaxPools) R.Hazards[Oldest].Spent=true;
        FRegentHazard H; H.Kind=ERegentHazard::Pool; H.Center=FVector(Centre.X,Centre.Y,0); H.Radius=Radius; H.Damage=PoolDamage;
        // Pools ignite after a beat, so a roll out of the slam that made them is enough.
        H.Start=T; H.Arm=H.NextHit=T+PoolIgnite; H.End=T+Ticks; R.Hazards.Add(H);
    };
    if(F.Action==EWardenAction::Strike && IsRegent(F.Move))
    {
        const auto& D=F.Definition();
        const int32 A=F.Age, Since=A-D.Windup;
        // Sound: one cue per readable beat (presentation only; never affects resolution).
        const FVector Head=Warden->CenserWorld();
        if(Kind(F.Move)==EKind::Blade || F.Move==AshStep)
            if(Since==0 || (F.Move==Rite && (Since==20 || Since==56))) RegentSound(TEXT("RegentThrust"),BossAt,.5f);
        if(F.Move==Arc && (A==12 || Since==-4)) RegentSound(TEXT("RegentWhoosh"),Head,A==12 ? .35f : .7f);
        if(F.Move==Bell && A==20) RegentSound(TEXT("RegentWhoosh"),Head,.4f);
        if(F.Move==Drift && A==2) RegentSound(TEXT("RegentWhoosh"),BossAt,.3f);
        if(F.Move==AshStep && (A==AshVanish || A==AshAppear)) RegentSound(TEXT("RegentBlink"),A==AshVanish ? BossAt : R.AshTarget,.6f);
        if(F.Move==Wakes && A==1) RegentSound(TEXT("RegentWakes"),BossAt,.55f);
        if(F.Move==Pyre && Since==0) RegentSound(TEXT("RegentPyre"),BossAt,.8f);
        switch(F.Move)
        {
        case Wakes:
            if(Since==0) { R.PhaseTwo=true; R.Step=0; R.Waiting=30; LastEvent=TEXT("THE PYRE WAKES | The Regent burns blue. New rites follow."); }
            break;
        case Bell:
            if(Since==3) { AddPool(Head,BellPoolRadius,BellPoolTicks); RegentSound(TEXT("RegentBell"),Head,.9f); }
            break;
        case Volley:
            if(Since>=0 && Since%12==0 && Since/12<(R.PhaseTwo ? 3 : 2))
                for(int32 S=0;S<Skulls;++S)
                    if(R.Regrow[S]==0)
                    {
                        FRegentSkull K; K.Slot=S; K.Position=BossAt+SkullOrbit(S,T);
                        K.Velocity=(Player->GetActorLocation()-K.Position).GetSafeNormal()*SkullSpeed;
                        R.Flying.Add(K); R.Regrow[S]=R.PhaseTwo ? SkullRegrowPhaseTwo : SkullRegrow;
                        RegentSound(TEXT("RegentSkull"),K.Position,.3f);
                        break;
                    }
            break;
        case Furrow:
            if(Since==0) { R.FurrowOrigin=BossAt; R.FurrowDirection=Warden->CommittedDirection.GetSafeNormal2D(); }
            if(Since>=0 && Since%FurrowStagger==0 && Since/FurrowStagger<FurrowMarks)
            {
                const FVector C=R.FurrowOrigin+R.FurrowDirection*(170+FurrowSpacing*(Since/FurrowStagger));
                if(FVector2D(C).Size()<FloorRadius-150)
                {
                    FRegentHazard H; H.Kind=ERegentHazard::Eruption; H.Center=FVector(C.X,C.Y,0); H.Radius=D.Radius; H.Damage=D.Damage;
                    H.Start=T; H.Arm=T+FurrowWarn; H.End=H.Arm+FurrowBurst; R.Hazards.Add(H);
                }
            }
            break;
        case Pyre:
            if(Since==0)
            {
                if(FVector::Dist2D(Player->GetActorLocation(),BossAt)<=D.Radius) Hurt(D.Damage,true,TEXT("Caught in the Funeral Pyre. Roll out through the blast."));
                for(int32 K=0;K<3;++K) AddPool(BossAt+Yaw.RotateVector(FRotator(0,60+120*K,0).Vector()*PyreSpread),PyrePoolRadius,PyrePoolTicks);
            }
            break;
        default: break;
        }
    }
    // Witness skulls: home slowly, stop turning close to the player, and pass through a
    // protected roll instead of waiting for the i-frames to end.
    const FVector Target=Player->GetActorLocation();
    FCollisionQueryParams Query(SCENE_QUERY_STAT(RegentSkull),false,Warden); Query.AddIgnoredActor(Player);
    for(int32 I=R.Flying.Num()-1;I>=0;--I)
    {
        auto& K=R.Flying[I]; ++K.Age;
        const FVector To=Target-K.Position;
        if(K.Homing)
        {
            if(To.Size2D()<SkullLockDistance) K.Homing=false;
            else
            {
                const FVector Have=K.Velocity.GetSafeNormal(), Want=To.GetSafeNormal();
                const float Angle=FMath::Acos(FMath::Clamp(float(Have|Want),-1.f,1.f)), Max=FMath::DegreesToRadians(SkullTurnDegrees);
                const FVector Turned=Angle<=Max ? Want : FQuat::Slerp(FQuat::Identity,FQuat::FindBetweenNormals(Have,Want),Max/Angle).RotateVector(Have);
                K.Velocity=Turned.GetSafeNormal()*SkullSpeed;
            }
        }
        const FVector Next=K.Position+K.Velocity*WardenRules::Step;
        FHitResult Wall;
        bool Gone=K.Age>SkullLife || FVector2D(Next).Size()>FloorRadius+200 || GetWorld()->LineTraceSingleByChannel(Wall,K.Position,Next,ECC_WorldStatic,Query);
        if(!Gone && !K.Passed && Player->Fight.Alive())
        {
            const FVector Closest=FMath::ClosestPointOnSegment(Next,Target-FVector(0,0,56),Target+FVector(0,0,56));
            if(FVector::Dist(Closest,Next)<SkullRadius+34)
            {
                if(Player->Fight.Invulnerable()) K.Passed=true;
                else if(Hurt(SkullDamage,true,TEXT("A witness skull struck. They stop turning up close: sidestep late."))) Gone=true;
            }
        }
        K.Position=Next;
        if(Gone) R.Flying.RemoveAt(I);
    }
    // Fire pools burn without flinching (chip damage); furrow eruptions hit once.
    for(auto& H:R.Hazards)
    {
        if(H.Kind==ERegentHazard::Eruption && H.Arm==T) RegentSound(TEXT("RegentEruption"),H.Center,.45f);
        if(!H.Armed(T) || H.Kind==ERegentHazard::Mark) continue;
        // Fire pools burn the floor: jumping over one avoids the chip damage.
        if(H.Kind==ERegentHazard::Pool && Player->AirLift>25) continue;
        if(FVector::Dist2D(Target,H.Center)>H.Radius+20) continue;
        if(H.Kind==ERegentHazard::Pool) { if(T>=H.NextHit && Hurt(H.Damage,false,TEXT("Soul fire burns. Leave the pool."))) H.NextHit=T+PoolInterval; }
        else if(Hurt(H.Damage,true,TEXT("The furrow erupted. Read the marks, then cross behind them."))) H.Spent=true;
    }
    R.Hazards.RemoveAll([T](const FRegentHazard& H) { return T>=H.End || H.Spent; });
}

void AWardenArenaMode::RegentSound(const TCHAR* Name,const FVector& At,float Volume)
{
    if(bMuted || !GetWorld()->GetFirstPlayerController()) return;
    auto* Sound=LoadObject<USoundWave>(nullptr,*(FString(TEXT("/Game/BossLab/Regent/Audio/"))+Name),nullptr,LOAD_Quiet|LOAD_NoWarn);
    if(!Sound) return;
    auto* Attenuation=NewObject<USoundAttenuation>(this);
    Attenuation->Attenuation.bAttenuate=true; Attenuation->Attenuation.bSpatialize=true;
    Attenuation->Attenuation.AttenuationShapeExtents=FVector(300);
    Attenuation->Attenuation.FalloffDistance=2600;
    UGameplayStatics::PlaySoundAtLocation(this,Sound,At,Volume,1.f,0.f,Attenuation);
}
FVector WardenRegentStudyDistance(int32 Move)
{
    using namespace WardenRegent;
    switch(Move)
    {
        case Volley: return FVector(650,0,95);
        case Dash: return FVector(750,0,95);
        case Furrow: return FVector(600,0,95);
        case Rite: case Drift: return FVector(240,0,95);
        default: return FVector(290,0,95);
    }
}
void AWardenArenaMode::RegentStudyStep()
{
    using namespace WardenRegent;
    // Capture-only review: every Regent move once, in table order, against a stationary
    // player at its preferred distance, framed side-on by a fixed camera. Not a fight.
    auto& F=Warden->Fight;
    if(--RegentStudyWait>0 || RegentStudyMove>=End) return;
    if(!F.Alive() || F.Action!=EWardenAction::Ready) { RegentStudyWait=1; return; }
    const FVector At=WardenRegentStudyDistance(RegentStudyMove);
    Warden->SetActorLocation(FVector(0,0,128)); Warden->SetActorRotation(FRotator::ZeroRotator);
    Player->SetActorLocation(At); Player->SetActorRotation(FRotator(0,180,0));
    Player->Fight=FWardenFighterState(); Player->Fight.Health=Player->Fight.MaxHealth=100000;
    F.Stamina=100; F.Gap=0; for(int32& C:F.Cooldowns) C=0;
    Regent.Flying.Reset(); Regent.Hazards.Reset(); for(int32& G:Regent.Regrow) G=0;
    if(RegentStudyCamera.IsValid()) RegentStudyCamera->SetActorLocationAndRotation(FVector(At.X*.5f,-820,240),(FVector(At.X*.5f,0,120)-FVector(At.X*.5f,-820,240)).Rotation());
    if(Warden->BeginAction(EWardenAction::Strike,RegentStudyMove,FVector::ForwardVector))
    {
        AcceptedMove=RegentStudyMove; AcceptedTick=CombatTick;
        LastEvent=FString::Printf(TEXT("REGENT STUDY %d/%d | %s"),RegentStudyMove-First+1,Count,F.Definition().Name);
        if(RegentStudyMove==Pyre)
        {
            FRegentHazard Mark; Mark.Kind=ERegentHazard::Mark; Mark.Center=FVector(0,0,0); Mark.Radius=F.Definition().Radius;
            Mark.Start=Mark.Arm=CombatTick; Mark.End=CombatTick+F.Definition().Windup; Regent.Hazards.Add(Mark);
        }
        RegentStudyWait=F.Definition().Total()+30;
    }
    ++RegentStudyMove;
}

// ---- Presentation: reads the state above every rendered frame, never writes it. ----
void AWardenArenaMode::BuildRegentView()
{
    auto& V=RegentView;
    if(V.Owner.IsValid()) return;
    auto* Owner=GetWorld()->SpawnActor<AActor>();
    V.Owner=Owner;
    auto Load=[](const TCHAR* Path,const TCHAR* Fallback)
    {
        if(auto* M=LoadObject<UMaterialInterface>(nullptr,Path,nullptr,LOAD_Quiet|LOAD_NoWarn)) return M;
        return LoadObject<UMaterialInterface>(nullptr,*(FString(TEXT("/Game/BossLab/Materials/MI_"))+Fallback));
    };
    // Local props from ue_import_regent_props.py; engine primitives stand in when absent.
    auto Mesh=[&](const TCHAR* Prop,const TCHAR* Primitive,bool& Found)
    {
        UStaticMesh* M=LoadObject<UStaticMesh>(nullptr,*(FString(TEXT("/Game/BossLab/Regent/Props/"))+Prop),nullptr,LOAD_Quiet|LOAD_NoWarn);
        Found=M!=nullptr;
        return M ? M : LoadObject<UStaticMesh>(nullptr,Primitive);
    };
    auto Root=NewObject<USceneComponent>(Owner); Owner->SetRootComponent(Root); Root->RegisterComponent();
    auto Prepare=[&](UPrimitiveComponent* C)
    {
        C->SetupAttachment(Root); C->SetCollisionEnabled(ECollisionEnabled::NoCollision); C->SetCanEverAffectNavigation(false);
        C->SetCastShadow(false); C->RegisterComponent(); Owner->AddInstanceComponent(C);
    };
    auto Set=[&](UStaticMesh* M,UMaterialInterface* Material,int32 Count)
    {
        auto* C=NewObject<UInstancedStaticMeshComponent>(Owner);
        C->SetStaticMesh(M); if(Material) C->SetMaterial(0,Material);
        Prepare(C);
        TArray<FTransform> Hidden; Hidden.Init(FTransform(FRotator::ZeroRotator,FVector::ZeroVector,FVector::ZeroVector),Count);
        C->AddInstances(Hidden,false);
        return C;
    };
    bool Lantern=false, Link=false, Skull=false;
    V.Censer=Set(Mesh(TEXT("SM_RegentCenser"),TEXT("/Engine/BasicShapes/Sphere"),Lantern),Lantern?nullptr:Load(TEXT("none"),TEXT("Bronze")),1);
    V.bLantern=Lantern;
    V.Chain=Set(Mesh(TEXT("SM_RegentLink"),TEXT("/Engine/BasicShapes/Cube"),Link),Link?nullptr:Load(TEXT("none"),TEXT("BlackIron")),FWardenRegentView::Links);
    V.bLinks=Link;
    V.Bones=Set(Mesh(TEXT("SM_RegentSkull"),TEXT("/Engine/BasicShapes/Sphere"),Skull),Skull?nullptr:Load(TEXT("/Game/BossLab/Regent/M_RegentBone"),TEXT("Stone")),WardenRegent::Skulls);
    V.bSkull=Skull;
    V.Eyes=Set(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Sphere")),Load(TEXT("/Game/BossLab/Regent/Props/M_RegentLanternCore"),TEXT("Jade")),WardenRegent::Skulls*2);
    V.Fire=Set(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Plane")),Load(TEXT("/Game/BossLab/Regent/M_RegentFlame"),TEXT("Jade")),FWardenRegentView::Flames);
    V.Glint=Set(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Plane")),Load(TEXT("/Game/BossLab/Regent/Props/M_RegentLanternCore"),TEXT("Jade")),2);
    UMaterialInterface* Rune=Load(TEXT("/Game/BossLab/Regent/M_RegentRune"),TEXT("Jade"));
    for(int32 I=0;I<FWardenRegentView::Discs;++I)
    {
        auto* D=NewObject<UStaticMeshComponent>(Owner);
        D->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cylinder")));
        auto* M=UMaterialInstanceDynamic::Create(Rune,D); D->SetMaterial(0,M);
        Prepare(D); D->SetVisibility(false);
        V.Disc.Add(D); V.DiscMaterial.Add(M);
    }
    auto* Light=NewObject<UPointLightComponent>(Owner);
    Light->SetupAttachment(Root); Light->SetMobility(EComponentMobility::Movable);
    Light->SetIntensity(1600); Light->SetAttenuationRadius(420); Light->SetLightColor(FLinearColor(.3,.55,1));
    Light->SetCastShadows(false); Light->RegisterComponent(); Owner->AddInstanceComponent(Light);
    V.Glow=Light;
}
void AWardenArenaMode::AnimateRegentView(float Seconds)
{
    using namespace WardenRegent;
    auto& V=RegentView;
    if(!bRegent || !Warden || !V.Fire.IsValid()) return;
    const auto& F=Warden->Fight;
    const bool Striking=F.Action==EWardenAction::Strike && IsRegent(F.Move);
    const bool Gone=Striking && Vanished(F.Move,F.Age);
    Warden->SetActorHiddenInGame(Gone);
    const FVector BossAt=Warden->GetActorLocation();
    const int32 T=CombatTick;
    // Flame cards turn to face the camera, so they never show their flat edge.
    FVector Eye=BossAt+FVector(-600,0,200);
    if(auto* PC=GetWorld()->GetFirstPlayerController(); PC && PC->PlayerCameraManager) Eye=PC->PlayerCameraManager->GetCameraLocation();
    TArray<FTransform> Fire; Fire.Reserve(FWardenRegentView::Flames);
    auto Flame=[&](const FVector& Base,float Width,float Tall,int32 Seed)
    {
        if(Fire.Num()>=FWardenRegentView::Flames || Tall<1) return;
        const float Yaw=(Eye-Base).Rotation().Yaw-90+FMath::Sin(Seed*1.7f+Seconds*.5f)*8;
        Fire.Add(FTransform(FRotator(0,Yaw,90),Base+FVector(0,0,Tall*.5f),FVector(Width,Tall,100)/100));
    };
    auto Set=[](UInstancedStaticMeshComponent* C,int32 I,const FTransform& X) { C->UpdateInstanceTransform(I,X,true,false,true); };
    const FTransform Hidden(FRotator::ZeroRotator,BossAt,FVector::ZeroVector);

    // Censer and chain: the chain end follows the engine-owned path; the lantern hangs from
    // it along the chain, and the chain sags from the posed left hand when slack.
    const FVector Head=Warden->CenserWorld();
    const FVector Hand=Warden->VisualBody->GetBoneLocationByName(TEXT("hand_l"),EBoneSpaces::WorldSpace);
    const FVector Hang=(Head-Hand).GetSafeNormal();
    const FQuat Along=FQuat::FindBetweenNormals(-FVector::UpVector,Hang.IsNearlyZero()||Hang.Z>-.2f?FVector(Hang.X,Hang.Y,FMath::Min(Hang.Z,-.2f)).GetSafeNormal():Hang);
    const FVector Body=Head+Along.RotateVector(FVector(0,0,-18));
    const float LanternScale=2.4f;
    Set(V.Censer.Get(),0,Gone?Hidden:V.bLantern ? FTransform(Along*FQuat(FVector::UpVector,Seconds*.6f),Head,FVector(LanternScale))
                                               : FTransform(FRotator(0,Seconds*40,0),Head,FVector(.26f)));
    const bool Flaring=Striking && Kind(F.Move)==EKind::Censer && F.Age<F.Definition().Windup;
    if(!Gone) Flame(Body-FVector(0,0,8),Flaring?44:26,Flaring?110:50,7);
    const float Chord=FVector::Dist(Hand,Head), Length=440;
    const float Sag=FMath::Sqrt(FMath::Max(0.f,Length*Length-Chord*Chord))*.35f;
    auto At=[&](float U) { return FMath::Lerp(Hand,Head,U)-FVector(0,0,Sag*FMath::Sin(PI*U)); };
    const float LinkScale=2.2f, Pitch=6.4f;
    const int32 Needed=FMath::Clamp(FMath::CeilToInt((Chord+Sag*1.3f)/Pitch),2,FWardenRegentView::Links);
    for(int32 I=0;I<FWardenRegentView::Links;++I)
    {
        if(Gone || I>=Needed) { Set(V.Chain.Get(),I,Hidden); continue; }
        const float U=(I+.5f)/Needed;
        const FVector Dir=(At(U+.01f)-At(U-.01f)).GetSafeNormal();
        const FQuat Q=FQuat::FindBetweenNormals(FVector::UpVector,Dir.IsNearlyZero()?FVector::UpVector:Dir)*FQuat(FVector::UpVector,I%2?HALF_PI:0);
        Set(V.Chain.Get(),I,FTransform(Q,At(U),V.bLinks?FVector(LinkScale):FVector(.05f,.018f,FMath::Max(.06f,Chord/Needed/100*1.15f))));
    }
    if(auto* L=V.Glow.Get()) { L->SetWorldLocation(Body); L->SetVisibility(!Gone); L->SetIntensity((Flaring?3200:1600)*(1+.15f*FMath::Sin(Seconds*11)+.1f*FMath::Sin(Seconds*23))); }

    // Witness skulls: orbit while ready (bobbing, facing the player), fly as projectiles,
    // re-form over the last second of regrowth. Eyes burn brighter during the volley call.
    const bool Calling=Striking && F.Move==Volley && F.Age<F.Definition().Windup;
    const float SkullScale=V.bSkull?1.4f:.3f;
    for(int32 S=0;S<Skulls;++S)
    {
        FVector Pos=BossAt+SkullOrbit(S,T)+FVector(0,0,6*FMath::Sin(Seconds*2.1f+S*2));
        FVector Facing=(Player?Player->GetActorLocation()+FVector(0,0,60):Pos)-Pos;
        float Size=1-FMath::Clamp(Regent.Regrow[S]/60.f,0.f,1.f);
        for(const auto& K:Regent.Flying) if(K.Slot==S) { Pos=K.Position; Facing=K.Velocity; Size=1; }
        if(Gone && Regent.Regrow[S]==0) Size=0;
        const FQuat Look=Facing.Rotation().Quaternion();
        Set(V.Bones.Get(),S,FTransform(Look,Pos,FVector(SkullScale*Size)));
        for(int32 E=0;E<2;++E)
            Set(V.Eyes.Get(),S*2+E,FTransform(Look,Pos+Look.RotateVector(FVector(7.5f,E?3.f:-3.f,1)*SkullScale)*Size,FVector((Calling?.05f:.035f)*Size)));
        if(Size>.2f) Flame(Pos+FVector(0,0,10*SkullScale/1.4f),30*Size,(Calling?100:45)*Size,S+20);
    }

    // Blade glint: the classic tell, a star flash on the estoc point just before a thrust.
    int32 GlintAt=-1;
    if(Striking && (Kind(F.Move)==EKind::Blade || F.Move==AshStep))
    {
        const int32 Contact=F.Definition().Windup;
        const int32 Into=F.Age-(Contact-16);
        if(Into>=0 && Into<12) GlintAt=Into;
    }
    for(int32 K=0;K<2;++K)
    {
        if(GlintAt<0) { Set(V.Glint.Get(),K,Hidden); continue; }
        const FVector Tip=Warden->BladePoint(1);
        const float Pulse=FMath::Sin(PI*GlintAt/12.f);
        const FQuat Face=FRotationMatrix::MakeFromZ((Eye-Tip).GetSafeNormal()).ToQuat()*FQuat(FVector::UpVector,FMath::DegreesToRadians(45+90*K+GlintAt*4));
        Set(V.Glint.Get(),K,FTransform(Face,Tip,FVector(.6f*Pulse,.045f*Pulse,1)));
    }

    // Floor marks and fire: pools burn, furrow marks warm up then erupt, the ash-step
    // destination and the pyre blast radius are drawn before they resolve.
    int32 Used=0;
    auto Disc=[&](const FVector& Centre,float Radius,float Intensity,FLinearColor Tint)
    {
        if(Used>=V.Disc.Num()) return;
        auto* D=V.Disc[Used].Get(); auto* M=V.DiscMaterial[Used].Get(); ++Used;
        D->SetWorldLocationAndRotation(FVector(Centre.X,Centre.Y,1.5f),FRotator::ZeroRotator);
        D->SetWorldScale3D(FVector(Radius/50,Radius/50,.01f)); D->SetVisibility(true);
        M->SetScalarParameterValue(TEXT("Radius"),Radius); M->SetScalarParameterValue(TEXT("Intensity"),Intensity); M->SetVectorParameterValue(TEXT("Tint"),Tint);
    };
    for(int32 I=0;I<Regent.Hazards.Num();++I)
    {
        const auto& H=Regent.Hazards[I];
        const float Age=float(T-H.Start), Left=float(H.End-T);
        if(H.Kind==ERegentHazard::Pool)
        {
            // Smoulders (dim, low flames) until it ignites, then burns.
            const float Fade=FMath::Clamp(Left/30.f,0.f,1.f), Lit=T>=H.Arm ? 1.f : .35f;
            Disc(H.Center,H.Radius,.75f*Fade*Lit,FLinearColor(.12,.42,1));
            for(int32 K=0;K<9;++K)
            {
                const float A=K*2.4f+I, R=H.Radius*(.15f+.6f*FMath::Frac(K*.618f+I*.31f));
                Flame(H.Center+FVector(FMath::Cos(A)*R,FMath::Sin(A)*R,0),60+20*FMath::Frac(K*.37f),(80+45*FMath::Sin(Seconds*3+K))*Fade*Lit,I*11+K);
            }
        }
        else if(H.Kind==ERegentHazard::Eruption)
        {
            const float Warm=FMath::Clamp(Age/FurrowWarn,0.f,1.f);
            if(T<H.Arm) { Disc(H.Center,H.Radius,.25f+1.2f*Warm*Warm,FLinearColor(.35,.6,1)); Flame(H.Center,40,30*Warm,I*7); }
            else { Disc(H.Center,H.Radius,2.2f,FLinearColor(.4,.7,1)); for(int32 K=0;K<4;++K) Flame(H.Center+Ring(K*90.f+I*40,35,0),110,300*(1-FMath::Square((T-H.Arm)/float(FurrowBurst)-.3f)),I*7+K); }
        }
        else
        {
            // The pyre circle spans the whole duel, so it stays dim and brightens toward the blast.
            const float Pulse=.6f+.4f*FMath::Sin(Seconds*9), Build=FMath::Clamp(Age/(H.End-H.Start),0.f,1.f);
            const bool Wide=H.Radius>200;
            Disc(H.Center,H.Radius,Wide ? .08f+.22f*Build*Build+.05f*Pulse : .7f*Pulse+.5f*Build,Wide?FLinearColor(.4,.35,1):FLinearColor(.3,.6,1));
            if(!Wide) for(int32 K=0;K<4;++K) Flame(H.Center+Ring(K*90.f+Seconds*120,50,0),55,40+160*FMath::Clamp(Age/24.f,0.f,1.f),K+90);
        }
    }
    // Pyre blast ring and the phase-change burst.
    if(Striking && F.Move==Pyre && F.Age>=F.Definition().Windup && F.Age<F.Definition().Windup+16)
    {
        const float U=(F.Age-F.Definition().Windup)/16.f;
        for(int32 K=0;K<24;++K) Flame(FVector(BossAt.X,BossAt.Y,0)+Ring(K*15.f,F.Definition().Radius*(.3f+.7f*U),0),110,260*(1-U),K+200);
    }
    if(Striking && F.Move==Wakes)
    {
        // A low, uneven ring of soul fire spreading out, not a palisade of tall spikes.
        const float Swell=FMath::Sin(PI*FMath::Clamp(F.Age/100.f,0.f,1.f)), Spread=170+110*FMath::Clamp(F.Age/60.f,0.f,1.f);
        for(int32 K=0;K<18;++K)
        {
            const float Jitter=FMath::Frac(FMath::Sin(K*7.31f)*93.7f);
            Flame(FVector(BossAt.X,BossAt.Y,0)+Ring(K*20.f+Seconds*40,Spread*(.9f+.2f*Jitter),0),85+30*Jitter,(70+70*Jitter)*Swell*(.85f+.15f*FMath::Sin(Seconds*9+K)),K+300);
        }
    }
    for(int32 I=Used;I<V.Disc.Num();++I) if(auto* D=V.Disc[I].Get()) D->SetVisibility(false);
    while(Fire.Num()<FWardenRegentView::Flames) Fire.Add(Hidden);
    V.Fire->BatchUpdateInstancesTransforms(0,Fire,true,true);
    for(auto* C:{V.Censer.Get(),V.Chain.Get(),V.Bones.Get(),V.Eyes.Get(),V.Glint.Get()}) C->MarkRenderStateDirty();

    // Second phase: the hall's fire turns to soul fire (dungeon arena only).
    if(bDungeon && Regent.PhaseTwo!=V.bBlueHall)
    {
        V.bBlueHall=Regent.PhaseTwo;
        if(auto* Hall=Dungeon.Fire.Get())
            Hall->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,V.bBlueHall?TEXT("/Game/BossLab/Regent/M_RegentFlame"):TEXT("/Game/BossLab/Dungeon/M_DungeonFlame"),nullptr,LOAD_Quiet|LOAD_NoWarn));
        if(V.HallColors.IsEmpty())
            for(const auto& L:Dungeon.Lights) V.HallColors.Add(L.IsValid()?L->GetLightColor():FLinearColor::White);
        // The moonlight key stays; every fire light swaps to soul fire and back on reset.
        for(int32 I=0;I<Dungeon.Lights.Num();++I)
            if(auto* L=Dungeon.Lights[I].Get(); L && !L->IsA<USpotLightComponent>())
                L->SetLightColor(V.bBlueHall?FLinearColor(.32,.52,1):V.HallColors[I]);
    }
}
