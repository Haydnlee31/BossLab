// Quality-of-life: persisted options and the pause-menu Options panel.
// Presentation/input feel only; combat rules stay in WardenCombat.
#include "WardenQoL.h"
#include "WardenPrototype.h"
#include "AudioDevice.h"
#include "GameFramework/SpringArmComponent.h"
#include "Engine/World.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Layout/SBox.h"
#include "Styling/CoreStyle.h"

void FWardenSettings::Clamp()
{
    Sensitivity=FMath::Clamp(Sensitivity,.25f,3.f);
    CameraDistance=FMath::Clamp(CameraDistance,.7f,1.5f);
    MasterVolume=FMath::Clamp(MasterVolume,0.f,1.f);
    MusicVolume=FMath::Clamp(MusicVolume,0.f,1.f);
    SfxVolume=FMath::Clamp(SfxVolume,0.f,1.f);
}
FString FWardenSettings::Serialize() const
{
    return FString::Printf(TEXT("[BossLab.Settings]\nSensitivity=%.2f\nCameraDistance=%.2f\nMasterVolume=%.2f\nMusicVolume=%.2f\nSfxVolume=%.2f\nInvertY=%s\nDamageNumbers=%s\nControlHints=%s\nCameraFollow=%s\n"),
        Sensitivity,CameraDistance,MasterVolume,MusicVolume,SfxVolume,bInvertY?TEXT("True"):TEXT("False"),bDamageNumbers?TEXT("True"):TEXT("False"),bControlHints?TEXT("True"):TEXT("False"),bCameraFollow?TEXT("True"):TEXT("False"));
}
void FWardenSettings::Parse(const FString& Text)
{
    TArray<FString> Lines; Text.ParseIntoArrayLines(Lines);
    for(const FString& Line:Lines)
    {
        FString Key,Value;
        if(!Line.Split(TEXT("="),&Key,&Value)) continue;
        Key.TrimStartAndEndInline(); Value.TrimStartAndEndInline();
        const float F=FCString::Atof(*Value); const bool B=Value.ToBool();
        if(Key==TEXT("Sensitivity")) Sensitivity=F;
        else if(Key==TEXT("CameraDistance")) CameraDistance=F;
        else if(Key==TEXT("MasterVolume")) MasterVolume=F;
        else if(Key==TEXT("MusicVolume")) MusicVolume=F;
        else if(Key==TEXT("SfxVolume")) SfxVolume=F;
        else if(Key==TEXT("InvertY")) bInvertY=B;
        else if(Key==TEXT("DamageNumbers")) bDamageNumbers=B;
        else if(Key==TEXT("ControlHints")) bControlHints=B;
        else if(Key==TEXT("CameraFollow")) bCameraFollow=B;
    }
    Clamp();
}
bool FWardenSettings::Save(const FString& File) const { return FFileHelper::SaveStringToFile(Serialize(),*File); }
bool FWardenSettings::Load(const FString& File)
{
    FString Text;
    if(!FFileHelper::LoadFileToString(Text,*File)) return false;
    Parse(Text); return true;
}
FString FWardenSettings::DefaultFile() { return FPaths::Combine(FPaths::ProjectSavedDir(),TEXT("Config"),TEXT("BossLabSettings.ini")); }

void AWardenArenaMode::LoadSettings()
{
    // Tests, captures and benchmarks keep the built-in defaults so evidence stays comparable.
    const TCHAR* Cmd=FCommandLine::Get();
    if(!GIsAutomationTesting && !FParse::Param(Cmd,TEXT("BossLabCapture")) && !FParse::Param(Cmd,TEXT("BossLabBenchmark")))
        Settings.Load(FWardenSettings::DefaultFile());
    ApplySettings();
}
void AWardenArenaMode::SaveSettings()
{
    if(!GIsAutomationTesting) Settings.Save(FWardenSettings::DefaultFile());
}
void AWardenArenaMode::ApplySettings()
{
    Settings.Clamp();
    if(Player) { Player->SetSensitivity(Settings.Sensitivity); Player->bInvertLook=Settings.bInvertY; Player->CameraDistanceScale=Settings.CameraDistance;
        // Camera follow (presentation only): soft spring-arm lag and idle re-centre.
        Player->bCameraRecentre=Settings.bCameraFollow;
        Player->Arm->bEnableCameraLag=Settings.bCameraFollow; Player->Arm->CameraLagSpeed=11.f; Player->Arm->CameraLagMaxDistance=60.f; }
    SfxMaster=2.5f*Settings.SfxVolume;
    MusicVolumeScale=Settings.MusicVolume;
    if(UWorld* World=GetWorld()) if(FAudioDeviceHandle Device=World->GetAudioDevice()) Device->SetTransientPrimaryVolume(Settings.MasterVolume);
}

