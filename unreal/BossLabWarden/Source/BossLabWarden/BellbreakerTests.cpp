#include "WardenPrototype.h"
#include "WardenBellbreaker.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Misc/AutomationTest.h"
#include "EngineUtils.h"
#include "Engine/OverlapResult.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "GameFramework/PlayerController.h"
#if WITH_DEV_AUTOMATION_TESTS
// Bellbreaker greybox (docs/BELLBREAKER_GREYBOX.md): the stun rule, the Bell Quake's blast and shockwave,
// the Twin Quake, and that one timed roll beats each hammer blow.
#define BELLBREAKER_TEST(Type,Name) IMPLEMENT_SIMPLE_AUTOMATION_TEST(Type,Name,(EAutomationTestFlags::EditorContext|EAutomationTestFlags::ClientContext)|EAutomationTestFlags::EngineFilter)
namespace {
UWorld* NewWorld() { auto* W=UWorld::CreateWorld(EWorldType::Game,false); GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W); return W; }
void CloseWorld(UWorld* W) { GEngine->DestroyWorldContext(W); W->DestroyWorld(false); }
AWardenArenaMode* BellArena(UWorld* W)
{
    auto* M=W->SpawnActor<AWardenArenaMode>();
    M->Player=W->SpawnActor<AWardenChallenger>(FVector(-450,0,95),FRotator::ZeroRotator); M->Player->DispatchBeginPlay(); M->Player->ResetFighter(false);
    M->DispatchBeginPlay(); M->Warden->DispatchBeginPlay();
    M->EnableBellbreaker(); M->ConfigureEncounter(303,true,1);
    M->bScriptedPlayer=false; M->Bellbreaker.Waiting=1000000;
    M->Warden->SetActorLocation(FVector(0,0,WardenBellbreaker::StandZ)); M->Warden->SetActorRotation(FRotator::ZeroRotator);
    return M;
}
struct FResponse { EWardenAction Action=EWardenAction::Ready; int32 At=-1; FVector Direction=FVector::RightVector; };
struct FDuel { int32 FirstDamageWaveAge=INDEX_NONE; float Taken=0; int32 Stuns=0; int32 Avoided=0; bool Kneel=false; bool ActedWhileStunned=false; };
// One committed Bellbreaker move. The player stands Distance from the point of impact (Quake) or from
// the boss (melee), straight ahead. Responses fire at boss action ages (step indices from the commit).
FDuel Duel(int32 Move,float Distance,TArray<FResponse> Responses,bool PhaseTwo=false)
{
    using namespace WardenBellbreaker;
    auto* W=NewWorld(); auto* M=BellArena(W);
    M->Bellbreaker.PhaseTwo=PhaseTwo;
    const FVector Impact=QuakeImpactOffset();
    const FVector At=Move==Quake ? FVector(Impact.X+Distance,Impact.Y,95) : FVector(Distance,0,95);
    M->Player->SetActorLocation(At); M->Player->SetActorRotation(FRotator(0,180,0));
    M->Warden->BeginAction(EWardenAction::Strike,Move,FVector::ForwardVector);
    FDuel R;
    const int32 Ticks=M->Warden->Fight.Definition().Total()+160;
    for(int32 T=0;T<Ticks;++T)
    {
        for(const auto& Resp:Responses) if(T==Resp.At) { M->Player->PendingAction=Resp.Action; M->Player->PendingDirection=Resp.Direction; }
        const bool WasStunned=M->Player->Fight.Stunned();
        if(WasStunned) { M->Player->PendingAction=EWardenAction::Dodge; M->Player->PendingDirection=FVector::RightVector; }   // mashing roll while stunned
        M->FixedStep();
        if(R.FirstDamageWaveAge==INDEX_NONE && M->Bellbreaker.Waves.Num() && M->Player->Fight.Health<M->Player->Fight.MaxHealth)
            R.FirstDamageWaveAge=M->CombatTick-M->Bellbreaker.Waves[0].Start;
        R.Kneel|=M->Player->Fight.Stunned() && M->Player->Fight.StunKneel;
        if(WasStunned && M->Player->Fight.Action==EWardenAction::Dodge) R.ActedWhileStunned=true;
        if(WasStunned && M->Player->Fight.Stunned()) M->Player->PendingAction=EWardenAction::Ready;
    }
    R.Taken=M->Player->Fight.MaxHealth-M->Player->Fight.Health; R.Stuns=M->Bellbreaker.Stuns; R.Avoided=M->Bellbreaker.Avoided;
    CloseWorld(W);
    return R;
}
// Step index at which the (first) crest reaches a player Distance beyond the impact point.
int32 CrestArrival(float Distance)
{
    using namespace WardenBellbreaker;
    return Strike(Quake).Windup+FMath::CeilToInt((Distance-CrestHalfWidth-RingStart)/(RingSpeed*WardenRules::Step));
}
}

