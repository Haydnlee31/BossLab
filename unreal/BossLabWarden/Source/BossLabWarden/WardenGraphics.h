// Overnight 2026-11-14 graphics toggles (presentation only; combat never reads these).
// BOSSLAB_GRAPHICS unset: every feature on. BOSSLAB_GRAPHICS=off: all off (previous look).
// A comma list of "-name" entries turns single features off, e.g.
// BOSSLAB_GRAPHICS=-volumetric,-rim. Names: grade, volumetric, rim, sparks, warmth (warm fire
// grade, 2026-11-14), spectacle (WardenSpectacle.cpp, 2026-11-14).
// See docs/OVERNIGHT_2026-11-14_GRAPHICS.md.
#pragma once
#include "CoreMinimal.h"
#include "HAL/PlatformMisc.h"

namespace WardenGraphics
{
inline bool Enabled(const TCHAR* Feature)
{
    const FString Value=FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_GRAPHICS")).ToLower();
    if(Value==TEXT("off") || Value==TEXT("0")) return false;
    TArray<FString> Parts; Value.ParseIntoArray(Parts,TEXT(","));
    for(FString& P:Parts) if(P.TrimStartAndEnd()==FString(TEXT("-"))+FString(Feature).ToLower()) return false;
    return true;
}
}
