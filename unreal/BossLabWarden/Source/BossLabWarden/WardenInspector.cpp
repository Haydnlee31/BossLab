#include "WardenPrototype.h"
#include "Engine/World.h"
#include "Engine/Canvas.h"
#include "Engine/GameViewportClient.h"
#include "UnrealClient.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"

void AWardenChallenger::ToggleInspector() { if(auto* M=GetWorld()->GetAuthGameMode<AWardenArenaMode>()) M->bInspector=!M->bInspector; }
void AWardenChallenger::ToggleRecording() { if(auto* M=GetWorld()->GetAuthGameMode<AWardenArenaMode>()) M->bRecording=!M->bRecording; }
void AWardenChallenger::ToggleEvents() { if(auto* M=GetWorld()->GetAuthGameMode<AWardenArenaMode>()) { M->bInspector=true; M->bEvents=!M->bEvents; } }
void AWardenChallenger::ExportReport() { if(auto* M=GetWorld()->GetAuthGameMode<AWardenArenaMode>()) M->SaveReport(); }
void AWardenChallenger::ToggleController()
{
    if(auto* M=GetWorld()->GetAuthGameMode<AWardenArenaMode>())
    {
        if(M->bFrontendSession) return;
        if(!M->bTitle && !M->bPaused && Fight.Alive() && M->Warden->Fight.Alive())
        { M->SetMenuOpen(true); M->LastEvent=TEXT("F5 again: toggle boss rehearsal and reset. P resumes."); return; }
        M->bRehearsal=!M->bRehearsal; M->bAdaptive=false; M->bDemo=false; M->ResetEncounter(); M->bTitle=false;
    }
}
void AWardenChallenger::StartDemo()
{
    if(auto* M=GetWorld()->GetAuthGameMode<AWardenArenaMode>())
    {
        if(M->bFrontendSession) return;
        if(!M->bTitle && !M->bPaused && Fight.Alive() && M->Warden->Fight.Alive())
        { M->SetMenuOpen(true); M->LastEvent=TEXT("F7 again: begin disclosed switch demo. P resumes."); return; }
        M->ConfigureEncounter(202,true,3); M->bAdaptive=true; M->bDemo=true; M->bInspector=true;
        M->LastEvent=TEXT("Demo: early dodges switch to late at 30s; real deaths and round resets.");
    }
}
void AWardenPrototypeHUD::DrawInspector(AWardenArenaMode* M)
{
    if(!M->bInspector) return;
    const float X=Canvas->SizeX-380,Y=65;
    DrawRect(FLinearColor(.009,.016,.024,.94),X-16,Y-12,380,245);
    auto Line=[&](const FString& Text,int32 Row) { DrawText(Text,FColor(200,210,215),X,Y+Row*24,nullptr,.95f); };
    Line(TEXT("COMBAT FUNDAMENTALS"),0);
    Line(TEXT("Tab target / WASD move / Shift sprint"),1);
    Line(TEXT("LMB or J greatsword / Space roll / E heal"),2);
    Line(TEXT("F5 fixed boss rehearsal or practice dummy"),3);
    Line(TEXT("F6 test pilot / R restart / Esc menu"),4);
    Line(TEXT("M mute / F2 motion / F4 sensitivity"),5);
    Line(TEXT("F3 blade contact debug / F9 export"),6);
    Line(TEXT("Adaptive AI / RL / models: deferred, inactive"),7);
    Line(FString::Printf(TEXT("Two-hand grip error %.2f cm | I close"),M->Player->GripError),8);
}
void AWardenArenaMode::SaveReport()
{
    FString Directory=FPaths::Combine(FPaths::ProjectSavedDir(),TEXT("BossLabEvidence"));
#if WITH_EDITOR
    Directory=FPaths::ConvertRelativePathToFull(FPaths::Combine(FPaths::ProjectDir(),TEXT("../../artifacts/unreal")));
#endif
    IFileManager::Get().MakeDirectory(*Directory,true);
    const FString Stem=FPaths::Combine(Directory,FString::Printf(TEXT("encounter-%s-%d-%d"),*FDateTime::UtcNow().ToString(TEXT("%Y%m%d-%H%M%S")),Encounter,CombatTick));
    const TCHAR* Outcome=!Player->Fight.Alive()?TEXT("boss_win"):!Warden->Fight.Alive()?TEXT("player_win"):TEXT("in_progress");
    FString Json=FString::Printf(TEXT("{\"rules\":\"warden-gameplay-rework-v2\",\"controller\":\"%s\",\"scripted\":%s,\"demo\":%s,\"demo_tick\":%d,\"disclosed_round_resets\":%d,\"outcome\":\"%s\",\"tick\":%d,\"player_hp\":%g,\"boss_hp\":%g,\"player_damage\":%g,\"boss_damage\":%g,\"moves\":[%d,%d,%d],\"samples\":%d,\"censored\":%d,\"recent\":[%g,%g,%g],\"events\":["),bRehearsal?TEXT("fixed-rehearsal"):TEXT("practice-dummy"),bScriptedPlayer?TEXT("true"):TEXT("false"),bDemo?TEXT("true"):TEXT("false"),DemoTick,DemoRounds,Outcome,CombatTick,Player->Fight.Health,Warden->Fight.Health,PlayerDamage,BossDamage,MoveCounts[0],MoveCounts[1],MoveCounts[2],Statistics.Pooled.Samples,Statistics.Censored,Statistics.Pooled.Probability(0),Statistics.Pooled.Probability(1),Statistics.Pooled.Probability(2));
    FString Csv=TEXT("encounter,attack,family,cue,close,delivered,response,heading,censored\n");
    for(int32 I=0;I<Statistics.Events.Num();++I)
    {
        const auto& E=Statistics.Events[I];
        if(I) Json+=TEXT(",");
        Json+=FString::Printf(TEXT("{\"encounter\":%d,\"attack\":%d,\"family\":%d,\"cue\":%d,\"close\":%d,\"delivered\":%d,\"response\":%d,\"heading\":%d,\"censored\":%s}"),E.Encounter,E.Attack,E.Family,E.CueTick,E.CloseTick,E.DeliveredTick,E.Response,E.Heading,E.Censored?TEXT("true"):TEXT("false"));
        Csv+=FString::Printf(TEXT("%d,%d,%d,%d,%d,%d,%d,%d,%d\n"),E.Encounter,E.Attack,E.Family,E.CueTick,E.CloseTick,E.DeliveredTick,E.Response,E.Heading,int32(E.Censored));
    }
    TArray<double> Sorted=FrameMilliseconds; Sorted.Sort(); double Mean=0;
    for(double V:Sorted) Mean+=V; if(Sorted.Num()) Mean/=Sorted.Num();
    const double P95=Sorted.Num()?Sorted[FMath::Min(Sorted.Num()-1,FMath::FloorToInt(Sorted.Num()*.95))]:0;
    Json+=FString::Printf(TEXT("],\"frame_timing\":{\"kind\":\"wall-clock game-thread frame intervals; first 180 active frames excluded\",\"samples\":%d,\"mean_ms\":%g,\"p95_ms\":%g,\"editor_binary\":%s}}"),Sorted.Num(),Mean,P95,
#if WITH_EDITOR
        TEXT("true")
#else
        TEXT("false")
#endif
    );
    if(bBenchmark)
    {
        FString FramesCsv=TEXT("frame,wall_ms\n");
        for(int32 I=0;I<FrameMilliseconds.Num();++I) FramesCsv+=FString::Printf(TEXT("%d,%.8f\n"),I,FrameMilliseconds[I]);
        FFileHelper::SaveStringToFile(FramesCsv,*FPaths::Combine(Directory,TEXT("frame-times.csv")));
        const FIntPoint Size=GetWorld()->GetGameViewport() && GetWorld()->GetGameViewport()->Viewport ? GetWorld()->GetGameViewport()->Viewport->GetSizeXY():FIntPoint::ZeroValue;
        const FString Perf=FString::Printf(TEXT("{\"kind\":\"actual wall-clock frame intervals; active gameplay, 180 warmup frames excluded\",\"width\":%d,\"height\":%d,\"samples\":%d,\"mean_ms\":%g,\"p95_ms\":%g,\"demo_tick\":%d,\"editor_binary\":%s}"),Size.X,Size.Y,Sorted.Num(),Mean,P95,DemoTick,
#if WITH_EDITOR
            TEXT("true")
#else
            TEXT("false")
#endif
        );
        FFileHelper::SaveStringToFile(Perf,*FPaths::Combine(Directory,TEXT("benchmark.json")));
    }
    const bool Saved=FFileHelper::SaveStringToFile(Json,*(Stem+TEXT(".json"))) && FFileHelper::SaveStringToFile(Csv,*(Stem+TEXT(".csv")));
    LastEvent=Saved?TEXT("Encounter report exported (JSON + event CSV)"):TEXT("Report export failed; inspect log");
    UE_LOG(LogTemp,Display,TEXT("BossLab report saved=%d: %s"),Saved,*Stem);
}