BELLBREAKER_TEST(FBellbreakerStunRulesTest,"BossLab.Bellbreaker.StunRules");
bool FBellbreakerStunRulesTest::RunTest(const FString&)
{
    using namespace WardenRules;
    FWardenFighterState S;
    TestTrue(TEXT("A standing fighter can be stunned"),S.Stun(84));
    TestTrue(TEXT("Stunned"),S.Stunned());
    TestFalse(TEXT("No roll while stunned"),S.Request(EWardenAction::Dodge));
    TestFalse(TEXT("No attack while stunned"),S.Request(EWardenAction::Strike,S.NextPlayerMove()));
    TestFalse(TEXT("No heal while stunned"),S.Request(EWardenAction::Heal));
    TestFalse(TEXT("A running stun is never restarted"),S.Stun(84));
    const float Stamina=S.Stamina=40;
    for(int32 I=0;I<83;++I) S.Advance();
    TestTrue(TEXT("Still stunned at 83 ticks"),S.Stunned());
    TestEqual(TEXT("No stamina regeneration while stunned"),S.Stamina,Stamina);
    S.Advance();
    TestFalse(TEXT("Stun ends after 84 ticks"),S.Stunned());
    TestEqual(TEXT("Immunity starts when the stun ends"),S.StunImmunity,StunImmunityTicks);
    TestFalse(TEXT("No second stun while immune"),S.Stun(84));
    for(int32 I=0;I<StunImmunityTicks;++I) S.Advance();
    TestTrue(TEXT("Stunnable again after the immunity"),S.Stun(84));
    // A blow breaks the stun into the ordinary short hurt: no guaranteed follow-up.
    TestTrue(TEXT("Blow lands on a stunned fighter"),S.Damage(5,true));
    TestTrue(TEXT("The blow ends the stun"),!S.Stunned() && S.Action==EWardenAction::Hurt && S.Age==0);
    for(int32 I=0;I<HurtTicks;++I) S.Advance();
    TestTrue(TEXT("Ordinary hurt length after the break"),S.Action==EWardenAction::Ready);
    TestEqual(TEXT("Breaking a stun still grants immunity"),S.StunImmunity,StunImmunityTicks-HurtTicks);
    // Owner limit: stuns end within 2 s, and the last StunWalkOut ticks can be walked out of.
    TestTrue(TEXT("Shockwave and blast stuns last at most 2 s"),WardenBellbreaker::WaveStun<=120 && WardenBellbreaker::BlastStun<=120);
    {
        FWardenFighterState W; W.Stun(WardenBellbreaker::WaveStun);
        for(int32 I=0;I<WardenBellbreaker::WaveStun-StunWalkOut-1;++I) W.Advance();
        TestFalse(TEXT("No walking out early in the stun"),W.CancelIntoMove());
        W.Advance();
        TestTrue(TEXT("Walk out in the last quarter-second"),W.CancelIntoMove() && W.Action==EWardenAction::Ready && !W.Stunned() && W.StunImmunity==StunImmunityTicks);
    }
    FWardenFighterState Roll;
    TestTrue(TEXT("Roll starts"),Roll.Request(EWardenAction::Dodge));
    for(int32 I=0;I<5;++I) Roll.Advance();
    TestFalse(TEXT("Roll i-frames refuse a stun"),Roll.Stun(84));
    // The boss table: readable telegraphs; the quake's damage is all blast and crest.
    for(int32 M=WardenBellbreaker::First;M<WardenBellbreaker::End;++M)
    {
        const auto& D=WardenRules::Strike(M);
        TestTrue(FString::Printf(TEXT("%s telegraph >= 40 ticks (%d)"),D.Name,D.Windup),D.Windup>=40);
        TestTrue(FString::Printf(TEXT("%s recovery >= 50 ticks (punish window)"),D.Name),D.Recovery>=50);
    }
    for(int32 Move : {WardenBellbreaker::HammerFall,WardenBellbreaker::Sweep,WardenBellbreaker::Quake})
    {
        FWardenFighterState B; B.IsBoss=true;
        TestTrue(TEXT("Heavy move can commit"),B.Request(EWardenAction::Strike,Move));
        const int32 Lock=WardenBellbreaker::RepeatLock(Move);
        for(int32 I=1;I<Lock;++I) B.Advance();
        TestTrue(TEXT("Boss has finished recovery before repeat lock expires"),B.Ready());
        TestFalse(TEXT("Cannot repeat a special one tick early"),B.Request(EWardenAction::Strike,Move));
        B.Advance();
        TestTrue(TEXT("Can repeat on the first eligible tick"),B.Request(EWardenAction::Strike,Move));
    }
    TestEqual(TEXT("Quake deals no swept damage"),WardenRules::Strike(WardenBellbreaker::Quake).Damage,0.f);
    TestTrue(TEXT("Crest passes a player in about 4 ticks"),2*WardenBellbreaker::CrestHalfWidth/(WardenBellbreaker::RingSpeed*Step)<=4.5f);
    return true;
}

