#pragma once
#include "CoreMinimal.h"

// Player-facing options (pause menu Options panel, WardenQoL.cpp). Presentation and input
// feel only: nothing here touches combat rules, timing or damage. Persisted to a small
// ini-format file in the project's Saved directory (never machine-wide).
struct FWardenSettings
{
    float Sensitivity=1.f;      // mouse look multiplier (0.25 - 3)
    float CameraDistance=1.f;   // spring-arm length multiplier (0.7 - 1.5)
    float MasterVolume=1.f, MusicVolume=1.f, SfxVolume=1.f;   // 0 - 1
    bool bInvertY=false, bDamageNumbers=true, bControlHints=true;

    void Clamp();
    FString Serialize() const;
    void Parse(const FString& Text);
    bool Save(const FString& File) const;
    bool Load(const FString& File);
    static FString DefaultFile();
    bool operator==(const FWardenSettings& O) const
    {
        return Sensitivity==O.Sensitivity && CameraDistance==O.CameraDistance && MasterVolume==O.MasterVolume
            && MusicVolume==O.MusicVolume && SfxVolume==O.SfxVolume && bInvertY==O.bInvertY
            && bDamageNumbers==O.bDamageNumbers && bControlHints==O.bControlHints;
    }
};

// Session record for the results screen and the corner timer (WardenQoL.cpp). Counts only
// human-played encounters (no demo/scripted pilot/capture). Session only, not persisted.
struct FWardenRunRecord
{
    int32 Attempts=0, Deaths=0, Victories=0;
    float BestBossFraction=1.f;     // lowest boss health fraction any attempt reached
    float BestVictorySeconds=0;     // fastest victory (0 = none yet)
    FString KilledBy;               // what landed the last killing blow
    bool bCounted=false;            // current attempt already counted / result recorded
    bool bResult=false;
    bool bPractice=false;           // current attempt used a practice option
};
