// Game audio (presentation only): layered sound variations from ue_import_game_audio.py,
// played through one path that picks a variation (never the same one twice running), jitters
// pitch and volume, limits overlapping voices per sound, fades with distance and sends to a
// room reverb. Ambience beds loop under the fight. See docs/AUDIO.md.
#include "WardenPrototype.h"
#include "Components/AudioComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SpotLightComponent.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "AudioMixerBlueprintLibrary.h"
#include "SubmixEffects/AudioMixerSubmixEffectDynamicsProcessor.h"
#include "Misc/Paths.h"
#include "Sound/ReverbEffect.h"
#include "Sound/SoundAttenuation.h"
#include "Sound/SoundConcurrency.h"
#include "Sound/SoundWave.h"

namespace
{
    // Older single sounds, used when the layered set has not been imported.
    const TCHAR* LegacyFolders[]={TEXT("/Game/BossLab/Effects/Audio/"),TEXT("/Game/BossLab/Regent/Audio/"),TEXT("/Game/BossLab/Audio/")};
}

const TArray<TWeakObjectPtr<USoundBase>>& AWardenArenaMode::SfxVariations(const FString& Name,const TCHAR* Legacy)
{
    if(const auto* Found=SfxBank.Find(Name)) return *Found;
    auto& List=SfxBank.Add(Name);
    for(int32 I=0;I<12;++I)
    {
        auto* Sound=LoadObject<USoundBase>(nullptr,*FString::Printf(TEXT("/Game/BossLab/Sound/%s_%d"),*Name,I),nullptr,LOAD_Quiet|LOAD_NoWarn);
        if(!Sound) break;
        List.Add(Sound); SfxKeepAlive.Add(Sound);
    }
    if(List.IsEmpty())
        for(const TCHAR* Folder:LegacyFolders)
            if(auto* Sound=LoadObject<USoundBase>(nullptr,*(FString(Folder)+(Legacy?Legacy:*Name)),nullptr,LOAD_Quiet|LOAD_NoWarn))
            { List.Add(Sound); SfxKeepAlive.Add(Sound); break; }
    return List;
}

int32 AWardenArenaMode::SfxPick(const FString& Name,int32 Count)
{
    // Random variation, never the one that just played (repetition is what sounds cheap).
    int32& Last=SfxLast.FindOrAdd(Name,-1);
    int32 Pick=FMath::RandRange(0,Count-1);
    if(Count>1 && Pick==Last) Pick=(Pick+1+FMath::RandRange(0,Count-2))%Count;
    return Last=Pick;
}

void AWardenArenaMode::PlaySfx(const FString& Name,const FVector& At,float Volume,float PitchJitter,float Falloff,const TCHAR* Legacy)
{
    if(bMuted || !GetWorld() || !GetWorld()->GetFirstPlayerController()) return;
    const auto& List=SfxVariations(Name,Legacy);
    if(List.IsEmpty()) return;
    USoundBase* Sound=List[SfxPick(Name,List.Num())].Get();
    if(!Sound) return;
    // One attenuation per falloff distance and one voice limit per sound name.
    const int32 Key=FMath::RoundToInt(Falloff);
    USoundAttenuation*& Attenuation=SfxAttenuation.FindOrAdd(Key);
    if(!Attenuation)
    {
        Attenuation=NewObject<USoundAttenuation>(this);
        Attenuation->Attenuation.bAttenuate=true; Attenuation->Attenuation.bSpatialize=true;
        // Full volume within a quarter of the falloff: the listener is the camera, several
        // metres behind the player, so a small inner radius made everything sound distant.
        Attenuation->Attenuation.AttenuationShapeExtents=FVector(Falloff*.25f);
        Attenuation->Attenuation.FalloffDistance=Falloff;
        Attenuation->Attenuation.bEnableReverbSend=true;
        SfxKeepAlive.Add(Attenuation);
    }
    USoundConcurrency*& Limit=SfxLimit.FindOrAdd(Name);
    if(!Limit)
    {
        Limit=NewObject<USoundConcurrency>(this);
        Limit->Concurrency.MaxCount=Name.StartsWith(TEXT("Step")) ? 4 : 3;
        Limit->Concurrency.bLimitToOwner=false;
        Limit->Concurrency.ResolutionRule=EMaxConcurrentResolutionRule::StopOldest;
        SfxKeepAlive.Add(Limit);
    }
    const float Pitch=1+FMath::FRandRange(-PitchJitter,PitchJitter);
    // Effects master (+8 dB): the first recorded mix sat near -36 dBFS integrated.
    const float Gain=Volume*SfxMaster*FMath::FRandRange(.88f,1.f);
    UGameplayStatics::PlaySoundAtLocation(this,Sound,At,Gain,Pitch,0.f,Attenuation,Limit);
}

