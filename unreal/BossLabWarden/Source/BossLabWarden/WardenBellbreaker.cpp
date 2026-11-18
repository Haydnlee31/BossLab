#include "WardenBellbreaker.h"
#include "WardenPrototype.h"
#include "Animation/SkeletalMeshActor.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/CapsuleComponent.h"
#include "EngineUtils.h"
#include "Engine/CollisionProfile.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "GameFramework/PlayerController.h"
#include "Camera/PlayerCameraManager.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Sound/SoundBase.h"

// The Bellbreaker greybox (docs/BELLBREAKER_GREYBOX.md). Everything that decides damage, stun, timing
// and reach is in this file's engine-owned tables and the fixed step; the rigged model, clips, hammer,
// rings and sounds only present that state.
namespace
{
float Smooth(float T) { T=FMath::Clamp(T,0.f,1.f); return T*T*(3-2*T); }
// Overhead swing: a vertical arc about the right shoulder, bell 480 cm from the pivot.
const FVector OverPivot(0,40,340);
constexpr float OverRadius=480, OverTop=110, OverEnd=-38;
FVector OverArc(float Degrees) { const float A=FMath::DegreesToRadians(Degrees); return OverPivot+FVector(FMath::Cos(A)*OverRadius,0,FMath::Sin(A)*OverRadius); }
// Floor sweep: a horizontal arc 470 cm out, bell 70 cm off the floor, from his right round to his left.
constexpr float SweepRadius=470, SweepHeight=70, SweepFrom=135, SweepTo=-105;
FVector SweepArc(float Degrees) { const float A=FMath::DegreesToRadians(Degrees); return FVector(FMath::Cos(A)*SweepRadius,FMath::Sin(A)*SweepRadius,SweepHeight); }
// Carry: bell low ahead and to his right (the idle clip's diagonal hold, roughly).
const FVector Rest(150,120,40);
int32 Embed(int32 Move) { using namespace WardenBellbreaker; return Move==Quake ? 60 : Move==Sweep ? 18 : 40; }
}

const FWardenStrike& WardenBellbreaker::Strike(int32 Index)
{
    // Name, clip, bone, windup, active, recovery, (unused anim times), damage, radius (x Scale), advance,
    // stamina, stance. The Quake and the transition deal their damage through the blast and the
    // shockwave in BellbreakerResolve, so their swept damage is zero.
    static const FWardenStrike Moves[Count]={
        {TEXT("HAMMER FALL"),TEXT("BBHammerFall"),TEXT("hand_r"),54,6,70,0,0,1,34,26,60,0,1},
        {TEXT("FORGE SWEEP"),TEXT("BBSweep"),TEXT("hand_r"),46,10,52,0,0,1,28,26,40,0,1},
        {TEXT("BELL QUAKE"),TEXT("BBQuake"),TEXT("hand_r"),70,4,80,0,0,1,0,0,0,0,1},
        {TEXT("THE BELL BREAKS"),TEXT("BBBreak"),TEXT("hand_r"),60,4,56,0,0,1,0,0,0,0,1}};
    check(IsBellbreaker(Index));
    return Moves[Index-First];
}
FVector WardenBellbreaker::BellOffset(int32 Move,int32 Age,bool Striking) { return BellOffsetAt(Move,float(Age),Striking); }
FVector WardenBellbreaker::BellOffsetAt(int32 Move,float Age,bool Striking)
{
    if(!Striking || !IsBellbreaker(Move)) return Rest;
    const auto& D=Strike(Move);
    const float T=Age;
    if(Move==Sweep)
    {
        if(T<D.Windup) return FMath::Lerp(Rest,SweepArc(SweepFrom),Smooth(T/(D.Windup*.85f)));
        if(T<D.Windup+D.Active) return SweepArc(FMath::Lerp(SweepFrom,SweepTo,(T-D.Windup+1)/D.Active));
        const float R=T-D.Windup-D.Active;
        return FMath::Lerp(SweepArc(SweepTo),Rest,Smooth((R-Embed(Move))/FMath::Max(1.f,D.Recovery-Embed(Move))));
    }
    // Hammer Fall, Bell Quake and the transition share the overhead arc.
    if(T<D.Windup) return FMath::Lerp(Rest,OverArc(OverTop),Smooth(T/(D.Windup*.8f)));
    if(T<D.Windup+D.Active) return OverArc(FMath::Lerp(OverTop,OverEnd,(T-D.Windup+1)/D.Active));
    const float R=T-D.Windup-D.Active;
    return FMath::Lerp(OverArc(OverEnd),Rest,Smooth((R-Embed(Move))/FMath::Max(1.f,D.Recovery-Embed(Move))));
}
FVector WardenBellbreaker::GripOffset(int32 Move,int32 Age,bool Striking)
{
    const FVector Bell=BellOffset(Move,Age,Striking);
    const FVector Pivot=Striking && Move==Sweep ? FVector(0,0,200) : OverPivot;
    const FVector Out=Bell-Pivot;
    return Pivot+Out.GetSafeNormal()*FMath::Max(50.f,Out.Size()-BellReach);
}
FVector WardenBellbreaker::QuakeImpactOffset() { const FVector E=OverArc(OverEnd); return FVector(E.X,E.Y,0); }
FVector2D WardenBellbreaker::Band(int32 Move)
{
    switch(Move)
    {
        case HammerFall: return FVector2D(0,420);
        case Sweep: return FVector2D(0,440);
        case Quake: return FVector2D(0,700);
        default: return FVector2D(0,100000);
    }
}
int32 WardenBellbreaker::Pause(int32 Move)
{
    switch(Move)
    {
        case HammerFall: case Quake: return 40;   // the bell is embedded: main punish windows
        case Sweep: return 24;
        default: return 20;
    }
}

// Engine-owned hammer sweep: five samples from the grip to the bell (WardenChallenger::ResolveStrike).
FVector AWardenChallenger::BellbreakerHitPoint(int32 Sample) const
{
    const bool Striking=Fight.Action==EWardenAction::Strike;
    const FVector G=WardenBellbreaker::GripOffset(Fight.Move,Fight.Age,Striking), B=WardenBellbreaker::BellOffset(Fight.Move,Fight.Age,Striking);
    const FVector Floor(GetActorLocation().X,GetActorLocation().Y,0);
    return Floor+FRotator(0,GetActorRotation().Yaw,0).RotateVector(FMath::Lerp(G,B,Sample/4.f));
}