BELLBREAKER_TEST(FBellbreakerQuakeTest,"BossLab.Bellbreaker.QuakeJumpOrRollOrStun");
bool FBellbreakerQuakeTest::RunTest(const FString&)
{
    using namespace WardenBellbreaker;
    const float D=500; const int32 Arrive=CrestArrival(D);
    const FDuel Stand=Duel(Quake,D,{});
    AddInfo(FString::Printf(TEXT("Standing at %.0f cm: crest at step %d, took %.0f, stuns %d"),D,Arrive,Stand.Taken,Stand.Stuns));
    TestEqual(TEXT("Standing: stunned once"),Stand.Stuns,1);
    TestEqual(TEXT("Standing: crest chip damage"),Stand.Taken,WaveDamage);
    TestFalse(TEXT("Mashing roll does nothing while stunned"),Stand.ActedWhileStunned);
    const FDuel Jump=Duel(Quake,D,{{EWardenAction::Jump,Arrive-18}});
    AddInfo(FString::Printf(TEXT("Jump 18 steps early: took %.0f, stuns %d, avoided %d"),Jump.Taken,Jump.Stuns,Jump.Avoided));
    TestTrue(TEXT("A timed jump clears the crest"),Jump.Stuns==0 && Jump.Taken==0 && Jump.Avoided==1);
    const FDuel Roll=Duel(Quake,D,{{EWardenAction::Dodge,Arrive-12,FVector::RightVector}});
    AddInfo(FString::Printf(TEXT("Side roll 12 steps early: took %.0f, stuns %d, avoided %d"),Roll.Taken,Roll.Stuns,Roll.Avoided));
    TestTrue(TEXT("A timed roll clears the crest"),Roll.Stuns==0 && Roll.Taken==0 && Roll.Avoided==1);
    const FDuel EarlyJump=Duel(Quake,D,{{EWardenAction::Jump,Arrive-60}});
    TestEqual(TEXT("A jump long before the crest lands in time to be stunned"),EarlyJump.Stuns,1);
    // At 9.8 m the old shader expired before its brightest line ever reached the player.
    // Compare the first damaging tick at this distance to the band sent to the material.
    const float EdgeDistance=980.f;
    const FDuel Outer=Duel(Quake,EdgeDistance,{});
    TestEqual(TEXT("Outer live band still chips"),Outer.Taken,WaveDamage);
    int32 FirstEdgeTick=0;
    while(FirstEdgeTick<120 && WaveBand(FirstEdgeTick).Y<EdgeDistance) ++FirstEdgeTick;
    TestEqual(TEXT("First actual damage coincides with first visible-band tick at 9.8 m"),Outer.FirstDamageWaveAge,FirstEdgeTick);
    const FVector2D Visible=WaveBand(FirstEdgeTick);
    TestTrue(TEXT("Rendered swept band contains outer target on its first threatening tick"),
        FirstEdgeTick>0 && WaveRadius(FirstEdgeTick)<=RingEnd && Visible.X<=EdgeDistance &&
        Visible.Y>=EdgeDistance && WaveBand(FirstEdgeTick-1).Y<EdgeDistance);
    const FDuel Far=Duel(Quake,RingEnd+200,{});
    TestTrue(TEXT("Beyond the crest's reach: untouched"),Far.Stuns==0 && Far.Taken==0);
    const FDuel Blast=Duel(Quake,100,{});
    AddInfo(FString::Printf(TEXT("Under the bell: took %.0f, kneel %d"),Blast.Taken,int32(Blast.Kneel)));
    TestEqual(TEXT("Blast damage under the bell"),Blast.Taken,BlastDamage);
    TestTrue(TEXT("The blast knocks down (kneel stun)"),Blast.Kneel);
    const FDuel BlastJump=Duel(Quake,100,{{EWardenAction::Jump,Strike(Quake).Windup-18}});
    TestEqual(TEXT("Jumping does not clear the blast"),BlastJump.Taken,BlastDamage);
    const FDuel BlastRoll=Duel(Quake,100,{{EWardenAction::Dodge,Strike(Quake).Windup-6,FVector::RightVector}});
    TestTrue(TEXT("A timed roll beats the blast"),BlastRoll.Taken<BlastDamage);
    return true;
}

BELLBREAKER_TEST(FBellbreakerTwinTest,"BossLab.Bellbreaker.TwinQuake");
bool FBellbreakerTwinTest::RunTest(const FString&)
{
    using namespace WardenBellbreaker;
    const float D=500; const int32 A1=CrestArrival(D), A2=A1+TwinDelay;
    const FDuel Stand=Duel(Quake,D,{},true);
    AddInfo(FString::Printf(TEXT("Twin, standing: took %.0f, stuns %d"),Stand.Taken,Stand.Stuns));
    TestEqual(TEXT("Standing: one stun (the second crest only chips)"),Stand.Stuns,1);
    TestEqual(TEXT("Standing: both crests chip"),Stand.Taken,2*WaveDamage);
    const FDuel OneJump=Duel(Quake,D,{{EWardenAction::Jump,A1-18}},true);
    TestEqual(TEXT("Answering only the first crest: stunned by the second"),OneJump.Stuns,1);
    struct FCase { const TCHAR* Name; FResponse First, Second; };
    const FCase Cases[]={
        {TEXT("roll, roll"),{EWardenAction::Dodge,A1-12,FVector::RightVector},{EWardenAction::Dodge,A2-12,-FVector::RightVector}},
        {TEXT("jump, jump"),{EWardenAction::Jump,A1-18},{EWardenAction::Jump,A2-10}},
        {TEXT("jump, roll"),{EWardenAction::Jump,A1-18},{EWardenAction::Dodge,A2-8,FVector::RightVector}},
        {TEXT("roll, jump"),{EWardenAction::Dodge,A1-12,FVector::RightVector},{EWardenAction::Jump,A2-8}}};
    for(const auto& C:Cases)
    {
        const FDuel R=Duel(Quake,D,{C.First,C.Second},true);
        AddInfo(FString::Printf(TEXT("Twin, %s: took %.0f, stuns %d, avoided %d"),C.Name,R.Taken,R.Stuns,R.Avoided));
        TestTrue(FString::Printf(TEXT("Twin Quake answered by %s"),C.Name),R.Stuns==0 && R.Taken==0 && R.Avoided==2);
    }
    return true;
}

