#include "WardenPrototype.h"
#include "Engine/GameViewportClient.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Text/STextBlock.h"
#include "Styling/CoreStyle.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"

bool AWardenChallenger::AllowsGameplayInput() const
{
    const auto* M=GetWorld()->GetAuthGameMode<AWardenArenaMode>();
    return Fight.Alive() && (!M || (!M->bPaused && !M->bTitle && !M->bScriptedPlayer));
}
void AWardenChallenger::ClearGameplayInput()
{
    ForwardInput=RightInput=0; SprintHeld=false;
    PendingAction=EWardenAction::Ready; PendingAge=0; PendingHeld=0; PendingDirection=FVector::ZeroVector; FollowAction=EWardenAction::Ready;
    MoveVelocity=FVector::ZeroVector; Fight.Sprinting=false;
}
void AWardenChallenger::QueueAction(EWardenAction Action)
{
    if(!AllowsGameplayInput()) return;
    // Jump/roll then attack in quick succession: keep the jump or roll and queue the
    // attack behind it, instead of the second press overwriting the first.
    if(Action==EWardenAction::Strike && (PendingAction==EWardenAction::Jump || PendingAction==EWardenAction::Dodge))
    { FollowAction=Action; return; }
    PendingAction=Action; PendingAge=0; PendingHeld=0; PendingDirection=MoveIntent();
}
void AWardenChallenger::QuitMenu()
{
    if(auto* M=GetWorld()->GetAuthGameMode<AWardenArenaMode>()) M->QuitFromMenu();
}
#include "Widgets/Layout/SScaleBox.h"
#include "Widgets/Layout/SSpacer.h"
#include "Widgets/Layout/SScrollBox.h"
#include "Widgets/Images/SImage.h"
#include "Brushes/SlateDynamicImageBrush.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"

#include "Widgets/SOverlay.h"
#include "Widgets/Colors/SSimpleGradient.h"
#include "Brushes/SlateNoResource.h"
#include "Fonts/CompositeFont.h"