void AWardenArenaMode::EnableBellbreaker()
{
    bBellbreaker=true;
    if(!Warden) return;
    Warden->bBellbreaker=true;
    Warden->SetActorScale3D(FVector(WardenBellbreaker::Scale));
    // His torso is ~1.2 m across at scale; the default capsule (34 cm x 2.55 = 87 cm) let the player
    // stand inside his apron. 48 x 2.55 = 122 cm. Half-height unchanged (StandZ convention).
    Warden->Capsule->SetCapsuleRadius(WardenBellbreaker::CapsuleRadius);
    Warden->SetActorLocation(FVector(Warden->GetActorLocation().X,Warden->GetActorLocation().Y,WardenBellbreaker::StandZ));
    Warden->SetActorHiddenInGame(true);   // the rigged model below is his body
    Bellbreaker=FWardenBellbreakerState();
    BuildBellbreakerView();
}
void AWardenArenaMode::BellbreakerDecide(FVector& BossDirection)
{
    using namespace WardenBellbreaker;
    auto& R=Bellbreaker; auto& F=Warden->Fight;
    const FVector ToPlayer=Player->GetActorLocation()-Warden->GetActorLocation();
    const float Distance=ToPlayer.Size2D();
    if(F.Action==EWardenAction::Strike && IsBellbreaker(F.Move))
    {
        // Track until shortly before contact, then the aim locks so a late roll or sidestep beats it.
        if(F.Age<F.Definition().Windup-14) Warden->CommittedDirection=ToPlayer.GetSafeNormal2D();
        return;
    }
    if(!F.Ready()) return;
    auto Commit=[&](int32 Move)
    {
        if(!Warden->BeginAction(EWardenAction::Strike,Move,ToPlayer)) return false;
        AcceptedMove=Move; AcceptedTick=CombatTick;
        LastEvent=FString(F.Definition().Name)+(Move==Quake ? TEXT(" | Jump or roll the shockwave.") : TEXT(" | Aim committed."));
        return true;
    };
    if(!R.PhaseTwo && F.Health<=PhaseTwoHealth) { Commit(BellBreaks); return; }
    // Fixed rehearsal sequence, labelled as such: no learning and no input reading. Each step walks into
    // its band and commits, or is skipped after four seconds.
    static const int32 One[]={HammerFall,Sweep,Quake,Sweep,HammerFall,Quake};
    static const int32 Two[]={Quake,HammerFall,Sweep,Quake,Sweep,HammerFall};
    const int32 Next=R.PhaseTwo ? Two[R.Step%UE_ARRAY_COUNT(Two)] : One[R.Step%UE_ARRAY_COUNT(One)];
    const FVector2D B=Band(Next);
    if(Distance>B.Y) BossDirection=ToPlayer.GetSafeNormal2D();
    if(R.Waiting>0) { --R.Waiting; return; }
    if(Distance>B.Y) { if(++R.Seeking>240) { ++R.Step; R.Seeking=0; } return; }
    if(Commit(Next)) { ++R.Step; R.Seeking=0; R.Waiting=R.PhaseTwo ? Pause(Next)*3/5 : Pause(Next); }
}
void AWardenArenaMode::BellbreakerSound(const TCHAR* Name,const FVector& At,float Volume)
{
    if(GIsAutomationTesting) return;
    if(USoundBase* const* S=BellbreakerSounds.Find(Name)) if(*S) UGameplayStatics::PlaySoundAtLocation(GetWorld(),*S,At,Volume*FMath::Max(.05f,Settings.SfxVolume));
}
void AWardenArenaMode::BellbreakerResolve()
{
    using namespace WardenBellbreaker;
    auto& R=Bellbreaker; auto& F=Warden->Fight;
    const int32 T=CombatTick;
    const FVector BossAt=Warden->GetActorLocation();
    const FRotator Yaw(0,Warden->GetActorRotation().Yaw,0);
    const FVector Floor(BossAt.X,BossAt.Y,0);
    auto& P=Player->Fight;
    auto Flinched=[&](const FVector& From)
    {
        Player->HitFlash=.18f; Player->PlayCue(1);
        Player->ImpactDir=(Player->GetActorLocation()-From).GetSafeNormal2D();
        Player->BleedAt=Player->GetActorLocation()+FVector(0,0,35); Player->BleedDir=Player->ImpactDir; ++Player->BleedCount;
    };
    auto DropInput=[&]() { Player->PendingAction=EWardenAction::Ready; Player->PendingAge=0; Player->PendingHeld=0; Player->FollowAction=EWardenAction::Ready; };
    if(F.Action==EWardenAction::Strike && IsBellbreaker(F.Move))
    {
        const auto& D=F.Definition();
        const int32 A=F.Age, Since=A-D.Windup;
        const FVector Bell=Floor+Yaw.RotateVector(BellOffset(F.Move,A,true));
        // Sound: one cue per readable beat (presentation only).
        if(A==1 && F.Move!=Sweep) BellbreakerSound(F.Move==BellBreaks ? TEXT("bell_crack_v1") : TEXT("clapper_tell_v0"),Bell,.8f);
        if(Since==-8) BellbreakerSound(TEXT("bell_whoosh_v0"),Bell,.8f);
        if(F.Move==HammerFall && Since==D.Active-1) { BellbreakerSound(TEXT("bell_slam_ground_v1"),Bell,.9f); Impact(3,.5f); }
        if((F.Move==Quake || F.Move==BellBreaks) && Since==0)
        {
            // Impact: the blast, then the shockwave crest(s) from where the bell lands.
            const FVector Centre=Floor+Yaw.RotateVector(QuakeImpactOffset());
            BellbreakerSound(F.Move==Quake ? TEXT("bell_slam_ground_v0") : TEXT("bell_crack_v0"),Centre,1.f);
            BellbreakerSound(TEXT("shockwave_v0"),Centre,.9f);
            Impact(5,1.f);
            const float Reach=F.Move==Quake ? BlastRadius : 400.f;
            bool Blasted=false;
            if(P.Alive() && FVector::Dist2D(Player->GetActorLocation(),Centre)<=Reach)
            {
                const float Before=P.Health;
                if(P.Damage(BlastDamage,true))
                {
                    Blasted=true; BossDamage+=Before-P.Health; Flinched(Centre);
                    if(F.Move==Quake && P.Stun(BlastStun,true)) { ++R.Stuns; DropInput(); BellbreakerSound(TEXT("stun_ring_v0"),Player->GetActorLocation(),.7f); }
                    R.LastOutcome=EBellbreakerOutcome::Blasted;
                    LastEvent=F.Move==Quake ? TEXT("BELL QUAKE | Caught in the blast: knocked down.") : TEXT("THE BELL BREAKS | Caught in the blast.");
                }
            }
            if(F.Move==Quake)
            {
                FBellbreakerWave Wave; Wave.Center=Centre; Wave.Start=T; Wave.PlayerResolved=Blasted; R.Waves.Add(Wave);
                // Twin Quake (phase two): a second crest a beat behind the first.
                if(R.PhaseTwo) { Wave.Start=T+TwinDelay; Wave.PlayerResolved=false; R.Waves.Add(Wave); }
            }
            else { R.PhaseTwo=true; LastEvent=TEXT("THE BELL BREAKS | Second phase: every Quake now sends two crests."); }
        }
    }
    // Hammer blows that landed this step (ResolveStrike ran first): a bronze thud on the player.
    if(F.Action==EWardenAction::Strike && IsBellbreaker(F.Move) && F.HitConsumed && P.Action==EWardenAction::Hurt && P.Age==0 && !P.Stunned())
        BellbreakerSound(TEXT("bell_hit_body_v0"),Player->GetActorLocation(),.9f);
    // Shockwave crests: a player the crest passes over is stunned unless airborne or inside roll i-frames
    // for every tick of the crossing.
    for(auto& W:R.Waves)
    {
        if(W.PlayerResolved || T<W.Start || !W.Live(T) || !P.Alive()) continue;
        const float R0=WaveRadius(FMath::Max(0,T-1-W.Start)), R1=WaveRadius(T-W.Start);
        const float Dist=FVector::Dist2D(Player->GetActorLocation(),W.Center);
        if(Dist+CrestHalfWidth<R0 || Dist-CrestHalfWidth>R1) continue;   // the crest is not over the player this tick
        if(Player->AirLift>AirborneLift) { R.LastOutcome=EBellbreakerOutcome::Jumped; continue; }
        if(P.Invulnerable()) { R.LastOutcome=EBellbreakerOutcome::Rolled; continue; }
        W.PlayerResolved=true;
        const float Before=P.Health;
        P.Damage(WaveDamage,false);
        BossDamage+=Before-P.Health;
        if(P.Stun(WaveStun))
        {
            ++R.Stuns; DropInput(); Flinched(W.Center);
            R.LastOutcome=EBellbreakerOutcome::Stunned;
            BellbreakerSound(TEXT("stun_ring_v1"),Player->GetActorLocation(),.8f);
            LastEvent=TEXT("STUNNED | The shockwave caught you on the ground. Jump or roll it.");
        }
        else LastEvent=TEXT("The shockwave hit you, but you are still shaking off the last stun.");
    }
    // Count clean avoidances once the crest has fully passed the player.
    for(auto& W:R.Waves)
        if(!W.PlayerResolved && T>W.Start && FVector::Dist2D(Player->GetActorLocation(),W.Center)+CrestHalfWidth<WaveRadius(T-W.Start)
           && FVector::Dist2D(Player->GetActorLocation(),W.Center)+CrestHalfWidth>=WaveRadius(T-1-W.Start))
        {
            W.PlayerResolved=true; ++R.Avoided;
            if(R.LastOutcome!=EBellbreakerOutcome::Jumped && R.LastOutcome!=EBellbreakerOutcome::Rolled) R.LastOutcome=EBellbreakerOutcome::OutOfReach;
        }
    R.Waves.RemoveAll([&](const FBellbreakerWave& W){ return T>=W.Start && !W.Live(T); });
}

