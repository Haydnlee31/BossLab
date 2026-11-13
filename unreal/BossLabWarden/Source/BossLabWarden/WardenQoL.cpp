// Quality-of-life: persisted options and the pause-menu Options panel.
// Presentation/input feel only; combat rules stay in WardenCombat.
#include "WardenQoL.h"
#include "WardenPrototype.h"
#include "AudioDevice.h"
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
    return FString::Printf(TEXT("[BossLab.Settings]\nSensitivity=%.2f\nCameraDistance=%.2f\nMasterVolume=%.2f\nMusicVolume=%.2f\nSfxVolume=%.2f\nInvertY=%s\nDamageNumbers=%s\nControlHints=%s\n"),
        Sensitivity,CameraDistance,MasterVolume,MusicVolume,SfxVolume,bInvertY?TEXT("True"):TEXT("False"),bDamageNumbers?TEXT("True"):TEXT("False"),bControlHints?TEXT("True"):TEXT("False"));
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
    if(Player) { Player->SetSensitivity(Settings.Sensitivity); Player->bInvertLook=Settings.bInvertY; Player->CameraDistanceScale=Settings.CameraDistance; }
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
