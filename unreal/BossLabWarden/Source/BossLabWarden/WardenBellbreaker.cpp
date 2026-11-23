#include "WardenBellbreaker.h"
#include "BellbreakerSkinProbe.h"
#if WITH_EDITOR
#include "Rendering/SkeletalMeshRenderData.h"
#include "Rendering/SkeletalMeshLODRenderData.h"
#include "Rendering/SkinWeightVertexBuffer.h"
#endif
#include "WardenPrototype.h"
#include "Animation/SkeletalMeshActor.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/AudioComponent.h"
#include "EngineUtils.h"
#include "Engine/CollisionProfile.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "GameFramework/PlayerController.h"
#include "Camera/PlayerCameraManager.h"
#include "Camera/CameraActor.h"
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
constexpr float OverTop=101.f, OverEnd=-48.46335f, SweepFrom=62.f, SweepTo=-54.f;
constexpr float BellRim=60.f, BellLength=125.f;
const FVector BlastOffset(378.25,40,0);
int32 Embed(int32 Move) { using namespace WardenBellbreaker; return Move==Quake ? 60 : Move==Sweep ? 18 : 40; }
struct FBellPose { FVector Grip, Shaft; };
// The readiness-pass rows (2026-11-23). Each pose is a grip point and shaft direction in the facing frame,
// blended from the carry over the hoist and back over the recovery. The same function is the hit path
// (BellbreakerHitPoint) and the drawn hammer, so what you see is what hits.
FBellPose NewMovePose(int32 Move,float Age,const FWardenStrike& Def,const FVector& Carry,float CarryPitch,float CarryYaw)
{
    using namespace WardenBellbreaker;
    const float W=Def.Windup, A=Def.Active, R=Def.Recovery, Since=Age-W;
    auto Blend=[&](const FVector& Grip,float Pitch,float Heading,float HoistTicks,float ReturnStart)
    {
        const float Weight=Smooth(Age/HoistTicks)*(1.f-Smooth((Age-ReturnStart)/(W+A+R-ReturnStart)));
        return FBellPose{FMath::Lerp(Carry,Grip,Weight),FRotator(FMath::Lerp(CarryPitch,Pitch,Weight),FMath::Lerp(CarryYaw,Heading,Weight),0).Vector()};
    };
    // Shaft-based pose: grip on a circle of Radius around Hub, bell further out along the shaft.
    auto Swing=[&](const FVector& Hub,float Radius,float Pitch,float Heading,float HoistTicks,float ReturnStart)
    {
        const FVector Dir=FRotator(Pitch,Heading,0).Vector();
        return Blend(Hub+Dir*(Radius-BellReach),Pitch,Heading,HoistTicks,ReturnStart);
    };
    switch(Move)
    {
    case Backhand:
    {
        // The Sweep mirrored: from the left, wound across the chest, out to the right.
        const float Drop=FMath::Clamp((Since+1)/A,0.f,1.f);
        return Swing(FVector(118,10,351),355,-32,FMath::Lerp(-58.f,60.f,Smooth(Drop)),W*.8f,W+A+30);
    }
    case Uppercut: case Fling:
    {
        // Bell dragged low on the right (sparks), then swung up through the front.
        const float Drag=Smooth(Age/(W*.55f)), Rise=Smooth((Since+2)/A);
        const float Pitch=Since<-2 ? -47.f : FMath::Lerp(-47.f,Move==Fling ? 38.f : 64.f,Rise);
        const float Heading=Since<-2 ? FMath::Lerp(48.f,16.f,Smooth((Age-W*.55f)/(W*.45f))) : FMath::Lerp(16.f,0.f,Rise);
        return Swing(FVector(96,20,330),362,Pitch,Heading,W*.5f*Drag+1,W+A+26);
    }
    case Stamp:
        // The weapon is held clear to the side while the boot comes down.
        return Blend(FVector(120,40,320),-14,-58,W*.6f,W+A+12);
    case Charge:
        // Ram: bell levelled forward at chest height for the run.
        // Grip out on the right hip so the levelled haft clears the belly (study: 14 cm intrusion at 14 cm out).
        return Blend(FVector(126,62,300),-22,-8,W*.7f,W+A+10);
    case Toll:
    {
        // Raised high, mouth down, then the toll: a short heavy drop to the level.
        const float Strike=Smooth((Since+10)/12.f);
        return Swing(FVector(70,30,360),330,FMath::Lerp(78.f,8.f,Strike),0,W*.6f,W+A+20);
    }
    case HeldNote: case StridingFall:
    {
        // The Hammer Fall arc with a long hold at the top (Held Note) or a quick hoist and a lunge.
        const float Hoist=Move==HeldNote ? 58.f : W*.72f;
        const float Drop=FMath::Clamp((Since+1)/A,0.f,1.f);
        const float Pitch=FMath::Min(89.f,FMath::Lerp(OverTop,OverEnd,Drop));
        const FVector Dir=FRotator(Pitch,0,0).Vector();
        const FVector Hub(82,38+38*Smooth((Dir.Z+.4f)/1.25f),315);
        return Swing(Hub,365,Pitch,0,Hoist,W+A+40);
    }
    case Cyclone:
        // Constant level pose; the body and the bell turn together (CycloneSpin).
        {
            const FBellPose P=Swing(FVector(120,0,345),355,-30,24,W*.7f,W+A+20);
            const FRotator Spin(0,CycloneSpin(Move,Age),0);
            return {Spin.RotateVector(P.Grip),Spin.RotateVector(P.Shaft)};
        }
    case Knell:
    {
        // Three slams on the same mark (contact at Since 0, KnellGap, 2*KnellGap), lifting between them.
        const int32 K=FMath::Clamp(FMath::FloorToInt((Since+KnellGap)/float(KnellGap)),0,2);
        const float Local=Since<0 ? Since+KnellGap : Since-K*KnellGap+KnellGap;   // 0..KnellGap toward each contact
        const float Up=Since<-KnellGap ? 1.f : FMath::Sin(PI*FMath::Clamp(Local/KnellGap,0.f,1.f))*(Since<0 ? 1.f : .7f);
        const float Pitch=Since>2*KnellGap ? OverEnd : FMath::Lerp(OverEnd,62.f,Up);
        return Swing(FVector(82,46,315),365,Pitch,0,W*.6f,W+A+20);
    }
    default: return {Carry,FRotator(CarryPitch,CarryYaw,0).Vector()};
    }
}
FBellPose WeaponPose(int32 Move,float Age,bool Striking)
{
    using namespace WardenBellbreaker;
    const FVector Carry(138,8,297);
    constexpr float CarryPitch=-22.f, CarryYaw=-70.f;
    if(!Striking || !IsBellbreaker(Move)) return {Carry,FRotator(CarryPitch,CarryYaw,0).Vector()};
    const auto& Def=Strike(Move);
    if(Move>=Backhand) return NewMovePose(Move,Age,Def,Carry,CarryPitch,CarryYaw);
    const bool Lateral=Move==Sweep, Slam=Move==Quake || Move==BellBreaks;
    const float Hoist=Smooth(Age/(Def.Windup*(Slam ? .68f : .78f)));
    const float Return=Smooth((Age-Def.Windup-Def.Active-Embed(Move))/(Def.Recovery-Embed(Move)));
    const float Weight=Hoist*(1.f-Return);
    const float DropTicks=Move==Quake ? 31.f : 28.f;
    const float Drop=Slam ? Smooth((Age-Def.Windup+DropTicks)/DropTicks)
                          : FMath::Clamp((Age-Def.Windup+1)/Def.Active,0.f,1.f);
    // Lift to a balanced vertical hold. The first active hammer sample still
    // follows its established arc; the preparatory pose no longer tips back.
    const float Pitch=Lateral ? -34.f : Slam ? FMath::Lerp(87.f,OverEnd,Drop) :
        FMath::Min(89.f,FMath::Lerp(OverTop,OverEnd,Drop));
    const float Heading=Lateral ? FMath::Lerp(SweepFrom,SweepTo,Drop) : 0.f;
    const FVector StrikeDir=FRotator(Pitch,Heading,0).Vector();
    // The hub sits in front of the chest. Near the high hold it moves alongside
    // the smith's right shoulder so the projecting pommel clears his head.
    const FVector Hub=Lateral ? FVector(123,-12,351) : FVector(82,38+38*Smooth((StrikeDir.Z+.4f)/1.25f),315);
    const float Radius=Lateral ? 355.f : 365.f;
    FVector AttackGrip=Hub+StrikeDir*(Radius-BellReach);
    if(Slam)
    {
        const FVector TerminalDir=FRotator(OverEnd,0,0).Vector();
        const FVector TerminalMouth=FVector(82,38,315)+TerminalDir*Radius;
        const FVector TerminalRim=TerminalMouth-FVector::VectorPlaneProject(FVector::UpVector,TerminalDir).GetSafeNormal()*BellRim;
        AttackGrip+=(BlastOffset-FVector(TerminalRim.X,TerminalRim.Y,0))*Smooth(Drop);
    }
    return {FMath::Lerp(Carry,AttackGrip,Weight),
            FRotator(FMath::Lerp(CarryPitch,Pitch,Weight),FMath::Lerp(CarryYaw,Heading,Weight),0).Vector()};
}
}