BELLBREAKER_TEST(FBellbreakerRollTest,"BossLab.Bellbreaker.RollBeatsHammer");
bool FBellbreakerRollTest::RunTest(const FString&)
{
    using namespace WardenBellbreaker;
    struct FCase { int32 Move; float Distance; int32 RollAt; FVector Direction; };
    const FCase Cases[]={{HammerFall,330,Strike(HammerFall).Windup-4,FVector::RightVector},{Sweep,380,Strike(Sweep).Windup-4,FVector::RightVector}};
    for(const auto& C:Cases)
    {
        const FDuel Still=Duel(C.Move,C.Distance,{});
        const FDuel Rolled=Duel(C.Move,C.Distance,{{EWardenAction::Dodge,C.RollAt,C.Direction}});
        AddInfo(FString::Printf(TEXT("%s: standing still takes %.0f, timed roll takes %.0f"),Strike(C.Move).Name,Still.Taken,Rolled.Taken));
        TestTrue(FString::Printf(TEXT("%s hits a player who stands still"),Strike(C.Move).Name),Still.Taken>=Strike(C.Move).Damage);
        TestEqual(FString::Printf(TEXT("%s is beaten by one timed roll"),Strike(C.Move).Name),Rolled.Taken,0.f);
    }
    return true;
}

BELLBREAKER_TEST(FBellbreakerEncounterTest,"BossLab.Bellbreaker.RehearsalUsesEveryMove");
bool FBellbreakerEncounterTest::RunTest(const FString&)
{
    // The fixed rehearsal against the scripted practice player: every move commits, phase two arrives,
    // and nothing outside the Bellbreaker's own rows is selected.
    auto* W=NewWorld(); auto* M=BellArena(W);
    M->bScriptedPlayer=true; M->Bellbreaker.Waiting=60;
    M->bPracticeInfiniteHealth=true;   // the practice refill (creative-only through the menu)
    TSet<int32> Seen; bool Foreign=false;
    for(int32 T=0;T<60*260 && M->Warden->Fight.Alive();++T)
    {
        M->FixedStep();
        if(M->Warden->Fight.Action==EWardenAction::Strike) { Seen.Add(M->Warden->Fight.Move); Foreign|=!WardenBellbreaker::IsBellbreaker(M->Warden->Fight.Move); }
        if(T==60*120) M->Warden->Fight.Health=WardenBellbreaker::PhaseTwoHealth;   // jump to the threshold
        // The scripted practice player hugs the boss; step it away now and then so the ranged rows
        // (Charge, Fling, Striding Fall) get their room, as a real player gives it.
        if(T%(60*20)>=60*10 && T%(60*20)<60*16) { const FVector Away=(M->Player->GetActorLocation()-M->Warden->GetActorLocation()).GetSafeNormal2D(); M->Player->SetActorLocation(M->Warden->GetActorLocation()*FVector(1,1,0)+FVector(0,0,95)+(Away.IsNearlyZero()?FVector::ForwardVector:Away)*950.f); }
    }
    AddInfo(FString::Printf(TEXT("Moves seen %d, phase two %d, stuns %d, avoided %d, boss hp %.0f"),Seen.Num(),int32(M->Bellbreaker.PhaseTwo),M->Bellbreaker.Stuns,M->Bellbreaker.Avoided,M->Warden->Fight.Health));
    for(int32 Move=WardenBellbreaker::First;Move<WardenBellbreaker::End;++Move)
        TestTrue(FString::Printf(TEXT("%s commits"),WardenRules::Strike(Move).Name),Seen.Contains(Move));
    TestTrue(TEXT("Phase two reached"),M->Bellbreaker.PhaseTwo);
    TestFalse(TEXT("Only Bellbreaker moves"),Foreign);
    CloseWorld(W);
    return true;
}

