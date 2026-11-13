#include "WardenPrototype.h"
#include "WardenQoL.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "GameFramework/InputSettings.h"
#include "HAL/FileManager.h"
#include "Misc/Paths.h"
#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#define QOL_TEST(Type,Name) IMPLEMENT_SIMPLE_AUTOMATION_TEST(Type,Name,(EAutomationTestFlags::EditorContext|EAutomationTestFlags::ClientContext)|EAutomationTestFlags::EngineFilter)
namespace {
UWorld* QoLWorld() { auto* W=UWorld::CreateWorld(EWorldType::Game,false); GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W); return W; }
void QoLClose(UWorld* W) { GEngine->DestroyWorldContext(W); W->DestroyWorld(false); }
AWardenArenaMode* QoLArena(UWorld* W,bool Regent)
{
    auto* M=W->SpawnActor<AWardenArenaMode>();
    M->Player=W->SpawnActor<AWardenChallenger>(FVector(-450,0,95),FRotator::ZeroRotator); M->Player->DispatchBeginPlay(); M->Player->ResetFighter(false);
    M->DispatchBeginPlay(); M->Warden->DispatchBeginPlay();
    if(Regent) M->EnableRegent();
    M->ConfigureEncounter(303,false,1);
    return M;
}
}
QOL_TEST(FWardenSettingsTest,"BossLab.QoL.SettingsPersistAndApply");
bool FWardenSettingsTest::RunTest(const FString&)
{
    // Defaults reproduce the pre-options game exactly.
    const FWardenSettings D;
    TestEqual(TEXT("Default sensitivity"),D.Sensitivity,1.f); TestEqual(TEXT("Default camera"),D.CameraDistance,1.f);
    TestEqual(TEXT("Default volumes"),D.MasterVolume+D.MusicVolume+D.SfxVolume,3.f);
    TestTrue(TEXT("Default toggles"),!D.bInvertY && D.bDamageNumbers && D.bControlHints);
    // Round trip through the Saved-dir file format.
    FWardenSettings S; S.Sensitivity=1.75f; S.CameraDistance=1.2f; S.MasterVolume=.5f; S.MusicVolume=.3f; S.SfxVolume=.8f; S.bInvertY=true; S.bDamageNumbers=false; S.bControlHints=false;
    const FString File=FPaths::Combine(FPaths::ProjectSavedDir(),TEXT("Automation"),TEXT("BossLabSettingsTest.ini"));
    TestTrue(TEXT("Settings save"),S.Save(File));
    FWardenSettings L; TestTrue(TEXT("Settings load"),L.Load(File));
    TestTrue(TEXT("Round trip preserves every option"),L==S);
    IFileManager::Get().Delete(*File);
    TestTrue(TEXT("Default file lives under the project Saved dir"),FWardenSettings::DefaultFile().StartsWith(FPaths::ProjectSavedDir()));
    FWardenSettings C; C.Parse(TEXT("Sensitivity=9\nCameraDistance=0.1\nMasterVolume=-2\nGarbage\n"));
    TestEqual(TEXT("Sensitivity clamps"),C.Sensitivity,3.f); TestEqual(TEXT("Camera clamps"),C.CameraDistance,.7f); TestEqual(TEXT("Volume clamps"),C.MasterVolume,0.f);
    // Hints key does not collide with any other action.
    int32 HKeys=0; for(const auto& B:GetDefault<UInputSettings>()->GetActionMappings()) if(B.Key==EKeys::H) { ++HKeys; TestEqual(TEXT("H is the hints toggle"),B.ActionName,FName(TEXT("Hints"))); }
    TestEqual(TEXT("H bound once"),HKeys,1);
    // Applying options reaches the player and the mix, and defaults leave them as before.
    auto* W=QoLWorld(); auto* M=QoLArena(W,true);
    const float MusicBefore=M->MusicLevel();
    TestEqual(TEXT("Defaults keep effects gain"),M->SfxMaster,2.5f);
    M->Settings=S; M->ApplySettings();
    TestEqual(TEXT("Sensitivity applied"),M->Player->GetSensitivity(),1.75f);
    TestTrue(TEXT("Invert applied"),M->Player->bInvertLook);
    TestEqual(TEXT("Camera distance applied"),M->Player->CameraDistanceScale,1.2f);
    TestTrue(TEXT("Effects gain scaled"),FMath::IsNearlyEqual(M->SfxMaster,2.f,.001f));
    TestTrue(TEXT("Music scaled"),FMath::IsNearlyEqual(M->MusicLevel(),MusicBefore*.3f,.001f));
    M->Settings=FWardenSettings(); M->ApplySettings();
    TestEqual(TEXT("Defaults restore effects gain"),M->SfxMaster,2.5f);
    QoLClose(W);
    return true;
}
#endif
