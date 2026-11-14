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
#include "Brushes/SlateNoResource.h"

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
    const auto Font=FCoreStyle::GetDefaultFontStyle("Regular",16);
    const FLinearColor Gold(.78f,.62f,.37f), Ivory(.92f,.88f,.79f);
    static const FButtonStyle Style=FButtonStyle().SetNormal(FSlateNoResource()).SetHovered(FSlateNoResource())
        .SetPressed(FSlateNoResource()).SetDisabled(FSlateNoResource()).SetNormalPadding(FMargin(0)).SetPressedPadding(FMargin(0));
    auto Arrow=[&](const TCHAR* Glyph,TFunction<FReply()> Press)
    {
        auto Button=SNew(SButton).ButtonStyle(&Style).IsFocusable(true).ContentPadding(FMargin(13,7)).OnClicked_Lambda([Press](){return Press();});
        TWeakPtr<SButton> WeakButton=Button;
        Button->SetContent(SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Regular",21)).Text(FText::FromString(Glyph))
            .ColorAndOpacity_Lambda([WeakButton,Gold,Ivory](){auto B=WeakButton.Pin();return FSlateColor(B.IsValid() && (B->IsHovered() || B->HasKeyboardFocus())?Gold:Ivory);})
            .ShadowOffset(FVector2D(0,1)).ShadowColorAndOpacity(FLinearColor::Black));
        return Button;
    };
    auto Box=SNew(SVerticalBox);
    Box->AddSlot().AutoHeight().Padding(0,0,0,8)
    [ SNew(STextBlock).Text(FText::FromString("CAMERA & CONTROLS")).Font(FCoreStyle::GetDefaultFontStyle("Bold",12)).ColorAndOpacity(Gold) ];
    // One row: live label plus a < / > pair. Change(Step) edits Settings; then apply and save.
    auto Row=[&](TFunction<FString(const FWardenSettings&)> Label,TFunction<void(FWardenSettings&,int32)> Change)
    {
        auto Press=[WeakThis,Change](int32 Step)
        {
            if(!WeakThis.IsValid()) return FReply::Handled();
            Change(WeakThis->Settings,Step); WeakThis->ApplySettings(); WeakThis->SaveSettings(); WeakThis->PlayInterfaceCue(true);
            return FReply::Handled();
        };
        Box->AddSlot().AutoHeight().Padding(0,2)
        [ SNew(SHorizontalBox)
            +SHorizontalBox::Slot().FillWidth(1).VAlign(VAlign_Center)
            [ SNew(STextBlock).Font(Font).ColorAndOpacity(Ivory).Text_Lambda([WeakThis,Label]() { return FText::FromString(WeakThis.IsValid()?Label(WeakThis->Settings):FString()); }) ]
            +SHorizontalBox::Slot().AutoWidth().Padding(4,0)
            [ Arrow(TEXT("‹"),[Press]() { return Press(-1); }) ]
            +SHorizontalBox::Slot().AutoWidth()
            [ Arrow(TEXT("›"),[Press]() { return Press(1); }) ]
        ];
    };
    auto Percent=[](float V) { return FString::Printf(TEXT("%d%%"),FMath::RoundToInt(V*100)); };
    auto OnOff=[](bool B) { return B?FString(TEXT("On")):FString(TEXT("Off")); };
    Row([](const FWardenSettings& S) { return FString::Printf(TEXT("Mouse sensitivity   %.2fx"),S.Sensitivity); },
        [](FWardenSettings& S,int32 D) { S.Sensitivity+=.25f*D; });
    Row([OnOff](const FWardenSettings& S) { return TEXT("Camera follow   ")+OnOff(S.bCameraFollow); },
        [](FWardenSettings& S,int32) { S.bCameraFollow=!S.bCameraFollow; });
    Row([OnOff](const FWardenSettings& S) { return TEXT("Invert look Y   ")+OnOff(S.bInvertY); },
        [](FWardenSettings& S,int32) { S.bInvertY=!S.bInvertY; });
    Row([Percent](const FWardenSettings& S) { return TEXT("Camera distance   ")+Percent(S.CameraDistance); },
        [](FWardenSettings& S,int32 D) { S.CameraDistance+=.1f*D; });
    Box->AddSlot().AutoHeight().Padding(0,24,0,10)[ SNew(STextBlock).Text(FText::FromString("AUDIO")).Font(FCoreStyle::GetDefaultFontStyle("Bold",12)).ColorAndOpacity(Gold) ];
    Row([Percent](const FWardenSettings& S) { return TEXT("Master volume   ")+Percent(S.MasterVolume); },
        [](FWardenSettings& S,int32 D) { S.MasterVolume+=.1f*D; });
    Row([Percent](const FWardenSettings& S) { return TEXT("Music volume   ")+Percent(S.MusicVolume); },
        [](FWardenSettings& S,int32 D) { S.MusicVolume+=.1f*D; });
    Row([Percent](const FWardenSettings& S) { return TEXT("Effects volume   ")+Percent(S.SfxVolume); },
        [](FWardenSettings& S,int32 D) { S.SfxVolume+=.1f*D; });
    Box->AddSlot().AutoHeight().Padding(0,24,0,10)[ SNew(STextBlock).Text(FText::FromString("INTERFACE")).Font(FCoreStyle::GetDefaultFontStyle("Bold",12)).ColorAndOpacity(Gold) ];
    Row([OnOff](const FWardenSettings& S) { return TEXT("Damage numbers   ")+OnOff(S.bDamageNumbers); },
        [](FWardenSettings& S,int32) { S.bDamageNumbers=!S.bDamageNumbers; });
    Row([OnOff](const FWardenSettings& S) { return TEXT("Control hints [H]   ")+OnOff(S.bControlHints); },
        [](FWardenSettings& S,int32) { S.bControlHints=!S.bControlHints; });
    return Box;
}