BELLBREAKER_TEST(FBellbreakerReadyMovesTest,"BossLab.Bellbreaker.ReadinessMoves");
bool FBellbreakerReadyMovesTest::RunTest(const FString&)
{
    using namespace WardenBellbreaker;
    // At least as many rows as a full boss: 14 Bellbreaker moves, every one with its own repeat lock.
    TestTrue(TEXT("Fourteen Bellbreaker moves"),Count>=14);
    for(int32 Move=First;Move<End;++Move)
    {
        FWardenFighterState B; B.IsBoss=true;
        TestTrue(FString::Printf(TEXT("%s commits"),Strike(Move).Name),B.Request(EWardenAction::Strike,Move));
        TestTrue(FString::Printf(TEXT("%s has a cooldown longer than itself"),Strike(Move).Name),B.Cooldowns[Move]>Strike(Move).Total());
        while(!B.Ready()) B.Advance();
        TestFalse(FString::Printf(TEXT("%s cannot repeat straight away"),Strike(Move).Name),B.Request(EWardenAction::Strike,Move));
        // Every pose, start to end: finite and within the giant's reach (the drawn hammer is the hit path).
        bool Sane=true;
        for(int32 Age=0;Age<=Strike(Move).Total();++Age)
        {
            const FVector Bell=BellOffset(Move,Age,true), Grip=GripOffset(Move,Age,true);
            Sane&=!Bell.ContainsNaN() && Bell.Size2D()<700 && Bell.Z>-5 && Bell.Z<800 && FMath::IsNearlyEqual(FVector::Dist(Bell,Grip),BellReach,1.f);
        }
        TestTrue(FString::Printf(TEXT("%s bell path stays sane"),Strike(Move).Name),Sane);
    }
    TestEqual(TEXT("Cyclone ends facing forward"),FMath::Fmod(CycloneSpin(Cyclone,Strike(Cyclone).Windup+Strike(Cyclone).Active)+720.f,360.f),0.f,.5f);
    // The Toll: standing or jumping is hit; a roll through it is not.
    const FDuel Stand=Duel(Toll,500,{});
    TestTrue(TEXT("Toll hits a standing player"),Stand.Taken>=TollDamage);
    const int32 Arrive=Strike(Toll).Windup+FMath::CeilToInt((500-TollStart)/(TollSpeed*WardenRules::Step));
    const FDuel Jumped=Duel(Toll,500,{{EWardenAction::Jump,Arrive-14}});
    TestTrue(TEXT("Jumping does not clear the toll"),Jumped.Taken>=TollDamage);
    const FDuel Rolled=Duel(Toll,500,{{EWardenAction::Dodge,Arrive-6}});
    TestEqual(TEXT("A roll through the toll takes nothing"),Rolled.Taken,0.f);
    // Anvil Stamp: in reach is hit, outside is safe.
    TestTrue(TEXT("Stamp hits a hugging player"),Duel(Stamp,150,{}).Taken>=StampDamage);
    TestEqual(TEXT("Stamp misses outside its radius"),Duel(Stamp,StampAhead+StampRadius+120,{}).Taken,0.f);
    // Slag Fling: three globs land on the marks; a player who walks off the mark is safe.
    TestTrue(TEXT("Slag lands on a player who stays"),Duel(Fling,900,{}).Taken>=SlagDamage);
    // Death Knell: three blasts on one mark, then a crest.
    TestTrue(TEXT("Knell blasts a player on the mark"),Duel(Knell,QuakeImpactOffset().X,{},true).Taken>=KnellDamage);
    return true;
}

BELLBREAKER_TEST(FBellbreakerMoveAfterTest,"BossLab.Bellbreaker.MoveAfterStunAndHits");
bool FBellbreakerMoveAfterTest::RunTest(const FString&)
{
    // Owner report 2026-11-18: after a stun or other effects the player could roll but not walk. For each
    // effect: let it play out, then hold the stick away from the boss for 60 ticks and measure the walk.
    using namespace WardenBellbreaker;
    struct FCase { const TCHAR* Name; int32 Move; float Distance; };
    const FCase Cases[]={{TEXT("shockwave stun"),Quake,500},{TEXT("blast knockdown"),Quake,100},{TEXT("hammer hit"),HammerFall,330},{TEXT("sweep hit"),Sweep,380}};
    for(const auto& C:Cases)
    {
        auto* W=NewWorld(); auto* M=BellArena(W);
        const FVector Impact=QuakeImpactOffset();
        M->Player->SetActorLocation(C.Move==Quake ? FVector(Impact.X+C.Distance,Impact.Y,95) : FVector(C.Distance,0,95));
        M->Warden->BeginAction(EWardenAction::Strike,C.Move,FVector::ForwardVector);
        bool Hit=false; int32 Ticks=0;
        while(Ticks<600 && !(Hit && M->Player->Fight.Ready() && M->Warden->Fight.Action!=EWardenAction::Strike)) { M->FixedStep(); Hit|=M->Player->Fight.Action==EWardenAction::Hurt; ++Ticks; }
        const FVector Start=M->Player->GetActorLocation();
        M->TestPilot=[](AWardenArenaMode&,FVector& Intent){ Intent=FVector(1,0,0); };
        for(int32 T=0;T<60;++T) M->FixedStep();
        const float Walked=FVector::Dist2D(Start,M->Player->GetActorLocation());
        AddInfo(FString::Printf(TEXT("%s: hit %d, ready after %d ticks, then walked %.0f cm in 1 s (action %d, z %.1f)"),C.Name,int32(Hit),Ticks,Walked,int32(M->Player->Fight.Action),M->Player->GetActorLocation().Z));
        TestTrue(FString::Printf(TEXT("%s lands"),C.Name),Hit);
        TestTrue(FString::Printf(TEXT("%s: the player walks afterwards"),C.Name),Walked>200);
        CloseWorld(W);
    }
    return true;
}

