#include "WardenPrototype.h"
#include "WardenQoL.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "GameFramework/InputSettings.h"
#include "HAL/FileManager.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/PlayerController.h"
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
    TestTrue(TEXT("Camera follow on by default after apply"),M->Player->Arm->bEnableCameraLag && M->Player->bCameraRecentre);
    S.bCameraFollow=false; M->Settings=S; M->ApplySettings();
    TestTrue(TEXT("Camera follow switches off"),!M->Player->Arm->bEnableCameraLag && !M->Player->bCameraRecentre);
    TestTrue(TEXT("Follow flag round-trips"),[&]{ S.Save(File); FWardenSettings R; R.Load(File); IFileManager::Get().Delete(*File); return !R.bCameraFollow; }());
    TestTrue(TEXT("Effects gain scaled"),FMath::IsNearlyEqual(M->SfxMaster,2.f,.001f));
    TestTrue(TEXT("Music scaled"),FMath::IsNearlyEqual(M->MusicLevel(),MusicBefore*.3f,.001f));
    M->Settings=FWardenSettings(); M->ApplySettings();
    TestEqual(TEXT("Defaults restore effects gain"),M->SfxMaster,2.5f);
    QoLClose(W);
    return true;
}
QOL_TEST(FWardenRunRecordTest,"BossLab.QoL.AttemptsAndDeathRecap");
bool FWardenRunRecordTest::RunTest(const FString&)
{
    auto* W=QoLWorld(); auto* M=QoLArena(W,false);
    M->FixedStep();
    TestEqual(TEXT("First combat tick counts an attempt"),M->Run.Attempts,1);
    TestTrue(TEXT("Human attempt is counted"),M->Run.bCounted);
    M->LastEvent=TEXT("You were hit. Recover before committing again."); M->Warden->Fight.Move=1;
    M->RunKilled();
    TestEqual(TEXT("Blade kill names the boss strike"),M->Run.KilledBy,FString(WardenRules::Strike(1).Name));
    M->LastEvent=TEXT("Caught in the Funeral Pyre. Roll out through the blast.");
    M->RunKilled();
    TestEqual(TEXT("Magic kill names the hazard"),M->Run.KilledBy,FString(TEXT("Caught in the Funeral Pyre")));
    M->Warden->Fight.Health=M->Warden->Fight.MaxHealth*.25f;
    M->Player->Fight.Health=0;
    M->FixedStep(); M->FixedStep();
    TestEqual(TEXT("Death recorded once"),M->Run.Deaths,1);
    TestTrue(TEXT("Best boss fraction recorded"),FMath::IsNearlyEqual(M->Run.BestBossFraction,.25f,.001f));
    M->ResetEncounter(); M->FixedStep();
    TestEqual(TEXT("Retry counts a second attempt"),M->Run.Attempts,2);
    TestTrue(TEXT("Recap cleared on retry"),M->Run.KilledBy.IsEmpty());
    // Scripted pilot runs are not the player's attempts.
    M->ConfigureEncounter(101,true,1); M->FixedStep();
    TestEqual(TEXT("Scripted pilot not counted"),M->Run.Attempts,2);
    QoLClose(W);
    return true;
}
QOL_TEST(FWardenRecentreTest,"BossLab.QoL.CameraRecentreBehindHeading");
bool FWardenRecentreTest::RunTest(const FString&)
{
    auto* W=QoLWorld();
    auto* P=W->SpawnActor<AWardenChallenger>(FVector(0,0,95),FRotator(0,90,0)); P->DispatchBeginPlay(); P->ResetFighter(false);
    auto* PC=W->SpawnActor<APlayerController>(); PC->Possess(P); P->SetLocked(false);
    P->SetActorRotation(FRotator(0,90,0));
    auto Run=[&](bool Follow,FVector Velocity,float StartYaw)
    {
        P->bCameraRecentre=Follow; P->LookIdle=0; PC->SetControlRotation(FRotator(-12,StartYaw,0));
        for(int32 I=0;I<240;++I) { P->MoveVelocity=Velocity; P->Tick(1.f/60); }
        return FRotator::NormalizeAxis(PC->GetControlRotation().Yaw);
    };
    const FVector Running(0,400,0);
    TestTrue(TEXT("Follow off: camera yaw untouched"),FMath::IsNearlyEqual(Run(false,Running,30),30.f,.5f));
    TestTrue(TEXT("Follow on: idle camera eases behind the heading"),FMath::IsNearlyEqual(Run(true,Running,30),90.f,2.f));
    TestTrue(TEXT("Standing still: no re-centre"),FMath::IsNearlyEqual(Run(true,FVector::ZeroVector,30),30.f,.5f));
    TestTrue(TEXT("Running toward the camera: no 180 swing"),FMath::IsNearlyEqual(Run(true,Running,-90),-90.f,.5f));
    QoLClose(W);
    return true;
}
QOL_TEST(FWardenPracticeTest,"BossLab.QoL.PracticeOptionsOptInAndUnrecorded");
bool FWardenPracticeTest::RunTest(const FString&)
{
    auto* W=QoLWorld(); auto* M=QoLArena(W,true);
    TestFalse(TEXT("Infinite health defaults off"),M->bPracticeInfiniteHealth);
    TestFalse(TEXT("Phase-two start defaults off"),M->bRegentPhaseTwoStart);
    M->Player->Fight.Health=10; M->FixedStep();
    TestEqual(TEXT("Default game does not refill health"),M->Player->Fight.Health,10.f);
    TestFalse(TEXT("Default attempt is not practice"),M->Run.bPractice);
    M->bPracticeInfiniteHealth=true; M->FixedStep();
    TestEqual(TEXT("Practice refills health"),M->Player->Fight.Health,M->Player->Fight.MaxHealth);
    TestTrue(TEXT("Attempt marked practice"),M->Run.bPractice);
    M->Warden->Fight.Health=1; M->Player->Fight.Health=0; M->bPracticeInfiniteHealth=false; M->FixedStep();
    TestEqual(TEXT("Practice attempt sets no record"),M->Run.BestBossFraction,1.f);
    TestEqual(TEXT("Practice death not counted"),M->Run.Deaths,0);
    M->bRegentPhaseTwoStart=true; M->ResetEncounter();
    TestEqual(TEXT("Phase-two practice opens at the threshold"),M->Warden->Fight.Health,WardenRegent::PhaseTwoHealth);
    M->FixedStep();
    TestTrue(TEXT("Phase-two start is practice"),M->Run.bPractice);
    QoLClose(W);
    return true;
}
#endif