// Frontend sessions use the existing fixed Regent rehearsal, never an adaptive policy.
void AWardenArenaMode::OpenHome()
{
    bFrontendSession=true; bTitle=true;
    Run.bChallengeEligible=false;
    bCreativeMode=false; bPracticeInfiniteHealth=false; bPracticeInfiniteStamina=false; bRegentPhaseTwoStart=false;
    if(Player) Player->ClearGameplayInput();
    ShowFrontPage(EWardenFrontScreen::Home);
}
void AWardenArenaMode::OpenBossSelect()
{
    bTitle=true; ShowFrontPage(EWardenFrontScreen::BossSelect);
}
void AWardenArenaMode::StartRegentSession(bool Creative)
{
    if(!Player || !Warden) return;
    bFrontendSession=true; bCreativeMode=Creative;
    if(!Creative) { bPracticeInfiniteHealth=false; bPracticeInfiniteStamina=false; bRegentPhaseTwoStart=false; }
    bDemo=false; bScriptedPlayer=false; bAdaptive=false; bRehearsal=true;
    bInspector=false; bEvents=false; bRecording=false; bDebugGeometry=false;
    TestPilot=nullptr;
    if(!bRegent) EnableRegent();
    ResetEncounter();
    Run.bCounted=false; Run.bResult=false; Run.bChallengeVictory=false;
    bTitle=false; FrontScreen=EWardenFrontScreen::None;
    SetMenuOpen(false);
    Player->ClearGameplayInput(); Player->SuppressMouseAttack=true;
}
void AWardenArenaMode::RetrySession() { StartRegentSession(bCreativeMode); }
void AWardenArenaMode::SetCreativeInfiniteHealth(bool Enabled)
{
    if(!bCreativeMode && !(bTitle && FrontScreen==EWardenFrontScreen::CreativeSetup)) return;
    bPracticeInfiniteHealth=Enabled; Run.bPractice=true; Run.bChallengeEligible=false;
}
void AWardenArenaMode::SetCreativeInfiniteStamina(bool Enabled)
{
    if(!bCreativeMode && !(bTitle && FrontScreen==EWardenFrontScreen::CreativeSetup)) return;
    bPracticeInfiniteStamina=Enabled; Run.bPractice=true; Run.bChallengeEligible=false;
}
void AWardenArenaMode::UpdateRunStats()
{
    if(!Player || !Warden || Run.bResult) return;
    Run.Seconds=CombatTick/60.f; Run.DamageDealt=PlayerDamage; Run.DamageTaken=BossDamage;
    Run.HitsTaken=FMath::Max(0,Player->BleedCount-Run.StartBleedCount);
    Run.HealsUsed=FMath::Max(0,Run.StartHeals-Player->Fight.Heals);
    if(bCreativeMode || bPracticeInfiniteHealth || bPracticeInfiniteStamina || bRegentPhaseTwoStart || !bRehearsal || bScriptedPlayer || bDemo || bCaptureFrames || bBenchmark || TestPilot)
        Run.bChallengeEligible=false;
}
FString AWardenArenaMode::ChallengeStatsText() const
{
    return FString::Printf(TEXT("Time  %02d:%02d\nDamage dealt  %.0f\nDamage taken  %.0f\nHits taken  %d\nFlasks used  %d"),
        int32(Run.Seconds)/60,int32(Run.Seconds)%60,Run.DamageDealt,Run.DamageTaken,Run.HitsTaken,Run.HealsUsed);
}