BELLBREAKER_TEST(FBellbreakerRealInputTest,"BossLab.Bellbreaker.RealInputAfterStun");
bool FBellbreakerRealInputTest::RunTest(const FString&)
{
    // The real play path: a possessed player controller, lock-on, a menu-started challenge, roll mashed during the
    // stun and the stick held from the stun on, movement read through MoveIntent (control rotation + axis input).
    // Default arena and (when imported) the Hearth A2 forge; stick directions away from and across the boss.
    using namespace WardenBellbreaker;
    const bool Forge=IFileManager::Get().FileExists(*(FPaths::ProjectContentDir()/TEXT("BossLab/HearthA2/layout.json")));
    for(int32 Arena=0;Arena<(Forge?2:1);++Arena)
    for(const bool Blast:{false,true})
    for(const float StickF:{-1.f,0.f})
    {
        auto* W=NewWorld();
        AWardenArenaMode* M=nullptr;
        if(Arena==0) M=BellArena(W);
        else
        {
            M=W->SpawnActor<AWardenArenaMode>(); M->bForgeArena=true;
            M->Player=W->SpawnActor<AWardenChallenger>(FVector(0,-500,95),FRotator::ZeroRotator); M->Player->DispatchBeginPlay(); M->Player->ResetFighter(false);
            M->DispatchBeginPlay(); M->Warden->DispatchBeginPlay(); M->EnableBellbreaker(); M->ConfigureEncounter(303,false,1);
        }
        auto* PC=W->SpawnActor<APlayerController>(); PC->Possess(M->Player);
        M->StartRegentSession(false); M->Bellbreaker.Waiting=1000000;
        const FVector Base=Arena==0 ? FVector::ZeroVector : FVector(0,300,0);
        M->Warden->SetActorLocation(Base+FVector(0,0,StandZ)); M->Warden->SetActorRotation(FRotator::ZeroRotator);
        const FVector Impact=QuakeImpactOffset();
        M->Player->SetActorLocation(Base+FVector(Impact.X+(Blast?100.f:500.f),Impact.Y,95)); M->Player->SetActorRotation(FRotator(0,180,0));
        M->Player->SetLocked(true);
        M->Warden->BeginAction(EWardenAction::Strike,Quake,FVector::ForwardVector);
        int32 StunnedAt=-1, FreeAt=-1; FVector At=FVector::ZeroVector; float Walked=0;
        for(int32 T=0;T<420;++T)
        {
            const bool Hold=StunnedAt>=0;
            M->Player->ForwardInput=Hold && M->Player->AllowsGameplayInput()?StickF:0.f;
            M->Player->RightInput=Hold && M->Player->AllowsGameplayInput()&&StickF==0.f?1.f:0.f;
            if(M->Player->Fight.Stunned() && T%20==0) M->Player->QueueAction(EWardenAction::Dodge);
            M->Player->Tick(WardenRules::Step);
            M->FixedStep();
            if(StunnedAt<0 && M->Player->Fight.Stunned()) StunnedAt=T;
            if(StunnedAt>=0 && FreeAt<0 && !M->Player->Fight.Stunned() && M->Player->Fight.Action!=EWardenAction::Hurt) { FreeAt=T; At=M->Player->GetActorLocation(); }
            if(FreeAt>=0 && T==FreeAt+60) Walked=FVector::Dist2D(At,M->Player->GetActorLocation());
        }
        const FString Name=FString::Printf(TEXT("%s, %s, stick %s"),Arena?TEXT("forge"):TEXT("ring"),Blast?TEXT("blast"):TEXT("shockwave"),StickF<0?TEXT("back"):TEXT("right"));
        AddInfo(FString::Printf(TEXT("%s: stunned at %d, free after %.2f s, then moved %.0f cm in 1 s (ends at %s)"),*Name,StunnedAt,(FreeAt-StunnedAt)/60.f,Walked,*M->Player->GetActorLocation().ToString()));
        TestTrue(Name+TEXT(": stunned"),StunnedAt>=0);
        TestTrue(Name+TEXT(": free within 2 s"),FreeAt>=0 && FreeAt-StunnedAt<=120);
        TestTrue(Name+TEXT(": moves afterwards (walk or the held roll)"),Walked>150);
        CloseWorld(W);
    }
    return true;
}