void AWardenArenaMode::SetupAudio()
{
    if(!GetWorld() || !GetWorld()->GetFirstPlayerController()) return;
    // Room reverb: a long, dark stone hall for the dungeon; a smaller court otherwise.
    auto* Reverb=NewObject<UReverbEffect>(this);
    Reverb->Density=1; Reverb->Diffusion=bDungeon ? .9f : .7f;
    Reverb->Gain=bDungeon ? .38f : .25f; Reverb->GainHF=.6f;
    Reverb->DecayTime=bDungeon ? 2.6f : 1.4f; Reverb->DecayHFRatio=.55f;
    Reverb->ReflectionsGain=.35f; Reverb->ReflectionsDelay=bDungeon ? .03f : .015f;
    Reverb->LateGain=1.4f; Reverb->LateDelay=bDungeon ? .04f : .02f;
    Reverb->AirAbsorptionGainHF=.98f; Reverb->RoomRolloffFactor=0;
    SfxKeepAlive.Add(Reverb);
    // Master bus: +6 dB into a look-ahead limiter at -2 dBFS, so the louder mix never clips.
    auto* Limiter=NewObject<USubmixEffectDynamicsProcessorPreset>(this);
    FSubmixEffectDynamicsProcessorSettings Dyn;
    Dyn.DynamicsProcessorType=ESubmixEffectDynamicsProcessorType::Limiter;
    Dyn.InputGainDb=6; Dyn.ThresholdDb=-2; Dyn.LookAheadMsec=5; Dyn.AttackTimeMsec=1; Dyn.ReleaseTimeMsec=120;
    Limiter->SetSettings(Dyn); SfxKeepAlive.Add(Limiter);
    UAudioMixerBlueprintLibrary::AddMasterSubmixEffect(this,Limiter);
    int32 Loaded=0;
    for(const TCHAR* Name:{TEXT("SwordHit"),TEXT("SwordWhooshLight"),TEXT("StepStone"),TEXT("StepHeavy"),TEXT("RegentBell")}) Loaded+=SfxVariations(Name,nullptr).Num();
    UGameplayStatics::ActivateReverbEffect(this,Reverb,TEXT("BossLabRoom"),1,.8f,.5f);
    // Ambience beds: room tone everywhere; brazier crackle at the dungeon's nearest fires.
    auto Bed=[&](const FString& Name)->USoundBase* { const auto& L=SfxVariations(Name,nullptr); return L.IsEmpty()?nullptr:L[0].Get(); };
    if(USoundBase* Room=Bed(TEXT("AmbDungeon")))
        if(auto* C=UGameplayStatics::SpawnSound2D(this,Room,bDungeon ? .6f : .35f,1,0,nullptr,true,false))
        { AmbienceVolume.Add(C->VolumeMultiplier); Ambience.Add(C); }
    if(bDungeon)
        if(USoundBase* Fire=Bed(TEXT("AmbFire")))
        {
            TArray<FVector> Fires;
            for(const auto& L:Dungeon.Lights)
                if(L.IsValid() && L->IsA<UPointLightComponent>() && !L->IsA<USpotLightComponent>()) Fires.Add(L->GetComponentLocation());
            Fires.Sort([](const FVector& A,const FVector& B){ return A.Size2D()<B.Size2D(); });
            auto* Falloff=NewObject<USoundAttenuation>(this);
            Falloff->Attenuation.bAttenuate=true; Falloff->Attenuation.bSpatialize=true;
            Falloff->Attenuation.AttenuationShapeExtents=FVector(80); Falloff->Attenuation.FalloffDistance=1100;
            SfxKeepAlive.Add(Falloff);
            for(int32 I=0;I<FMath::Min(6,Fires.Num());++I)
                if(auto* C=UGameplayStatics::SpawnSoundAtLocation(this,Fire,Fires[I],FRotator::ZeroRotator,1.f,FMath::FRandRange(.9f,1.08f),FMath::FRandRange(0.f,7.f),Falloff,nullptr,false))
                { AmbienceVolume.Add(C->VolumeMultiplier); Ambience.Add(C); }
        }
    // Boss music: the Scattered Ghost bed loops under the fight (MusicBoss), deeper and louder
    // in the Regent's second phase, and fades out when the boss falls (UpdateAudio).
    if(USoundBase* Music=Bed(TEXT("MusicBoss")))
        if(auto* C=UGameplayStatics::SpawnSound2D(this,Music,1,1,0,nullptr,true,false))
        { C->FadeIn(4.f,FMath::Max(MusicLevel(),.0001f)); MusicComponent=C; MusicTarget=MusicLevel(); }
    // Benchmark-only: record the final mix so its loudness can be measured offline
    // (./scripts/bosslab-unreal benchmark record-audio).
    if(FParse::Param(FCommandLine::Get(),TEXT("BossLabRecordAudio"))) { UAudioMixerBlueprintLibrary::StartRecordingOutput(this,90.f); bRecordingAudio=true; }
    UE_LOG(LogTemp,Display,TEXT("BOSSLAB audio: reverb %s, %d ambience beds, music %s, %d variations across 5 sample events"),bDungeon?TEXT("hall"):TEXT("court"),Ambience.Num(),MusicComponent.IsValid()?TEXT("on"):TEXT("absent"),Loaded);
}

