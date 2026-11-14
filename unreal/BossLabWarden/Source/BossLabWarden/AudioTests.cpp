#include "WardenPrototype.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Sound/SoundBase.h"
#include "Components/AudioComponent.h"
#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FWardenAudioVariationTest,"BossLab.Audio.VariationsNeverRepeat",(EAutomationTestFlags::EditorContext|EAutomationTestFlags::ClientContext)|EAutomationTestFlags::EngineFilter)
bool FWardenAudioVariationTest::RunTest(const FString&)
{
    auto* W=UWorld::CreateWorld(EWorldType::Game,false); GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
    auto* M=W->SpawnActor<AWardenArenaMode>();
    // The picker never plays the same variation twice running and reaches every variation.
    TSet<int32> Seen; int32 Last=-1;
    for(int32 I=0;I<400;++I)
    {
        const int32 Pick=M->SfxPick(TEXT("Probe"),5);
        TestTrue(TEXT("Pick in range"),Pick>=0 && Pick<5);
        TestNotEqual(TEXT("No immediate repeat"),Pick,Last);
        Last=Pick; Seen.Add(Pick);
    }
    TestEqual(TEXT("Every variation is used"),Seen.Num(),5);
    TestEqual(TEXT("A single sound still plays"),M->SfxPick(TEXT("Single"),1),0);
    // The layered set (ue_import_game_audio.py) is local; when present every event in the
    // spotting list must have its variations. Absent, the older single sounds stand in.
    if(LoadObject<USoundBase>(nullptr,TEXT("/Game/BossLab/Sound/SwordHit_0"),nullptr,LOAD_Quiet|LOAD_NoWarn))
    {
        const TPair<const TCHAR*,int32> Events[]={{TEXT("SwordWhooshLight"),5},{TEXT("SwordWhooshHeavy"),4},{TEXT("SwordHit"),5},{TEXT("SwordSlam"),3},
            {TEXT("RuneHum"),3},{TEXT("BodyHit"),5},{TEXT("GearSwing"),4},{TEXT("RollCloth"),4},{TEXT("StepStone"),8},{TEXT("StepHeavy"),5},
            {TEXT("LandHeavy"),3},{TEXT("FlaskDrink"),3},{TEXT("RegentBell"),3},{TEXT("RegentWhoosh"),4},{TEXT("RegentThrust"),4},
            {TEXT("RegentSkull"),5},{TEXT("RegentSkullDive"),3},{TEXT("RegentWhisper"),4},{TEXT("RegentCast"),4},{TEXT("RegentCastLong"),2},{TEXT("RegentChoir"),3},{TEXT("MusicBoss"),1},{TEXT("RegentRaise"),3},{TEXT("SkeletonRise"),3},{TEXT("SkeletonStep"),5},{TEXT("SkeletonSwing"),3},{TEXT("SkeletonHit"),5},{TEXT("SkeletonFall"),3},{TEXT("CenserScrape"),4},{TEXT("RegentDashCharge"),3},{TEXT("RegentDash"),3},{TEXT("RegentBlink"),3},{TEXT("RegentEruption"),3},{TEXT("RegentPyre"),2},{TEXT("RegentWakes"),3},
            {TEXT("AmbDungeon"),1},{TEXT("AmbFire"),1}};
        for(const auto& E:Events) TestEqual(FString::Printf(TEXT("%s variations"),E.Key),M->SfxVariations(E.Key,nullptr).Num(),E.Value);
    }
    else AddInfo(TEXT("Layered sound set not imported here; legacy sounds stand in."));
    GEngine->DestroyWorldContext(W); W->DestroyWorld(false);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FWardenInterfaceAudioTest,"BossLab.Audio.InterfaceRouting",(EAutomationTestFlags::EditorContext|EAutomationTestFlags::ClientContext)|EAutomationTestFlags::EngineFilter)
bool FWardenInterfaceAudioTest::RunTest(const FString&)
{
    auto* W=UWorld::CreateWorld(EWorldType::Game,false); GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
    auto* M=W->SpawnActor<AWardenArenaMode>();
    M->Warden=W->SpawnActor<AWardenChallenger>(); M->Player=W->SpawnActor<AWardenChallenger>();
    M->Warden->Fight.Health=M->Player->Fight.Health=100;
    M->bTitle=true; M->bPaused=true; M->MusicVolumeScale=1;
    TestFalse(TEXT("Home blocks world ambience and one-shots"),M->WorldAudioEnabled());
    TestEqual(TEXT("Living boss cannot play music behind Home"),M->MusicLevel(),0.f);
    TestTrue(TEXT("Home has separate quiet score"),M->MenuMusicLevel()>0 && M->MenuMusicLevel()<.5f);
    M->MusicVolumeScale=0; TestEqual(TEXT("Music slider mutes title score"),M->MenuMusicLevel(),0.f);
    M->MusicVolumeScale=1; M->bMuted=true; TestEqual(TEXT("Mute silences title score"),M->MenuMusicLevel(),0.f);
    M->bMuted=false; M->bTitle=false; M->bPaused=false;
    TestTrue(TEXT("Fight restores world audio"),M->WorldAudioEnabled() && M->MusicLevel()>0);
    TestEqual(TEXT("Fight has no menu score"),M->MenuMusicLevel(),0.f);
    M->bPaused=true; TestTrue(TEXT("Pause/settings are quiet"),!M->WorldAudioEnabled() && M->MusicLevel()==0 && M->MenuMusicLevel()==0);
    M->bPaused=false; M->Player->Fight.Health=0;
    TestEqual(TEXT("Death stops boss music even while boss lives"),M->MusicLevel(),0.f);
    M->Player->Fight.Health=100;
    auto* Music=NewObject<UAudioComponent>(M); M->MusicComponent=Music;
    M->bTitle=true; M->bPaused=true; M->UpdateAudio();
    TestEqual(TEXT("Home suppresses actual boss component gain"),Music->VolumeMultiplier,0.f);
    M->bTitle=false; M->bPaused=false; M->UpdateAudio();
    TestEqual(TEXT("Challenge restores component gain independently of fade envelope"),Music->VolumeMultiplier,1.f);
    M->bPaused=true; M->UpdateAudio(); M->bPaused=false; M->UpdateAudio();
    TestEqual(TEXT("Resume restores gain a second time"),Music->VolumeMultiplier,1.f);
    GEngine->DestroyWorldContext(W); W->DestroyWorld(false); return true;
}
#endif