namespace BossLabUI
{
    TWeakPtr<SWidget> FirstButton;
    const FLinearColor Gold(.78f,.62f,.37f), Ivory(.92f,.88f,.79f), Muted(.55f,.54f,.50f);
    FSlateFontInfo Font(int32 Size,bool Title=false)
    {
        const FString Path=FPaths::ProjectContentDir()/TEXT("UI/Fonts/Cinzel.ttf");
        static const auto DisplayFont=MakeShared<FCompositeFont>(FName(TEXT("Regular")),Path,EFontHinting::Default,EFontLoadingPolicy::LazyLoad);
        return Title && IFileManager::Get().FileExists(*Path) ? FSlateFontInfo(DisplayFont,Size) : FCoreStyle::GetDefaultFontStyle("Regular",Size);
    }
    TSharedRef<SWidget> Text(const FString& Value,int32 Size,FLinearColor Color=Ivory,float Wrap=0,bool Title=false)
    { return SNew(STextBlock).Text(FText::FromString(Value)).Font(Font(Size,Title)).ColorAndOpacity(Color).WrapTextAt(Wrap).ShadowOffset(FVector2D(0,1)).ShadowColorAndOpacity(FLinearColor(0,0,0,.8f)); }
    const FSlateBrush* Image(const FString& Name,FVector2D Size)
    {
        // Brushes outlive Slate widgets; only project-owned small menu images are loaded.
        static TMap<FString,TSharedPtr<FSlateDynamicImageBrush>> Images;
        const FString Path=FPaths::ProjectContentDir()/TEXT("UI")/Name;
        if(!IFileManager::Get().FileExists(*Path))return nullptr;
        auto& Brush=Images.FindOrAdd(Path);
        if(!Brush.IsValid())Brush=MakeShared<FSlateDynamicImageBrush>(FName(*Path),Size);
        return Brush.Get();
    }
    TSharedRef<SWidget> Button(const FString& Label,TFunction<void()> Action,bool Enabled=true)
    {
        static const FButtonStyle Style=FButtonStyle().SetNormal(FSlateNoResource()).SetHovered(FSlateNoResource())
            .SetPressed(FSlateNoResource()).SetDisabled(FSlateNoResource()).SetNormalPadding(FMargin(0)).SetPressedPadding(FMargin(0));
        auto Widget=SNew(SButton).ButtonStyle(&Style).IsEnabled(Enabled).IsFocusable(true)
            .ContentPadding(FMargin(0,10)).HAlign(HAlign_Left)
            .OnClicked_Lambda([Action](){Action();return FReply::Handled();});
        TWeakPtr<SButton> Weak=Widget;
        auto Selected=[Weak](){auto B=Weak.Pin();return B.IsValid() && (B->IsHovered() || B->HasKeyboardFocus());};
        Widget->SetContent(SNew(SHorizontalBox)
            +SHorizontalBox::Slot().AutoWidth()[SNew(SBox).WidthOverride(27)[SNew(STextBlock).Text(FText::FromString(TEXT("◆"))).Font(Font(11))
                .ColorAndOpacity_Lambda([Selected](){return FSlateColor(Selected()?Gold:FLinearColor(0,0,0,0));})]]
            +SHorizontalBox::Slot().AutoWidth()[SNew(STextBlock).Text(FText::FromString(Label)).Font(Font(21,true))
                .ColorAndOpacity_Lambda([Selected,Enabled](){return FSlateColor(!Enabled?Muted:(Selected()?Gold:Ivory));})]);
        if(Enabled && !FirstButton.IsValid())FirstButton=Widget;
        return Widget;
    }
}
void AWardenArenaMode::ShowFrontPage(EWardenFrontScreen Page)
{
    if(FrontScreen!=Page) PlayInterfaceCue();
    FrontScreen=Page; SetMenuOpen(true);
}
void AWardenArenaMode::SetMenuOpen(bool Open)
{
    using namespace BossLabUI;
    if(Open && FrontScreen==EWardenFrontScreen::None) FrontScreen=EWardenFrontScreen::Pause;
    if(auto* Viewport=GetWorld()->GetGameViewport())
    {
        if(PauseMenuWidget.IsValid()) Viewport->RemoveViewportWidgetContent(PauseMenuWidget.ToSharedRef());
        PauseMenuWidget.Reset();
        if(Open)
        {
            FirstButton.Reset();
            const TWeakObjectPtr<AWardenArenaMode> Weak(this);
            auto Go=[Weak](EWardenFrontScreen Page){if(Weak.IsValid())Weak->ShowFrontPage(Page);};
            auto Body=SNew(SVerticalBox);
            auto Add=[&](TSharedRef<SWidget> Widget,float Bottom=7.f){Body->AddSlot().AutoHeight().Padding(0,0,0,Bottom)[Widget];};
            const bool Home=FrontScreen==EWardenFrontScreen::Home;
            const bool Boss=FrontScreen==EWardenFrontScreen::BossSelect;
            const bool Result=FrontScreen==EWardenFrontScreen::Result;
            const bool Options=FrontScreen==EWardenFrontScreen::Settings || FrontScreen==EWardenFrontScreen::CreativeSetup;
            FString Eyebrow,Heading,Description;
            switch(FrontScreen)
            {
            case EWardenFrontScreen::Home:
                Eyebrow=TEXT("T H E   C R U C I B L E");Heading=TEXT("BossLab");
                Description=TEXT("Steel. Soul. Resolve.");
                Add(Button(TEXT("Challenge"),[Weak](){if(Weak.IsValid())Weak->OpenBossSelect();}));
                Add(Button(TEXT("Creative"),[Go](){Go(EWardenFrontScreen::CreativeSetup);}));
                Add(Button(TEXT("Settings"),[Go](){Go(EWardenFrontScreen::Settings);}));
                Add(Button(TEXT("Quit game"),[Weak](){if(Weak.IsValid())Weak->QuitFromMenu();}));break;
            case EWardenFrontScreen::BossSelect:
                Eyebrow=TEXT("I   /   CHALLENGE");Heading=TEXT("The Funeral\nRegent");
                Description=TEXT("Keeper of the unquiet dead.\nAn executioner's estoc. A censer full of souls.\nTwo acts of judgment.");
                Add(Button(TEXT("Begin challenge"),[Weak](){if(Weak.IsValid()){Weak->PlayInterfaceCue();Weak->StartRegentSession(false);}}));
                Add(Button(TEXT("Back"),[Weak](){if(Weak.IsValid())Weak->OpenHome();}));
                Add(Text(TEXT("II   /   COMING SOON          III   /   COMING SOON"),11,Muted),0);break;
            case EWardenFrontScreen::CreativeSetup:
                Eyebrow=TEXT("CREATIVE   /   THE FUNERAL REGENT");Heading=TEXT("Practice");
                Description=TEXT("Explore the encounter. Assists are optional.\nCreative sessions never earn challenge records.");
                Add(BuildPracticePanel());
                if(bTitle)Add(Button(TEXT("Enter encounter"),[Weak](){if(Weak.IsValid()){Weak->PlayInterfaceCue();Weak->StartRegentSession(true);}}));
                Add(Button(TEXT("Back"),[Weak,Go](){if(Weak.IsValid()){if(Weak->bTitle)Weak->OpenHome();else Go(EWardenFrontScreen::Pause);}}));break;
            case EWardenFrontScreen::Settings:
                Eyebrow=TEXT("BOSSLAB");Heading=TEXT("Settings");
                Description=TEXT("Changes apply immediately and are saved on this device.");
                Add(BuildOptionsPanel());
                Add(Button(TEXT("Back"),[Weak,Go](){if(Weak.IsValid()){if(Weak->bTitle)Weak->OpenHome();else Go(EWardenFrontScreen::Pause);}}));break;
            case EWardenFrontScreen::Result:
            {
                Eyebrow=bCreativeMode?TEXT("CREATIVE   /   NOT RANKED"):TEXT("THE FUNERAL REGENT");
                const bool UnrankedWin=!bCreativeMode && !Run.bChallengeVictory && Player && Player->Fight.Alive() && Warden && !Warden->Fight.Alive();
                Heading=UnrankedWin?TEXT("Encounter Complete"):(Run.bChallengeVictory?TEXT("Regent Felled"):(bCreativeMode?TEXT("Practice Complete"):TEXT("You Have Fallen")));
                Description=UnrankedWin?TEXT("Encounter complete. No challenge record awarded."):(Run.bChallengeVictory?TEXT("Challenge complete. The unquiet court falls silent."):(bCreativeMode?TEXT("A session explored. No challenge record awarded."):TEXT("Rise again. The court awaits.")));
                if(!bCreativeMode)
                {
                    auto Stats=SNew(SHorizontalBox);
                    auto Stat=[&](const FString& Label,const FString& Value)
                    {Stats->AddSlot().FillWidth(1).HAlign(HAlign_Center)[SNew(SVerticalBox)
                        +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center)[Text(Value,29,Gold,0,true)]
                        +SVerticalBox::Slot().AutoHeight().HAlign(HAlign_Center).Padding(0,10,0,0)[Text(Label,10,Muted)]];};
                    Stat(TEXT("TIME"),FString::Printf(TEXT("%02d:%02d"),int32(Run.Seconds)/60,int32(Run.Seconds)%60));
                    Stat(TEXT("DAMAGE DEALT"),FString::Printf(TEXT("%.0f"),Run.DamageDealt));
                    Stat(TEXT("DAMAGE TAKEN"),FString::Printf(TEXT("%.0f"),Run.DamageTaken));
                    Stat(TEXT("HITS TAKEN"),FString::FromInt(Run.HitsTaken));
                    Stat(TEXT("FLASKS USED"),FString::FromInt(Run.HealsUsed));
                    Add(Stats,42);
                }
                Add(SNew(SHorizontalBox)
                    +SHorizontalBox::Slot().FillWidth(1).HAlign(HAlign_Center)[Button(TEXT("Fight again"),[Weak](){if(Weak.IsValid())Weak->RetrySession();})]
                    +SHorizontalBox::Slot().FillWidth(1).HAlign(HAlign_Center)[Button(TEXT("Return home"),[Weak](){if(Weak.IsValid())Weak->OpenHome();})]);break;
            }
            default:
                Eyebrow=bCreativeMode?TEXT("CREATIVE"):TEXT("CHALLENGE");Heading=TEXT("Paused");
                Description=TEXT("A moment of stillness.");
                Add(Button(TEXT("Resume"),[Weak](){if(Weak.IsValid())Weak->SetMenuOpen(false);}));
                Add(Button(TEXT("Settings"),[Go](){Go(EWardenFrontScreen::Settings);}));
                if(bCreativeMode)Add(Button(TEXT("Creative assists"),[Go](){Go(EWardenFrontScreen::CreativeSetup);}));
                Add(Button(TEXT("Restart encounter"),[Weak](){if(Weak.IsValid())Weak->RetrySession();}));
                Add(Button(TEXT("Return home"),[Weak](){if(Weak.IsValid())Weak->OpenHome();}));break;
            }
            auto Backdrop=SNew(SOverlay);
            Backdrop->AddSlot()[SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush")).BorderBackgroundColor(FLinearColor(.008f,.01f,.012f))];
            if(const FSlateBrush* Art=Image(Boss?TEXT("RegentBackdrop.png"):TEXT("CrucibleBackdrop.png"),FVector2D(1536,864)))
                Backdrop->AddSlot()[SNew(SScaleBox).Stretch(EStretch::ScaleToFill).Clipping(EWidgetClipping::ClipToBounds)[SNew(SImage).Image(Art)]];
            Backdrop->AddSlot()[SNew(SSimpleGradient).Orientation(Orient_Horizontal).StartColor(FLinearColor(.004f,.006f,.008f,.94f)).EndColor(FLinearColor(0,0,0,.10f)).Visibility(EVisibility::HitTestInvisible)];
            if(Result || Options || !bTitle)
                Backdrop->AddSlot()[SNew(SBorder).BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush")).BorderBackgroundColor(FLinearColor(0,0,0,Result?.64f:.38f)).Visibility(EVisibility::HitTestInvisible)];
            auto Content=SNew(SVerticalBox);
            if(Home)
            {
                if(const FSlateBrush* Logo=Image(TEXT("BossLabLogo.png"),FVector2D(84,84)))
                    Content->AddSlot().AutoHeight().HAlign(HAlign_Left).Padding(0,0,0,20)[SNew(SImage).Image(Logo)];
            }
            const EHorizontalAlignment Align=Result?HAlign_Center:HAlign_Left;
            Content->AddSlot().AutoHeight().HAlign(Align).Padding(0,0,0,18)[Text(Eyebrow,11,Gold)];
            Content->AddSlot().AutoHeight().HAlign(Align).Padding(0,0,0,18)[Text(Heading,Home?70:(Result?49:(Boss?48:40)),Result?Gold:Ivory,Result?1080:650,true)];
            Content->AddSlot().AutoHeight().HAlign(Align).Padding(0,0,0,Home?86:32)[Text(Description,14,Muted,Result?900:580)];
            if(Options)Content->AddSlot().FillHeight(1)[SNew(SScrollBox)+SScrollBox::Slot()[Body]];
            else Content->AddSlot().AutoHeight()[Body];
            auto Foreground=SNew(SOverlay);
            Foreground->AddSlot().Padding(Result?FMargin(180,215,180,100):FMargin(105,Home?78:125,Options?555:(Boss?590:640),100))[Content];
            Foreground->AddSlot().VAlign(VAlign_Bottom).Padding(105,0,80,35)
                [SNew(SVerticalBox)
                    +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,9)[Text(TEXT("ARROW KEYS / TAB   Navigate     ENTER   Select     ESC   Back"),10,Muted)]
                    +SVerticalBox::Slot().AutoHeight()[Text(TEXT("Voices: OGsoundFX · qubodup (CC BY). belarathbone · Kenney (CC0). Full credits: CREDITS.md"),9,Muted)]];
            Backdrop->AddSlot()[SNew(SScaleBox).Stretch(EStretch::ScaleToFit)[SNew(SBox).WidthOverride(1440).HeightOverride(900)[Foreground]]];
            PauseMenuWidget=Backdrop;
            Viewport->AddViewportWidgetContent(PauseMenuWidget.ToSharedRef(),100);
        }
    }
    bPaused=Open;CombatAccumulator=0;
    UpdateAudio();
    if(!Open)FrontScreen=EWardenFrontScreen::None;
    if(Player)Player->ClearGameplayInput();
    if(auto* PC=Player?Cast<APlayerController>(Player->GetController()):nullptr)
    {
        PC->bShowMouseCursor=Open;PC->bEnableClickEvents=Open;
        if(Open){FInputModeGameAndUI Menu;Menu.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);Menu.SetHideCursorDuringCapture(false);if(FirstButton.IsValid())Menu.SetWidgetToFocus(FirstButton.Pin());PC->SetInputMode(Menu);}
        else{if(Player)Player->SuppressMouseAttack=PC->IsInputKeyDown(EKeys::LeftMouseButton);FInputModeGameOnly Game;Game.SetConsumeCaptureMouseDown(true);PC->SetInputMode(Game);}
    }
}
void AWardenArenaMode::QuitFromMenu()
{
    if(bPaused) if(auto* PC=Player?Cast<APlayerController>(Player->GetController()):nullptr) PC->ConsoleCommand(TEXT("quit"));
}
void AWardenArenaMode::EndPlay(const EEndPlayReason::Type Reason)
{
    if(PauseMenuWidget.IsValid())
        if(auto* Viewport=GetWorld()->GetGameViewport()) Viewport->RemoveViewportWidgetContent(PauseMenuWidget.ToSharedRef());
    PauseMenuWidget.Reset();
    StopAudioRecording();
    Super::EndPlay(Reason);
}