void AWardenArenaMode::StopAudioRecording()
{
    if(!bRecordingAudio) return;
    bRecordingAudio=false;
    const FString Dir=FPaths::ConvertRelativePathToFull(FPaths::Combine(FPaths::ProjectDir(),TEXT("../../artifacts/unreal")));
    UAudioMixerBlueprintLibrary::StopRecordingOutput(this,EAudioRecordingExportType::WavFile,TEXT("audio-mix"),Dir);
    UE_LOG(LogTemp,Display,TEXT("BOSSLAB audio recording saved to %s/audio-mix.wav"),*Dir);
}

float AWardenArenaMode::MusicLevel() const
{
    const bool Living=Warden && Warden->Fight.Alive();
    if(bMuted || !Living) return 0;
    return (bRegent ? (Regent.PhaseTwo ? 1.f : .8f) : .6f)*MusicVolumeScale;
}

void AWardenArenaMode::UpdateAudio()
{
    if(auto* C=MusicComponent.Get())
    {
        const float Level=MusicLevel(), Pitch=bRegent && Regent.PhaseTwo ? .92f : 1.f;
        // Restart the bed if anything stopped it (it must never silently stay off).
        if(!C->IsPlaying() && Level>0) { C->Play(); C->FadeIn(3.f,Level); MusicTarget=Level; }
        if(!FMath::IsNearlyEqual(Level,MusicTarget) || !FMath::IsNearlyEqual(Pitch,MusicPitch))
        {
            // Swell into phase two, fall away with the boss, return on a fresh encounter.
            C->AdjustVolume(Level>MusicTarget ? 2.5f : 4.f,FMath::Max(Level,.0001f));
            C->SetPitchMultiplier(Pitch);
            MusicTarget=Level; MusicPitch=Pitch;
        }
    }
    // Mute applies to the looping beds as well as one-shots.
    if(bAmbienceMuted==bMuted) return;
    bAmbienceMuted=bMuted;
    for(int32 I=0;I<Ambience.Num();++I)
        if(auto* C=Ambience[I].Get()) C->SetVolumeMultiplier(bMuted ? 0.f : AmbienceVolume[I]);
}