const FWardenStrike& WardenBellbreaker::Strike(int32 Index)
{
    // Name, clip, bone, windup, active, recovery, (unused anim times), damage, radius (x Scale), advance,
    // stamina, stance. The Quake and the transition deal their damage through the blast and the
    // shockwave in BellbreakerResolve, so their swept damage is zero.
    static const FWardenStrike Moves[Count]={
        {TEXT("HAMMER FALL"),TEXT("BBHammerFall"),TEXT("hand_r"),84,12,94,0,0,1,34,26,60,0,1},
        {TEXT("FORGE SWEEP"),TEXT("BBSweep"),TEXT("hand_r"),68,18,80,0,0,1,28,26,40,0,1},
        {TEXT("BELL QUAKE"),TEXT("BBQuake"),TEXT("hand_r"),106,4,108,0,0,1,0,0,0,0,1},
        {TEXT("THE BELL BREAKS"),TEXT("BBBreak"),TEXT("hand_r"),90,4,88,0,0,1,0,0,0,0,1},
        {TEXT("BACKHAND TOLL"),TEXT("BBBackhand"),TEXT("hand_r"),50,16,78,0,0,1,26,26,30,0,1},
        {TEXT("ANVIL STAMP"),TEXT("BBStamp"),TEXT("hand_r"),44,4,62,0,0,1,0,0,0,0,1},
        {TEXT("SHOULDER CHARGE"),TEXT("BBCharge"),TEXT("hand_r"),58,28,72,0,0,1,30,34,640,0,1},
        {TEXT("RISING TOLL"),TEXT("BBUppercut"),TEXT("hand_r"),56,14,84,0,0,1,32,26,70,0,1},
        {TEXT("THE TOLL"),TEXT("BBToll"),TEXT("hand_r"),72,4,76,0,0,1,0,0,0,0,1},
        {TEXT("SLAG FLING"),TEXT("BBFling"),TEXT("hand_r"),60,6,72,0,0,1,0,0,0,0,1},
        {TEXT("HELD NOTE"),TEXT("BBHeldNote"),TEXT("hand_r"),132,12,94,0,0,1,38,26,60,0,1},
        {TEXT("FORGE CYCLONE"),TEXT("BBCyclone"),TEXT("hand_r"),62,48,96,0,0,1,28,28,0,0,1},
        {TEXT("DEATH KNELL"),TEXT("BBKnell"),TEXT("hand_r"),76,64,110,0,0,1,0,0,0,0,1},
        {TEXT("STRIDING FALL"),TEXT("BBStridingFall"),TEXT("hand_r"),70,12,96,0,0,1,34,26,380,0,1}};
    check(IsBellbreaker(Index));
    return Moves[Index-First];
}
FVector WardenBellbreaker::BellOffset(int32 Move,int32 Age,bool Striking) { return BellOffsetAt(Move,float(Age),Striking); }
FVector WardenBellbreaker::BellOffsetAt(int32 Move,float Age,bool Striking)
{
    const FBellPose Pose=WeaponPose(Move,Age,Striking);
    return Pose.Grip+Pose.Shaft*BellReach;
}
FVector WardenBellbreaker::GripOffset(int32 Move,int32 Age,bool Striking)
{
    return WeaponPose(Move,float(Age),Striking).Grip;
}
FVector WardenBellbreaker::QuakeImpactOffset() { return BlastOffset; }
float WardenBellbreaker::CycloneSpin(int32 Move,float Age)
{
    if(Move!=Cyclone) return 0.f;
    const auto& D=Strike(Move);
    // Wind back a little, one full clockwise turn through the active window, settle at the facing.
    if(Age<D.Windup) return 28.f*Smooth(Age/(D.Windup*.8f));
    return FMath::Lerp(28.f,-360.f,Smooth((Age-D.Windup)/float(D.Active)));
}
FVector2D WardenBellbreaker::Band(int32 Move)
{
    switch(Move)
    {
        case HammerFall: return FVector2D(0,420);
        case Sweep: return FVector2D(0,440);
        case Quake: return FVector2D(0,700);
        case Backhand: case Uppercut: case HeldNote: return FVector2D(0,430);
        case Stamp: return FVector2D(0,280);
        case Charge: return FVector2D(480,1400);
        case Toll: return FVector2D(0,850);
        case Fling: return FVector2D(420,1500);
        case Cyclone: return FVector2D(0,470);
        case Knell: return FVector2D(0,650);
        case StridingFall: return FVector2D(360,820);
        default: return FVector2D(0,100000);
    }
}
int32 WardenBellbreaker::RepeatLock(int32 Move)
{
    // Combat ticks from commitment, including the swing. Survives interruption.
    switch(Move)
    {
        case Quake: return 16*60; case Sweep: return 8*60; case HammerFall: return 10*60;
        case Backhand: return 9*60; case Stamp: return 12*60; case Charge: return 14*60; case Uppercut: return 10*60;
        case Toll: return 20*60; case Fling: return 15*60; case HeldNote: return 14*60; case Cyclone: return 22*60;
        case Knell: return 26*60; case StridingFall: return 12*60;
        default: return 24*60;
    }
}
int32 WardenBellbreaker::Pause(int32 Move)
{
    switch(Move)
    {
        case Quake: return 72; case HammerFall: return 52;   // the bell is embedded: main punish windows
        case Sweep: return 38;
        case Backhand: return 30; case Stamp: return 40; case Charge: return 50; case Uppercut: return 44;
        case Toll: return 56; case Fling: return 40; case HeldNote: return 52; case Cyclone: return 70;
        case Knell: return 80; case StridingFall: return 52;
        default: return 48;
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
        LastEvent=FString(F.Definition().Name)+(Move==Quake || Move==Knell ? TEXT(" | Jump or roll the shockwave.") : Move==Toll ? TEXT(" | Roll through the toll; jumping will not clear it.")
            : Move==Fling ? TEXT(" | Leave the glowing marks.") : Move==Stamp ? TEXT(" | Step out of his reach.") : TEXT(" | Aim committed."));
        return true;
    };
    if(!R.PhaseTwo && F.Health<=PhaseTwoHealth)
    {
        if(R.Waiting>0) { --R.Waiting; return; }
        if(Commit(BellBreaks)) R.Waiting=Pause(BellBreaks);
        return;
    }
    // Fixed rehearsal sequence, labelled as such: no learning and no input reading. Each step walks into
    // its band and commits, or is skipped after four seconds.
    // A step whose move is still on its repeat lock (cooldown) is skipped at once; a step whose band the
    // player is inside of (the Charge, Fling and Striding Fall need room) is skipped after half a second.
    static const int32 One[]={HammerFall,Backhand,Charge,Sweep,Stamp,Quake,Uppercut,Fling,HeldNote,Toll,StridingFall,Sweep,Backhand,Stamp};
    static const int32 Two[]={Quake,Cyclone,Charge,Knell,Uppercut,Backhand,Toll,Fling,StridingFall,HeldNote,Stamp,Sweep,HammerFall,Backhand};
    const int32 Next=R.PhaseTwo ? Two[R.Step%UE_ARRAY_COUNT(Two)] : One[R.Step%UE_ARRAY_COUNT(One)];
    if(F.Cooldowns[Next]>0) { ++R.Step; R.Seeking=0; return; }
    const FVector2D B=Band(Next);
    if(Distance>B.Y) BossDirection=ToPlayer.GetSafeNormal2D();
    if(R.Waiting>0) { --R.Waiting; return; }
    if(Distance<B.X) { if(++R.Seeking>30) { ++R.Step; R.Seeking=0; } return; }
    if(Distance>B.Y) { if(++R.Seeking>240) { ++R.Step; R.Seeking=0; } return; }
    if(Commit(Next)) { ++R.Step; R.Seeking=0; R.Waiting=Pause(Next); }
}
void AWardenArenaMode::BellbreakerSound(const TCHAR* Name,const FVector& At,float Volume)
{
    if(GIsAutomationTesting || !WorldAudioEnabled() || Settings.SfxVolume<=0.f) return;
    const bool Scrape=FCString::Strncmp(Name,TEXT("bell_scrape_"),11)==0;
    if(Scrape && bForgeSpeechPriority) return;
    USoundBase* const* Sound=BellbreakerSounds.Find(Name);
    if(!Sound || !*Sound) return;
    if(auto* Voice=UGameplayStatics::SpawnSoundAtLocation(this,*Sound,At,FRotator::ZeroRotator,Volume*Settings.SfxVolume,
        Scrape ? .86f : FMath::FRandRange(.98f,1.02f)))
    {
        TrackWorldEffect(Voice);
        if(Scrape)
        {
            BellbreakerScrape=Voice;
            Voice->SetLowPassFilterEnabled(true);
            Voice->SetLowPassFilterFrequency(1450.f);
            Voice->FadeOut(.62f,0.f);
        }
    }
}
void AWardenArenaMode::BellbreakerFx(uint8 Kind,const FVector& At,float Size0,float Size1,float Life,const FVector& Velocity,float Rise)
{
    auto& V=BBView;
    if(Kind>=FWardenBellbreakerView::FxKinds || V.Fx[Kind].Num()==0 || !V.FxLayer[Kind].IsValid()) return;
    auto& P=V.Fx[Kind][V.FxNext[Kind]]; V.FxNext[Kind]=(V.FxNext[Kind]+1)%V.Fx[Kind].Num();
    P.Start=V.FxClock; P.Life=Life; P.At=At; P.Velocity=Velocity; P.Size0=Size0; P.Size1=Size1; P.Rise=Rise;
    P.Spin=FMath::FRandRange(0.f,360.f);
}
void AWardenArenaMode::BellbreakerSparks(const FVector& At,int32 Count,float Speed)
{
    auto& V=BBView;
    for(int32 K=0;K<Count;++K)
    {
        auto& P=V.Buffer[V.Next]; V.Next=(V.Next+1)%FWardenBellbreakerView::MaxSparks;
        const float A=FMath::FRandRange(0.f,2*PI);
        P.Start=V.FxClock; P.At=At+FVector(FMath::FRandRange(-15.f,15.f),FMath::FRandRange(-15.f,15.f),4);
        P.Velocity=FVector(FMath::Cos(A),FMath::Sin(A),0)*Speed*FMath::FRandRange(.35f,1.f)+FVector(0,0,FMath::FRandRange(.5f,1.2f)*Speed);
    }
}
void AWardenArenaMode::BellbreakerBurst(const FVector& At,float Strength,bool Crack)
{
    // A heavy blow on stone: a glowing crack that cools over a few seconds, a ring of dust rolling out low,
    // a short fire flash and sparks.
    using V=FWardenBellbreakerView;
    const FVector Ground(At.X,At.Y,0);
    if(Crack) BellbreakerFx(V::FxCrack,Ground,260*Strength,300*Strength,4.5f);
    const int32 Puffs=FMath::RoundToInt(8*Strength);
    for(int32 K=0;K<Puffs;++K)
    {
        const float A=2*PI*(K+FMath::FRandRange(-.3f,.3f))/Puffs;
        const FVector Out(FMath::Cos(A),FMath::Sin(A),0);
        BellbreakerFx(V::FxDust,Ground+Out*60*Strength+FVector(0,0,30),70*Strength,240*Strength,FMath::FRandRange(1.1f,1.7f),Out*FMath::FRandRange(260.f,420.f)*Strength,40);
    }
    BellbreakerFx(V::FxFire,Ground+FVector(0,0,45),90*Strength,230*Strength,.38f,FVector::ZeroVector,90);
    BellbreakerSparks(Ground,FMath::RoundToInt(22*Strength),520);
}
void AWardenArenaMode::BellbreakerSpeak(const TCHAR* Line)
{
    if (GIsAutomationTesting || !WorldAudioEnabled() || Settings.SfxVolume <= 0.f) return;
    USoundBase* const* Sound = BellbreakerSounds.Find(Line);
    if (!Sound || !*Sound) return;
    if (BellbreakerSpeech.IsValid()) BellbreakerSpeech->Stop();
    BellbreakerSpeech = UGameplayStatics::SpawnSound2D(this, *Sound, Settings.SfxVolume*1.15f);
    if (BellbreakerSpeech.IsValid())
    {
        WorldAudioVoices.Add(BellbreakerSpeech);
        SetForgeSpeechPriority(true);
        UE_LOG(LogTemp, Display, TEXT("BOSSLAB forge dialogue: %s"), Line);
    }
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
        if (A == 1 && F.Move == BellBreaks) BellbreakerSpeak(TEXT("PhaseBreak"));
        if(A==1 && F.Move!=Sweep) BellbreakerSound(F.Move==BellBreaks ? TEXT("bell_crack_v1") : TEXT("clapper_tell_v0"),Bell,.8f);
        if(Since==-8) BellbreakerSound(TEXT("bell_whoosh_v0"),Bell,.8f);
        auto GroundPulse=[&](const FVector& Source,float Strength)
        {
            R.GroundAmplitude=Strength*FMath::Clamp(1.f-FVector::Dist2D(Source,Player->GetActorLocation())/1600.f,.12f,1.f);
            R.GroundAge=0;
        };
        if((F.Move==HammerFall || F.Move==HeldNote || F.Move==StridingFall) && Since==D.Active-1)
        {
            GroundPulse(Bell,.82f); BellbreakerSound(TEXT("bell_slam_ground_v1"),Bell,.9f); Impact(3,0.f);
            BellbreakerBurst(Bell,.75f,true);
        }
        // Effects pass: dust kicked up by the run and by the bell skimming the floor in the Cyclone.
        if(F.Move==Charge && Since>=-6 && Since<D.Active && A%6==0)
        {
            const FVector Back=Yaw.RotateVector(FVector(-40,FMath::FRandRange(-70.f,70.f),30));
            BellbreakerFx(FWardenBellbreakerView::FxDust,Floor+Back,90,260,1.3f,Yaw.RotateVector(FVector(-160,0,0)),50);
            if(A%12==0) BellbreakerSound(A%24 ? TEXT("giant_footstep_v0") : TEXT("giant_footstep_v1"),Floor,.75f);
        }
        if(F.Move==Cyclone && Since>=0 && Since<D.Active && A%4==0)
            BellbreakerFx(FWardenBellbreakerView::FxDust,FVector(Bell.X,Bell.Y,30),80,220,1.0f,(Bell-Floor).GetSafeNormal2D()*300,30);
        // Readiness-pass rows (2026-11-23). A blast flinches whoever is inside its radius on that tick unless
        // they are airborne or inside roll i-frames (Damage refuses while invulnerable).
        auto Blast=[&](const FVector& Centre,float Radius,float Amount,const TCHAR* Event)
        {
            if(!P.Alive() || FVector::Dist2D(Player->GetActorLocation(),Centre)>Radius) return;
            if(Player->AirLift>AirborneLift) { R.LastOutcome=EBellbreakerOutcome::Jumped; return; }
            const float Before=P.Health;
            if(P.Damage(Amount,true)) { BossDamage+=Before-P.Health; Flinched(Centre); LastEvent=Event; }
            else R.LastOutcome=EBellbreakerOutcome::Rolled;
        };
        if(F.Move==Stamp && Since==0)
        {
            const FVector Centre=Floor+Yaw.RotateVector(FVector(StampAhead,0,0));
            BellbreakerSound(TEXT("stamp_quake_v0"),Centre,1.f); GroundPulse(Centre,.7f); Impact(3,0.f);
            Blast(Centre,StampRadius,StampDamage,TEXT("ANVIL STAMP | Too close: step out or roll."));
            BellbreakerBurst(Centre,1.15f,true); BellbreakerSound(TEXT("rubble_settle_v0"),Centre,.7f);
        }
        if(F.Move==Charge && Since==-8) BellbreakerSound(TEXT("charge_rumble_v0"),BossAt,.95f);
        if(F.Move==Uppercut && A==8) BellbreakerSound(TEXT("upswing_scrape_v0"),Bell,.8f);
        if(F.Move==Cyclone && Since==0) BellbreakerSound(TEXT("cyclone_whoosh_v0"),BossAt,1.f);
        if(F.Move==Toll && Since==0)
        {
            BellbreakerSound(TEXT("toll_ring_v0"),BossAt,1.f); GroundPulse(BossAt,.55f);
            FBellbreakerWave Wave; Wave.Center=Floor; Wave.Start=T; Wave.bToll=true; R.Waves.Add(Wave);
            for(int32 K=0;K<14;++K)
            {
                const float Ang=2*PI*K/14.f; const FVector Out(FMath::Cos(Ang),FMath::Sin(Ang),0);
                BellbreakerFx(FWardenBellbreakerView::FxDust,Floor+Out*120+FVector(0,0,60),80,300,1.0f,Out*700,20);
            }
        }
        if(F.Move==Fling && Since==0)
        {
            BellbreakerSound(TEXT("slag_fling_v0"),Bell,.9f); BellbreakerSound(TEXT("ember_whoosh_v0"),Bell,.7f);
            BellbreakerFx(FWardenBellbreakerView::FxFire,Bell,70,190,.4f,FVector::ZeroVector,60); BellbreakerSparks(Bell,18,420);
            // Three marks: on the player and either side of them, across the line from the boss.
            const FVector Target=Player->GetActorLocation(), Across=FVector::CrossProduct((Target-BossAt).GetSafeNormal2D(),FVector::UpVector);
            for(int32 K=0;K<SlagCount;++K)
            {
                FBellbreakerSlag S; S.From=Bell; S.Launch=T; S.Land=T+SlagFlight+K*6;
                S.At=Target+Across*(K-1)*230.f; S.At.Z=0; R.Slag.Add(S);
            }
        }
        if(F.Move==Knell && (Since==0 || Since==KnellGap || Since==2*KnellGap))
        {
            const FVector Centre=Floor+Yaw.RotateVector(QuakeImpactOffset());
            const int32 K=Since/KnellGap;
            BellbreakerSound(K==2 ? TEXT("bell_slam_ground_v0") : TEXT("bell_slam_ground_v1"),Centre,.9f+.05f*K);
            if(K==0) BellbreakerSound(TEXT("knell_triple_v0"),Centre,.8f);
            GroundPulse(Centre,.7f+.15f*K); Impact(3+K,0.f);
            Blast(Centre,KnellRadius+40.f*K,KnellDamage,TEXT("DEATH KNELL | Three slams; the last sends a crest."));
            BellbreakerBurst(Centre,.8f+.2f*K,K!=1);
            if(K==2) BellbreakerSound(TEXT("rubble_settle_v1"),Centre,.7f);
            if(K==2) { FBellbreakerWave Wave; Wave.Center=Centre; Wave.Start=T; R.Waves.Add(Wave); BellbreakerSound(TEXT("shockwave_v0"),Centre,.9f); }
        }
        if((F.Move==Quake || F.Move==BellBreaks) && Since==0)
        {
            // Impact: the blast, then the shockwave crest(s) from where the bell lands.
            const FVector Centre=Floor+Yaw.RotateVector(QuakeImpactOffset());
            BellbreakerSound(F.Move==Quake ? TEXT("bell_slam_ground_v0") : TEXT("bell_crack_v0"),Centre,1.f);
            BellbreakerSound(TEXT("shockwave_v0"),Centre,.9f);
            GroundPulse(Centre,F.Move==Quake ? 1.f : 1.10f);
            BellbreakerBurst(Centre,F.Move==Quake ? 1.35f : 1.6f,true);
            BellbreakerSound(TEXT("rubble_settle_v0"),Centre,.75f);
            if(F.Move==BellBreaks)
            {
                BellbreakerSound(TEXT("ember_whoosh_v1"),Centre,.9f);
                for(int32 K=0;K<6;++K)
                    BellbreakerFx(FWardenBellbreakerView::FxFire,Centre+FVector(FMath::FRandRange(-90.f,90.f),FMath::FRandRange(-90.f,90.f),60+40*K),
                                  80,200,.6f+.06f*K,FVector(0,0,120),160);
            }
            Impact(5,0.f);
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
        const FVector2D ThreatBand=W.Band(T);
        const float Dist=FVector::Dist2D(Player->GetActorLocation(),W.Center);
        if(Dist<ThreatBand.X || Dist>ThreatBand.Y) continue;   // the crest is not over the player this tick
        if(!W.bToll && Player->AirLift>AirborneLift) { R.LastOutcome=EBellbreakerOutcome::Jumped; continue; }
        if(P.Invulnerable()) { R.LastOutcome=EBellbreakerOutcome::Rolled; continue; }
        W.PlayerResolved=true;
        if(W.bToll)
        {
            // The toll is sound: it fills the air, so a jump does not clear it. Damage and a flinch, no stun.
            const float Before=P.Health;
            if(P.Damage(TollDamage,true)) { BossDamage+=Before-P.Health; Flinched(W.Center); }
            R.LastOutcome=EBellbreakerOutcome::Blasted;
            LastEvent=TEXT("THE TOLL | Roll through the ring; jumping will not clear it.");
            continue;
        }
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
        if(!W.PlayerResolved && T>W.Start && FVector::Dist2D(Player->GetActorLocation(),W.Center)+CrestHalfWidth<W.Radius(T)
           && FVector::Dist2D(Player->GetActorLocation(),W.Center)+CrestHalfWidth>=W.Radius(T-1))
        {
            W.PlayerResolved=true; ++R.Avoided;
            if(R.LastOutcome!=EBellbreakerOutcome::Jumped && R.LastOutcome!=EBellbreakerOutcome::Rolled) R.LastOutcome=EBellbreakerOutcome::OutOfReach;
        }
    R.Waves.RemoveAll([&](const FBellbreakerWave& W){ return T>=W.Start && !W.Live(T); });
    // Slag landings: each glob hits its mark once.
    for(const auto& S:R.Slag)
        if(T==S.Land)
        {
            BellbreakerSound(S.Land%2 ? TEXT("slag_land_v0") : TEXT("slag_land_v1"),S.At,.8f);
            BellbreakerSound(S.Land%2 ? TEXT("slag_sizzle_v0") : TEXT("slag_sizzle_v1"),S.At,.6f);
            BellbreakerFx(FWardenBellbreakerView::FxPuddle,FVector(S.At.X,S.At.Y,0),SlagRadius*1.6f,SlagRadius*2.1f,3.2f);
            BellbreakerFx(FWardenBellbreakerView::FxFire,FVector(S.At.X,S.At.Y,40),60,170,.45f,FVector::ZeroVector,80);
            BellbreakerSparks(FVector(S.At.X,S.At.Y,0),14,380);
            if(P.Alive() && FVector::Dist2D(Player->GetActorLocation(),S.At)<=SlagRadius)
            {
                const float Before=P.Health;
                if(P.Damage(SlagDamage,true)) { BossDamage+=Before-P.Health; Flinched(S.At); LastEvent=TEXT("SLAG FLING | Leave the glowing marks."); }
            }
        }
    R.Slag.RemoveAll([&](const FBellbreakerSlag& S){ return T>=S.Land; });
}

// ---------------------------------------------------------------- presentation (no rules below)
namespace
{
struct FBBClip { int32 Move; const TCHAR* Clip; float Impact; };
const FBBClip StrikeClips[]={
    {WardenBellbreaker::HammerFall,TEXT("hammer_overhead_s0"),1.05f},
    {WardenBellbreaker::Sweep,TEXT("sweep_rl_s1"),.6f},   // s0 sprawled almost flat (2026-11-18 study)
    {WardenBellbreaker::Quake,TEXT("bell_quake_s0"),1.18f},
    {WardenBellbreaker::BellBreaks,TEXT("hammer_overhead_s1"),1.05f},
    // Readiness pass: existing retargeted takes; impact -1 = 45% of the take. Legs, hips and spine are
    // layered over the planted stance and the anatomy governor limits every pose (WardenBellbreaker.cpp 3b).
    {WardenBellbreaker::Backhand,TEXT("sweep_lr_s1"),-1.f},
    {WardenBellbreaker::Stamp,TEXT("stamp_s0"),-1.f},
    {WardenBellbreaker::Charge,TEXT("shoulder_charge_s0"),-1.f},
    {WardenBellbreaker::Uppercut,TEXT("cut_heavy_s0"),-1.f},
    {WardenBellbreaker::Toll,TEXT("toll_s0"),-1.f},
    {WardenBellbreaker::Fling,TEXT("fling_s0"),-1.f},
    {WardenBellbreaker::HeldNote,TEXT("hammer_overhead_s0"),1.05f},
    {WardenBellbreaker::Cyclone,TEXT("sweep_rl_s1"),.6f},
    {WardenBellbreaker::Knell,TEXT("bell_quake_s0"),1.18f},
    {WardenBellbreaker::StridingFall,TEXT("hammer_overhead_s1"),1.05f}};
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
    USkeletalMesh* Rig=nullptr;
    const FString RequestedSkin=FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_BB_SKIN"));
    const bool PriorForge=FParse::Param(FCommandLine::Get(),TEXT("BossLabPriorForgeSkin"));
    if(!PriorForge && (RequestedSkin.IsEmpty() || RequestedSkin==TEXT("bellfounder")))
    {
        Rig=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/BossLab/Bellbreaker/Bellfounder/SKM_Bellfounder"),nullptr,LOAD_Quiet|LOAD_NoWarn);
        if(!Rig && !RequestedSkin.IsEmpty()) UE_LOG(LogTemp,Warning,TEXT("BOSSLAB bellfounder skin missing, using installed forge skin"));
    }
    else if(RequestedSkin==TEXT("weathered"))
        Rig=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/BossLab/Bellbreaker/WeatheredStudy/SKM_BellbreakerWeathered"),nullptr,LOAD_Quiet|LOAD_NoWarn);
    if(!Rig && !PriorForge)
        Rig=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/BossLab/Bellbreaker/ForgeShoulder/SKM_BellbreakerForgeShoulder"),nullptr,LOAD_Quiet|LOAD_NoWarn);
    if(!Rig) Rig=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/BossLab/Bellbreaker/ForgeSkin/SKM_BellbreakerForgeSkin"),nullptr,LOAD_Quiet|LOAD_NoWarn);
    if (!Rig) Rig=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/BossLab/Bellbreaker/Rig/SKM_BellbreakerRig"),nullptr,LOAD_Quiet|LOAD_NoWarn);
    if (Rig) UE_LOG(LogTemp, Display, TEXT("BOSSLAB forge skin: %s"), *Rig->GetPathName());
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
    BBView.Soles.Fit(Body);
    UE_LOG(LogTemp,Display,TEXT("BOSSLAB tread landmarks %d"),BBView.Soles.Samples.Num());
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
    if(auto* ShadeMat=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/BossLab/Bellbreaker/FX/M_BB_SoleShade"),nullptr,LOAD_Quiet|LOAD_NoWarn); ShadeMat && Plane && bForgeArena)
    {
        for(int32 Side=0;Side<2;++Side)
        {
            auto* Shade=NewObject<UStaticMeshComponent>(View);
            Shade->SetStaticMesh(Plane); Shade->SetMaterial(0,ShadeMat);
            Shade->SetMobility(EComponentMobility::Movable);
            Shade->SetCollisionEnabled(ECollisionEnabled::NoCollision);
            Shade->SetCastShadow(false); Shade->SetVisibility(false);
            Shade->SetupAttachment(C); Shade->SetAbsolute(true,true,true);
            Shade->RegisterComponent(); View->AddInstanceComponent(Shade);
            Shade->CreateDynamicMaterialInstance(0);
            BBView.SoleShades[Side]=Shade;
        }
    }
    if(auto* SparkMat=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/BossLab/Regent/M_RegentSpark"),nullptr,LOAD_Quiet|LOAD_NoWarn); SparkMat && Plane)
    {
        auto* S=NewObject<UInstancedStaticMeshComponent>(View,TEXT("BellbreakerSparks"));
        S->SetStaticMesh(Plane); S->SetMaterial(0,SparkMat); S->SetCollisionEnabled(ECollisionEnabled::NoCollision); S->SetCastShadow(false);
        S->SetupAttachment(C); S->RegisterComponent(); S->SetUsingAbsoluteLocation(true); S->SetUsingAbsoluteRotation(true); S->SetUsingAbsoluteScale(true);
        S->SetWorldTransform(FTransform::Identity); View->AddInstanceComponent(S);
        for(int32 I=0;I<FWardenBellbreakerView::MaxSparks;++I) S->AddInstance(FTransform(FQuat::Identity,FVector(0,0,-10000),FVector(0)),true);
        BBView.Sparks=S;
    }
    // Effects pass (2026-11-23): one instanced plane layer per effect kind with a per-instance fade
    // (PerInstanceCustomData 0). Materials and FLUX textures from ue_import_bellbreaker_fx_pass.py; absent ones are skipped.
    {
        static const TCHAR* const FxMats[FWardenBellbreakerView::FxKinds]={TEXT("M_BB_FxCrack"),TEXT("M_BB_FxDust"),TEXT("M_BB_FxFire"),TEXT("M_BB_FxPuddle")};
        static const int32 FxCap[FWardenBellbreakerView::FxKinds]={10,64,56,8};
        for(int32 K=0;K<FWardenBellbreakerView::FxKinds && Plane;++K)
        {
            auto* Mat=LoadObject<UMaterialInterface>(nullptr,*FString::Printf(TEXT("/Game/BossLab/Bellbreaker/FX/%s"),FxMats[K]),nullptr,LOAD_Quiet|LOAD_NoWarn);
            if(!Mat) continue;
            auto* L=NewObject<UInstancedStaticMeshComponent>(View,*FString::Printf(TEXT("BellbreakerFx%d"),K));
            L->SetStaticMesh(Plane); L->SetMaterial(0,Mat); L->SetCollisionEnabled(ECollisionEnabled::NoCollision); L->SetCastShadow(false);
            L->SetNumCustomDataFloats(1);
            L->SetupAttachment(C); L->RegisterComponent(); L->SetUsingAbsoluteLocation(true); L->SetUsingAbsoluteRotation(true); L->SetUsingAbsoluteScale(true);
            L->SetWorldTransform(FTransform::Identity); View->AddInstanceComponent(L);
            for(int32 I=0;I<FxCap[K];++I) L->AddInstance(FTransform(FQuat::Identity,FVector(0,0,-10000),FVector(0)),true);
            BBView.Fx[K].SetNum(FxCap[K]); BBView.FxLayer[K]=L;
        }
    }
    for(const TCHAR* N:{TEXT("idle_hammer_s0"),TEXT("walk_hammer_s0"),TEXT("stun_s1"),TEXT("stun_kneel_s0"),TEXT("hammer_overhead_s0"),TEXT("sweep_rl_s1"),TEXT("bell_quake_s0"),TEXT("hammer_overhead_s1"),
                        TEXT("sweep_lr_s1"),TEXT("stamp_s0"),TEXT("shoulder_charge_s0"),TEXT("cut_heavy_s0"),TEXT("toll_s0"),TEXT("fling_s0")})
        if(UAnimSequence* A=BBClip(N)) { BellbreakerClips.Add(N,A); SfxKeepAlive.Add(A); }
    for(const TCHAR* Alias:{TEXT("BB_ForgeGait"),TEXT("BB_ForgePress")})
    {
        const FString Path=FString::Printf(TEXT("/Game/BossLab/Bellbreaker/MotionStudy20261120/Anim/%s"),Alias);
        if(UAnimSequence* Sequence=LoadObject<UAnimSequence>(nullptr,*Path,nullptr,LOAD_Quiet|LOAD_NoWarn))
        {
            BellbreakerClips.Add(Alias,Sequence);
            SfxKeepAlive.Add(Sequence);
            UE_LOG(LogTemp,Display,TEXT("BOSSLAB smith motion selected %s length %.3fs"),*Sequence->GetName(),Sequence->GetPlayLength());
        }
    }
    for(const TCHAR* N:{TEXT("clapper_tell_v0"),TEXT("bell_whoosh_v0"),TEXT("bell_scrape_v0"),TEXT("bell_scrape_v1"),TEXT("bell_slam_ground_v0"),TEXT("bell_slam_ground_v1"),TEXT("shockwave_v0"),
                        TEXT("bell_crack_v0"),TEXT("bell_crack_v1"),TEXT("stun_ring_v0"),TEXT("stun_ring_v1"),TEXT("bell_hit_body_v0"),TEXT("bell_hit_anvil_v0"),TEXT("bell_hit_anvil_v1"),
                        TEXT("toll_ring_v0"),TEXT("toll_ring_v1"),TEXT("stamp_quake_v0"),TEXT("stamp_quake_v1"),TEXT("slag_fling_v0"),TEXT("slag_land_v0"),TEXT("slag_land_v1"),
                        TEXT("cyclone_whoosh_v0"),TEXT("charge_rumble_v0"),TEXT("upswing_scrape_v0"),TEXT("knell_triple_v0"),
                        TEXT("slag_sizzle_v0"),TEXT("slag_sizzle_v1"),TEXT("rubble_settle_v0"),TEXT("rubble_settle_v1"),TEXT("ember_whoosh_v0"),
                        TEXT("ember_whoosh_v1"),TEXT("giant_footstep_v0"),TEXT("giant_footstep_v1")})
        if(USoundBase* S=LoadObject<USoundBase>(nullptr,*FString::Printf(TEXT("/Game/BossLab/Bellbreaker/Sound/S_%s"),N),nullptr,LOAD_Quiet|LOAD_NoWarn)) { BellbreakerSounds.Add(N,S); SfxKeepAlive.Add(S); }
    const int32 WeaponSounds=BellbreakerSounds.Num();
    for(const TCHAR* N:{TEXT("Challenge"),TEXT("PhaseBreak"),TEXT("Defeat")})
        if(auto* S=LoadObject<USoundBase>(nullptr,*FString::Printf(TEXT("/Game/BossLab/Bellbreaker/Dialogue/S_BB_%s"),N),nullptr,LOAD_Quiet|LOAD_NoWarn))
        { BellbreakerSounds.Add(N,S); SfxKeepAlive.Add(S); }
    UE_LOG(LogTemp,Display,TEXT("BOSSLAB forge dialogue bank: %d/3 loaded"),BellbreakerSounds.Num()-WeaponSounds);
    auto* RingMat=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/BossLab/Bellbreaker/FX/M_BB_Shockwave"),nullptr,LOAD_Quiet|LOAD_NoWarn);
    for(int32 I=0;I<8 && Plane && RingMat;++I)
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
    // Slag Fling globs: glowing spheres on their engine arcs (presentation of FBellbreakerSlag).
    auto* Sphere=LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Sphere"),nullptr,LOAD_Quiet|LOAD_NoWarn);
    auto* Molten=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/BossLab/Regent/M_RegentFlame"),nullptr,LOAD_Quiet|LOAD_NoWarn);
    for(int32 I=0;I<WardenBellbreaker::SlagCount && Sphere;++I)
    {
        auto* G=NewObject<UStaticMeshComponent>(View);
        G->SetStaticMesh(Sphere); if(Molten) G->SetMaterial(0,Molten);
        G->SetMobility(EComponentMobility::Movable); G->SetCollisionEnabled(ECollisionEnabled::NoCollision); G->SetCastShadow(false);
        G->SetupAttachment(C); G->SetAbsolute(true,true,true); G->RegisterComponent(); View->AddInstanceComponent(G);
        G->SetVisibility(false); BellbreakerGlobs.Add(G);
    }
    // Forge dressing from the readiness pass (TRELLIS.2 props, ue_import_readiness.py): a fallen cracked bell,
    // a clay casting mould and a hanging test bell on its oak frame, at the edges of the 16 x 18 m floor so
    // they never sit in the fight. Presentation only, no collision; absent assets are simply skipped.
    if(bForgeArena && !GIsAutomationTesting)
    {
        struct FProp { const TCHAR* Mesh; FVector At; float Yaw, Scale; };
        const FProp Props[]={{TEXT("SM_BB_CrackedBell"),FVector(-640,760,0),35,1.f},{TEXT("SM_BB_BellMould"),FVector(660,-780,0),-20,1.f},
                             {TEXT("SM_BB_BellFrame"),FVector(-760,-520,0),0,.85f},{TEXT("SM_BB_BellShards"),FVector(-420,820,0),10,.65f},
                             {TEXT("SM_BB_Crucible"),FVector(760,420,0),40,1.f}};
        int32 Placed=0;
        for(const auto& Pr:Props)
            if(auto* Mesh=LoadObject<UStaticMesh>(nullptr,*FString::Printf(TEXT("/Game/BossLab/Bellbreaker/ArenaProps/%s"),Pr.Mesh),nullptr,LOAD_Quiet|LOAD_NoWarn))
            {
                auto* A=W->SpawnActor<AStaticMeshActor>(Pr.At,FRotator(0,Pr.Yaw,0),Params);
                A->GetStaticMeshComponent()->SetStaticMesh(Mesh); A->SetActorScale3D(FVector(Pr.Scale));
                A->Tags.Add(TEXT("SmelteryDressing")); WardenNeverCollide(A); ++Placed;
            }
        UE_LOG(LogTemp,Display,TEXT("BOSSLAB BELLBREAKER forge props placed %d/%d"),Placed,int32(UE_ARRAY_COUNT(Props)));
    }
    WardenNeverCollide(View);   // again: hammer and sparks were added after the first call
    for(auto& R:BellbreakerRings) if(R.IsValid()) WardenNeverCollide(R->GetOwner());
    for(auto& R:BellbreakerRings) if(R.IsValid()) UE_LOG(LogTemp,Display,TEXT("BOSSLAB BELLBREAKER ring actor %s (never collides)"),*R->GetOwner()->GetName());
    UE_LOG(LogTemp,Display,TEXT("BOSSLAB BELLBREAKER greybox view: clips %d (8 base, 2 refit), sounds %d/14, rings %d, hammer %d, sparks %d"),BellbreakerClips.Num(),WeaponSounds,BellbreakerRings.Num(),BellbreakerHammer.IsValid(),BBView.Sparks.IsValid());
}

namespace
{
// Presentation constants, world cm unless noted. Mannequin-space (component) values are divided by Scale.
#if WITH_EDITOR
// Sample actual skin-weighted LOD triangles after all IK. Bone lengths alone cannot
// detect a folding sleeve or wrist. This diagnostic is only called by the forge study.
void TraceBellbreakerSkin(UPoseableMeshComponent* Body,int32 Move,float Age)
{
    const int32 LOD=Body->GetPredictedLODLevel();
    const FSkeletalMeshRenderData* Data=Body->GetSkeletalMeshRenderData();
    if(!Data || !Data->LODRenderData.IsValidIndex(LOD)) return;
    const auto& Mesh=Data->LODRenderData[LOD];
    const auto& BindPositions=Mesh.StaticVertexBuffers.PositionVertexBuffer;
    const auto* Indices=Mesh.MultiSizeIndexContainer.GetIndexBuffer();
    auto* Weights=Body->GetSkinWeightBuffer(LOD);
    if(!Indices || !Indices->Num() || !BindPositions.GetVertexData() || !Weights || !Weights->GetDataVertexBuffer()->GetWeightData()) return;
    TArray<FMatrix44f> Matrices;
    Body->GetCurrentRefToLocalMatrices(Matrices,LOD);
    if(Matrices.IsEmpty()) return;
    TArray<float> Ratios;
    for(int32 I=0;I+2<Indices->Num();I+=3*83)
    {
        const int32 A=Indices->Get(I), B=Indices->Get(I+1), C=Indices->Get(I+2);
        const FVector3f U=BindPositions.VertexPosition(B)-BindPositions.VertexPosition(A), V=BindPositions.VertexPosition(C)-BindPositions.VertexPosition(A);
        const float Area=FVector3f::CrossProduct(U,V).Size();
        // Exclude near-collinear source slivers where an area ratio is unstable.
        if(Area<.04f || Area<.13f*FMath::Max3(U.SizeSquared(),V.SizeSquared(),(U-V).SizeSquared())) continue;
        const auto Skin=[&](int32 Id){return USkinnedMeshComponent::GetSkinnedVertexPosition(Body,Id,Mesh,*Weights,Matrices);};
        const FVector3f P=Skin(A);
        Ratios.Add(FVector3f::CrossProduct(Skin(B)-P,Skin(C)-P).Size()/Area);
    }
    if(Ratios.IsEmpty()) return;
    Ratios.Sort();
    int32 BelowHalf=0;
    while(BelowHalf<Ratios.Num() && Ratios[BelowHalf]<.5f) ++BelowHalf;
    UE_LOG(LogTemp,Display,TEXT("BOSSLAB skin move %d age %.2f lod %d triangles %d p01 %.3f p05 %.3f median %.3f belowHalf %d"),
        Move,Age,LOD,Ratios.Num(),Ratios[Ratios.Num()/100],Ratios[Ratios.Num()/20],Ratios[Ratios.Num()/2],BelowHalf);
}
#endif
constexpr float TorsoHand=27, TorsoElbow=23;   // mannequin cm: hands/elbows kept outside the torso axis

// Anatomy limits, degrees. The rig faces component +Y; at rest every bone's lateral axis is component +X.
constexpr float GovMinHip=.78f;
constexpr float GovPelvisYaw=28.f, GovChestTwist=32.f, GovHeadYaw=18.f, GovNeckTurn=40.f, GovHeadDown=22.f, GovHeadUp=18.f;
template<typename FIdx,typename FRotate>
void GovernBellbreakerAnatomy(TArray<FTransform>& Local,TArray<FTransform>& CS,const FReferenceSkeleton& Ref,FIdx&& Idx,FRotate&& RotateCS,
                              bool bFreePelvis,FWardenBellbreakerView::FGovernor& Stats)
{
    // Rest component-space rotations, to read each bone's lateral/forward axes in its own frame.
    TArray<FQuat,TInlineAllocator<128>> Rest; Rest.SetNum(Local.Num());
    for(int32 I=0;I<Local.Num();++I) { const int32 P=Ref.GetParentIndex(I); const FQuat Q=Ref.GetRefBonePose()[I].GetRotation(); Rest[I]=P<0 ? Q : Rest[P]*Q; }
    auto Lateral=[&](int32 I){ return CS[I].GetRotation().RotateVector(Rest[I].UnrotateVector(FVector(1,0,0))); };
    auto Forward=[&](int32 I){ return CS[I].GetRotation().RotateVector(Rest[I].UnrotateVector(FVector(0,1,0))); };
    auto YawOf=[](const FVector& L){ return FMath::RadiansToDegrees(FMath::Atan2(L.Y,L.X)); };   // 0 = facing
    auto Turn=[&](int32 I,float Degrees){ if(I>=0 && FMath::Abs(Degrees)>.01f) RotateCS(I,FQuat(FVector::UpVector,FMath::DegreesToRadians(Degrees))); };
    const int32 Pelvis=Idx(TEXT("pelvis"));
    if(Pelvis<0) return;
    // 1. The hips lead part of a big upper-body turn (as a real heavy swing does), so the waist twists less,
    //    but never more than GovPelvisYaw from the facing. Outside the gait the feet are not planted.
    if(bFreePelvis)
    {
        const float Yaw=YawOf(Lateral(Pelvis));
        const int32 Top=Idx(TEXT("spine_05"));
        const float Chest=Top>=0 ? YawOf(Lateral(Top)) : Yaw;
        Stats.WorstPelvisIn=FMath::Max(Stats.WorstPelvisIn,FMath::Abs(Yaw));
        const float Want=FMath::Clamp(Yaw+.4f*FMath::FindDeltaAngleDegrees(Yaw,Chest),-GovPelvisYaw,GovPelvisYaw);
        Turn(Pelvis,FMath::FindDeltaAngleDegrees(Yaw,Want));
    }
    // 2. Chest twist relative to the hips: capped, then spread evenly up the spine (no single-bone wringing).
    const TCHAR* SpineNames[]={TEXT("spine_01"),TEXT("spine_02"),TEXT("spine_03"),TEXT("spine_04"),TEXT("spine_05")};
    static const float Share[]={.14f,.20f,.22f,.22f,.22f};
    int32 Spine[5]; int32 Found=0;
    for(int32 K=0;K<5;++K) { Spine[K]=Idx(SpineNames[K]); Found+=Spine[K]>=0; }
    if(Found==5)
    {
        const float Hip=YawOf(Lateral(Pelvis));
        const float Total=FMath::FindDeltaAngleDegrees(Hip,YawOf(Lateral(Spine[4])));
        Stats.WorstTwistIn=FMath::Max(Stats.WorstTwistIn,FMath::Abs(Total));
        const float Target=FMath::Clamp(Total,-GovChestTwist,GovChestTwist);
        float Accum=0;
        for(int32 K=0;K<5;++K)
        {
            Accum+=Target*Share[K];
            const float Now=FMath::FindDeltaAngleDegrees(Hip,YawOf(Lateral(Spine[K])));
            Turn(Spine[K],Accum-Now);
        }
        Stats.WorstTwistOut=FMath::Max(Stats.WorstTwistOut,FMath::Abs(FMath::FindDeltaAngleDegrees(Hip,YawOf(Lateral(Spine[4])))));
    }
    // 3. Head faces forward (toward the player he is fighting), within the neck's turn from the chest,
    //    and is never buried in the chest or thrown back.
    const int32 Neck1=Idx(TEXT("neck_01")), Neck2=Idx(TEXT("neck_02")), Head=Idx(TEXT("head"));
    if(Neck1>=0 && Neck2>=0 && Head>=0 && Found==5)
    {
        const float Chest=YawOf(Lateral(Spine[4]));
        const float Now=YawOf(Lateral(Head));
        float Want=FMath::Clamp(Now,-GovHeadYaw,GovHeadYaw);
        Want=Chest+FMath::Clamp(FMath::FindDeltaAngleDegrees(Chest,Want),-GovNeckTurn,GovNeckTurn);
        const float Fix=FMath::FindDeltaAngleDegrees(Now,Want);
        Stats.WorstHeadYawIn=FMath::Max(Stats.WorstHeadYawIn,FMath::Abs(Now));
        Turn(Neck1,Fix*.3f); Turn(Neck2,Fix*.3f); Turn(Head,Fix*.4f);
        const FVector Fwd=Forward(Head);
        const float Elevation=FMath::RadiansToDegrees(FMath::Asin(FMath::Clamp(Fwd.Z,-1.,1.)));
        const float Pitch=Elevation<-GovHeadDown ? -GovHeadDown-Elevation : Elevation>GovHeadUp ? GovHeadUp-Elevation : 0.f;
        Stats.WorstHeadPitchIn=FMath::Max(Stats.WorstHeadPitchIn,FMath::Abs(Elevation));
        const FVector Axis=FVector::CrossProduct(Fwd,FVector::UpVector).GetSafeNormal();
        if(FMath::Abs(Pitch)>.01f && !Axis.IsNearlyZero())
            for(const TPair<int32,float> B:{TPair<int32,float>(Neck1,.3f),TPair<int32,float>(Neck2,.3f),TPair<int32,float>(Head,.4f)})
                RotateCS(B.Key,FQuat(Axis,FMath::DegreesToRadians(Pitch*B.Value)));
        Stats.WorstHeadPitchOut=FMath::Max(Stats.WorstHeadPitchOut,FMath::Abs(FMath::RadiansToDegrees(FMath::Asin(FMath::Clamp(Forward(Head).Z,-1.,1.)))));
    }
}
}
void AWardenArenaMode::AnimateBellbreakerView(float Seconds)
{
    using namespace WardenBellbreaker;
    ASkeletalMeshActor* View=BellbreakerView.Get();
    UPoseableMeshComponent* Body=BBView.Body.Get();
    if(!View || !Warden || !Body) return;
    auto& V=BBView;
    const float Dt=V.LastTime<0 ? 0.f : FMath::Clamp(Seconds-V.LastTime,0.f,.1f); V.LastTime=Seconds;
    V.FxClock=Seconds;
    const float PreviousWalkPelvisZ=Body->GetSocketLocation(TEXT("pelvis")).Z;
    const FVector At=Warden->GetActorLocation();
    const FVector Floor(At.X,At.Y,0);
    const bool SpinStrike=Warden->Fight.Alive() && Warden->Fight.Action==EWardenAction::Strike && Warden->Fight.Move==Cyclone;
    const float Spin=SpinStrike ? CycloneSpin(Cyclone,Warden->Fight.Age+FMath::Clamp(CombatAccumulator/WardenRules::Step,0.,1.)) : 0.f;
    View->SetActorLocationAndRotation(FVector(At.X,At.Y,At.Z-90*Scale),FRotator(0,Warden->GetActorRotation().Yaw-90+Spin,0));   // rig faces +Y
    const FRotator Yaw(0,Warden->GetActorRotation().Yaw,0);
    // The body's own facing: the actor's, plus the Cyclone's presentation spin. Everything that aims a
    // body part or the weapon relative to "his front" uses this, never the unspun actor yaw.
    const FRotator WYaw(0,Yaw.Yaw+Spin,0);
    const auto& F=Warden->Fight;
    const bool Striking=F.Alive() && F.Action==EWardenAction::Strike && IsBellbreaker(F.Move);
    const float AgeF=F.Age+FMath::Clamp(CombatAccumulator/WardenRules::Step,0.,1.);

    // The two blast moves land on the first active tick. Their visual downstroke
    // occupies the last part of anticipation; the fixed-step blast is unchanged.
    const bool Slam=Striking && (F.Move==Quake || F.Move==BellBreaks);
    auto* C=View->GetSkeletalMeshComponent();
    // ---- 1. Clip and clock (unchanged choice; time-warped strikes) -------------------------------------
    UAnimSequence* Clip=nullptr; float Clock=0; bool GaitWrapped=false;
    bool GroundGait=false;
    constexpr float GiantStride=216.f; // centimetres travelled in two steps
    const float FrameTravel=V.HasPreviousFloor ? FVector::Dist2D(Floor,V.PreviousFloor) : 0.f;
    const float FrameYaw=V.HasPreviousFloor ? FMath::FindDeltaAngleDegrees(V.WalkYaw,float(Yaw.Yaw)) : 0.f;
    V.WalkYaw=Yaw.Yaw;
    V.WalkTurnRate=FMath::FInterpTo(V.WalkTurnRate,Dt>0 ? FrameYaw/Dt : 0.f,Dt,10.f);
    V.WalkSpeed=FMath::FInterpTo(V.WalkSpeed,Warden->MoveVelocity.Size2D(),Dt,8.f);
    V.PreviousFloor=Floor; V.HasPreviousFloor=true;
    auto Get=[&](const TCHAR* N){ UAnimSequence* const* A=BellbreakerClips.Find(N); return A ? *A : nullptr; };
    if(!F.Alive())
    {
        Clip=Get(TEXT("stun_kneel_s0"));
        // The smith yields to the weight on one knee. Hold the kneel; the
        // second half of this forge-authored take would stand him back up.
        if(Clip) Clock=Smooth(Warden->DeathAge/64.f)*Clip->GetPlayLength()*.54f;
    }
    else if(Striking)
    {
        const FBBClip* Entry=nullptr;
        // Keep the phase-break tell, then blend to the braced contact pose:
        // the upright overhead clip leaves the ground target outside arm reach.
        const int32 PoseMove=(F.Move==BellBreaks && AgeF>=F.Definition().Windup-40) ? int32(Quake) : F.Move;
        for(const auto& E:StrikeClips) if(E.Move==PoseMove) Entry=&E;
        Clip=Entry ? Get(Entry->Clip) : nullptr;
        if(Clip)
        {
            const auto& D=F.Definition();
            const float Len=Clip->GetPlayLength(), Ti=FMath::Min(Entry->Impact>0 ? Entry->Impact : Len*.45f,Len-.2f);
            // Slow the hoist, show the shoulders taking the load, then commit the
            // last fifth of clip time to a crisp drop rather than uniform slow motion.
            const float U=FMath::Clamp(AgeF/D.Windup,0.f,1.f);
            const float Lift=U<.67f ? .76f*Smooth(U/.67f) : U<.81f ? .76f+.035f*Smooth((U-.67f)/.14f) : .795f+.205f*Smooth((U-.81f)/.19f);
            Clock=AgeF<D.Windup ? Ti*Lift
                : AgeF<D.Windup+D.Active ? Ti+.1f*(AgeF-D.Windup)/D.Active
                : FMath::Lerp(Ti+.1f,Len*.98f,FMath::Clamp((AgeF-D.Windup-D.Active)/D.Recovery,0.f,1.f));
            if(Slam && AgeF>=D.Windup-24.f && AgeF<D.Windup)
            {
                // Both blast moves use the braced quake clip for contact.
                // Its shoulders cover most of their travel at 0.99–1.15 s.
                // Pace the trunk by measured travel across 0.40 s; the bell
                // keeps its separate, faster authoritative impact arc.
                const float StartU=(D.Windup-24.f)/D.Windup;
                const float StartTime=1.18f*(.76f+.035f*Smooth((StartU-.67f)/.14f));
                const FVector2f Knots[]={{0.f,StartTime},{.10f,.955f},{.20f,.990f},{.36f,1.030f},
                    {.55f,1.068f},{.76f,1.111f},{.90f,1.148f},{1.f,1.180f}};
                const float Phase=(AgeF-D.Windup+24.f)/24.f;
                for(int32 J=1;J<UE_ARRAY_COUNT(Knots);++J)
                {
                    if(Phase>Knots[J].X) continue;
                    const auto& A=Knots[J-1]; const auto& B=Knots[J];
                    Clock=Ti/1.18f*FMath::Lerp(A.Y,B.Y,(Phase-A.X)/(B.X-A.X));
                    break;
                }
            }
        }
    }
    else if(F.Action==EWardenAction::Hurt)
    {
        Clip=Get(TEXT("stun_s1"));
        if(Clip) Clock=FMath::Lerp(.05f,Clip->GetPlayLength()*.85f,FMath::Clamp(AgeF/WardenRules::BossHurtTicks,0.f,1.f));
    }
    else
    {
        const float Speed=Warden->MoveVelocity.Size2D();
        // Start below the old 40 cm/s clip switch and retain small stepping
        // during a pivot. Turning the capsule must not drag two frozen soles.
        const bool TakingStep=Speed>(V.WasGroundGait ? 8.f : 18.f) ||
            FMath::Abs(V.WalkTurnRate)>(V.WasGroundGait ? 9.f : 16.f);
        UAnimSequence* Gait=TakingStep ? Get(TEXT("BB_ForgeGait")) : nullptr;
        Clip=Gait ? Gait : Get(Speed>40.f ? TEXT("walk_hammer_s0") : TEXT("idle_hammer_s0"));
        if(Clip && Clip->GetPlayLength()>.01f)
        {
            auto* Node=C->GetSingleNodeInstance();
            const bool Continuing=Node && V.LastClip.Get()==Clip;
            if(Gait)
            {
                // Frames 19 and 69 are matching phases on the measured 120-frame
                // 30Hz source. Account for the imported sequence's duration.
                const float FrameSeconds=Clip->GetPlayLength()/119.f;
                const float Start=19.f*FrameSeconds, Span=50.f*FrameSeconds;
                // The giant's feet travel in two sagittal lanes. Ground
                // distance sets the phase, so a slow approach cannot outrun
                // the boots even when the simulation advances unevenly.
                GroundGait=true;
                const float OldPhase=Continuing ? V.WalkPhase : 0.f;
                // Tangential travel at the boot lane advances a pivot even
                // when actor translation is zero. Teleports do not step.
                const float TurnTravel=FMath::DegreesToRadians(FMath::Abs(FrameYaw))*90.f;
                const float Advance=FrameTravel<100.f ? FMath::Min(.08f,FMath::Max(FrameTravel,TurnTravel)/GiantStride) : 0.f;
                V.WalkPhase=FMath::Fmod(OldPhase+Advance,1.f);
                // The measured source left/right support exchange is .14/.78
                // of the source loop. Map each onto half of the larger stride.
                auto SourcePhase=[](float P)
                {
                    return FMath::Fmod(P<.5f ? .14f+1.28f*P : .78f+.72f*(P-.5f),1.f);
                };
                const float Phase=SourcePhase(V.WalkPhase);
                GaitWrapped=Continuing && Phase<SourcePhase(OldPhase);
                Clock=Start+Span*Phase;
            }
            else
            {
                const float Previous=Continuing ? Node->GetCurrentTime() : 0.f;
                Clock=FMath::Fmod(Previous+Dt*(Speed>40 ? Speed/300.f : 1.f),Clip->GetPlayLength());
            }
        }
    }
    if(!Clip || !C->GetSkeletalMeshAsset()) return;
    if(V.LastClip.Get()!=Clip || GaitWrapped)
    {
        // The source pose can itself be mid-blend when a stagger interrupts.
        // The grip, spine and foot corrections run once on the blended result.
        if(!V.LastSourcePose.IsEmpty())
        {
            Swap(V.Frozen,V.LastSourcePose);
            V.BlendFrom=Seconds;
            V.SourceBlendSeconds=GaitWrapped ? .08f : F.Alive() ? .20f : .30f;
        }
        if(V.LastClip.Get()!=Clip) { V.LastClip=Clip; C->PlayAnimation(Clip,false); }
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
    if(Striking && V.Stance.Num()==Local.Num())
        for(int32 I=0;I<Local.Num();++I)
        {
            const FString N=Ref.GetBoneName(I).ToString();
            const float Contact=Slam ? Smooth((AgeF-F.Definition().Windup+31)/24.f)*
                (1-Smooth((AgeF-F.Definition().Windup-F.Definition().Active-Embed(F.Move))/37.f)) : 0.f;
            // The source hoist spins the shoulder girdle almost 180 degrees
            // away from the weapon. Keep its weight shift in a planted stance,
            // then recover the full deep crouch at the two blast contacts.
            const bool Leg=N.StartsWith(TEXT("thigh"))||N.StartsWith(TEXT("calf"))||N.StartsWith(TEXT("foot"))||N.StartsWith(TEXT("ball"));
            const float Base=N==TEXT("root") || N==TEXT("pelvis") ? .22f : N.StartsWith(TEXT("spine")) ? .28f :
                N.StartsWith(TEXT("clavicle")) ? .45f : Leg ? .60f : 1.f;
            const float W=FMath::Lerp(Base,1.f,Contact);
            if(W<1) { FTransform B; B.Blend(V.Stance[I],Local[I],W); Local[I]=B; }
        }
    // The generated heave has a useful lift, plant and compression, but
    // its legs lift off the floor. Retain the established lower body and
    // sample only local thoracic and clavicle rotations on Hammer Fall.
    UAnimSequence* Heave=Striking && F.Move==HammerFall ? Get(TEXT("BB_ForgePress")) : nullptr;
    float HeaveTime=0.f;
    if(Heave && Heave->GetSkeleton())
    {
        const auto& Def=F.Definition();
        const float LoadEnd=Def.Windup*.78f, Contact=Def.Windup+Def.Active-1.f;
        const float Release=Contact+Embed(F.Move);
        if(AgeF<LoadEnd) HeaveTime=1.50f*Smooth(AgeF/LoadEnd);
        else if(AgeF<Def.Windup) HeaveTime=FMath::Lerp(1.50f,1.80f,Smooth((AgeF-LoadEnd)/(Def.Windup-LoadEnd)));
        else if(AgeF<Contact) HeaveTime=FMath::Lerp(1.80f,2.20f,Smooth((AgeF-Def.Windup)/(Contact-Def.Windup)));
        else if(AgeF<Release) HeaveTime=FMath::Lerp(2.20f,2.56f,Smooth((AgeF-Contact)/(Release-Contact)));
        else HeaveTime=FMath::Lerp(2.56f,119.f/30.f,Smooth((AgeF-Release)/(Def.Total()-Release)));
        HeaveTime*=Heave->GetPlayLength()/(119.f/30.f);
        const FAnimExtractContext Sample(double(HeaveTime),false);
        const auto& Src=Heave->GetSkeleton()->GetReferenceSkeleton();
        for(const FName Bone:{FName(TEXT("spine_02")),FName(TEXT("spine_03")),FName(TEXT("spine_04")),FName(TEXT("spine_05")),FName(TEXT("clavicle_r")),FName(TEXT("clavicle_l"))})
        {
            const int32 Target=Ref.FindBoneIndex(Bone), Source=Src.FindBoneIndex(Bone);
            if(Target<0 || Source<0) continue;
            FTransform Authored=Local[Target];
            Heave->GetBoneTransform(Authored,FSkeletonPoseBoneIndex(Source),Sample,false);
            Local[Target].SetRotation(FQuat::Slerp(Local[Target].GetRotation(),Authored.GetRotation(),.48f).GetNormalized());
        }
        if(bBellbreakerStudy)
            UE_LOG(LogTemp,Display,TEXT("BOSSLAB heave overlay age=%.2f seconds=%.3f weight=.48 source=%s"),AgeF,HeaveTime,*Heave->GetName());
    }
    const float Fade=FMath::Clamp((Seconds-V.BlendFrom)/V.SourceBlendSeconds,0.f,1.f);
    if(Fade<1 && V.Frozen.Num()==Local.Num())
    {
        const float A=Smooth(Fade);
        for(int32 I=0;I<Local.Num();++I) { FTransform B; B.Blend(V.Frozen[I],Local[I],A); Local[I]=B; }
    }

    V.LastSourcePose=Local;

    // Retargeted clips and interrupted blends can carry the source skeleton's
    // local offsets. Keep the smith's fitted rest proportions. The root and
    // pelvis retain their animated travel for grounded weight shifts.
    const int32 HipIndex=Ref.FindBoneIndex(TEXT("pelvis"));
    for(int32 I=0;I<Local.Num();++I)
    {
        const FTransform& Bind=Ref.GetRefBonePose()[I];
        Local[I].SetScale3D(Bind.GetScale3D());
        if(I!=HipIndex && Ref.GetParentIndex(I)>=0) Local[I].SetTranslation(Bind.GetTranslation());
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
    // A finger rotation only changes its descendants. Keep the original
    // parent-before-child multiplication order without rebuilding the whole rig.
    TArray<int32,TInlineAllocator<256>> Changed;
    Changed.Init(0,Local.Num()); int32 Generation=0;
    auto RotateCS=[&](int32 I,const FQuat& Q)
    {
        const int32 P=Ref.GetParentIndex(I);
        const FQuat Parent=P<0 ? FQuat::Identity : CS[P].GetRotation();
        Local[I].SetRotation((Parent.Inverse()*(Q*CS[I].GetRotation())).GetNormalized());
        ++Generation; Changed[I]=Generation;
        CS[I]=P<0 ? Local[I] : Local[I]*CS[P];
        for(int32 J=I+1;J<Local.Num();++J)
        {
            const int32 Ancestor=Ref.GetParentIndex(J);
            if(Ancestor>=0 && Changed[Ancestor]==Generation)
            { CS[J]=Local[J]*CS[Ancestor]; Changed[J]=Generation; }
        }
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
    // Grounded load transfer: enter from the actual feet, spend a short
    // interval on both soles, then swing the unloaded boot. This modifies
    // presentation only; the fighter's velocity and facing remain authoritative.
    const bool GaitEntry=GroundGait && !V.WasGroundGait;
    if(GaitEntry) V.WalkEntryTime=Seconds;
    const FTransform MeshFrame=Body->GetComponentTransform();
    const FVector StrideForward=Yaw.Vector(), Rightward=Yaw.RotateVector(FVector::RightVector);
    const float GaitEnter=Smooth((Seconds-V.WalkEntryTime)/.22f);
    // Keep the generated walk's vertical trunk excursion at human-scale
    // amplitude. Its deep knee cycle otherwise rises ~30 world cm in .10s
    // after giant scaling, even with the support boot correctly planted.
    const bool SettlingGait=!GroundGait && F.Alive() && F.Action!=EWardenAction::Hurt &&
        (!Striking || AgeF<6.f) && (!V.WalkFeet[0].Correction.IsNearlyZero(.02f) || !V.WalkFeet[1].Correction.IsNearlyZero(.02f));
    if((GroundGait || SettlingGait) && V.Stance.Num()==Local.Num())
    {
        const int32 Hip=Idx(TEXT("pelvis"));
        if(Hip>=0)
        {
            const float SourceZ=MeshFrame.TransformPosition(CS[Hip].GetLocation()).Z;
            float TargetZ=SourceZ;
            if(GroundGait)
            {
                TArray<FTransform,TInlineAllocator<128>> Standing;
                Standing.SetNum(Local.Num());
                for(int32 I=0;I<Local.Num();++I)
                {
                    FTransform Bone=V.Stance[I];
                    Bone.SetScale3D(Ref.GetRefBonePose()[I].GetScale3D());
                    const int32 Parent=Ref.GetParentIndex(I);
                    if(I!=Hip && Parent>=0) Bone.SetTranslation(Ref.GetRefBonePose()[I].GetTranslation());
                    Standing[I]=Parent<0 ? Bone : Bone*Standing[Parent];
                }
                double Tread=DBL_MAX;
                for(const auto& Sample:V.Soles.Samples)
                {
                    double Z=0;
                    for(const auto& Entry:Sample.Influences) Z+=Entry.Weight*Standing[Entry.Bone].TransformPosition(Entry.Point).Z;
                    Tread=FMath::Min(Tread,Z);
                }
                if(Tread<DBL_MAX)
                {
                    const float NeutralZ=Floor.Z+.6f+(Standing[Hip].GetLocation().Z-Tread)*Scale;
                    TargetZ=NeutralZ-7.f+FMath::Clamp((SourceZ-NeutralZ)*.18f,-4.f,4.f);
                }
            }
            const float Smoothed=Dt>0 ? FMath::FInterpTo(PreviousWalkPelvisZ,TargetZ,Dt,8.f) : TargetZ;
            const float Freedom=GroundGait ? GaitEnter : Striking ? 1.f-Smooth(AgeF/6.f) : 1.f;
            const FVector Shift=MeshFrame.InverseTransformVector(FVector(0,0,(Smoothed-SourceZ)*Freedom));
            const int32 Parent=Ref.GetParentIndex(Hip);
            Local[Hip].AddToTranslation(Parent>=0 ? CS[Parent].GetRotation().Inverse().RotateVector(Shift) : Shift);
            Build();
        }
    }
    if(GroundGait)
    {
        const int32 Hip=Idx(TEXT("pelvis")), Spine=Idx(TEXT("spine_02"));
        const float Support=FMath::Sin(2.f*PI*V.WalkPhase);
        if(Hip>=0)
        {
            // Carry the trunk over the loaded leg, with a low centre rather
            // than the source clip's upright march. Small world-space offsets.
            const FVector Shift=MeshFrame.InverseTransformVector(
                -Rightward*(12.f*Support*GaitEnter));
            const int32 Parent=Ref.GetParentIndex(Hip);
            Local[Hip].AddToTranslation(Parent>=0 ? CS[Parent].GetRotation().Inverse().RotateVector(Shift) : Shift);
            Build();
        }
        if(Spine>=0)
        {
            const FVector LeanAxis=MeshFrame.InverseTransformVectorNoScale(Rightward).GetSafeNormal();
            RotateCS(Spine,FQuat(LeanAxis,FMath::DegreesToRadians(5.f*GaitEnter)));
            // Shoulder mass trails a turn slightly while the next foot places.
            const FVector UpAxis=MeshFrame.InverseTransformVectorNoScale(FVector::UpVector).GetSafeNormal();
            RotateCS(Spine,FQuat(UpAxis,FMath::DegreesToRadians(FMath::Clamp(-V.WalkTurnRate*.035f,-5.f,5.f)*GaitEnter)));
        }
    }
    // The generated boot is weighted to calf/ankle/toe, so a locked ball
    // joint is not a fixed tread offset. Measure the fitted skin landmarks
    // of each leg, rather than grounding only whichever boot is lowest.
    for(int32 Side=0;Side<2;++Side)
    {
        auto& FootState=V.WalkFeet[Side];
        if(!GroundGait && FootState.Correction.IsNearlyZero(.02f)) continue;
        const bool Left=Side==0;
        const int32 A=Idx(Left?TEXT("thigh_l"):TEXT("thigh_r")), B=Idx(Left?TEXT("calf_l"):TEXT("calf_r"));
        const int32 E=Idx(Left?TEXT("foot_l"):TEXT("foot_r")), T=Idx(Left?TEXT("ball_l"):TEXT("ball_r"));
        if(A<0 || B<0 || E<0 || T<0) continue;
        const FVector Toe=CS[T].GetLocation(), Ankle=CS[E].GetLocation();
        const FQuat SourceFootQ=CS[E].GetRotation();
        FQuat FootQ=SourceFootQ;
        float DesiredSoleZ=Floor.Z+.6f;
        if(GroundGait)
        {
            const float P=FMath::Fmod(V.WalkPhase+(Left ? 0.f : .5f),1.f);
            constexpr float SupportEnd=.60f, CentreX=26.f, Lane=62.f;
            const bool Stance=P<SupportEnd;
            const FQuat SourceWorld=MeshFrame.GetRotation()*FootQ;
            if(GaitEntry)
            {
                FootState.Anchor=MeshFrame.TransformPosition(Toe);
                FootState.SwingFrom=FootState.Anchor;
                FootState.GroundRotation=SourceWorld;
                FootState.Planted=true;
            }
            FVector Desired=FootState.Anchor;
            if(!Stance)
            {
                if(FootState.Planted) FootState.SwingFrom=FootState.Anchor;
                const float Swing=(P-SupportEnd)/(1.f-SupportEnd);
                FVector Landing=Floor+StrideForward*(CentreX+GiantStride*.25f)+Rightward*(Left ? -Lane : Lane);
                Landing.Z=FootState.SwingFrom.Z;
                Desired=FMath::Lerp(FootState.SwingFrom,Landing,Smooth(Swing));
                Desired.Z+=16.f*FMath::Sin(PI*Swing);
                DesiredSoleZ+=16.f*FMath::Sin(PI*Swing);
                FootQ=MeshFrame.GetRotation().Inverse()*FQuat::Slerp(FootState.GroundRotation,SourceWorld,Smooth(Swing));
                // Last airborne position becomes the landing anchor; do not
                // snap it to a fresh lane point at the support boundary.
                FootState.Anchor=Desired;
            }
            else
            {
                if(!FootState.Planted)
                {
                    FootState.Anchor.Z=FootState.SwingFrom.Z; Desired=FootState.Anchor; FootState.GroundRotation=SourceWorld;
                    // Footfall (2026-11-24): a 4.6 m smith lands every step with a boom, a dust puff
                    // and, close by, a faint floor kick (never over a bigger pulse). Presentation only.
                    if(GaitEnter>.5f && F.Alive() && Dt>0)
                    {
                        const FVector Sole(Desired.X,Desired.Y,Floor.Z);
                        BellbreakerSound(Left ? TEXT("giant_footstep_v0") : TEXT("giant_footstep_v1"),Sole,.5f);
                        for(int32 K=0;K<4;++K)
                        {
                            const float Ang=2*PI*(K+FMath::FRand()*.6f)/4;
                            BellbreakerFx(FWardenBellbreakerView::FxDust,Sole+FVector(FMath::Cos(Ang),FMath::Sin(Ang),0)*60+FVector(0,0,20),80,210,1.3f,FVector(FMath::Cos(Ang),FMath::Sin(Ang),0)*120,18);
                        }
                        if(Bellbreaker.GroundAge>=.32f && Player)
                        {
                            Bellbreaker.GroundAmplitude=.16f*FMath::Clamp(1.f-FVector::Dist2D(Sole,Player->GetActorLocation())/1100.f,0.f,1.f);
                            Bellbreaker.GroundAge=0;
                        }
                    }
                }
                FootQ=MeshFrame.GetRotation().Inverse()*FootState.GroundRotation;
            }
            FootState.Planted=Stance;
            FootState.Correction=(MeshFrame.InverseTransformPosition(Desired)-Toe)*GaitEnter;
        }
        else
        {
            FootState.Planted=false;
            FootState.Correction=FMath::VInterpTo(FootState.Correction,FVector::ZeroVector,Dt,14.f);
        }
        const FVector KneeGuide=CS[B].GetLocation()+MeshFrame.InverseTransformVector(StrideForward*42.f);
        // IK targets the ankle, but the planted witness is the toe. Retaining
        // world foot rotation changes that lever arm during turns. Compensate
        // it before solving the leg, otherwise a planted toe orbits the ankle.
        const FVector ToeOffset=Toe-Ankle;
        const FVector RotatedOffset=(FootQ*SourceFootQ.Inverse()).RotateVector(ToeOffset);
        FVector AnkleTarget=Ankle+FootState.Correction+ToeOffset-RotatedOffset;
        TwoBone(A,B,E,AnkleTarget,KneeGuide,1.f);
        RotateCS(E,FootQ*CS[E].GetRotation().Inverse());
        if(GroundGait)
        {
            for(int32 Pass=0;Pass<2;++Pass)
            {
                double Sole;
                if(!V.Soles.Lowest(CS,Sole,A)) break;
                const float Error=DesiredSoleZ-MeshFrame.TransformPosition(FVector(0,0,Sole)).Z;
                if(FMath::Abs(Error)<.08f) break;
                AnkleTarget+=MeshFrame.InverseTransformVector(FVector(0,0,FMath::Clamp(Error,-40.f,40.f)*GaitEnter));
                TwoBone(A,B,E,AnkleTarget,KneeGuide,1.f);
                RotateCS(E,FootQ*CS[E].GetRotation().Inverse());
            }
            if(FootState.Planted) FootState.Anchor.Z=MeshFrame.TransformPosition(CS[T].GetLocation()).Z;
        }
        if(bBellApproachStudy && GroundGait)
            UE_LOG(LogTemp,Display,TEXT("BOSSLAB gait reach side=%s stance=%d residual_cm=%.3f target_z=%.3f toe_z=%.3f"),
                Left?TEXT("L"):TEXT("R"),FootState.Planted?1:0,
                FVector::Dist(MeshFrame.TransformPosition(AnkleTarget),MeshFrame.TransformPosition(CS[E].GetLocation())),
                MeshFrame.TransformPosition(AnkleTarget).Z,MeshFrame.TransformPosition(CS[T].GetLocation()).Z);
    }
    if(bBellApproachStudy)
        UE_LOG(LogTemp,Display,TEXT("BOSSLAB gait phase=%.4f active=%d enter=%.3f yawrate=%.2f support_l=%d support_r=%d"),
            V.WalkPhase,GroundGait?1:0,GaitEnter,V.WalkTurnRate,V.WalkFeet[0].Planted?1:0,V.WalkFeet[1].Planted?1:0);
    V.WasGroundGait=GroundGait;
    const int32 Pelvis=Idx(TEXT("pelvis")), Chest=Idx(TEXT("spine_05")) >= 0 ? Idx(TEXT("spine_05")) : Idx(TEXT("spine_03"));
    // Distance from a point to the torso axis (pelvis -> chest) and the outward direction, mannequin space.
    auto TorsoOut=[&](const FVector& P,float& Dist)
    {
        const FVector A=CS[Pelvis].GetLocation(), B=CS[Chest].GetLocation()+(CS[Chest].GetLocation()-A)*.15f;
        const FVector Q=FMath::ClosestPointOnSegment(P,A,B);
        Dist=FVector::Dist(P,Q); FVector Out=(P-Q); Out.Z=FMath::Max(Out.Z,0.f);
        return Out.IsNearlyZero() ? FVector(0,1,0) : Out.GetSafeNormal();   // rig faces +Y
    };

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

    const float SweepLoad=Striking && F.Move==Sweep ? Smooth((AgeF-F.Definition().Windup+39)/22.f)*
        (1.f-Smooth((AgeF-F.Definition().Windup-3)/10.f)) : 0.f;
    // The guide shoulder begins moving before the weight comes through.
    // Both floor impacts retain their fully braced contact posture.
    const float DropTicks=F.Move==BellBreaks ? 28.f : 31.f;
    const float Downstroke=Slam ? FMath::Clamp((AgeF-F.Definition().Windup+DropTicks)/DropTicks,0.f,1.f) : 0.f;
    const float SlamDrive=Smooth(Downstroke/.42f)*(1.f-Smooth((Downstroke-.65f)/.35f));
    const float ImpactBrace=Slam ? Smooth((AgeF-F.Definition().Windup+32.f)/26.f)*
        (1.f-Smooth((AgeF-F.Definition().Windup-F.Definition().Active-Embed(F.Move))/23.f)) : 0.f;
    // The left hand leads a sledge. Turn the chest enough to bring that
    // shoulder forward; the source sweep turns the opposite shoulder forward.
    if(F.Alive())
    {
        const int32 R=Idx(TEXT("upperarm_r")), L=Idx(TEXT("upperarm_l"));
        const int32 Spine=Idx(TEXT("spine_02"));
        if(R>=0 && L>=0 && Spine>=0)
        {
            // Rig faces component +Y. Right minus left is component -X at rest.
            const FVector Line=CS[R].GetLocation()-CS[L].GetLocation();
            const FVector FacingLine=WYaw.UnrotateVector(Body->GetComponentTransform().TransformVector(Line));
            const float Desired=Striking && F.Move==Sweep ? 120.f : 105.f;
            const float Turn=FMath::Clamp(FMath::FindDeltaAngleDegrees(float(FacingLine.Rotation().Yaw),Desired),-38.f,52.f);
            const float Freedom=Slam ? 1.f-Smooth((AgeF-F.Definition().Windup+34)/14.f)*
                (1.f-Smooth((AgeF-F.Definition().Windup-F.Definition().Active-Embed(F.Move))/20.f)) : 1.f;
            RotateCS(Spine,FQuat(FVector::UpVector,FMath::DegreesToRadians(Turn*Freedom)));
            if(ImpactBrace>0)
            {
                // Stay behind the rear fist while sitting into the floor strike.
                // The source pose otherwise puts the right shoulder on top of
                // the wrist and forces the elbow through its folded singularity.
                const FVector SagittalAxis=MeshFrame.InverseTransformVectorNoScale(Yaw.RotateVector(FVector::RightVector));
                RotateCS(Spine,FQuat(FVector::UpVector,FMath::DegreesToRadians(34.f*ImpactBrace)));
                // Let the upper body settle behind the seated pommel while
                // the bell stays planted at the authoritative impact point.
                const float Settled=Smooth((AgeF-F.Definition().Windup+2.f)/8.f);
                RotateCS(Spine,FQuat(SagittalAxis,FMath::DegreesToRadians((-22.f-12.f*Settled)*ImpactBrace)));
            }
            const float Drive=FMath::Max(SweepLoad,SlamDrive);
            if(Drive>0)
            {
                // The guide arm otherwise extends directly down the back of
                // the shaft. Put the left shoulder into the right-side load
                // and keep the torso movement upstream of both hand IK chains.
                const FTransform& BodyTransform=Body->GetComponentTransform();
                const FVector LoadDirection=Slam ? FVector(.89,.46,0) : FVector(.75,.66,0);
                const FVector Lean=BodyTransform.InverseTransformVector(Yaw.RotateVector(LoadDirection)).GetSafeNormal();
                const FVector Axis=FVector::CrossProduct(FVector::UpVector,Lean).GetSafeNormal();
                // Sit back a few degrees before the side cut releases. The
                // forward lean otherwise grazes the pommel against the apron.
                const float Brace=Striking && F.Move==Sweep ? Smooth((AgeF-F.Definition().Windup+11)/6.f)*
                    (1.f-Smooth((AgeF-F.Definition().Windup-7)/9.f)) : 0.f;
                RotateCS(Spine,FQuat(Axis,FMath::DegreesToRadians(19.f*SweepLoad-18.f*Brace + (F.Move==BellBreaks ? 15.f : 12.f)*SlamDrive)));
                const int32 Clavicle=Idx(TEXT("clavicle_l"));
                if(Clavicle>=0)
                {
                    const FVector Arm=CS[L].GetLocation()-CS[Clavicle].GetLocation();
                    const FVector Wanted=(Arm.GetSafeNormal()+Lean*(.60f*SweepLoad + .72f*SlamDrive)).GetSafeNormal();
                    RotateCS(Clavicle,FQuat::FindBetweenNormals(Arm.GetSafeNormal(),Wanted));
                }
            }
        }
    }
    // ---- 3b. Anatomy governor (2026-11-23, owner: "twisting model looks super unnatural") -----------------
    // The retargeted HY clips spin the shoulder girdle far from the hips and the turns above stacked on one
    // spine bone, wringing the waist and apron. Every move (old and new) passes through these limits, so no
    // move can twist the model past them: pelvis near the facing, chest-vs-pelvis twist capped and spread
    // evenly over five spine bones, head facing forward and never buried in the chest.
    // Squat limit: the retargeted slam crouch folds the thighs past 90 degrees and smears the apron/thigh
    // skin. Keep the hips at least GovMinHip of the standing hip height above the ankles, re-solving each
    // leg to the same ankle so the feet stay where they were.
    if(F.Alive() && !GroundGait && Pelvis>=0)
    {
        const int32 Ft[2]={Idx(TEXT("foot_l")),Idx(TEXT("foot_r"))}, Th[2]={Idx(TEXT("thigh_l")),Idx(TEXT("thigh_r"))}, Ca[2]={Idx(TEXT("calf_l")),Idx(TEXT("calf_r"))};
        if(Ft[0]>=0 && Ft[1]>=0 && Th[0]>=0 && Th[1]>=0 && Ca[0]>=0 && Ca[1]>=0)
        {
            auto RefZ=[&](int32 I){ FTransform T=Ref.GetRefBonePose()[I]; for(int32 P=Ref.GetParentIndex(I);P>=0;P=Ref.GetParentIndex(P)) T=T*Ref.GetRefBonePose()[P]; return T.GetLocation().Z; };
            const float RestHip=RefZ(Pelvis)-FMath::Min(RefZ(Ft[0]),RefZ(Ft[1]));
            const float Hip=CS[Pelvis].GetLocation().Z-FMath::Min(CS[Ft[0]].GetLocation().Z,CS[Ft[1]].GetLocation().Z);
            const float Need=GovMinHip*RestHip-Hip;
            V.GovernorStats.WorstSquatIn=FMath::Max(V.GovernorStats.WorstSquatIn,1.f-Hip/FMath::Max(1.f,RestHip));
            if(Need>.2f)
            {
                FVector Ankle[2]; FQuat FootQ[2];
                for(int32 K=0;K<2;++K) { Ankle[K]=CS[Ft[K]].GetLocation(); FootQ[K]=CS[Ft[K]].GetRotation(); }
                const int32 Parent=Ref.GetParentIndex(Pelvis);
                const FVector Up(0,0,Need);
                Local[Pelvis].AddToTranslation(Parent>=0 ? CS[Parent].GetRotation().Inverse().RotateVector(Up) : Up);
                Build();
                for(int32 K=0;K<2;++K)
                {
                    TwoBone(Th[K],Ca[K],Ft[K],Ankle[K],CS[Ca[K]].GetLocation()+FVector(0,42,0),1.f);
                    RotateCS(Ft[K],FootQ[K]*CS[Ft[K]].GetRotation().Inverse());
                }
            }
        }
    }
    if(F.Alive())
        GovernBellbreakerAnatomy(Local,CS,Ref,Idx,RotateCS,!GroundGait,V.GovernorStats);
    // Hit flinch (2026-11-24): the combat mannequin that used to recoil is hidden, so a landed cut
    // showed nothing on the giant. Lean the upper spine and snap the head away from the blow for
    // ~0.45 s (small: he is 4.6 m and keeps his footing), and shudder through the hit-stop. Skipped
    // while staggered (that has its own clip). Presentation only; the hammer path is unchanged.
    if(Warden->BleedCount!=V.HitSeen)
    {
        V.HitSeen=Warden->BleedCount; V.HitAt=Seconds; V.HitAway=Warden->ImpactDir;
        if(bCaptureFrames) UE_LOG(LogTemp,Display,TEXT("BOSSLAB bellbreaker flinch at %.2f s, action %d, away %s"),Seconds,int32(F.Action),*V.HitAway.ToCompactString());
    }
    {
        const float HitAge=Seconds-V.HitAt;
        const int32 S3=Idx(TEXT("spine_03")), S5=Idx(TEXT("spine_05")), Head=Idx(TEXT("head"));
        if(F.Alive() && F.Action!=EWardenAction::Hurt && HitAge>=0 && HitAge<.45f && !V.HitAway.IsNearlyZero() && S3>=0 && S5>=0 && Head>=0 && !bReducedMotion)
        {
            const float Env=Smooth(HitAge/.06f)*(1-Smooth((HitAge-.08f)/.37f));
            const FVector Away=MeshFrame.InverseTransformVectorNoScale(V.HitAway).GetSafeNormal();
            const FVector UpC=MeshFrame.InverseTransformVectorNoScale(FVector::UpVector).GetSafeNormal();
            const FVector Axis=FVector::CrossProduct(UpC,Away).GetSafeNormal();
            const float Shudder=HitStop>0 && HitAge<.2f ? 1.2f*FMath::Sin(Seconds*190.f) : 0.f;
            RotateCS(S3,FQuat(Axis,FMath::DegreesToRadians(4.f*Env)));
            RotateCS(S5,FQuat(Axis,FMath::DegreesToRadians(3.f*Env+Shudder)));
            RotateCS(Head,FQuat(Axis,FMath::DegreesToRadians(9.f*Env)));
        }
    }
    // ---- 4. Floor: nothing of him below the stones (kneels, crouches, the death fall) --------------------
    {
        struct FProbe { const TCHAR* Bone; float Clear; };   // mannequin cm above the floor
        const FProbe Probes[]={{TEXT("ball_l"),1.5f},{TEXT("ball_r"),1.5f},{TEXT("foot_l"),6},{TEXT("foot_r"),6},{TEXT("calf_l"),5},{TEXT("calf_r"),5},
                               {TEXT("hand_l"),4},{TEXT("hand_r"),4},{TEXT("lowerarm_l"),5},{TEXT("lowerarm_r"),5},{TEXT("pelvis"),9},{TEXT("head"),9}};
        float Need=0;
        for(const auto& P:Probes) if(const int32 I=Idx(P.Bone); I>=0) Need=FMath::Max(Need,P.Clear-CS[I].GetLocation().Z);
        V.Lift=Dt>0 ? FMath::FInterpTo(V.Lift,Need,Dt,Need>V.Lift ? 30.f : 6.f) : Need;   // rise at once, settle slowly
        double Sole=0;
        float GroundLift=FMath::Max(0.f,V.Lift);
        if(F.Alive() && F.Action!=EWardenAction::Hurt)
        {
            // Body is attached above the forge floor at capsule rest. Subtract
            // that world-space offset as well as the actual skinned boot height.
            if(V.Soles.Lowest(CS,Sole))
                GroundLift=float((Floor.Z+.6-C->GetComponentLocation().Z)/Scale-Sole);
            else
                GroundLift-=(C->GetComponentLocation().Z-Floor.Z)/Scale;
        }
        Body->SetRelativeLocation(FVector(0,0,GroundLift));
        V.WorstFloor=FMath::Max(V.WorstFloor,(Need-FMath::Max(0.f,V.Lift))*Scale);
    }
    Body->UpdateComponentToWorld();
    const FTransform CT=Body->GetComponentTransform();
    for(int32 Side=0;Side<2;++Side)
    {
        auto* Shade=V.SoleShades[Side].Get();
        if(!Shade) continue;
        const bool Left=Side==0;
        const int32 Ankle=Idx(Left?TEXT("foot_l"):TEXT("foot_r"));
        const int32 Ball=Idx(Left?TEXT("ball_l"):TEXT("ball_r"));
        const int32 Thigh=Idx(Left?TEXT("thigh_l"):TEXT("thigh_r"));
        double Tread=0;
        if(Ankle<0 || Ball<0 || Thigh<0 || !V.Soles.Lowest(CS,Tread,Thigh))
        {
            Shade->SetVisibility(false);
            continue;
        }
        const FVector Heel=CT.TransformPosition(CS[Ankle].GetLocation());
        const FVector Toe=CT.TransformPosition(CS[Ball].GetLocation());
        const float Air=FMath::Max(0.f,float(CT.TransformPosition(FVector(0,0,Tread)).Z-Floor.Z));
        const float Soft=FMath::Clamp(Air/34.f,0.f,1.f);
        FVector Contact=FMath::Lerp(Heel,Toe,.48); Contact.Z=Floor.Z+1.15f;
        Shade->SetWorldLocationAndRotation(Contact,FRotator(0,(Toe-Heel).Rotation().Yaw,0));
        Shade->SetWorldScale3D(FVector(.92f+.16f*Soft,.52f+.10f*Soft,1));
        Shade->SetVisibility(Air<48.f);
        if(auto* Mat=Cast<UMaterialInstanceDynamic>(Shade->GetMaterial(0)))
            Mat->SetScalarParameterValue(TEXT("Contact"),.50f*(1.f-Smooth(Air/48.f)));
    }

    // Choreograph the rigid hammer in the smith's facing frame. The clip moves
    // shoulders and feet, but individual finger rotations never steer the bell.
    const int32 WeaponShoulder=Idx(TEXT("upperarm_r"));
    // The Cyclone spins the body and the bell together (CycloneSpin). Solve the weapon and both grips in
    // that spun body frame: an unspun facing swept the elbow poles and haft mount a full turn in 0.8 s,
    // past the grip solver's rate limits, and the guide hand let go (study: 65.5 cm gap).
    FBellPose Pose=WeaponPose(F.Move,AgeF,Striking);
    if(Spin!=0.f) { const FRotator Unspin(0,-Spin,0); Pose.Grip=Unspin.RotateVector(Pose.Grip); Pose.Shaft=Unspin.RotateVector(Pose.Shaft); }
    FVector GripGoal=Pose.Grip, LocalShaft=Pose.Shaft;
    // Moving carry shares the support transfer instead of keeping the weapon
    // perfectly level while the trunk walks beneath it. Decay in the first
    // six anticipation ticks; active weapon/hit samples are unchanged.
    const float CarryLoad=FMath::Sin(2.f*PI*V.WalkPhase);
    const FVector CarryDelta=GroundGait ? FVector(-5.f,-6.f*CarryLoad,-14.f-3.f*FMath::Abs(CarryLoad)) : FVector::ZeroVector;
    V.WalkCarryDelta=FMath::VInterpTo(V.WalkCarryDelta,CarryDelta,Dt,8.f);
    V.WalkCarryPitch=FMath::FInterpTo(V.WalkCarryPitch,GroundGait ? 2.5f+FMath::Abs(CarryLoad) : 0.f,Dt,8.f);
    const float CarryFreedom=Striking ? 1.f-Smooth(AgeF/6.f) : F.Alive() && F.Action!=EWardenAction::Hurt ? 1.f : 0.f;
    GripGoal+=V.WalkCarryDelta*CarryFreedom;
    const FVector CarryAxis=FVector::CrossProduct(FVector::UpVector,FVector(LocalShaft.X,LocalShaft.Y,0)).GetSafeNormal();
    if(!CarryAxis.IsNearlyZero()) LocalShaft=FQuat(CarryAxis,FMath::DegreesToRadians(V.WalkCarryPitch*CarryFreedom)).RotateVector(LocalShaft);

    if(!Striking && V.bHammerWasStriking)
    {
        V.ReturnFromShaft=V.PreviousShaft;
        V.ReturnFromGrip=V.PreviousGrip;
        V.WeaponReleaseTime=Seconds;
    }
    if(!Striking && Seconds-V.WeaponReleaseTime<.45f)
    {
        const float T=Smooth((Seconds-V.WeaponReleaseTime)/.45f);
        const FQuat Rotation=FQuat::FindBetweenNormals(V.ReturnFromShaft,LocalShaft);
        LocalShaft=FQuat::Slerp(FQuat::Identity,Rotation,T).RotateVector(V.ReturnFromShaft);
        GripGoal=FMath::Lerp(V.ReturnFromGrip,GripGoal,T);
    }
    FVector D=WYaw.RotateVector(LocalShaft);
    FVector G=Floor+WYaw.RotateVector(GripGoal);
    const bool Holding=F.Alive();
    const FVector SideAxis=WYaw.RotateVector(FVector::RightVector);

    FQuat Mount=FRotationMatrix::MakeFromZX(-D,SideAxis).ToQuat();
    auto ShaftCentre=[&](float MeshZ)
    {
        // The generated haft bows toward the pommel. These centimetre offsets
        // are measured on FBX cross sections at z=230,270,290 and 310.
        const float Depth=FMath::Clamp(MeshZ-230.f,-100.f,80.f);
        return Mount.RotateVector(FVector(-6.7f-.085f*Depth,5.9f+.145f*Depth,0));
    };
    // Off contact the rear and guide sockets can follow small shoulder shifts
    // together, keeping the rigid head supported through starts and staggers.
    const float Commit=Striking ? Smooth((AgeF-F.Definition().Windup+15)/14.f)*
        (1-Smooth((AgeF-F.Definition().Windup-F.Definition().Active-Embed(F.Move))/18.f)) : 0.f;
    const int32 LeftShoulder=Idx(TEXT("upperarm_l"));
    bool CompareOldGrip=false;
#if WITH_EDITOR
    if(bBellbreakerStudy)
    {
        static const bool OldGripStudy=FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_BB_COMPARE_OLD_GRIP"))==TEXT("1");
        CompareOldGrip=OldGripStudy;
    }
#endif
    // The short pommel clears the rear bracer with this grip centre.
    constexpr float RearSocketZ=306.f;
    // Slide toward the rear hand as the bell accelerates downward, then
    // open the grip again on the plant. The two palms remain separated.
    const float Lead=42.f-13.f*SweepLoad-15.f*SlamDrive-6.f*ImpactBrace;
    auto GripPoint=[&](float MeshZ) { return G+D*(BellReach-MeshZ)+ShaftCentre(MeshZ); };
    if(F.Alive() && WeaponShoulder>=0 && LeftShoulder>=0)
    {
        FVector Fitted=G;
        for(int32 Pass=0;Pass<5;++Pass)
            for(int32 Side=0;Side<2;++Side)
            {
                const float Offset=Side ? Lead : 0.f;
                const FVector Shoulder=CT.TransformPosition(CS[Side ? LeftShoulder : WeaponShoulder].GetLocation());
                const FVector Socket=Fitted+D*(BellReach-RearSocketZ+Offset)+ShaftCentre(RearSocketZ-Offset);
                // 167 cm from shoulder to finger pocket at full extension;
                // 133 cm leaves elbow bend for a two-handed load.
                const FVector Delta=Socket-Shoulder;
                Fitted+=Delta.GetClampedToMaxSize(133.f)-Delta;
            }
        // Maintain the exterior of the apron when the left shoulder retracts.
        const FVector Forward=WYaw.Vector();
        const float Retreat=FVector::DotProduct(G-Fitted,Forward);
        if(Retreat>6.f) Fitted+=Forward*(Retreat-6.f);
        G=FMath::Lerp(Fitted,G,Commit);
    }
    if(Striking && Commit<1.f)
    {
        // During a free lift/retrieval the beard and apron follow the live
        // torso, including blends out of the deep crouch. Clear their forward
        // silhouettes with the full physical pommel. Contacts stay authored.
        const FVector Forward=WYaw.Vector();
        float Need=0;
        auto Around=[&](const TCHAR* Bone,FVector CentreOffset,FVector Radius)
        {
            const int32 I=Idx(Bone);
            if(I<0) return;
            const FVector Centre=WYaw.UnrotateVector(CT.TransformPosition(CS[I].GetLocation())-Floor)+CentreOffset;
            for(float Z=120;Z<=325;Z+=5)
            {
                const FVector P=WYaw.UnrotateVector(GripPoint(Z)-Floor)-Centre;
                const float YZ=FMath::Square(P.Y/Radius.Y)+FMath::Square(P.Z/Radius.Z);
                if(YZ<1.f && P.X>-Radius.X)
                    Need=FMath::Max(Need,float(Radius.X*FMath::Sqrt(1-YZ)-P.X));
            }
        };
        // The transition lifts the crown past the pommel as the body stands
        // out of its deepest crouch; allow extra room for that blend.
        const float CrownMargin=F.Move==BellBreaks ? 12.f : 0.f;
        Around(TEXT("head"),FVector(9,0,-6),FVector(53,55,66)+FVector(CrownMargin));
        Around(TEXT("neck_01"),FVector(7,0,-6),FVector(48,49,45));
        Around(TEXT("spine_03"),FVector(7,0,0),FVector(81,83,55));
        G+=Forward*FMath::Min(55.f,Need)*(1.f-Commit);
    }
    if(F.Alive())
    {
        const float SweepSpace=Striking && F.Move==Sweep ? 28.f : 0.f;
        const float ReturnSpace=!Striking ? 9.f : 0.f;
        double Space=(SweepSpace+ReturnSpace)*(1.f-Commit);
        if(Striking && F.Move==Sweep)
        {
            const auto& Def=F.Definition();
            const double ToContact=FMath::Max(0.,double(Def.Windup-AgeF));
            const double AfterContact=FMath::Max(0.,double(AgeF-Def.Windup-Def.Active+1));
            // Give the butt room to leave the chest at the end of the sweep.
            const double ExitClearance=10.*Smooth(AfterContact/5.f)*(1.-Smooth((AgeF-98.f)/9.f));
            Space=43.*Smooth(ToContact/6.f)+6.*Smooth(AfterContact/12.f)+ExitClearance;
        }
        G+=WYaw.Vector()*Space;
    }
    if(!F.Alive())
    {
        const float Fall=Smooth(Warden->DeathAge/35.f);
        const FVector GroundDir=WYaw.RotateVector(FRotator(9.1f,-48,0).Vector());
        D=FMath::Lerp(D,GroundDir,Fall).GetSafeNormal();
        Mount=FRotationMatrix::MakeFromZX(-D,SideAxis).ToQuat();
        const FVector FinalMouth=Floor+WYaw.RotateVector(FVector(210,112,2.f+BellRim*GroundDir.Size2D()));
        G=FMath::Lerp(G,FinalMouth-GroundDir*BellReach,Fall);
    }
    // Body clearance (2026-11-23, after the readiness study found Anvil Stamp 3.8 cm and Death Knell 6.1 cm
    // inside the torso/thighs as their clips crouch into a fixed haft). Test the whole hammer (bell, haft,
    // pommel) against the posed hips, chest and legs (the study's ellipsoid hull) and move it rigidly out along
    // the deepest contact's normal before the hands are solved, so the grips follow. It engages only when
    // the hammer would enter the body; release is eased so it never pops. Presentation only: engine hits
    // use the authored bell path, which this changes by the few centimetres of the overlap at most.
    if(F.Alive())
    {
        struct FHull { FVector A,B,Radius; };
        TArray<FHull,TInlineAllocator<8>> Hull;
        auto AddHull=[&](const TCHAR* Start,const TCHAR* End,FVector Radii)
        {
            const int32 A=Idx(Start),B=Idx(End);
            if(A>=0 && B>=0) Hull.Add({WYaw.UnrotateVector(CT.TransformPosition(CS[A].GetLocation())-Floor),
                                       WYaw.UnrotateVector(CT.TransformPosition(CS[B].GetLocation())-Floor),Radii});
        };
        AddHull(TEXT("pelvis"),TEXT("spine_03"),{55,61,39});
        AddHull(TEXT("spine_03"),TEXT("spine_05"),{57,67,42});
        for(const TCHAR* S:{TEXT("_l"),TEXT("_r")})
        {
            AddHull(*(FString(TEXT("thigh"))+S),*(FString(TEXT("calf"))+S),{31,33,29});
            AddHull(*(FString(TEXT("calf"))+S),*(FString(TEXT("foot"))+S),{23,24,22});
        }
        FVector Push=FVector::ZeroVector;   // facing frame
        for(int32 Pass=0;Pass<4;++Pass)
        {
            float Deepest=0; FVector Normal=FVector::ZeroVector;
            for(float Along=BellReach-320;Along<=BellReach;Along+=10)
            {
                const float MeshZ=BellReach-Along;
                const float Pad=(MeshZ>BellLength ? 10.f : FMath::Lerp(BellRim,14.f,MeshZ/BellLength))+2.f;
                const FVector P=WYaw.UnrotateVector(G+D*Along+ShaftCentre(MeshZ)-Floor)+Push;
                for(const auto& Shape:Hull)
                {
                    const FVector R=Shape.Radius+FVector(Pad);
                    const FVector Offset=P/R-FMath::ClosestPointOnSegment(P/R,Shape.A/R,Shape.B/R);
                    const float Depth=float((1-Offset.Size())*R.GetMin());
                    if(Depth>Deepest) { Deepest=Depth; Normal=(Offset/R).GetSafeNormal(); }
                }
            }
            if(Deepest<=0 || Normal.IsNearlyZero()) break;
            Normal.Z=FMath::Max(Normal.Z,0.f);   // never push the hammer down into the floor
            Push+=Normal.GetSafeNormal()*(Deepest+.5f);
        }
        Push=Push.GetClampedToMaxSize(30.f);
        // Instant where it is needed, eased away (about 0.25 s) where it is not.
        FVector& Held=V.ClearPush;
        for(int32 Axis=0;Axis<3;++Axis)
        {
            const float Want=Push[Axis];
            Held[Axis]=FMath::Abs(Want)>=FMath::Abs(Held[Axis]) || Want*Held[Axis]<0 ? Want : FMath::FInterpTo(Held[Axis],Want,Dt,10.f);
        }
        G+=WYaw.RotateVector(Held);
    }
    // Each palm keeps its thumb on the same side of the haft as the arms load and recover.
    struct FHand { int32 Hand=-1, Index=-1, Middle=-1, Pinky=-1, Thumb=-1; bool bLeft=false; };
    auto HandOf=[&](bool Left){ FHand H; H.bLeft=Left; const TCHAR* S=Left?TEXT("_l"):TEXT("_r");
        H.Hand=Idx(*(FString(TEXT("hand"))+S)); H.Index=Idx(*(FString(TEXT("index_01"))+S)); H.Middle=Idx(*(FString(TEXT("middle_01"))+S));
        H.Pinky=Idx(*(FString(TEXT("pinky_01"))+S)); H.Thumb=Idx(*(FString(TEXT("thumb_01"))+S)); return H; };
    auto Palm=[&](const FHand& H){ const FVector W=CS[H.Hand].GetLocation(); const FVector M=CS[H.Middle].GetLocation(), K=CS[H.Pinky].GetLocation()-CS[H.Index].GetLocation();
        const FVector Inward=FVector::CrossProduct(K,M-W).GetSafeNormal()*(H.bLeft ? -V.PalmSign : V.PalmSign);
        return W+1.09f*(M-W)+Inward*(H.bLeft ? 7.2f : 5.8f); };
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
        // Keep a single hinge direction per digit. Rebuilding the axis from the
        // bent segment reverses its sign when the middle phalanx passes the palm normal.
        static const float Curl[3]={51,62,43};
        for(const TCHAR* Finger:{TEXT("index"),TEXT("middle"),TEXT("ring"),TEXT("pinky")})
        {
            int32 Digit[3];
            for(int32 Joint=0;Joint<3;++Joint)
                Digit[Joint]=Idx(*FString::Printf(TEXT("%s_0%d%s"),Finger,Joint+1,S));
            if(Digit[0]<0 || Digit[1]<0 || Digit[2]<0) continue;
            const FVector FingerDirection=(CS[Digit[1]].GetLocation()-CS[Digit[0]].GetLocation()).GetSafeNormal();
            const FVector Hinge=FVector::CrossProduct(FingerDirection,N).GetSafeNormal();
            if(Hinge.IsNearlyZero()) continue;
            for(int32 Joint=0;Joint<3;++Joint)
                RotateCS(Digit[Joint],FQuat(Hinge,FMath::DegreesToRadians(Curl[Joint]*Amount)));
        }
        const int32 ThumbBase=H.Thumb, ThumbMid=Idx(*FString::Printf(TEXT("thumb_02%s"),S));
        const int32 ThumbTip=Idx(*FString::Printf(TEXT("thumb_03%s"),S));
        if(ThumbBase>=0 && ThumbMid>=0 && ThumbTip>=0)
        {
            // Oppose the thumb at its base, then flex it across the curled index.
            const FVector PadGoal=CS[H.Index].GetLocation()+Fd*2.8+N*3.3;
            const FVector ToPad=(PadGoal-CS[ThumbBase].GetLocation()).GetSafeNormal();
            const FVector ThumbRay=(CS[ThumbTip].GetLocation()-CS[ThumbBase].GetLocation()).GetSafeNormal();
            const FQuat Oppose=FQuat::FindBetweenNormals(ThumbRay,ToPad);
            const double Strength=FMath::Min(1.,FMath::DegreesToRadians(34.)/FMath::Max(.001,Oppose.AngularDistance(FQuat::Identity)));
            RotateCS(ThumbBase,FQuat::Slerp(FQuat::Identity,Oppose,Strength*Amount));
            const FVector Along=(CS[ThumbTip].GetLocation()-CS[ThumbMid].GetLocation()).GetSafeNormal();
            const FVector Toward=(PadGoal-CS[ThumbTip].GetLocation()).GetSafeNormal();
            const FVector Hinge=FVector::CrossProduct(Along,Toward).GetSafeNormal();
            if(!Hinge.IsNearlyZero())
            {
                RotateCS(ThumbMid,FQuat(Hinge,FMath::DegreesToRadians(26.f*Amount)));
                RotateCS(ThumbTip,FQuat(Hinge,FMath::DegreesToRadians(22.f*Amount)));
            }
        }
    };
    const FHand Right=HandOf(false), LeftH=HandOf(true);
    const FVector FinalDc=CT.InverseTransformVectorNoScale(D).GetSafeNormal();
    const FVector ForwardCS=CT.InverseTransformVectorNoScale(WYaw.Vector()).GetSafeNormal();
    const FVector RightCS=CT.InverseTransformVectorNoScale(SideAxis).GetSafeNormal();
    const FVector UpCS=CT.InverseTransformVectorNoScale(FVector::UpVector).GetSafeNormal();
    auto SignedTurn=[](const FVector& From,const FVector& To,const FVector& Axis)
    {
        return FMath::Atan2(FVector::DotProduct(Axis,FVector::CrossProduct(From,To)),FVector::DotProduct(From,To));
    };
    auto SetGrip=[&](const FHand& Hand,int32 A,int32 B,float Z)
    {
        if(!Holding || A<0 || B<0 || Hand.Hand<0 || Hand.Pinky<0 || Hand.Index<0 || Hand.Middle<0) return;
        auto& Grip=V.ArmGrip[Hand.bLeft ? 1 : 0];
        // Establish the smith's braced wrist from the fitted skeleton. Close the
        // fingers around the shaft, then use the pocket as the chain endpoint.
        // Forearm pronation and elbow flexion carry the load above that wrist.
        for(const int32 Bone : {A,B,Hand.Hand}) Local[Bone].SetRotation(Ref.GetRefBonePose()[Bone].GetRotation());
        Build();
        Fist(Hand,Hand.bLeft,1.f);
        const FVector Target=CT.InverseTransformPosition(GripPoint(Z));
        const FVector Wrist=CS[Hand.Hand].GetLocation(), NeutralPocket=Palm(Hand)-Wrist;
        const FVector Straight=(Wrist-CS[B].GetLocation()).GetSafeNormal();
        const FQuat Level=FQuat::FindBetweenNormals(NeutralPocket.GetSafeNormal(),Straight);
        const double ReachAmount=FMath::Clamp((FVector::Dist(Target,CS[A].GetLocation())-36.)/26.,0.,1.);
        const double BendAllowance=FMath::DegreesToRadians(5.+18.*ReachAmount);
        const double Fraction=FMath::Min(1.,BendAllowance/FMath::Max(.001,Level.AngularDistance(FQuat::Identity)));
        RotateCS(Hand.Hand,FQuat::Slerp(FQuat::Identity,Level,Fraction));
        const FVector Root=CS[A].GetLocation(), BindElbow=CS[B].GetLocation(), BindPalm=Palm(Hand);
        const FVector Upper=BindElbow-Root, Lower=BindPalm-BindElbow;
        const FVector UpperBind=Upper.GetSafeNormal();
        const FVector Aim=(Target-Root).GetSafeNormal();
        const double L1=Upper.Size(),L2=Lower.Size();
        const double Reach=FMath::Clamp(FVector::Dist(Target,Root),FMath::Abs(L1-L2)+.02,L1+L2-.02);
        const double Along=(L1*L1-L2*L2+Reach*Reach)/(2.*Reach);
        const double Rise=FMath::Sqrt(FMath::Max(0.,L1*L1-Along*Along));
        const FVector Outside=RightCS*(Hand.bLeft ? -1. : 1.);
        const FVector Pole=FVector::VectorPlaneProject(Outside*.60-UpCS*.95-ForwardCS*.35,Aim).GetSafeNormal();
        const FVector Goal=FinalDc*(Hand.bLeft ? 1. : -1.);
        // While the sweep passes the chest, an elbow pointing inward can
        // fold the guide shoulder all the way back onto its own shell.
        // Fit the upper arm outside the body as well as fitting the palm.
        const double SweepBrace=Hand.bLeft && Striking && F.Move==Sweep ?
            Smooth((AgeF-39.f)/19.f)*(1.-Smooth((AgeF-85.f)/19.f)) : 0.;
        const FVector Span=(CS[Hand.Pinky].GetLocation()-CS[Hand.Index].GetLocation()).GetSafeNormal();
        const FVector Normal=FVector::CrossProduct(Span,CS[Hand.Middle].GetLocation()-Wrist).GetSafeNormal();
        const FQuat WeaponQ=CT.GetRotation().Inverse()*Mount;
        const FQuat UpperRest=CS[A].GetRotation(),LowerRest=CS[B].GetRotation();
        const auto& PreviousCS=Body->GetComponentSpaceTransforms();
        const bool TrackImpact=ImpactBrace>0.f && !Hand.bLeft && Grip.bValid && PreviousCS.IsValidIndex(B);
        const FQuat PreviousUpper=TrackImpact ? PreviousCS[A].GetRotation() : FQuat::Identity;
        struct FPose { double Cost=DBL_MAX,Swivel=0,Roll=0; FQuat Upper,Lower; FVector Normal; };
        auto Evaluate=[&](double Swivel,double Roll)
        {
            FPose P; P.Swivel=Swivel; P.Roll=Roll;
            const FVector Elbow=Root+Aim*Along+FQuat(Aim,Swivel).RotateVector(Pole)*Rise;
            const FVector U=(Elbow-Root).GetSafeNormal(),L=(Root+Aim*Reach-Elbow).GetSafeNormal();
            const FQuat UpperSwing=FQuat::FindBetweenNormals(UpperBind,U);
            const FVector From=FVector::VectorPlaneProject(UpperSwing.RotateVector(Lower.GetSafeNormal()),U).GetSafeNormal();
            const FVector To=FVector::VectorPlaneProject(L,U).GetSafeNormal();
            const FQuat Humerus=FQuat(U,SignedTurn(From,To,U))*UpperSwing;
            const FQuat LowerTurn=FQuat(L,Roll)*FQuat::FindBetweenNormals(Humerus.RotateVector(Lower.GetSafeNormal()),L)*Humerus;
            const FVector Knuckles=LowerTurn.RotateVector(Span);
            P.Normal=WeaponQ.UnrotateVector(LowerTurn.RotateVector(Normal));
            const FVector WristPos=Elbow+LowerTurn.RotateVector(Wrist-BindElbow);
            const FVector E=FVector::VectorPlaneProject(Elbow-Target,Goal),W=FVector::VectorPlaneProject(WristPos-Target,Goal);
            const double Cuff=FMath::Max(0.,7.0-FMath::ClosestPointOnSegment(FVector::ZeroVector,E,W).Size());
            const double Wrong=1.-FVector::DotProduct(Knuckles,Goal);
            P.Cost=7.5*Wrong*Wrong+.12*Swivel*Swivel+.06*Roll*Roll+.042*Cuff*Cuff;
            if(SweepBrace>0.)
            {
                const double Inside=FMath::Max(0.,-.04-FVector::DotProduct(U,Outside));
                const double ShoulderTurn=FMath::Max(0.,Humerus.AngularDistance(FQuat::Identity)-FMath::DegreesToRadians(113.));
                const double Backward=FMath::Max(0.,Wrong-.80);
                P.Cost+=SweepBrace*(74.*Inside*Inside+12.*ShoulderTurn*ShoulderTurn+19.*Backward*Backward);
            }
            if(Grip.bValid) P.Cost+=.34*(1.-FVector::DotProduct(P.Normal,Grip.PreviousPalmNormal));
            P.Upper=Humerus*UpperRest; P.Lower=LowerTurn*LowerRest;
            if(TrackImpact) P.Cost+=ImpactBrace*2.2*FMath::Square(PreviousUpper.AngularDistance(P.Upper));
            return P;
        };
        FPose Best;
        for(int32 I=-4;I<=4;++I)
            for(int32 J=-3;J<=3;++J)
            {
                auto Candidate=Evaluate(I*.52,J*.45);
                if(Grip.bValid) Candidate.Cost+=.04*(FMath::Square(Candidate.Swivel-Grip.ElbowSwivel)+FMath::Square(Candidate.Roll-Grip.Pronation));
                if(Candidate.Cost<Best.Cost) Best=Candidate;
            }
        const double SeedSwivel=Best.Swivel,SeedRoll=Best.Roll;
        for(int32 I=-1;I<=1;++I)
            for(int32 J=-1;J<=1;++J)
            {
                auto Candidate=Evaluate(FMath::Clamp(SeedSwivel+I*.20,-2.1,2.1),FMath::Clamp(SeedRoll+J*.2,-1.4,1.4));
                if(Candidate.Cost<Best.Cost) Best=Candidate;
            }
        if(Grip.bValid)
            Best=Evaluate(Grip.ElbowSwivel+FMath::Clamp(Best.Swivel-Grip.ElbowSwivel,-6.*Dt,6.*Dt),
                          Grip.Pronation+FMath::Clamp(Best.Roll-Grip.Pronation,-5.8*Dt,5.8*Dt));
        Grip.bValid=true; Grip.ElbowSwivel=Best.Swivel; Grip.Pronation=Best.Roll; Grip.PreviousPalmNormal=Best.Normal;
        RotateCS(A,Best.Upper*CS[A].GetRotation().Inverse());
        RotateCS(B,Best.Lower*CS[B].GetRotation().Inverse());
        // Near a vertical shaft the arm can run out of comfortable pronation.
        // A modest wrist adjustment keeps the thumb on its original side;
        // reseat the wrist around the same pocket without rolling the whole arm.
        const FVector ActualSpan=(CS[Hand.Pinky].GetLocation()-CS[Hand.Index].GetLocation()).GetSafeNormal();
        double LogBend=0;
        const double Separation=FMath::Acos(FMath::Clamp(ActualSpan|Goal,-1.,1.));
        const double Adjust=FMath::Clamp(Separation-FMath::DegreesToRadians(50.),0.,FMath::DegreesToRadians(28.));
        if(Adjust>.0001)
        {
            const FQuat Toward=FQuat::Slerp(FQuat::Identity,FQuat::FindBetweenNormals(ActualSpan,Goal),Adjust/Separation);
            const FVector NewWrist=Target-Toward.RotateVector(Palm(Hand)-CS[Hand.Hand].GetLocation());
            const FQuat Want=Toward*CS[Hand.Hand].GetRotation();
            FVector Guide=CS[B].GetLocation();
            if(TrackImpact)
            {
                const FVector PreviousUpperLink=PreviousCS[B].GetLocation()-PreviousCS[A].GetLocation();
                Guide=FMath::Lerp(Guide,Root+PreviousUpperLink,ImpactBrace*.82f);
            }
            TwoBone(A,B,Hand.Hand,NewWrist,Guide,1.f);
            const FQuat Parent=CS[Ref.GetParentIndex(Hand.Hand)].GetRotation();
            const FQuat Rest=Ref.GetRefBonePose()[Hand.Hand].GetRotation();
            const FQuat WantedLocal=Parent.Inverse()*Want;
            const double Bend=Rest.AngularDistance(WantedLocal); LogBend=FMath::RadiansToDegrees(Bend);
            const double Limit=FMath::DegreesToRadians(53.);
            FQuat Seated=Bend>Limit ? Parent*FQuat::Slerp(Rest,WantedLocal,Limit/Bend) : Want;
            if(TrackImpact && Body->BoneSpaceTransforms.IsValidIndex(Hand.Hand))
            {
                const FQuat Previous=Body->BoneSpaceTransforms[Hand.Hand].GetRotation();
                const FQuat NewLocal=Parent.Inverse()*Seated;
                const double Step=Previous.AngularDistance(NewLocal);
                const double Allowed=FMath::DegreesToRadians(520.)*Dt;
                if(Step>Allowed) Seated=Parent*FQuat::Slerp(Previous,NewLocal,Allowed/Step);
            }
            RotateCS(Hand.Hand,Seated*CS[Hand.Hand].GetRotation().Inverse());
        }
        if(Hand.bLeft) V.WorstLeftGap=FMath::Max(V.WorstLeftGap,float(FVector::Dist(Palm(Hand),Target)*Scale));
        if(Hand.bLeft && bBellbreakerStudy && Striking)
            UE_LOG(LogTemp,Display,TEXT("BOSSLAB lefthand move %d age %.2f gap %.2f reach %.2f arm %.2f wristbend %.1f adjust %.1f"),F.Move,AgeF,
                FVector::Dist(Palm(Hand),Target)*Scale,FVector::Dist(Target,Root)*Scale,(L1+L2)*Scale,LogBend,FMath::RadiansToDegrees(Adjust));
    };
    SetGrip(Right,WeaponShoulder,Idx(TEXT("lowerarm_r")),RearSocketZ);
    // Guide-hand slide (2026-11-24): in the Backhand Toll's follow-through the bell swings out to his
    // right and the guide grip ended up 182 cm from the left shoulder with a 170 cm arm (11.5 cm gap).
    // The hammer is the engine hit path, so the hand moves instead: when the guide grip is out of
    // reach it slides along the haft to the nearest reachable point (toward the rear hand first,
    // never closer than 14 cm to it), eased in and out so the palm never jumps.
    float LeftZ=RearSocketZ-Lead;
    {
        const int32 Elbow=Idx(TEXT("lowerarm_l"));
        float Want=0;
        if(Holding && LeftShoulder>=0 && Elbow>=0 && LeftH.Hand>=0 && LeftH.Middle>=0 && LeftH.Pinky>=0 && LeftH.Index>=0)
        {
            const FVector Shoulder=CS[LeftShoulder].GetLocation();
            const double Arm=.97*(FVector::Dist(Shoulder,CS[Elbow].GetLocation())+FVector::Dist(CS[Elbow].GetLocation(),Palm(LeftH)));
            auto Over=[&](float Z) { return FVector::Dist(CT.InverseTransformPosition(GripPoint(Z)),Shoulder)-Arm; };
            if(Over(LeftZ)>0)
            {
                float Best=Over(LeftZ);
                for(float Step=2;Step<=60;Step+=2)
                {
                    bool Found=false;
                    for(const float Sign:{1.f,-1.f})
                    {
                        const float Z=LeftZ+Sign*Step;
                        if(Z>RearSocketZ-14.f || Z<RearSocketZ-110.f) continue;
                        const double O=Over(Z);
                        if(O<Best) { Best=O; Want=Sign*Step; }
                        if(O<=0) { Found=true; break; }
                    }
                    if(Found) break;
                }
            }
        }
        V.LeftSlide=FMath::FInterpTo(V.LeftSlide,Want,Dt,FMath::Abs(Want)>FMath::Abs(V.LeftSlide) ? 30.f : 8.f);
        LeftZ+=V.LeftSlide;
    }
    SetGrip(LeftH,LeftShoulder,Idx(TEXT("lowerarm_l")),LeftZ);
    // With the palms seated, wrap the phalanges around the measured shaft.
    // The thumb advances around the opposite side of the same cylinder.
    auto WrapDigits=[&](const FHand& Hand,float Z)
    {
        if(!Holding || Hand.Hand<0 || Hand.Middle<0) return;
        const TCHAR* Side=Hand.bLeft ? TEXT("_l") : TEXT("_r");
        const FVector Centre=CT.InverseTransformPosition(GripPoint(Z));
        const FVector Axis=CT.InverseTransformVector(GripPoint(Z-5.f)-GripPoint(Z+5.f)).GetSafeNormal();
        const FVector PalmForward=(CS[Hand.Middle].GetLocation()-CS[Hand.Hand].GetLocation()).GetSafeNormal();
        const FVector MiddleRadius=FVector::VectorPlaneProject(CS[Hand.Middle].GetLocation()-Centre,Axis).GetSafeNormal();
        const double NormalSign=(FVector::CrossProduct(Axis,MiddleRadius)|PalmForward)<0. ? -1. : 1.;
        for(const TCHAR* Finger:{TEXT("index"),TEXT("middle"),TEXT("ring"),TEXT("pinky"),TEXT("thumb")})
        {
            const bool Thumb=FCString::Strcmp(Finger,TEXT("thumb"))==0;
            int32 Chain[3];
            for(int Joint=0;Joint<3;++Joint)
                Chain[Joint]=Idx(*FString::Printf(TEXT("%s_0%d%s"),Finger,Joint+1,Side));
            if(Chain[0]<0 || Chain[1]<0 || Chain[2]<0) continue;
            const double Sign=Thumb ? -NormalSign : NormalSign;
            for(int Joint=0;Joint<3;++Joint)
            {
                const int32 Bone=Chain[Joint];
                const FVector Base=CS[Bone].GetLocation();
                FVector Link;
                if(Joint<2) Link=CS[Chain[Joint+1]].GetLocation()-Base;
                else Link=CS[Bone].GetRotation().RotateVector(Ref.GetRefBonePose()[Bone].GetTranslation())*.8;
                const double Length=Link.Size();
                const FVector Radial=FVector::VectorPlaneProject(Base-Centre,Axis);
                const double StartRadius=Radial.Size();
                if(Length<.01 || StartRadius<.01) continue;
                // Leave room for the finger pad between its bone and the metal.
                const double PadRadius=(Thumb ? 12.7 : 11.8)/Scale;
                const double Axial=FMath::Clamp(Link|Axis,-.16*Length,.16*Length);
                const double Across=FMath::Sqrt(FMath::Max(0.,Length*Length-Axial*Axial));
                const double EndRadius=FMath::Clamp(PadRadius,FMath::Max(.02,StartRadius-Across),StartRadius+Across);
                const double Cosine=FMath::Clamp((StartRadius*StartRadius+EndRadius*EndRadius-Across*Across)/(2.*StartRadius*EndRadius),-1.,1.);
                const FVector Pad=FQuat(Axis,Sign*FMath::Acos(Cosine)).RotateVector(Radial/StartRadius)*EndRadius;
                const FVector Desired=Pad-Radial+Axis*Axial;
                if(Desired.IsNearlyZero()) continue;
                const FQuat Reach=FQuat::FindBetweenNormals(Link/Length,Desired.GetSafeNormal());
                const double MaxTurn=FMath::DegreesToRadians(Thumb && Joint==0 ? 64. : 76.);
                const double Strength=FMath::Min(1.,MaxTurn/FMath::Max(.001,Reach.AngularDistance(FQuat::Identity)));
                RotateCS(Bone,FQuat::Slerp(FQuat::Identity,Reach,Strength));
            }
        }
    };
    if(!CompareOldGrip)
    {
        WrapDigits(Right,RearSocketZ);
        WrapDigits(LeftH,LeftZ);
    }
    if(bBellbreakerStudy && Right.Hand>=0 && Right.Middle>=0)
        UE_LOG(LogTemp,Display,TEXT("BOSSLAB rear grip move %d age %.2f gap %.1f"),
               Striking?F.Move:-1,AgeF,FVector::Dist(GripPoint(RearSocketZ),CT.TransformPosition(Palm(Right))));
    V.bHammerWasStriking=Striking;
    V.PreviousShaft=WYaw.UnrotateVector(D);
    V.PreviousGrip=WYaw.UnrotateVector(G-Floor);
    if(bBellbreakerStudy)
    {
        // Fit the handle and rear pommel, not merely the bell. Compact ellipsoids
        // follow the posed chest, hips, skull and legs instead of the origin of
        // the standing capsule. Push the entire grip outside before solving IK.
        struct FHammerBody { FVector A,B,Radius; };
        TArray<FHammerBody,TInlineAllocator<8>> Hull;
        auto AddHull=[&](const TCHAR* Start,const TCHAR* End,FVector Radii)
        {
            const int32 A=Idx(Start),B=Idx(End);
            if(A>=0 && B>=0) Hull.Add({Yaw.UnrotateVector(CT.TransformPosition(CS[A].GetLocation())-Floor),
                                        Yaw.UnrotateVector(CT.TransformPosition(CS[B].GetLocation())-Floor),Radii});
        };
        AddHull(TEXT("pelvis"),TEXT("spine_03"),{55,61,39});
        AddHull(TEXT("spine_03"),TEXT("spine_05"),{57,67,42});
        AddHull(TEXT("neck_01"),TEXT("head"),{33,34,40});
        for(const TCHAR* S:{TEXT("_l"),TEXT("_r")})
        {
            AddHull(*(FString(TEXT("thigh"))+S),*(FString(TEXT("calf"))+S),{31,33,29});
            AddHull(*(FString(TEXT("calf"))+S),*(FString(TEXT("foot"))+S),{23,24,22});
        }
        float Intrusion=0;
        for(float Along=BellReach-320;Along<=BellReach;Along+=10)
        {
            const float MeshZ=BellReach-Along;
            const float Pad=MeshZ>BellLength ? 10.f : FMath::Lerp(BellRim,14.f,MeshZ/BellLength);
            const FVector P=Yaw.UnrotateVector(G+D*Along+ShaftCentre(MeshZ)-Floor);
            for(const auto& Shape:Hull)
            {
                const FVector R=Shape.Radius+FVector(Pad);
                const FVector Offset=P/R-FMath::ClosestPointOnSegment(P/R,Shape.A/R,Shape.B/R);
                Intrusion=FMath::Max(Intrusion,float((1-Offset.Size())*R.GetMin()));
            }
        }
        V.WorstBody=FMath::Max(V.WorstBody,Intrusion);
        UE_LOG(LogTemp,Display,TEXT("BOSSLAB shaft move %d age %.2f grip %s dir %s intrusion %.2f"),
               Striking?F.Move:-1,AgeF,*V.PreviousGrip.ToCompactString(),*V.PreviousShaft.ToCompactString(),Intrusion);
    }
    const FVector BellAt=G+D*BellReach;
    V.BellAxis=D.GetSafeNormal();
    const float BellLow=BellAt.Z-BellRim*D.Size2D();
    const FVector RimContact=BellAt-FVector::VectorPlaneProject(FVector::UpVector,D).GetSafeNormal()*BellRim;
    if(bBellbreakerStudy && Slam && F.Age>=F.Definition().Windup && F.Age<F.Definition().Windup+F.Definition().Active)
        UE_LOG(LogTemp,Display,TEXT("BOSSLAB contact move %d age %.2f rimZ %.2f cm rim XY-to-blast %.2f cm"),
            F.Move,AgeF,BellLow,FVector::Dist2D(RimContact,Floor+Yaw.RotateVector(QuakeImpactOffset())));
    if(UStaticMeshComponent* H=BellbreakerHammer.Get())
        H->SetWorldLocationAndRotation(BellAt,Mount);
    if(bBellbreakerStudy)
    {
        auto Position=[&](const TCHAR* Name)
        {
            const int32 Bone=Idx(Name);
            return Yaw.UnrotateVector(CT.TransformPosition(CS[Bone].GetLocation())-Floor);
        };
        auto Witness=[&](const FVector& Point) { return FString::Printf(TEXT("%.1f,%.1f,%.1f"),Point.X,Point.Y,Point.Z); };
        UE_LOG(LogTemp,Display,TEXT("BOSSLAB gripfit move=%d age=%.1f sr=%s sl=%s er=%s el=%s wr=%s wl=%s pr=%s pl=%s rear=%s dir=%s chest=%s pelvis=%s"),
            Striking?F.Move:-1,AgeF,*Witness(Position(TEXT("upperarm_r"))),*Witness(Position(TEXT("upperarm_l"))),
            *Witness(Position(TEXT("lowerarm_r"))),*Witness(Position(TEXT("lowerarm_l"))),*Witness(Position(TEXT("hand_r"))),*Witness(Position(TEXT("hand_l"))),
            *Witness(Yaw.UnrotateVector(CT.TransformPosition(Palm(Right))-Floor)),*Witness(Yaw.UnrotateVector(CT.TransformPosition(Palm(LeftH))-Floor)),
            *Witness(Yaw.UnrotateVector(GripPoint(RearSocketZ)-Floor)),*Witness(Yaw.UnrotateVector(D)),*Witness(Position(TEXT("spine_05"))),*Witness(Position(TEXT("pelvis"))));
    }
    if(bBellbreakerStudy && RegentStudyCamera.IsValid())
    {
        static const bool InspectHands=FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_BB_HAND_CAMERA"))==TEXT("1");
        if(InspectHands && Right.Hand>=0 && LeftH.Hand>=0 && Chest>=0)
        {
            const FVector Hands=.5*(CT.TransformPosition(CS[Right.Hand].GetLocation())+CT.TransformPosition(CS[LeftH.Hand].GetLocation()));
            const FVector Focus=FMath::Lerp(CT.TransformPosition(CS[Chest].GetLocation()),Hands,.61);
            const FVector Eye=Focus+Yaw.RotateVector(FVector(235,154,78));
            RegentStudyCamera->SetActorLocationAndRotation(Eye,(Focus-Eye).Rotation());
        }
        // Whole-body three-quarter view for deformation review (torso twist, shoulders, head).
        static const bool InspectBody=FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_BB_BODY_CAMERA"))==TEXT("1");
        if(InspectBody && !InspectHands && Pelvis>=0 && Chest>=0)
        {
            const FVector Focus=.5*(CT.TransformPosition(CS[Pelvis].GetLocation())+CT.TransformPosition(CS[Chest].GetLocation()))+FVector(0,0,20);
            const FVector Eye=Floor+FVector(0,0,Focus.Z-Floor.Z)+Yaw.RotateVector(FVector(560,-420,60));
            RegentStudyCamera->SetActorLocationAndRotation(Eye,(Focus-Eye).Rotation());
        }
    }
    if(bBellbreakerStudy || bBellApproachStudy)
    {
        for(const auto& Hand : {Right,LeftH})
        {
            if(Hand.Hand<0 || Hand.Index<0 || Hand.Pinky<0 || Hand.Middle<0) continue;
            const FVector Wrist=CS[Hand.Hand].GetLocation();
            const FVector Span=(CS[Hand.Pinky].GetLocation()-CS[Hand.Index].GetLocation()).GetSafeNormal();
            const FVector Normal=FVector::CrossProduct(Span,CS[Hand.Middle].GetLocation()-Wrist).GetSafeNormal();
            const int32 Lower=Idx(Hand.bLeft?TEXT("lowerarm_l"):TEXT("lowerarm_r"));
            const int32 Upper=Idx(Hand.bLeft?TEXT("upperarm_l"):TEXT("upperarm_r"));
            auto QuatText=[](const FQuat& Q){return FString::Printf(TEXT("%.6f,%.6f,%.6f,%.6f"),Q.X,Q.Y,Q.Z,Q.W);};
            auto VecText=[](const FVector& P){return FString::Printf(TEXT("%.5f,%.5f,%.5f"),P.X,P.Y,P.Z);};
            const FQuat WristRest=Ref.GetRefBonePose()[Hand.Hand].GetRotation();
            const FQuat ElbowRest=Ref.GetRefBonePose()[Lower].GetRotation();
            const FQuat ShoulderRest=Ref.GetRefBonePose()[Upper].GetRotation();
            const FVector RestFinger=Ref.GetRefBonePose()[Hand.Middle].GetTranslation().GetSafeNormal();
            const FVector RestForearm=Ref.GetRefBonePose()[Hand.Hand].GetTranslation().GetSafeNormal();
            UE_LOG(LogTemp,Display,TEXT("BOSSLAB anatomy move=%d age=%.1f side=%s span=%s normal=%s shaft=%s hand=%s elbow=%s shoulder=%s handaxis=%s loweraxis=%s"),
                Striking?F.Move:-1,AgeF,Hand.bLeft?TEXT("L"):TEXT("R"),*VecText(Span),*VecText(Normal),*VecText(FinalDc),
                *QuatText(WristRest.Inverse()*Local[Hand.Hand].GetRotation()),*QuatText(ElbowRest.Inverse()*Local[Lower].GetRotation()),
                *QuatText(ShoulderRest.Inverse()*Local[Upper].GetRotation()),*VecText(RestFinger),*VecText(RestForearm));
        }
    }
    Body->BoneSpaceTransforms=Local;
    Body->RefreshBoneTransforms();
#if WITH_EDITOR
    if (bBellApproachStudy || bBellbreakerStudy)
    {
        const FTransform Frame(FRotator(0,Warden->GetActorRotation().Yaw,0),Floor);
        auto RelativeJoint=[&](const TCHAR* Bone)
        {
            return Frame.InverseTransformPosition(Body->GetSocketLocation(FName(Bone))).ToCompactString();
        };
        UE_LOG(LogTemp,Display,TEXT("BOSSLAB forge pose move=%d age=%d speed=%.1f clip=%s clock=%.3f hip=%s lf=%s rf=%s chest=%s world_x=%.3f world_y=%.3f yaw=%.3f"),
            Striking ? F.Move : -1,F.Age,Warden->MoveVelocity.Size2D(),*GetNameSafe(Clip),Clock,
            *RelativeJoint(TEXT("pelvis")),*RelativeJoint(TEXT("ball_l")),*RelativeJoint(TEXT("ball_r")),*RelativeJoint(TEXT("spine_05")),Floor.X,Floor.Y,Warden->GetActorRotation().Yaw);
    }
    if (bBellbreakerStudy && Striking && (F.Move==HammerFall || F.Move==Sweep) && F.Age>=F.Definition().Windup && F.Age<F.Definition().Windup+F.Definition().Active)
    {
        const FVector RuleMouth=Floor+Yaw.RotateVector(BellOffsetAt(F.Move,AgeF,true));
        const FVector Actual=Yaw.UnrotateVector(BellAt-Floor);
        const FVector Rule=Yaw.UnrotateVector(RuleMouth-Floor);
        UE_LOG(LogTemp,Display,TEXT("BOSSLAB bell path move %d age %.2f error %.1f actual %s rule %s"),F.Move,AgeF,FVector::Dist(BellAt,RuleMouth),*Actual.ToCompactString(),*Rule.ToCompactString());
    }
    if ((bBellbreakerStudy || bBellApproachStudy) && BellbreakerHammer.IsValid())
        WardenAuditBellMesh(Body, BellbreakerHammer.Get(), Striking ? F.Move : -1, F.Age,Yaw.RotateVector(FVector::ForwardVector));
    if(bBellbreakerStudy && Striking && F.Move==Sweep && F.Age==71)
        WardenWriteBellbreakerSkinProbe(Body,TEXT("BellbreakerSweepProbe"));
    if(bBellbreakerStudy && Striking && F.Move==Quake && F.Age==82)
        WardenWriteBellbreakerSkinProbe(Body);
    if(bBellbreakerStudy && Striking && F.Age%6<2)
        TraceBellbreakerSkin(Body,F.Move,AgeF);
#endif

    // ---- 7. Bell on stone: sparks where the rim grinds, a burst when it slams in, metal-scrape sound --------
    const float Speed=Dt>0 ? FVector::Dist(BellAt,V.LastBell)/Dt : 0.f;
    const float DragSpeed=Dt>0 ? FVector::Dist2D(BellAt,V.LastBell)/Dt : 0.f;
    const FVector Move=Dt>0 ? (BellAt-V.LastBell).GetSafeNormal2D() : FVector::ZeroVector;
    V.LastBell=BellAt;
    const bool Contact=BellLow<14 && F.Alive();
    const FVector Touch(RimContact.X,RimContact.Y,3);
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
        BellbreakerSound(V.ScrapeVariant%2 ? TEXT("bell_hit_anvil_v1") : TEXT("bell_hit_anvil_v0"),Touch,.27f);
    }
    if(Contact && Speed>120)   // dragging: a trail of sparks thrown back from the motion
    {
        Emit(FMath::Max(1,FMath::CeilToInt(Dt*FMath::Clamp(Speed*.35f,60.f,320.f))),280,420,-Move);
        if(V.bContact && DragSpeed>200.f && Seconds>=V.ScrapeReady && !bForgeSpeechPriority)
        {
            BellbreakerSound(++V.ScrapeVariant%2 ? TEXT("bell_scrape_v0") : TEXT("bell_scrape_v1"),Touch,FMath::Clamp(DragSpeed/2400.f,.10f,.24f));
            V.ScrapeReady=Seconds+2.4f;
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
        // Use the entire swept band for the current damage tick, including its outer lip on the
        // final tick. Interpolating the radius here would shift the visible threat outside that band.
        const FVector2D Band=Wv.Band(Tick);
        const float PlaneRadius=Band.Y+4.f; // allow a small antialiased edge before the mesh ends
        if(UStaticMeshComponent* R=BellbreakerRings[Used].Get())
        {
            R->SetVisibility(true); R->SetWorldLocation(Wv.Center+FVector(0,0,6)); R->SetWorldScale3D(FVector(PlaneRadius/50.f,PlaneRadius/50.f,1));
            if(auto* M=BellbreakerRingMids[Used].Get())
            {
                M->SetScalarParameterValue(TEXT("PlaneRadiusCm"),PlaneRadius);
                M->SetScalarParameterValue(TEXT("BandInnerCm"),Band.X);
                M->SetScalarParameterValue(TEXT("BandOuterCm"),Band.Y);
            }
        }
        ++Used;
    }
    // Slag Fling: a molten mark where each glob will land, and the glob on its arc.
    for(int32 K=0;K<Bellbreaker.Slag.Num();++K)
    {
        const auto& Sl=Bellbreaker.Slag[K];
        if(Used<BellbreakerRings.Num())
            if(UStaticMeshComponent* R=BellbreakerRings[Used].Get())
            {
                const float Grow=FMath::Clamp(float(Tick-Sl.Launch)/12.f,.2f,1.f);
                const float PlaneRadius=SlagRadius+4.f;
                R->SetVisibility(true); R->SetWorldLocation(FVector(Sl.At.X,Sl.At.Y,6)); R->SetWorldScale3D(FVector(PlaneRadius/50.f,PlaneRadius/50.f,1));
                if(auto* M=BellbreakerRingMids[Used].Get())
                {
                    M->SetScalarParameterValue(TEXT("PlaneRadiusCm"),PlaneRadius);
                    M->SetScalarParameterValue(TEXT("BandInnerCm"),SlagRadius*(1.f-.22f*Grow));
                    M->SetScalarParameterValue(TEXT("BandOuterCm"),SlagRadius);
                }
                ++Used;
            }
        if(BellbreakerGlobs.IsValidIndex(K))
            if(UStaticMeshComponent* Gl=BellbreakerGlobs[K].Get())
            {
                const float U=FMath::Clamp((Tick+float(CombatAccumulator/WardenRules::Step)-Sl.Launch)/float(Sl.Land-Sl.Launch),0.f,1.f);
                Gl->SetVisibility(true);
                Gl->SetWorldLocation(FMath::Lerp(Sl.From,Sl.At,U)+FVector(0,0,4.f*380.f*U*(1.f-U)));
                Gl->SetWorldScale3D(FVector(.55f));
            }
    }
    for(int32 K=Bellbreaker.Slag.Num();K<BellbreakerGlobs.Num();++K) if(auto* Gl=BellbreakerGlobs[K].Get()) Gl->SetVisibility(false);
    for(int32 I=Used;I<BellbreakerRings.Num();++I) if(UStaticMeshComponent* R=BellbreakerRings[I].Get()) R->SetVisibility(false);
    UpdateBellbreakerFx(Seconds);
}

void AWardenArenaMode::UpdateBellbreakerFx(float Seconds)
{
    using namespace WardenBellbreaker;
    using FV=FWardenBellbreakerView;
    auto& V=BBView;
    if(!Warden) return;
    // Continuous emitters: embers off the smith once the bell has broken, ember trails behind slag globs.
    const FVector At=Warden->GetActorLocation();
    if(Bellbreaker.PhaseTwo && Warden->Fight.Alive() && Seconds>=V.EmberDue)
    {
        V.EmberDue=Seconds+.07f;
        const float A=FMath::FRandRange(0.f,2*PI), R=FMath::FRandRange(30.f,95.f);
        BellbreakerFx(FV::FxFire,FVector(At.X+FMath::Cos(A)*R,At.Y+FMath::Sin(A)*R,FMath::FRandRange(40.f,330.f)),14,4,FMath::FRandRange(1.f,1.6f),
                      FVector(FMath::FRandRange(-30.f,30.f),FMath::FRandRange(-30.f,30.f),0),FMath::FRandRange(90.f,170.f));
    }
    if(Seconds>=V.TrailDue)
    {
        V.TrailDue=Seconds+.035f;
        for(const auto& Gl:BellbreakerGlobs)
            if(const UStaticMeshComponent* G=Gl.Get(); G && G->IsVisible())
                BellbreakerFx(FV::FxFire,G->GetComponentLocation(),38,10,.32f,FVector::ZeroVector,40);
    }
    FVector Eye=At+FVector(0,0,300);
    if(auto* PC=GetWorld()->GetFirstPlayerController()) if(PC->PlayerCameraManager) Eye=PC->PlayerCameraManager->GetCameraLocation();
    TArray<FTransform> Xf;
    for(int32 K=0;K<FV::FxKinds;++K)
    {
        UInstancedStaticMeshComponent* L=V.FxLayer[K].Get();
        if(!L || V.Fx[K].Num()==0) continue;
        const bool Flat=K==FV::FxCrack || K==FV::FxPuddle;
        Xf.Reset(V.Fx[K].Num());
        for(int32 I=0;I<V.Fx[K].Num();++I)
        {
            const auto& P=V.Fx[K][I];
            const float T=(Seconds-P.Start)/FMath::Max(.01f,P.Life);
            if(T<0 || T>=1) { Xf.Add(FTransform(FQuat::Identity,FVector(0,0,-10000),FVector(0))); L->SetCustomDataValue(I,0,0.f,false); continue; }
            const float Age=Seconds-P.Start;
            const float Ease=1-FMath::Square(1-T);
            const float Size=FMath::Lerp(P.Size0,P.Size1,Ease)/100.f;
            float Fade;
            if(K==FV::FxCrack || K==FV::FxPuddle) Fade=1-T;                                  // heat: cools to dark
            else if(K==FV::FxDust) Fade=FMath::Min(1.f,T/.12f)*FMath::Pow(1-T,1.3f);           // billow in, settle out
            else Fade=FMath::Min(1.f,T/.06f)*FMath::Pow(1-T,1.6f);                           // flash, burn out
            FVector Where;
            FQuat Rot;
            if(Flat)
            {
                Where=FVector(P.At.X,P.At.Y,2.f+.3f*I+(K==FV::FxPuddle ? 3.f : 0.f));
                Rot=FRotator(0,P.Spin,0).Quaternion();
            }
            else
            {
                // Drag-damped drift (velocity halves every ~0.3 s) plus a steady rise.
                const float Drift=(1-FMath::Exp(-2.3f*Age))/2.3f;
                Where=P.At+P.Velocity*Drift+FVector(0,0,P.Rise*Age);
                const FVector ToEye=(Eye-Where).GetSafeNormal();
                Rot=FQuat(ToEye,FMath::DegreesToRadians(P.Spin+40*Age))*FRotationMatrix::MakeFromZ(ToEye).ToQuat();
            }
            Xf.Add(FTransform(Rot,Where,FVector(Size,Size,1)));
            L->SetCustomDataValue(I,0,Fade,false);
        }
        L->BatchUpdateInstancesTransforms(0,Xf,true,true);
    }
}

// Capture-only side-on review (-BossLabBellbreakerStudy): each move once, the player standing still in reach.
void AWardenArenaMode::BellbreakerStudyStep()
{
    using namespace WardenBellbreaker;
    // BOSSLAB_BB_STUDY_FROM=<n> starts at the n-th row (a 30 s capture shows about five moves).
    static const int32 Seq[]={HammerFall,Sweep,Quake,BellBreaks,Backhand,Stamp,Charge,Uppercut,Toll,Fling,HeldNote,Cyclone,Knell,StridingFall};
    static const int32 From=FCString::Atoi(*FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_BB_STUDY_FROM")));
    if(BellbreakerStudyIndex==0 && From>0 && From<int32(UE_ARRAY_COUNT(Seq))) BellbreakerStudyIndex=From;
    auto& F=Warden->Fight;
    const FVector ToPlayer=Player->GetActorLocation()-Warden->GetActorLocation();
    if(F.Action==EWardenAction::Strike) { if(F.Age<F.Definition().Windup-14) Warden->CommittedDirection=ToPlayer.GetSafeNormal2D(); return; }
    if(!F.Ready() || --BellbreakerStudyWait>0) return;
    if(BellbreakerStudyWait==0 && BellbreakerStudyIndex>0)
    {
        UE_LOG(LogTemp,Display,TEXT("BOSSLAB BELLBREAKER study after %s: worst body intrusion %.1f cm, worst floor %.1f cm, worst left-hand gap %.1f cm"),
            WardenRules::Strike(Seq[BellbreakerStudyIndex-1]).Name,BBView.WorstBody,BBView.WorstFloor,BBView.WorstLeftGap);
        const auto& G=BBView.GovernorStats;
        UE_LOG(LogTemp,Display,TEXT("BOSSLAB BELLBREAKER governor after %s: pelvis yaw in %.1f, chest twist in %.1f out %.1f, head yaw in %.1f, head pitch in %.1f out %.1f, squat %.2f (deg)"),
            WardenRules::Strike(Seq[BellbreakerStudyIndex-1]).Name,G.WorstPelvisIn,G.WorstTwistIn,G.WorstTwistOut,G.WorstHeadYawIn,G.WorstHeadPitchIn,G.WorstHeadPitchOut,G.WorstSquatIn);
        BBView.GovernorStats=FWardenBellbreakerView::FGovernor();
        BBView.WorstBody=BBView.WorstFloor=BBView.WorstLeftGap=0;
    }
    if(BellbreakerStudyIndex>=UE_ARRAY_COUNT(Seq)) return;
    const int32 Move=Seq[BellbreakerStudyIndex++];
    const FVector Fwd=Warden->GetActorForwardVector().GetSafeNormal2D();
    const float Distance=Move==Quake ? 700.f : Move==Charge || Move==Fling ? 900.f : Move==StridingFall || Move==Toll || Move==Knell ? 600.f : 430.f;
    Player->SetActorLocation(FVector(Warden->GetActorLocation().X,Warden->GetActorLocation().Y,95)+Fwd*Distance);
    Warden->BeginAction(EWardenAction::Strike,Move,Fwd);
    LastEvent=FString::Printf(TEXT("STUDY | %s"),F.Definition().Name);
    BellbreakerStudyWait=60;
}
