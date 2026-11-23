#pragma once
#include "Math/Vector.h"

#if WITH_EDITOR
class UPoseableMeshComponent;
class UStaticMeshComponent;
void WardenAuditBellMesh(UPoseableMeshComponent* Body, UStaticMeshComponent* Hammer, int Move, int Age, const FVector& Forward);
// One-frame surface audit in the deterministic forge presentation study.
void WardenWriteBellbreakerSkinProbe(UPoseableMeshComponent* Body,const TCHAR* Label=TEXT("BellbreakerSkinProbe"));
#endif
