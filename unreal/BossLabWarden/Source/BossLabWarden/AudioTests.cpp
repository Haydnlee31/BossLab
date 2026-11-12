#include "WardenPrototype.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Sound/SoundBase.h"
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
            {TEXT("RegentSkull"),4},{TEXT("RegentBlink"),3},{TEXT("RegentEruption"),3},{TEXT("RegentPyre"),2},{TEXT("RegentWakes"),3},
            {TEXT("AmbDungeon"),1},{TEXT("AmbFire"),1}};
        for(const auto& E:Events) TestEqual(FString::Printf(TEXT("%s variations"),E.Key),M->SfxVariations(E.Key,nullptr).Num(),E.Value);
    }
    else AddInfo(TEXT("Layered sound set not imported here; legacy sounds stand in."));
    GEngine->DestroyWorldContext(W); W->DestroyWorld(false);
    return true;
}
#endif