BELLBREAKER_TEST(FBellbreakerCameraElevationTest,"BossLab.Bellbreaker.CameraElevationHolds");
bool FBellbreakerCameraElevationTest::RunTest(const FString&)
{
    // Owner 2026-11-18: medium-height camera, player-adjustable elevation that stays where it is set.
    auto* W=NewWorld(); auto* M=BellArena(W);
    auto* PC=W->SpawnActor<APlayerController>(); PC->Possess(M->Player);
    M->StartRegentSession(false); M->Bellbreaker.Waiting=1000000;
    M->Warden->SetActorLocation(FVector(0,0,WardenBellbreaker::StandZ)); M->Player->SetActorLocation(FVector(-650,0,95));
    M->Player->SetLocked(true);
    for(int32 T=0;T<240;++T) M->Player->Tick(WardenRules::Step);
    const float Base=PC->GetControlRotation().Pitch>180 ? PC->GetControlRotation().Pitch-360 : PC->GetControlRotation().Pitch;
    M->Player->LockPitchOffset=10.f;   // the player nudged the view up
    for(int32 T=0;T<300;++T) M->Player->Tick(WardenRules::Step);   // 5 s without touching the mouse
    float Held=PC->GetControlRotation().Pitch; if(Held>180) Held-=360;
    AddInfo(FString::Printf(TEXT("locked pitch %.1f deg at 6.5 m; after +10 elevation and 5 s idle: %.1f (offset %.1f); socket %s arm %.0f"),Base,Held,M->Player->LockPitchOffset,*M->Player->Arm->SocketOffset.ToString(),M->Player->Arm->TargetArmLength));
    TestTrue(TEXT("Default view looks gently down, never up"),Base<=0.f && Base>=-25.f);
    TestTrue(TEXT("The player's elevation offset is kept"),FMath::IsNearlyEqual(M->Player->LockPitchOffset,10.f,.01f) && Held>Base+5.f);
    CloseWorld(W);
    return true;
}

// Explicit asset trial (needs the local Hearth A2 scene and Bellbreaker imports), like WardenAssetTrial.HearthA2.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBellbreakerForgeTrial,"WardenAssetTrial.BellbreakerForge",(EAutomationTestFlags::EditorContext|EAutomationTestFlags::ClientContext)|EAutomationTestFlags::EngineFilter)
bool FBellbreakerForgeTrial::RunTest(const FString&)
{
    if(!IFileManager::Get().FileExists(*(FPaths::ProjectContentDir()/TEXT("BossLab/HearthA2/layout.json"))))
    { AddError(TEXT("The forge trial needs the imported Hearth A2 scene")); return false; }
    auto* W=NewWorld();
    auto* M=W->SpawnActor<AWardenArenaMode>(); M->bForgeArena=true;
    M->Player=W->SpawnActor<AWardenChallenger>(FVector(0,-500,95),FRotator::ZeroRotator); M->Player->DispatchBeginPlay(); M->Player->ResetFighter(false);
    M->DispatchBeginPlay();
    if(!M->Warden) { AddError(TEXT("No boss spawned in the forge")); CloseWorld(W); return false; }
    M->Warden->DispatchBeginPlay(); M->EnableBellbreaker(); M->ConfigureEncounter(303,true,1);
    int32 Dressing=0, RingWalls=0, CameraWalls=0;
    for(TActorIterator<AStaticMeshActor> It(W);It;++It)
    {
        Dressing+=It->ActorHasTag(TEXT("SmelteryDressing"));
        if(It->ActorHasTag(TEXT("SmelteryBoundary")) && It->GetStaticMeshComponent()->GetCollisionResponseToChannel(ECC_Camera)==ECR_Block) ++CameraWalls;
        RingWalls+=It->GetActorScale3D().Equals(FVector(.55,2.8,2.6),.01);   // the default arena's ring of wall blocks
    }
    AddInfo(FString::Printf(TEXT("Forge: %d dressing actors, %d default ring walls"),Dressing,RingWalls));
    TestTrue(TEXT("Encounter mode, not the walkthrough"),M->bForgeArena && M->bBellbreaker && !M->bSmelteryWalkthrough && M->bRehearsal);
    TestTrue(TEXT("Hearth A2 art is built (40 layout instances plus fire, molten channel and steam)"),Dressing>=40);
    TestEqual(TEXT("No default ring arena"),RingWalls,0);
    TestEqual(TEXT("Fight camera retracts at each forge work bay"),CameraWalls,4);
    TestTrue(TEXT("Player enters at the entry side"),M->Player->GetActorLocation().Y<-300);
    TestTrue(TEXT("Bellbreaker stands before the furnace"),M->Warden->GetActorLocation().Y>300);
    // The rehearsal plays in the forge: the giant reaches the player around the work islands and commits.
    M->bPracticeInfiniteHealth=true; M->Bellbreaker.Waiting=60;
    TSet<int32> Seen; int32 Commits=0; float MaxX=0, MaxY=0;
    for(int32 T=0;T<60*60;++T)
    {
        const int32 Before=M->Warden->Fight.AttackInstance;
        M->FixedStep();
        if(M->Warden->Fight.AttackInstance!=Before) { ++Commits; Seen.Add(M->Warden->Fight.Move); }
        for(const AActor* A:{(const AActor*)M->Player.Get(),(const AActor*)M->Warden.Get()})
        { MaxX=FMath::Max(MaxX,FMath::Abs(A->GetActorLocation().X)); MaxY=FMath::Max(MaxY,FMath::Abs(A->GetActorLocation().Y)); }
        if(!M->Warden->Fight.Alive()) break;
    }
    AddInfo(FString::Printf(TEXT("60 s in the forge: %d commits, %d distinct moves, stuns %d, avoided %d, extent x %.0f y %.0f"),Commits,Seen.Num(),M->Bellbreaker.Stuns,M->Bellbreaker.Avoided,MaxX,MaxY));
    TestTrue(TEXT("The boss keeps committing in the forge (not stuck on props)"),Commits>=5);
    TestTrue(TEXT("Hammer Fall, Sweep and Quake all used"),Seen.Contains(WardenBellbreaker::HammerFall) && Seen.Contains(WardenBellbreaker::Sweep) && Seen.Contains(WardenBellbreaker::Quake));
    TestTrue(TEXT("Both fighters stay inside the forge field"),MaxX<=M->SmelteryHalfSize.X && MaxY<=M->SmelteryHalfSize.Y);
    // The menu's Begin challenge (StartRegentSession) keeps the Bellbreaker and the forge; it used to enable the Regent.
    M->StartRegentSession(false);
    TestTrue(TEXT("Menu challenge keeps the Bellbreaker, not the Regent"),M->bBellbreaker && !M->bRegent && M->Warden->bBellbreaker && !M->Warden->bRegent);
    TestTrue(TEXT("Menu challenge restarts at the forge positions"),M->Player->GetActorLocation().Y<-300 && M->Warden->GetActorLocation().Y>300);
    TestEqual(TEXT("Menu challenge restores his health"),M->Warden->Fight.Health,WardenBellbreaker::Health);
    CloseWorld(W);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBellbreakerForgeOverlapProbe,"WardenAssetTrial.BellbreakerForgeOverlap",(EAutomationTestFlags::EditorContext|EAutomationTestFlags::ClientContext)|EAutomationTestFlags::EngineFilter)