// ---------------------------------------------------------------- presentation (no rules below)
namespace
{
struct FBBClip { int32 Move; const TCHAR* Clip; float Impact; };
const FBBClip StrikeClips[]={
    {WardenBellbreaker::HammerFall,TEXT("hammer_overhead_s0"),1.05f},
    {WardenBellbreaker::Sweep,TEXT("sweep_rl_s1"),.6f},   // s0 sprawled almost flat (2026-11-18 study)
    {WardenBellbreaker::Quake,TEXT("bell_quake_s0"),1.18f},
    {WardenBellbreaker::BellBreaks,TEXT("hammer_overhead_s1"),1.05f}};
UAnimSequence* BBClip(const TCHAR* Name)
{
    return LoadObject<UAnimSequence>(nullptr,*FString::Printf(TEXT("/Game/BossLab/Bellbreaker/Anim/BB_HY_Anims_root_HY_%s"),Name),nullptr,LOAD_Quiet|LOAD_NoWarn);
}
}
void WardenNeverCollide(AActor* A)
{
    if(!A) return;
    A->SetActorEnableCollision(false);
    TInlineComponentArray<UPrimitiveComponent*> Prims(A);
    for(UPrimitiveComponent* P:Prims)
    {
        P->SetCollisionProfileName(UCollisionProfile::NoCollision_ProfileName);
        P->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        P->SetCollisionResponseToAllChannels(ECR_Ignore);
        P->SetGenerateOverlapEvents(false); P->SetCanEverAffectNavigation(false);
    }
    // Fighters ignore it when sweeping, whatever its settings become.
    if(UWorld* W=A->GetWorld())
        for(TActorIterator<AWardenChallenger> It(W);It;++It) if(It->Capsule) It->Capsule->IgnoreActorWhenMoving(A,true);
}
void AWardenArenaMode::BuildBellbreakerView()
{
    UWorld* W=GetWorld();
    if(!W || BellbreakerView.IsValid()) return;
    auto* Rig=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/BossLab/Bellbreaker/Rig/SKM_BellbreakerRig"),nullptr,LOAD_Quiet|LOAD_NoWarn);
    if(!Rig) { UE_LOG(LogTemp,Warning,TEXT("BOSSLAB BELLBREAKER rig missing: run ue_import_bellbreaker_rig.py; the capsule fights unseen.")); Warden->SetActorHiddenInGame(false); return; }
    FActorSpawnParameters Params; Params.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    auto* View=W->SpawnActor<ASkeletalMeshActor>(Warden->GetActorLocation(),FRotator::ZeroRotator,Params);
    View->SetActorScale3D(FVector(WardenBellbreaker::Scale));
    // The skeletal mesh component is only the clip sampler (hidden); the rendered body is a poseable copy
    // that receives the corrected pose (crossfades, torso push-out, left-hand IK, floor lift) each frame.
    auto* C=View->GetSkeletalMeshComponent();
    C->SetMobility(EComponentMobility::Movable); C->SetSkeletalMesh(Rig); C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    C->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    C->SetVisibility(false,false); C->SetCastShadow(false);
    auto* Body=NewObject<UPoseableMeshComponent>(View,TEXT("BellbreakerBody"));
    Body->SetSkinnedAssetAndUpdate(Rig); Body->SetupAttachment(C); Body->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Body->RegisterComponent(); View->AddInstanceComponent(Body);
    BBView=FWardenBellbreakerView(); BBView.Body=Body;
    BellbreakerView=View;
    WardenNeverCollide(View);
    // The hammer is solved in world space every frame (AnimateBellbreakerView), not glued to the fist.
    if(auto* HammerMesh=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/BossLab/Bellbreaker/SM_BellHammerGen"),nullptr,LOAD_Quiet|LOAD_NoWarn))
    {
        auto* H=NewObject<UStaticMeshComponent>(View,TEXT("BellbreakerHammer"));
        H->SetStaticMesh(HammerMesh); H->SetCollisionEnabled(ECollisionEnabled::NoCollision); H->SetMobility(EComponentMobility::Movable);
        H->SetupAttachment(C); H->RegisterComponent(); H->SetUsingAbsoluteScale(true); H->SetWorldScale3D(FVector(1));
        View->AddInstanceComponent(H); BellbreakerHammer=H;
    }
    auto* Plane=LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Plane"),nullptr,LOAD_Quiet|LOAD_NoWarn);
    if(auto* SparkMat=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/BossLab/Regent/M_RegentSpark"),nullptr,LOAD_Quiet|LOAD_NoWarn); SparkMat && Plane)
    {
        auto* S=NewObject<UInstancedStaticMeshComponent>(View,TEXT("BellbreakerSparks"));
        S->SetStaticMesh(Plane); S->SetMaterial(0,SparkMat); S->SetCollisionEnabled(ECollisionEnabled::NoCollision); S->SetCastShadow(false);
        S->SetupAttachment(C); S->RegisterComponent(); S->SetUsingAbsoluteLocation(true); S->SetUsingAbsoluteRotation(true); S->SetUsingAbsoluteScale(true);
        S->SetWorldTransform(FTransform::Identity); View->AddInstanceComponent(S);
        for(int32 I=0;I<FWardenBellbreakerView::MaxSparks;++I) S->AddInstance(FTransform(FQuat::Identity,FVector(0,0,-10000),FVector(0)),true);
        BBView.Sparks=S;
    }
    for(const TCHAR* N:{TEXT("idle_hammer_s0"),TEXT("walk_hammer_s0"),TEXT("stagger_s0"),TEXT("death_s0"),TEXT("hammer_overhead_s0"),TEXT("sweep_rl_s1"),TEXT("bell_quake_s0"),TEXT("hammer_overhead_s1")})
        if(UAnimSequence* A=BBClip(N)) { BellbreakerClips.Add(N,A); SfxKeepAlive.Add(A); }
    for(const TCHAR* N:{TEXT("clapper_tell_v0"),TEXT("bell_whoosh_v0"),TEXT("bell_scrape_v0"),TEXT("bell_scrape_v1"),TEXT("bell_slam_ground_v0"),TEXT("bell_slam_ground_v1"),TEXT("shockwave_v0"),
                        TEXT("bell_crack_v0"),TEXT("bell_crack_v1"),TEXT("stun_ring_v0"),TEXT("stun_ring_v1"),TEXT("bell_hit_body_v0"),TEXT("bell_hit_anvil_v0"),TEXT("bell_hit_anvil_v1")})
        if(USoundBase* S=LoadObject<USoundBase>(nullptr,*FString::Printf(TEXT("/Game/BossLab/Bellbreaker/Sound/S_%s"),N),nullptr,LOAD_Quiet|LOAD_NoWarn)) { BellbreakerSounds.Add(N,S); SfxKeepAlive.Add(S); }
    auto* RingMat=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/BossLab/Bellbreaker/FX/M_BB_Shockwave"),nullptr,LOAD_Quiet|LOAD_NoWarn);
    for(int32 I=0;I<2 && Plane && RingMat;++I)
    {
        auto* RingActor=W->SpawnActor<AStaticMeshActor>(FVector::ZeroVector,FRotator::ZeroRotator,Params);
        RingActor->SetMobility(EComponentMobility::Movable);
        auto* R=RingActor->GetStaticMeshComponent(); R->SetStaticMesh(Plane); R->SetCastShadow(false);
        // Owner log 2026-11-18: the player's capsule started 1 cm inside "StaticMeshActor_68" (top at 6 cm, normal
        // up) after a stun, so every walk and roll was refused, and it survived a restart. These floor planes are
        // that height. Presentation actors never collide, by every switch, and the fighters ignore them outright.
        WardenNeverCollide(RingActor);
        auto* Mid=UMaterialInstanceDynamic::Create(RingMat,RingActor); R->SetMaterial(0,Mid); R->SetVisibility(false);
        BellbreakerRings.Add(R); BellbreakerRingMids.Add(Mid);
    }
    WardenNeverCollide(View);   // again: hammer and sparks were added after the first call
    for(auto& R:BellbreakerRings) if(R.IsValid()) WardenNeverCollide(R->GetOwner());
    for(auto& R:BellbreakerRings) if(R.IsValid()) UE_LOG(LogTemp,Display,TEXT("BOSSLAB BELLBREAKER ring actor %s (never collides)"),*R->GetOwner()->GetName());
    UE_LOG(LogTemp,Display,TEXT("BOSSLAB BELLBREAKER greybox view: clips %d/8, sounds %d/14, rings %d, hammer %d, sparks %d"),BellbreakerClips.Num(),BellbreakerSounds.Num(),BellbreakerRings.Num(),BellbreakerHammer.IsValid(),BBView.Sparks.IsValid());
}

namespace
{
// Presentation constants, world cm unless noted. Mannequin-space (component) values are divided by Scale.
constexpr float BellRim=60;            // bell mouth radius (SM_BellHammerGen is 1.2 m across)
constexpr float BellLength=105;        // mouth to the crown along the haft
constexpr float BodyRadius=92;        // the giant's torso/legs as a vertical capsule around his root
constexpr float LeftOnHaft=70;         // left hand this far down the haft from the right hand
constexpr float TorsoHand=27, TorsoElbow=23;   // mannequin cm: hands/elbows kept outside the torso axis
}
void AWardenArenaMode::AnimateBellbreakerView(float Seconds)
{
    using namespace WardenBellbreaker;
    ASkeletalMeshActor* View=BellbreakerView.Get();
    UPoseableMeshComponent* Body=BBView.Body.Get();
    if(!View || !Warden || !Body) return;
    auto& V=BBView;
    const float Dt=V.LastTime<0 ? 0.f : FMath::Clamp(Seconds-V.LastTime,0.f,.1f); V.LastTime=Seconds;
    const FVector At=Warden->GetActorLocation();
    const FVector Floor(At.X,At.Y,0);
    View->SetActorLocationAndRotation(FVector(At.X,At.Y,At.Z-90*Scale),FRotator(0,Warden->GetActorRotation().Yaw-90,0));   // rig faces +Y
    const FRotator Yaw(0,Warden->GetActorRotation().Yaw,0);
    const auto& F=Warden->Fight;
    const bool Striking=F.Alive() && F.Action==EWardenAction::Strike && IsBellbreaker(F.Move);
    const float AgeF=F.Age+FMath::Clamp(CombatAccumulator/WardenRules::Step,0.,1.);

    // ---- 1. Clip and clock (unchanged choice; time-warped strikes) -------------------------------------
    UAnimSequence* Clip=nullptr; float Clock=0;
    auto Get=[&](const TCHAR* N){ UAnimSequence* const* A=BellbreakerClips.Find(N); return A ? *A : nullptr; };
    if(!F.Alive())
    {
        Clip=Get(TEXT("death_s0"));
        if(Clip) Clock=FMath::Min(Warden->DeathAge/72.f,1.f)*Clip->GetPlayLength()*.97f;
    }
    else if(Striking)
    {
        const FBBClip* Entry=nullptr;
        for(const auto& E:StrikeClips) if(E.Move==F.Move) Entry=&E;
        Clip=Entry ? Get(Entry->Clip) : nullptr;
        if(Clip)
        {
            const auto& D=F.Definition();
            const float Len=Clip->GetPlayLength(), Ti=FMath::Min(Entry->Impact,Len-.2f);
            Clock=AgeF<D.Windup ? Ti*AgeF/D.Windup
                : AgeF<D.Windup+D.Active ? Ti+.1f*(AgeF-D.Windup)/D.Active
                : FMath::Lerp(Ti+.1f,Len*.98f,FMath::Clamp((AgeF-D.Windup-D.Active)/D.Recovery,0.f,1.f));
        }
    }
    else if(F.Action==EWardenAction::Hurt)
    {
        Clip=Get(TEXT("stagger_s0"));
        if(Clip) Clock=FMath::Lerp(.05f,Clip->GetPlayLength()*.85f,FMath::Clamp(AgeF/WardenRules::BossHurtTicks,0.f,1.f));
    }
    else
    {
        const float Speed=Warden->MoveVelocity.Size2D();
        Clip=Get(Speed>40 ? TEXT("walk_hammer_s0") : TEXT("idle_hammer_s0"));
        if(Clip) Clock=FMath::Fmod(Seconds*(Speed>40 ? FMath::Clamp(Speed/300.f,.5f,1.4f) : 1.f),Clip->GetPlayLength());
    }
    auto* C=View->GetSkeletalMeshComponent();
    if(!Clip || !C->GetSkeletalMeshAsset()) return;
    if(V.LastClip.Get()!=Clip)
    {
        // Crossfade from the pose last shown (after corrections) instead of popping to the new clip.
        if(V.LastClip.IsValid() && Body->BoneSpaceTransforms.Num()) { V.Frozen=Body->BoneSpaceTransforms; V.BlendFrom=Seconds; }
        V.LastClip=Clip; C->PlayAnimation(Clip,false);
    }
    if(auto* N=C->GetSingleNodeInstance()) { N->SetPlayRate(0); N->SetPosition(FMath::Clamp(Clock,0.f,Clip->GetPlayLength()-.01f),false); }
    C->TickAnimation(0,false); C->RefreshBoneTransforms();
    TArray<FTransform> Local=C->GetBoneSpaceTransforms();
    const auto& Ref=C->GetSkeletalMeshAsset()->GetRefSkeleton();
    if(Local.Num()!=Ref.GetNum()) return;
    // A heavy stance under the Sweep: the HY sweep takes spin and splay the whole body (a lunge for a 1.8 m
    // figure, flailing at 4.6 m). Legs, hips and spine are layered over his planted idle stance; arms keep
    // the full clip (the hammer solver and IK run on top).
    if(V.Stance.Num()!=Local.Num())
        if(UAnimSequence* Idle=Get(TEXT("idle_hammer_s0")))
        {
            C->PlayAnimation(Idle,false);
            if(auto* N=C->GetSingleNodeInstance()) { N->SetPlayRate(0); N->SetPosition(0,false); }
            C->TickAnimation(0,false); C->RefreshBoneTransforms(); V.Stance=C->GetBoneSpaceTransforms();
            C->PlayAnimation(Clip,false);
            if(auto* N=C->GetSingleNodeInstance()) { N->SetPlayRate(0); N->SetPosition(FMath::Clamp(Clock,0.f,Clip->GetPlayLength()-.01f),false); }
            C->TickAnimation(0,false); C->RefreshBoneTransforms(); Local=C->GetBoneSpaceTransforms();
        }
    if(Striking && F.Move==Sweep && V.Stance.Num()==Local.Num())
        for(int32 I=0;I<Local.Num();++I)
        {
            const FString N=Ref.GetBoneName(I).ToString();
            const float W=N.StartsWith(TEXT("thigh"))||N.StartsWith(TEXT("calf"))||N.StartsWith(TEXT("foot"))||N.StartsWith(TEXT("ball")) ? .35f
                : N==TEXT("pelvis") ? .45f : N.StartsWith(TEXT("spine")) ? .6f : 1.f;
            if(W<1) { FTransform B; B.Blend(V.Stance[I],Local[I],W); Local[I]=B; }
        }
    const float Fade=FMath::Clamp((Seconds-V.BlendFrom)/(F.Alive() ? .2f : .3f),0.f,1.f);
    if(Fade<1 && V.Frozen.Num()==Local.Num())
    {
        const float A=Smooth(Fade);
        for(int32 I=0;I<Local.Num();++I) { FTransform B; B.Blend(V.Frozen[I],Local[I],A); Local[I]=B; }
    }

    // Neck and head stay within a believable range of rest: the HY clips throw the head back and to the side
    // (made for a mannequin looking around), which on this thick-necked giant read as a squashed, unhinged head
    // (owner photo 2026-11-18). Caps per joint: neck 14 degrees each, head 22.
    for(const auto& Cap:{TPair<const TCHAR*,float>(TEXT("neck_01"),14.f),TPair<const TCHAR*,float>(TEXT("neck_02"),14.f),TPair<const TCHAR*,float>(TEXT("head"),22.f)})
        if(const int32 I=Ref.FindBoneIndex(Cap.Key); I>=0)
        {
            const FQuat RestQ=Ref.GetRefBonePose()[I].GetRotation(), Q=Local[I].GetRotation();
            const FQuat Delta=(RestQ.Inverse()*Q).GetNormalized();
            const float Angle=Delta.GetAngle(), Max=FMath::DegreesToRadians(Cap.Value);
            if(Angle>Max) Local[I].SetRotation(RestQ*FQuat::Slerp(FQuat::Identity,Delta,Max/Angle));
        }
    // ---- 2. Component-space helpers (mannequin units; the actor scale makes them giant) ------------------
    TArray<FTransform> CS; CS.SetNum(Local.Num());
    auto Build=[&](){ for(int32 I=0;I<Local.Num();++I){ const int32 P=Ref.GetParentIndex(I); CS[I]=P<0 ? Local[I] : Local[I]*CS[P]; } };
    Build();
    // A giant does not leave the ground: the HY clips' hops (made for a 1.8 m figure) became ~1 m leaps at
    // 2.55x. Whenever both feet are off the floor the pelvis comes down by the gap, so the lowest foot stays
    // planted (stepping still lifts one foot). Crouches are untouched.
    if(const int32 Hip=Ref.FindBoneIndex(TEXT("pelvis")); Hip>=0)
    {
        float Air=1e9f;
        for(const TCHAR* N:{TEXT("ball_l"),TEXT("ball_r")}) if(const int32 I=Ref.FindBoneIndex(N); I>=0) Air=FMath::Min(Air,CS[I].GetLocation().Z-2.5f);
        for(const TCHAR* N:{TEXT("foot_l"),TEXT("foot_r")}) if(const int32 I=Ref.FindBoneIndex(N); I>=0) Air=FMath::Min(Air,CS[I].GetLocation().Z-8.f);
        if(Air>0 && Air<1e8f)
        {
            const int32 P=Ref.GetParentIndex(Hip);
            const FVector Down=FVector(0,0,-Air);
            Local[Hip].AddToTranslation(P>=0 ? CS[P].GetRotation().Inverse().RotateVector(Down) : Down);
            Build();
        }
    }
    auto Idx=[&](const TCHAR* N){ return Ref.FindBoneIndex(N); };
    auto RotateCS=[&](int32 I,const FQuat& Q)
    {
        const int32 P=Ref.GetParentIndex(I);
        const FQuat Parent=P<0 ? FQuat::Identity : CS[P].GetRotation();
        Local[I].SetRotation((Parent.Inverse()*(Q*CS[I].GetRotation())).GetNormalized());
        Build();
    };
    auto TwoBone=[&](int32 A,int32 B,int32 E,FVector Target,FVector Pole,float W)
    {
        if(A<0||B<0||E<0||W<=0) return;
        const FVector Root=CS[A].GetLocation();
        const float L1=FVector::Dist(Root,CS[B].GetLocation()), L2=FVector::Dist(CS[B].GetLocation(),CS[E].GetLocation());
        const FVector T=FMath::Lerp(CS[E].GetLocation(),Target,W);
        const FVector Aim=(T-Root).GetSafeNormal();
        const float D=FMath::Clamp(FVector::Dist(Root,T),FMath::Abs(L1-L2)+.1f,L1+L2-.1f);
        const float X=(L1*L1-L2*L2+D*D)/(2*D), H=FMath::Sqrt(FMath::Max(0.f,L1*L1-X*X));
        FVector Side=FVector::VectorPlaneProject(Pole-Root,Aim).GetSafeNormal(); if(Side.IsNearlyZero()) Side=FVector::UpVector;
        const FVector Elbow=Root+Aim*X+Side*H;
        RotateCS(A,FQuat::FindBetweenNormals((CS[B].GetLocation()-Root).GetSafeNormal(),(Elbow-Root).GetSafeNormal()));
        RotateCS(B,FQuat::FindBetweenNormals((CS[E].GetLocation()-CS[B].GetLocation()).GetSafeNormal(),(Root+Aim*D-CS[B].GetLocation()).GetSafeNormal()));
    };
    const int32 Pelvis=Idx(TEXT("pelvis")), Chest=Idx(TEXT("spine_05")) >= 0 ? Idx(TEXT("spine_05")) : Idx(TEXT("spine_03"));
    // Distance from a point to the torso axis (pelvis -> chest) and the outward direction, mannequin space.
    auto TorsoOut=[&](const FVector& P,float& Dist)
    {
        const FVector A=CS[Pelvis].GetLocation(), B=CS[Chest].GetLocation()+(CS[Chest].GetLocation()-A)*.15f;
        const FVector Q=FMath::ClosestPointOnSegment(P,A,B);
        Dist=FVector::Dist(P,Q); FVector Out=(P-Q); Out.Z=FMath::Max(Out.Z,0.f);
        return Out.IsNearlyZero() ? FVector(0,1,0) : Out.GetSafeNormal();   // rig faces +Y
    };
    const bool Upright=F.Alive() && F.Action!=EWardenAction::Hurt;

    // ---- 3. Arms out of the belly: the HY clips were made for a slim mannequin -----------------------------
    if(Pelvis>=0 && Chest>=0)
        for(int32 Side=0;Side<2;++Side)
        {
            const int32 A=Idx(Side?TEXT("upperarm_l"):TEXT("upperarm_r")), B=Idx(Side?TEXT("lowerarm_l"):TEXT("lowerarm_r")), E=Idx(Side?TEXT("hand_l"):TEXT("hand_r"));
            if(A<0||B<0||E<0) continue;
            float DH=0, DE=0;
            const FVector OutH=TorsoOut(CS[E].GetLocation(),DH), OutE=TorsoOut(CS[B].GetLocation(),DE);
            if(DH>=TorsoHand && DE>=TorsoElbow) continue;
            const FVector Hand=DH<TorsoHand ? CS[E].GetLocation()+OutH*(TorsoHand-DH) : CS[E].GetLocation();
            TwoBone(A,B,E,Hand,CS[B].GetLocation()+OutE*30+FVector(0,0,-10),1.f);
        }

    // ---- 4. Floor: nothing of him below the stones (kneels, crouches, the death fall) --------------------
    {
        struct FProbe { const TCHAR* Bone; float Clear; };   // mannequin cm above the floor
        const FProbe Probes[]={{TEXT("ball_l"),1.5f},{TEXT("ball_r"),1.5f},{TEXT("foot_l"),6},{TEXT("foot_r"),6},{TEXT("calf_l"),5},{TEXT("calf_r"),5},
                               {TEXT("hand_l"),4},{TEXT("hand_r"),4},{TEXT("lowerarm_l"),5},{TEXT("lowerarm_r"),5},{TEXT("pelvis"),9},{TEXT("head"),9}};
        float Need=0;
        for(const auto& P:Probes) if(const int32 I=Idx(P.Bone); I>=0) Need=FMath::Max(Need,P.Clear-CS[I].GetLocation().Z);
        V.Lift=Dt>0 ? FMath::FInterpTo(V.Lift,Need,Dt,Need>V.Lift ? 30.f : 6.f) : Need;   // rise at once, settle slowly
        Body->SetRelativeLocation(FVector(0,0,FMath::Max(0.f,V.Lift)));
        V.WorstFloor=FMath::Max(V.WorstFloor,(Need-FMath::Max(0.f,V.Lift))*Scale);
    }
    Body->UpdateComponentToWorld();
    const FTransform CT=Body->GetComponentTransform();

    // ---- 5. The hammer: grip in the right fist; aim along the engine's bell path during attacks; out of his
    // body; bell rim on or above the floor --------------------------------------------------------------
    FVector G=CT.TransformPosition(CS[Idx(TEXT("hand_r"))].GetLocation()), D=FVector::ForwardVector, Fingers=FVector::DownVector;
    {
        const int32 HandR=Idx(TEXT("hand_r")), Mid=Idx(TEXT("middle_01_r")), Ix=Idx(TEXT("index_01_r")), Pk=Idx(TEXT("pinky_01_r"));
        if(HandR>=0 && Mid>=0) { const FVector H=CS[HandR].GetLocation(), M=CS[Mid].GetLocation(); G=CT.TransformPosition(H+.55f*(M-H)); Fingers=CT.TransformVector(M-H).GetSafeNormal(); }
        const FVector Clip3=(Ix>=0 && Pk>=0) ? CT.TransformVector(CS[Pk].GetLocation()-CS[Ix].GetLocation()).GetSafeNormal() : -FVector::UpVector;
        D=Clip3;
        if(Striking)
        {
            const auto& Def=F.Definition();
            const float In=Smooth(AgeF/10.f), Out=1-Smooth((AgeF-(Def.Total()-22))/22.f);
            const FVector Bell=Floor+Yaw.RotateVector(BellOffsetAt(F.Move,AgeF,true));
            const FVector Engine=(Bell-G).GetSafeNormal();
            D=(Clip3*(1-In*Out)+Engine*In*Out).GetSafeNormal();
        }
        // His body as an ellipse in his own facing frame (deep 55, wide 85-90 cm; a 38 cm head above 380 cm),
        // measured from the v3 model. A plain circle (2026-11-18 v2) flagged a haft held in front of his chest.
        auto Inside=[&](const FVector& P,float Pad,FVector& Out)->float
        {
            const FVector L=Yaw.UnrotateVector(P-Floor);
            if(L.Z<20 || L.Z>470) return 0.f;
            const bool Head=L.Z>380;
            const float Rf=(Head ? 38.f : L.Z<200 ? 60.f : 55.f)+Pad, Rs=(Head ? 38.f : L.Z<200 ? 85.f : 90.f)+Pad;
            const float E=FMath::Sqrt(FMath::Square(L.X/Rf)+FMath::Square(L.Y/Rs));
            if(E>=1) return 0.f;
            FVector G2(L.X/(Rf*Rf),L.Y/(Rs*Rs),0); if(G2.IsNearlyZero()) G2=FVector(1,0,0);
            Out=Yaw.RotateVector(G2.GetSafeNormal());
            return (1-E)*FMath::Min(Rf,Rs);
        };
        for(int32 Pass=0;Pass<8;++Pass)
        {
            float Worst=0; FVector Push=FVector::ZeroVector;
            for(float S=40;S<=BellReach+BellLength*.5f;S+=20)
            {
                FVector Out; const float Need=Inside(G+D*S,S>BellReach-BellLength ? BellRim*.6f : 6.f,Out);
                if(Need>Worst) { Worst=Need; Push=Out*Need/S; }
            }
            if(Upright && Pass==7) V.WorstBody=FMath::Max(V.WorstBody,Worst);
            if(Worst>0) D=(D+Push*1.2f).GetSafeNormal();
            // Floor: the bell's lowest rim point no lower than the stones.
            const FVector Bell=G+D*BellReach;
            const float Low=Bell.Z-BellRim*FMath::Sqrt(FMath::Max(0.f,1-D.Z*D.Z));
            if(Low<2) D=(D+FVector(0,0,(2-Low)/BellReach)).GetSafeNormal();
            if(Worst<=0 && Low>=2) break;
        }
        if(G.Z<15) G.Z=15;
    }
    // ---- 5b. Grip: each hand closes around the haft. The knuckle line runs along the haft (thumb side toward
    // whichever end needs the smaller wrist turn, with hysteresis so it never flips mid-swing; the turn is
    // capped at 100 degrees), and the fingers curl into a fist, so the haft runs through the hand instead of
    // the clip's open, clawing fingers (2026-11-18 owner review). Presentation only.
    struct FHand { int32 Hand=-1, Index=-1, Middle=-1, Pinky=-1, Thumb=-1; };
    auto HandOf=[&](bool Left){ FHand H; const TCHAR* S=Left?TEXT("_l"):TEXT("_r");
        H.Hand=Idx(*(FString(TEXT("hand"))+S)); H.Index=Idx(*(FString(TEXT("index_01"))+S)); H.Middle=Idx(*(FString(TEXT("middle_01"))+S));
        H.Pinky=Idx(*(FString(TEXT("pinky_01"))+S)); H.Thumb=Idx(*(FString(TEXT("thumb_01"))+S)); return H; };
    auto Palm=[&](const FHand& H){ const FVector W=CS[H.Hand].GetLocation(); return W+.55f*(CS[H.Middle].GetLocation()-W); };
    auto Orient=[&](const FHand& H,const FVector& Dc,float& Sign,float Weight)
    {
        if(H.Hand<0||H.Index<0||H.Pinky<0) return;
        const FVector K=(CS[H.Pinky].GetLocation()-CS[H.Index].GetLocation()).GetSafeNormal();
        if(FVector::DotProduct(K,Dc)*Sign<-.3f) Sign=-Sign;
        FQuat Q=FQuat::FindBetweenNormals(K,Dc*Sign);
        const float Angle=Q.GetAngle(), Cap=FMath::DegreesToRadians(100.f);
        if(Angle>Cap) Q=FQuat::Slerp(FQuat::Identity,Q,Cap/Angle);
        RotateCS(H.Hand,FQuat::Slerp(FQuat::Identity,Q,FMath::Clamp(Weight,0.f,1.f)));
    };
    auto Fist=[&](const FHand& H,bool Left,float Amount)
    {
        if(H.Hand<0||H.Index<0||H.Middle<0||H.Pinky<0) return;
        const TCHAR* S=Left?TEXT("_l"):TEXT("_r");
        // Start every finger from its rest pose (the clip's fingers are flat or splayed).
        for(const TCHAR* Finger:{TEXT("index"),TEXT("middle"),TEXT("ring"),TEXT("pinky"),TEXT("thumb")})
            for(int32 J=1;J<=3;++J) if(const int32 B=Idx(*FString::Printf(TEXT("%s_0%d%s"),Finger,J,S)); B>=0) Local[B].SetRotation(Ref.GetRefBonePose()[B].GetRotation());
        Build();
        const FVector W=CS[H.Hand].GetLocation();
        const FVector K=(CS[H.Pinky].GetLocation()-CS[H.Index].GetLocation()).GetSafeNormal(), Fd=(CS[H.Middle].GetLocation()-W).GetSafeNormal();
        FVector N=FVector::CrossProduct(K,Fd).GetSafeNormal();
        // Palm side. The right hand's sign comes from its rest curl (fingertips bend slightly toward the palm);
        // the left hand is the mirror image, and mirroring flips this cross product, so its sign is the negative
        // of the right's (testing the left hand on its own picked the back of the hand: a backward claw).
        if(!Left)
        {
            const int32 Tip=Idx(TEXT("middle_03_r"));
            if(Tip>=0)
            {
                const FVector T=CS[Tip].GetLocation()-CS[H.Middle].GetLocation();
                V.PalmSign=FVector::DotProduct(T-Fd*FVector::DotProduct(T,Fd),N)<0 ? -1.f : 1.f;
            }
            N*=V.PalmSign;
        }
        else N*=-V.PalmSign;
        static const float Curl[3]={50,58,38};
        for(const TCHAR* Finger:{TEXT("index"),TEXT("middle"),TEXT("ring"),TEXT("pinky")})
            for(int32 J=1;J<=3;++J)
            {
                const int32 B=Idx(*FString::Printf(TEXT("%s_0%d%s"),Finger,J,S)); if(B<0) continue;
                const int32 Next=J<3 ? Idx(*FString::Printf(TEXT("%s_0%d%s"),Finger,J+1,S)) : -1, Prev=Ref.GetParentIndex(B);
                const FVector Along=(Next>=0 ? CS[Next].GetLocation()-CS[B].GetLocation() : CS[B].GetLocation()-CS[Prev].GetLocation()).GetSafeNormal();
                const FVector Axis=FVector::CrossProduct(Along,N).GetSafeNormal();
                if(!Axis.IsNearlyZero()) RotateCS(B,FQuat(Axis,FMath::DegreesToRadians(Curl[J-1]*Amount)));
            }
        for(int32 J=2;J<=3;++J)
            if(const int32 B=Idx(*FString::Printf(TEXT("thumb_0%d%s"),J,S)); B>=0)
            {
                const int32 Prev=Ref.GetParentIndex(B);
                const FVector Along=(CS[B].GetLocation()-CS[Prev].GetLocation()).GetSafeNormal();
                const FVector Axis=FVector::CrossProduct(Along,N).GetSafeNormal();
                if(!Axis.IsNearlyZero()) RotateCS(B,FQuat(Axis,FMath::DegreesToRadians(22.f*Amount)));
            }
    };
    const FHand Right=HandOf(false), LeftH=HandOf(true);
    const FVector Dc=CT.InverseTransformVector(D).GetSafeNormal();
    if(F.Alive() && Right.Hand>=0 && Right.Middle>=0)
    {
        Orient(Right,Dc,V.SignR,1.f);
        Fist(Right,false,1.f);
        G=CT.TransformPosition(Palm(Right));   // the hammer sits in the closed fist
        Fingers=CT.TransformVector(CS[Right.Middle].GetLocation()-CS[Right.Hand].GetLocation()).GetSafeNormal();
        if(G.Z<15) G.Z=15;
    }
    // Two hands meet on the haft: if the left hand would fall short of its grip, the right hand moves toward it
    // by the shortfall (up to 80 cm, eased), as a real two-handed grip does, instead of the left arm giving up.
    if(Upright && Right.Hand>=0 && LeftH.Hand>=0)
    {
        const int32 LA=Idx(TEXT("upperarm_l")), LB=Idx(TEXT("lowerarm_l")), RA=Idx(TEXT("upperarm_r")), RB=Idx(TEXT("lowerarm_r"));
        if(LA>=0 && LB>=0 && RA>=0 && RB>=0)
        {
            const FVector ShoulderL=CS[LA].GetLocation();
            const float ReachL=FVector::Dist(ShoulderL,CS[LB].GetLocation())+FVector::Dist(CS[LB].GetLocation(),CS[LeftH.Hand].GetLocation());
            const FVector Gc=CT.InverseTransformPosition(G);
            FVector Best=Gc; float BestD=1e9f;
            for(float Sw=30;Sw<=110;Sw+=5) { const FVector P=Gc-Dc*(Sw/Scale); const float Dd=FVector::Dist(P,ShoulderL); if(Dd<BestD) { BestD=Dd; Best=P; } }
            const float Want=FMath::Clamp(BestD-ReachL*.97f,0.f,80.f/Scale);
            V.Shift=Dt>0 ? FMath::FInterpTo(V.Shift,Want,Dt,8.f) : Want;
            if(V.Shift>.1f)
            {
                const FVector Dir=(ShoulderL-Best).GetSafeNormal();
                const FVector WristToPalm=Palm(Right)-CS[Right.Hand].GetLocation();
                float DE=0; const FVector Out=TorsoOut(CS[RB].GetLocation(),DE);
                TwoBone(RA,RB,Right.Hand,Palm(Right)+Dir*V.Shift-WristToPalm,CS[RB].GetLocation()+Out*30+FVector(0,0,-15),1.f);
                Orient(Right,Dc,V.SignR,1.f);
                G=CT.TransformPosition(Palm(Right));
                Fingers=CT.TransformVector(CS[Right.Middle].GetLocation()-CS[Right.Hand].GetLocation()).GetSafeNormal();
                if(G.Z<15) G.Z=15;
            }
        }
    }
    const FVector BellAt=G+D*BellReach;
    const float BellLow=BellAt.Z-BellRim*FMath::Sqrt(FMath::Max(0.f,1-D.Z*D.Z));
    if(UStaticMeshComponent* H=BellbreakerHammer.Get())
    {
        // SM_BellHammerGen: bell mouth at the origin, haft along +Z toward the butt.
        H->SetWorldLocationAndRotation(BellAt,FRotationMatrix::MakeFromZX(-D,Fingers).ToQuat());
    }

    // ---- 6. Left hand: on the haft when it is within reach (two-handed), otherwise a relaxed hang at his side
    // that follows his body (one-handed carry), never the clip's free arm flailing; the two blend over ~0.2 s.
    if(LeftH.Hand>=0 && LeftH.Middle>=0)
    {
        const int32 A=Idx(TEXT("upperarm_l")), B=Idx(TEXT("lowerarm_l"));
        if(A>=0 && B>=0 && F.Alive() && F.Action!=EWardenAction::Hurt)
        {
            const FVector Gc=CT.InverseTransformPosition(G), Shoulder=CS[A].GetLocation();
            const float Reach=FVector::Dist(Shoulder,CS[B].GetLocation())+FVector::Dist(CS[B].GetLocation(),CS[LeftH.Hand].GetLocation());
            FVector Best=Gc-Dc*(LeftOnHaft/Scale); float BestD=1e9f;
            for(float Sw=30;Sw<=110;Sw+=5)
            {
                const FVector P=Gc-Dc*(Sw/Scale); const float Dd=FVector::Dist(P,Shoulder);
                if(Dd<BestD) { BestD=Dd; Best=P; }
            }
            const float Want=BestD<=Reach*1.02f ? 1.f : 0.f;
            V.LeftGrip=Dt>0 ? FMath::FInterpConstantTo(V.LeftGrip,Want,Dt,5.f) : Want;
            const float Wg=Smooth(V.LeftGrip);
            // The hang: below the shoulder, a little out from the body and forward, elbow soft.
            float DS=0; const FVector Out=TorsoOut(Shoulder,DS);
            const FVector Hang=Shoulder+FVector(0,0,-Reach*.86f)+FVector(Out.X,Out.Y,0).GetSafeNormal()*7+FVector(0,6,0);
            for(int32 Pass=0;Pass<2;++Pass)
            {
                const FVector WristToPalm=Palm(LeftH)-CS[LeftH.Hand].GetLocation();
                const FVector Target=FMath::Lerp(Hang,Best-WristToPalm,Wg);
                float DE=0; const FVector OutE=TorsoOut(CS[B].GetLocation(),DE);
                TwoBone(A,B,LeftH.Hand,Target,CS[B].GetLocation()+OutE*30+FVector(0,0,-15),1.f);
                Orient(LeftH,Dc,V.SignL,Wg);
            }
            Fist(LeftH,true,FMath::Lerp(.35f,1.f,Wg));   // relaxed curl when hanging, closing as it takes the haft
            if(Wg>.95f) V.WorstLeftGap=FMath::Max(V.WorstLeftGap,FVector::Dist(Palm(LeftH),Best)*Scale);
        }
    }
    Body->BoneSpaceTransforms=Local;
    Body->RefreshBoneTransforms();

    // ---- 7. Bell on stone: sparks where the rim grinds, a burst when it slams in, metal-scrape sound --------
    const float Speed=Dt>0 ? FVector::Dist(BellAt,V.LastBell)/Dt : 0.f;
    const FVector Move=Dt>0 ? (BellAt-V.LastBell).GetSafeNormal2D() : FVector::ZeroVector;
    V.LastBell=BellAt;
    const bool Contact=BellLow<14 && F.Alive();
    const FVector Touch(BellAt.X-D.X*20,BellAt.Y-D.Y*20,3);
    auto Emit=[&](int32 Sparks,float Spread,float Rise,const FVector& Away)
    {
        for(int32 K=0;K<Sparks;++K)
        {
            auto& P=V.Buffer[V.Next]; V.Next=(V.Next+1)%FWardenBellbreakerView::MaxSparks;
            const FVector SideV=FVector::CrossProduct(Away.IsNearlyZero() ? FVector::ForwardVector : Away,FVector::UpVector);
            P.Start=Seconds; P.At=Touch+FVector(FMath::FRandRange(-40.f,40.f),FMath::FRandRange(-40.f,40.f),0);
            P.Velocity=Away*FMath::FRandRange(150.f,650.f)+SideV*FMath::FRandRange(-Spread,Spread)+FVector(0,0,FMath::FRandRange(Rise*.4f,Rise));
        }
    };
    if(Contact && !V.bContact && V.LastSpeed>500)   // slammed in
    {
        Emit(36,520,620,FVector::ZeroVector);
        for(int32 K=0;K<36;++K) { auto& P=V.Buffer[(V.Next+FWardenBellbreakerView::MaxSparks-1-K)%FWardenBellbreakerView::MaxSparks]; const float A=K*10.f; P.Velocity+=FVector(FMath::Cos(FMath::DegreesToRadians(A)),FMath::Sin(FMath::DegreesToRadians(A)),0)*420; }
        BellbreakerSound(V.ScrapeVariant%2 ? TEXT("bell_hit_anvil_v1") : TEXT("bell_hit_anvil_v0"),Touch,.55f);
    }
    if(Contact && Speed>120)   // dragging: a trail of sparks thrown back from the motion
    {
        Emit(FMath::Max(1,FMath::CeilToInt(Dt*FMath::Clamp(Speed*.35f,60.f,320.f))),280,420,-Move);
        if(Seconds>=V.ScrapeReady)
        {
            BellbreakerSound(++V.ScrapeVariant%2 ? TEXT("bell_scrape_v0") : TEXT("bell_scrape_v1"),Touch,FMath::Clamp(Speed/900.f,.35f,1.f));
            V.ScrapeReady=Seconds+1.1f;
        }
    }
    V.bContact=Contact; V.LastSpeed=Speed;
    if(UInstancedStaticMeshComponent* S=V.Sparks.Get())
    {
        FVector Eye=At+FVector(0,0,300);
        if(auto* PC=GetWorld()->GetFirstPlayerController()) if(PC->PlayerCameraManager) Eye=PC->PlayerCameraManager->GetCameraLocation();
        TArray<FTransform> Xf; Xf.Reserve(FWardenBellbreakerView::MaxSparks);
        for(const auto& P:V.Buffer)
        {
            const float Life=Seconds-P.Start;
            const FVector Vel=P.Velocity+FVector(0,0,-980*Life), SparkAt=P.At+P.Velocity*Life+FVector(0,0,-490*Life*Life);
            if(Life<0 || Life>.5f || SparkAt.Z<0) { Xf.Add(FTransform(FQuat::Identity,FVector(0,0,-10000),FVector(0))); continue; }
            const FVector Dir=Vel.GetSafeNormal();
            const float Glow=1-Life/.5f;
            Xf.Add(FTransform(FRotationMatrix::MakeFromYZ(Dir,(Eye-SparkAt).GetSafeNormal()).ToQuat(),SparkAt,FVector(.045f*Glow,(8+Vel.Size()*.05f)/100,1)));
        }
        S->BatchUpdateInstancesTransforms(0,Xf,true,true);
    }

    // ---- 8. Shockwave crests (engine radius, so what you see is what resolves) -----------------------------
    const int32 Tick=CombatTick;
    int32 Used=0;
    for(const auto& Wv:Bellbreaker.Waves)
    {
        if(Used>=BellbreakerRings.Num()) break;
        if(Tick<Wv.Start) continue;
        const float Radius=WaveRadius(Tick-Wv.Start)+CombatAccumulator/WardenRules::Step*RingSpeed*WardenRules::Step;
        if(UStaticMeshComponent* R=BellbreakerRings[Used].Get())
        {
            R->SetVisibility(true); R->SetWorldLocation(Wv.Center+FVector(0,0,6)); R->SetWorldScale3D(FVector(Radius/50.f,Radius/50.f,1));
            if(auto* M=BellbreakerRingMids[Used].Get()) M->SetScalarParameterValue(TEXT("Fade"),FMath::Clamp(1.f-(Radius-RingStart)/(RingEnd-RingStart),0.f,1.f));
        }
        ++Used;
    }
    for(int32 I=Used;I<BellbreakerRings.Num();++I) if(UStaticMeshComponent* R=BellbreakerRings[I].Get()) R->SetVisibility(false);
}

// Capture-only side-on review (-BossLabBellbreakerStudy): each move once, the player standing still in reach.
void AWardenArenaMode::BellbreakerStudyStep()
{
    using namespace WardenBellbreaker;
    static const int32 Seq[]={HammerFall,Sweep,Quake,BellBreaks};
    auto& F=Warden->Fight;
    const FVector ToPlayer=Player->GetActorLocation()-Warden->GetActorLocation();
    if(F.Action==EWardenAction::Strike) { if(F.Age<F.Definition().Windup-14) Warden->CommittedDirection=ToPlayer.GetSafeNormal2D(); return; }
    if(!F.Ready() || --BellbreakerStudyWait>0) return;
    if(BellbreakerStudyWait==0 && BellbreakerStudyIndex>0)
    {
        UE_LOG(LogTemp,Display,TEXT("BOSSLAB BELLBREAKER study after %s: worst body intrusion %.1f cm, worst floor %.1f cm, worst left-hand gap %.1f cm"),
            WardenRules::Strike(Seq[BellbreakerStudyIndex-1]).Name,BBView.WorstBody,BBView.WorstFloor,BBView.WorstLeftGap);
        BBView.WorstBody=BBView.WorstFloor=BBView.WorstLeftGap=0;
    }
    if(BellbreakerStudyIndex>=UE_ARRAY_COUNT(Seq)) return;
    const int32 Move=Seq[BellbreakerStudyIndex++];
    const FVector Fwd=Warden->GetActorForwardVector().GetSafeNormal2D();
    Player->SetActorLocation(FVector(Warden->GetActorLocation().X,Warden->GetActorLocation().Y,95)+Fwd*(Move==Quake ? 700.f : 430.f));
    Warden->BeginAction(EWardenAction::Strike,Move,Fwd);
    LastEvent=FString::Printf(TEXT("STUDY | %s"),F.Definition().Name);
    BellbreakerStudyWait=60;
}