void AWardenChallenger::ToggleHints()
{
    if(auto* M=GetWorld()->GetAuthGameMode<AWardenArenaMode>())
    {
        M->Settings.bControlHints=!M->Settings.bControlHints; M->SaveSettings();
        M->LastEvent=M->Settings.bControlHints?TEXT("Control hints shown (H hides)"):TEXT("Control hints hidden (H shows)");
    }
}

TSharedRef<SWidget> AWardenArenaMode::BuildOptionsPanel()
{
    const TWeakObjectPtr<AWardenArenaMode> WeakThis(this);
    const auto Font=FCoreStyle::GetDefaultFontStyle("Regular",13);
    auto Box=SNew(SVerticalBox);
    Box->AddSlot().AutoHeight().Padding(0,0,0,8)
    [ SNew(STextBlock).Text(FText::FromString("OPTIONS  (saved locally)")).Font(FCoreStyle::GetDefaultFontStyle("Bold",14)).ColorAndOpacity(FLinearColor(.9,.75,.49)) ];
    // One row: live label plus a < / > pair. Change(Step) edits Settings; then apply and save.
    auto Row=[&](TFunction<FString(const FWardenSettings&)> Label,TFunction<void(FWardenSettings&,int32)> Change)
    {
        auto Press=[WeakThis,Change](int32 Step)
        {
            if(!WeakThis.IsValid()) return FReply::Handled();
            Change(WeakThis->Settings,Step); WeakThis->ApplySettings(); WeakThis->SaveSettings();
            return FReply::Handled();
        };
        Box->AddSlot().AutoHeight().Padding(0,2)
        [ SNew(SHorizontalBox)
            +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)
            [ SNew(STextBlock).Font(Font).Text_Lambda([WeakThis,Label]() { return FText::FromString(WeakThis.IsValid()?Label(WeakThis->Settings):FString()); }) ]
            +SHorizontalBox::Slot().AutoWidth().Padding(4,0)
            [ SNew(SButton).IsFocusable(false).ContentPadding(FMargin(10,2)).OnClicked_Lambda([Press]() { return Press(-1); })[ SNew(STextBlock).Font(Font).Text(FText::FromString("<")) ] ]
            +SHorizontalBox::Slot().AutoWidth()
            [ SNew(SButton).IsFocusable(false).ContentPadding(FMargin(10,2)).OnClicked_Lambda([Press]() { return Press(1); })[ SNew(STextBlock).Font(Font).Text(FText::FromString(">")) ] ]
        ];
    };
    auto Percent=[](float V) { return FString::Printf(TEXT("%d%%"),FMath::RoundToInt(V*100)); };
    auto OnOff=[](bool B) { return B?FString(TEXT("On")):FString(TEXT("Off")); };
    Row([](const FWardenSettings& S) { return FString::Printf(TEXT("Mouse sensitivity   %.2fx"),S.Sensitivity); },
        [](FWardenSettings& S,int32 D) { S.Sensitivity+=.25f*D; });
    Row([OnOff](const FWardenSettings& S) { return TEXT("Camera follow (lag + re-centre)   ")+OnOff(S.bCameraFollow); },
        [](FWardenSettings& S,int32) { S.bCameraFollow=!S.bCameraFollow; });
    Row([OnOff](const FWardenSettings& S) { return TEXT("Invert look Y   ")+OnOff(S.bInvertY); },
        [](FWardenSettings& S,int32) { S.bInvertY=!S.bInvertY; });
    Row([Percent](const FWardenSettings& S) { return TEXT("Camera distance   ")+Percent(S.CameraDistance); },
        [](FWardenSettings& S,int32 D) { S.CameraDistance+=.1f*D; });
    Row([Percent](const FWardenSettings& S) { return TEXT("Master volume   ")+Percent(S.MasterVolume); },
        [](FWardenSettings& S,int32 D) { S.MasterVolume+=.1f*D; });
    Row([Percent](const FWardenSettings& S) { return TEXT("Music volume   ")+Percent(S.MusicVolume); },
        [](FWardenSettings& S,int32 D) { S.MusicVolume+=.1f*D; });
    Row([Percent](const FWardenSettings& S) { return TEXT("Effects volume   ")+Percent(S.SfxVolume); },
        [](FWardenSettings& S,int32 D) { S.SfxVolume+=.1f*D; });
    Row([OnOff](const FWardenSettings& S) { return TEXT("Damage numbers   ")+OnOff(S.bDamageNumbers); },
        [](FWardenSettings& S,int32) { S.bDamageNumbers=!S.bDamageNumbers; });
    Row([OnOff](const FWardenSettings& S) { return TEXT("Control hints [H]   ")+OnOff(S.bControlHints); },
        [](FWardenSettings& S,int32) { S.bControlHints=!S.bControlHints; });
    return Box;
}

