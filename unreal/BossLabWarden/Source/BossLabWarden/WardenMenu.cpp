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
void AWardenArenaMode::SetMenuOpen(bool Open)
{
    if(auto* Viewport=GetWorld()->GetGameViewport())
    {
        if(PauseMenuWidget.IsValid()) Viewport->RemoveViewportWidgetContent(PauseMenuWidget.ToSharedRef());
        PauseMenuWidget.Reset();
        if(Open)
        {
            const auto Font=FCoreStyle::GetDefaultFontStyle("Regular",18);
            const TWeakObjectPtr<AWardenArenaMode> WeakThis(this);
            PauseMenuWidget=SNew(SBorder)
                .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
                .BorderBackgroundColor(FLinearColor(0,0,0,.7f))
                .HAlign(HAlign_Center).VAlign(VAlign_Center)
                [ SNew(SBox).WidthOverride(860)
                    [ SNew(SBorder).Padding(28)
                        .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
                        .BorderBackgroundColor(FLinearColor(.025,.035,.045,1))
                        [ SNew(SVerticalBox)
                            +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,18)
                            [ SNew(STextBlock).Text(FText::FromString("PAUSED"))
                                .Font(FCoreStyle::GetDefaultFontStyle("Bold",28))
                                .ColorAndOpacity(FLinearColor(.9,.75,.49)) ]
                            +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,24)
                            [ SNew(STextBlock).Text(FText::FromString("Mouse released. Esc / P resumes.")).Font(FCoreStyle::GetDefaultFontStyle("Regular",14)) ]
                            +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,12)
                            [ SNew(SButton).ContentPadding(FMargin(18,14)).IsFocusable(false)
                                .OnClicked_Lambda([WeakThis]() { if(WeakThis.IsValid()) WeakThis->SetMenuOpen(false); return FReply::Handled(); })
                                [ SNew(STextBlock).Text(FText::FromString("Resume")).Font(Font) ] ]
                            +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,24)
                            [ SNew(SButton).ContentPadding(FMargin(18,14)).IsFocusable(false)
                                .OnClicked_Lambda([WeakThis]() { if(WeakThis.IsValid()) WeakThis->QuitFromMenu(); return FReply::Handled(); })
                                [ SNew(STextBlock).Text(FText::FromString("Quit game   [Q]")).Font(Font) ] ]
                            // Options (left) beside practice (right) so the menu fits at 720p.
                            +SVerticalBox::Slot().AutoHeight().Padding(0,0,0,18)
                            [ SNew(SHorizontalBox)
                                +SHorizontalBox::Slot().FillWidth(1.15f).Padding(0,0,24,0) [ BuildOptionsPanel() ]
                                +SHorizontalBox::Slot().FillWidth(1) [ BuildPracticePanel() ] ]
                            +SVerticalBox::Slot().AutoHeight()
                            [ SNew(STextBlock).Text(FText::FromString("R restart | M mute | H hints")).Font(FCoreStyle::GetDefaultFontStyle("Regular",12)) ]
                        ]
                    ]
                ];
            Viewport->AddViewportWidgetContent(PauseMenuWidget.ToSharedRef(),100);
        }
    }
    bPaused=Open; CombatAccumulator=0;
    if(Player) Player->ClearGameplayInput();
    if(auto* PC=Player?Cast<APlayerController>(Player->GetController()):nullptr)
    {
        PC->bShowMouseCursor=Open; PC->bEnableClickEvents=Open;
        if(Open)
        {
            FInputModeGameAndUI Menu;
            Menu.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
            Menu.SetHideCursorDuringCapture(false);
            PC->SetInputMode(Menu);
        }
        else
        {
            // The Resume click must never become a sword attack on re-entry.
            if(Player) Player->SuppressMouseAttack=PC->IsInputKeyDown(EKeys::LeftMouseButton);
            FInputModeGameOnly Game; Game.SetConsumeCaptureMouseDown(true);
            PC->SetInputMode(Game);
        }
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
    Super::EndPlay(Reason);
}
