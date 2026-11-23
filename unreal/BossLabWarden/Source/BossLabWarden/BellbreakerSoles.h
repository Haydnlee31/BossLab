#pragma once
#include "CoreMinimal.h"

class UPoseableMeshComponent;

// Bind-space samples from the bottoms of the installed boots. Cache their
// skinning influences once; the draw pass only transforms these few landmarks.
struct FBellbreakerSoles
{
    struct FInfluence { int32 Bone; float Weight; FVector Point; };
    struct FSample { int32 Thigh=INDEX_NONE; TArray<FInfluence,TInlineAllocator<4>> Influences; };
    TArray<FSample> Samples;
    void Fit(UPoseableMeshComponent* Body);
    bool Lowest(const TArray<FTransform>& Pose,double& Height,int32 Thigh=INDEX_NONE) const;
};