// ---- Attempt counter, fight timer and death recap ----
void AWardenArenaMode::RunStarted()
{
    Run.bResult=false; Run.KilledBy.Reset(); Run.bPractice=false;
    Run.bCounted=CountsRun();
    Run.bPractice=bPracticeInfiniteHealth || bRegentPhaseTwoStart;
    if(Run.bCounted) ++Run.Attempts;
}
void AWardenArenaMode::RunKilled()
{
    if(!Warden) return;
    // A blade/strike hit sets the generic "You were hit" event; Regent magic names itself.
    if(LastEvent.StartsWith(TEXT("You were hit")) || LastEvent.IsEmpty())
        Run.KilledBy=WardenRules::Strike(Warden->Fight.Move).Name;
    else
    {
        FString First; Run.KilledBy=LastEvent.Split(TEXT("."),&First,nullptr) ? First : LastEvent;
    }
}
void AWardenArenaMode::RunEnded()
{
    if(Run.bResult || !Run.bCounted || !Player || !Warden) return;
    Run.bResult=true;
    if(Run.bPractice) return;   // practice attempts never set records
    Run.BestBossFraction=FMath::Min(Run.BestBossFraction,FMath::Max(Warden->Fight.Health,0.f)/Warden->Fight.MaxHealth);
    if(!Player->Fight.Alive()) ++Run.Deaths;
    else if(!Warden->Fight.Alive())
    {
        ++Run.Victories;
        const float Seconds=CombatTick/60.f;
        Run.BestVictorySeconds=Run.BestVictorySeconds>0?FMath::Min(Run.BestVictorySeconds,Seconds):Seconds;
    }
}

// ---- Practice options (session only, default off) ----
TSharedRef<SWidget> AWardenArenaMode::BuildPracticePanel()
{
    const TWeakObjectPtr<AWardenArenaMode> WeakThis(this);
    const auto Font=FCoreStyle::GetDefaultFontStyle("Regular",13);
    auto Box=SNew(SVerticalBox);
    Box->AddSlot().AutoHeight().Padding(0,0,0,8)
    [ SNew(STextBlock).Text(FText::FromString("PRACTICE  (this session only, not recorded)")).Font(FCoreStyle::GetDefaultFontStyle("Bold",14)).ColorAndOpacity(FLinearColor(1,.55,.43)) ];
    auto Toggle=[&](TFunction<FString(const AWardenArenaMode&)> Label,TFunction<void(AWardenArenaMode&)> Press)
    {
        Box->AddSlot().AutoHeight().Padding(0,2)
        [ SNew(SButton).IsFocusable(false).ContentPadding(FMargin(10,4))
            .OnClicked_Lambda([WeakThis,Press]() { if(WeakThis.IsValid()) Press(*WeakThis); return FReply::Handled(); })
            [ SNew(STextBlock).Font(Font).Text_Lambda([WeakThis,Label]() { return FText::FromString(WeakThis.IsValid()?Label(*WeakThis):FString()); }) ] ];
    };
    Toggle([](const AWardenArenaMode& M) { return FString::Printf(TEXT("Infinite health   %s"),M.bPracticeInfiniteHealth?TEXT("ON"):TEXT("Off")); },
        [](AWardenArenaMode& M) { M.bPracticeInfiniteHealth=!M.bPracticeInfiniteHealth; });
    if(bRegent)
    {
        Toggle([](const AWardenArenaMode& M) { return FString::Printf(TEXT("Start at second phase   %s"),M.bRegentPhaseTwoStart?TEXT("ON"):TEXT("Off")); },
            [](AWardenArenaMode& M) { M.bRegentPhaseTwoStart=!M.bRegentPhaseTwoStart; });
    }
    Toggle([](const AWardenArenaMode&) { return FString(TEXT("Restart fight now")); },
        [](AWardenArenaMode& M) { M.bDemo=false; M.ResetEncounter(); M.bTitle=false; });
    return Box;
}
