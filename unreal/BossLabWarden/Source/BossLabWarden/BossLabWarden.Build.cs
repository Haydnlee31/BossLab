using UnrealBuildTool;
public class BossLabWarden : ModuleRules
{
    public BossLabWarden(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine", "InputCore", "Json" });
        PrivateDependencyModuleNames.AddRange(new[] { "Slate", "SlateCore", "MeshDescription", "StaticMeshDescription" });
        if (Target.bBuildEditor) PrivateDependencyModuleNames.AddRange(new[] { "UnrealEd", "LevelEditor" });
    }
}