bool FBellbreakerForgeOverlapProbe::RunTest(const FString&)
{
    // Owner log 2026-11-18: the player was blocked by a StaticMeshActor starting 1 cm inside it, normal straight up.
    // List everything the player's capsule overlaps at spawn: fresh, after a Quake, and after a reset.
    using namespace WardenBellbreaker;
    auto* W=NewWorld();
    auto* M=W->SpawnActor<AWardenArenaMode>(); M->bForgeArena=true;
    M->Player=W->SpawnActor<AWardenChallenger>(FVector(0,-500,95),FRotator::ZeroRotator); M->Player->DispatchBeginPlay(); M->Player->ResetFighter(false);
    M->DispatchBeginPlay(); M->Warden->DispatchBeginPlay(); M->EnableBellbreaker(); M->StartRegentSession(false);
    int32 Bad=0;
    auto Probe=[&](const TCHAR* When)
    {
        TArray<FOverlapResult> Hits; FCollisionQueryParams Q(SCENE_QUERY_STAT(Probe),false,M->Player);
        W->OverlapMultiByChannel(Hits,M->Player->GetActorLocation(),FQuat::Identity,ECC_Pawn,M->Player->Capsule->GetCollisionShape(),Q);
        for(const auto& H:Hits)
        {
            const auto* C=H.GetComponent(); if(!C) continue;
            const FBox B=C->Bounds.GetBox();
            const auto* SM=Cast<UStaticMeshComponent>(C);
            AddInfo(FString::Printf(TEXT("%s: %s/%s mesh %s blocking %d profile %s box min %s max %s scale %s tags %s"),When,*C->GetOwner()->GetName(),*C->GetName(),
                SM&&SM->GetStaticMesh()?*SM->GetStaticMesh()->GetName():TEXT("-"),int32(H.bBlockingHit),*C->GetCollisionProfileName().ToString(),*B.Min.ToString(),*B.Max.ToString(),
                *C->GetComponentScale().ToString(),C->GetOwner()->Tags.Num()?*C->GetOwner()->Tags[0].ToString():TEXT("-")));
            ++Bad;
        }
        AddInfo(FString::Printf(TEXT("%s: %d overlaps at %s"),When,Hits.Num(),*M->Player->GetActorLocation().ToString()));
    };
    Probe(TEXT("fresh"));
    M->Player->SetActorLocation(FVector(0,-100,95)); M->Bellbreaker.Waiting=1000000;
    M->Warden->BeginAction(EWardenAction::Strike,Quake,(M->Player->GetActorLocation()-M->Warden->GetActorLocation()).GetSafeNormal2D());
    for(int32 T=0;T<240;++T) { M->FixedStep(); M->Tick(WardenRules::Step); }
    Probe(TEXT("after quake"));
    M->ResetEncounter(); M->Tick(WardenRules::Step);
    Probe(TEXT("after reset"));
    // Regression for the owner's log: a shockwave ring plane left under the player's feet (z 6, 20 m wide).
    for(auto& R:M->BellbreakerRings) if(R.IsValid()) { R->SetVisibility(true); R->SetWorldLocation(M->Player->GetActorLocation()*FVector(1,1,0)+FVector(0,0,6)); R->SetWorldScale3D(FVector(20,20,1)); }
    const FVector Start=M->Player->GetActorLocation();
    for(int32 T=0;T<30;++T) M->Player->MoveSwept(FVector(0,7,0));
    const float Walked=FVector::Dist2D(Start,M->Player->GetActorLocation());
    AddInfo(FString::Printf(TEXT("ring under the feet: walked %.0f cm of 210"),Walked));
    TestTrue(TEXT("A shockwave ring under the player never blocks walking"),Walked>200);
    TestEqual(TEXT("Nothing blocks the player's capsule at spawn"),Bad,0);
    CloseWorld(W);
    return true;
}

#endif