// ---- Attempt counter, fight timer and death recap ----
void AWardenArenaMode::RunStarted()
{
    Run.bResult=false; Run.KilledBy.Reset(); Run.bPractice=false;
    Run.bCounted=CountsRun();
    Run.bPractice=bCreativeMode || bPracticeInfiniteHealth || bPracticeInfiniteStamina || bRegentPhaseTwoStart;
    Run.bChallengeVictory=false; Run.Seconds=Run.DamageDealt=Run.DamageTaken=0; Run.HitsTaken=Run.HealsUsed=0;
    Run.StartBleedCount=Player?Player->BleedCount:0; Run.StartHeals=Player?Player->Fight.Heals:0;
    Run.bChallengeEligible=Run.bCounted && !Run.bPractice && bRehearsal && !bBenchmark && !TestPilot;
    if(bFrontendSession && !Run.bChallengeEligible) Run.bCounted=false;
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
    if(Run.bResult || (!Run.bCounted && !bFrontendSession) || !Player || !Warden) return;
    UpdateRunStats();
    Run.bResult=true;
    Run.bChallengeVictory=Run.bChallengeEligible && Player->Fight.Alive() && !Warden->Fight.Alive();
    if(bFrontendSession) ShowFrontPage(EWardenFrontScreen::Result);
    if(Run.bPractice || (bFrontendSession && !Run.bChallengeEligible)) return;   // practice attempts never set records
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
    const auto Font=FCoreStyle::GetDefaultFontStyle("Regular",17);
    const FLinearColor Gold(.78f,.62f,.37f), Ivory(.92f,.88f,.79f);
    static const FButtonStyle Style=FButtonStyle().SetNormal(FSlateNoResource()).SetHovered(FSlateNoResource())
        .SetPressed(FSlateNoResource()).SetDisabled(FSlateNoResource()).SetNormalPadding(FMargin(0)).SetPressedPadding(FMargin(0));
    auto Box=SNew(SVerticalBox);
    Box->AddSlot().AutoHeight().Padding(0,0,0,8)
    [ SNew(STextBlock).Text(FText::FromString("ASSISTS  /  THIS SESSION ONLY")).Font(FCoreStyle::GetDefaultFontStyle("Bold",12)).ColorAndOpacity(Gold) ];
    auto Toggle=[&](TFunction<FString(const AWardenArenaMode&)> Label,TFunction<void(AWardenArenaMode&)> Press)
    {
        auto Button=SNew(SButton).ButtonStyle(&Style).IsFocusable(true).HAlign(HAlign_Left).ContentPadding(FMargin(0,12))
            .OnClicked_Lambda([WeakThis,Press]() { if(WeakThis.IsValid()) { Press(*WeakThis); WeakThis->PlayInterfaceCue(true); } return FReply::Handled(); });
        TWeakPtr<SButton> WeakButton=Button;
        auto Selected=[WeakButton](){auto B=WeakButton.Pin();return B.IsValid() && (B->IsHovered() || B->HasKeyboardFocus());};
        Button->SetContent(SNew(SHorizontalBox)
            +SHorizontalBox::Slot().AutoWidth()[SNew(SBox).WidthOverride(25)[SNew(STextBlock).Font(FCoreStyle::GetDefaultFontStyle("Regular",11)).Text(FText::FromString(TEXT("◆")))
                .ColorAndOpacity_Lambda([Selected,Gold](){return FSlateColor(Selected()?Gold:FLinearColor(0,0,0,0));})]]
            +SHorizontalBox::Slot().AutoWidth()[SNew(STextBlock).Font(Font)
                .ColorAndOpacity_Lambda([Selected,Gold,Ivory](){return FSlateColor(Selected()?Gold:Ivory);})
                .Text_Lambda([WeakThis,Label]() { return FText::FromString(WeakThis.IsValid()?Label(*WeakThis):FString()); })]);
        Box->AddSlot().AutoHeight().Padding(0,2)[Button];
    };
    Toggle([](const AWardenArenaMode& M) { return FString::Printf(TEXT("Infinite health   %s"),M.bPracticeInfiniteHealth?TEXT("ON"):TEXT("Off")); },
        [](AWardenArenaMode& M) { if(M.bFrontendSession) M.SetCreativeInfiniteHealth(!M.bPracticeInfiniteHealth); else M.bPracticeInfiniteHealth=!M.bPracticeInfiniteHealth; });
    Toggle([](const AWardenArenaMode& M) { return FString::Printf(TEXT("Infinite stamina   %s"),M.bPracticeInfiniteStamina?TEXT("ON"):TEXT("Off")); },
        [](AWardenArenaMode& M) { M.SetCreativeInfiniteStamina(!M.bPracticeInfiniteStamina); });
    if(bRegent || bFrontendSession)
    {
        Toggle([](const AWardenArenaMode& M) { return FString::Printf(TEXT("Start at second phase   %s"),M.bRegentPhaseTwoStart?TEXT("ON"):TEXT("Off")); },
            [](AWardenArenaMode& M) { if(!M.bFrontendSession || M.bCreativeMode || (M.bTitle && M.FrontScreen==EWardenFrontScreen::CreativeSetup)) { M.bRegentPhaseTwoStart=!M.bRegentPhaseTwoStart; M.Run.bChallengeEligible=false; } });
    }
    if(!bFrontendSession) Toggle([](const AWardenArenaMode&) { return FString(TEXT("Restart fight now")); },
        [](AWardenArenaMode& M) { M.bDemo=false; M.ResetEncounter(); M.bTitle=false; });
    return Box;
}
