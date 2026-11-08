#include "Modules/ModuleManager.h"
#if WITH_EDITOR
#include "Editor.h"
#include "LevelEditorSubsystem.h"
#include "Subsystems/SubsystemCollection.h"
#include "Misc/CoreDelegates.h"
#endif

class FBossLabModule : public FDefaultGameModuleImpl
{
public:
    virtual void StartupModule() override
    {
#if WITH_EDITOR
        PostInitHandle = FCoreDelegates::GetOnPostEngineInit().AddLambda([]
        {
            // UE 5.8.4 minimal plugin profile: verified absent in native automation.
            // Activate through the public subsystem lifecycle; never replace an existing instance.
            if (GEditor && !GEditor->GetEditorSubsystem<ULevelEditorSubsystem>())
            {
                FSubsystemCollectionBase::ActivateExternalSubsystem(ULevelEditorSubsystem::StaticClass());
                UE_LOG(LogTemp, Display, TEXT("BossLab: activated missing LevelEditorSubsystem via public API"));
            }
        });
#endif
    }
    virtual void ShutdownModule() override
    {
#if WITH_EDITOR
        FCoreDelegates::GetOnPostEngineInit().Remove(PostInitHandle);
#endif
    }
private:
#if WITH_EDITOR
    FDelegateHandle PostInitHandle;
#endif
};
IMPLEMENT_PRIMARY_GAME_MODULE(FBossLabModule, BossLabWarden, "BossLabWarden");
