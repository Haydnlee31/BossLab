#include "BellbreakerSkinProbe.h"
#include "CoreMinimal.h"

#if WITH_EDITOR
#include "Camera/PlayerCameraManager.h"
#include "Components/PoseableMeshComponent.h"
#include "Engine/GameViewportClient.h"
#include "Engine/LocalPlayer.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Rendering/SkeletalMeshLODRenderData.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "Rendering/SkinWeightVertexBuffer.h"
#include "SceneView.h"

void WardenWriteBellbreakerSkinProbe(UPoseableMeshComponent* Body,const TCHAR* Label)
{
    if(FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_SKIN_PROBE"))!=TEXT("1")) return;
    APlayerController* PC=Body->GetWorld()->GetFirstPlayerController();
    ULocalPlayer* Player=PC ? PC->GetLocalPlayer() : nullptr;
    if(!Player || !Player->ViewportClient || !PC->PlayerCameraManager) return;
    FSceneViewProjectionData Projection;
    if(!Player->GetProjectionData(Player->ViewportClient->Viewport,Projection)) return;

    const int32 LOD=Body->GetPredictedLODLevel();
    const auto* Data=Body->GetSkeletalMeshRenderData();
    if(!Data || !Data->LODRenderData.IsValidIndex(LOD)) return;
    const auto& Mesh=Data->LODRenderData[LOD];
    const auto& Positions=Mesh.StaticVertexBuffers.PositionVertexBuffer;
    auto* Weights=Body->GetSkinWeightBuffer(LOD);
    const auto* Indices=Mesh.MultiSizeIndexContainer.GetIndexBuffer();
    if(!Weights || !Weights->GetDataVertexBuffer()->GetWeightData() || !Indices || !Indices->Num() || !Positions.GetVertexData()) return;

    const FVector Eye=PC->PlayerCameraManager->GetCameraLocation();
    const FMatrix ViewProjection=Projection.ComputeViewProjectionMatrix();
    const FString Directory=FPaths::ProjectSavedDir()/Label;
    IFileManager::Get().MakeDirectory(*Directory,true);
    TUniquePtr<FArchive> File(IFileManager::Get().CreateFileWriter(*(Directory/TEXT("surface.bin"))));
    if(!File) return;
    int32 VertexCount=Positions.GetNumVertices(),IndexCount=Indices->Num();
    *File << VertexCount << IndexCount;
    const auto& Ref=Body->GetSkinnedAsset()->GetRefSkeleton();
    FString Bones;
    for(int32 I=0;I<Ref.GetNum();++I) Bones+=Ref.GetBoneName(I).ToString()+LINE_TERMINATOR;
    FFileHelper::SaveStringToFile(Bones,*(Directory/TEXT("bones.txt")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    // Exact UE skinning palette for reproducing this frame on another mesh
    // bound to the same rest skeleton. Row vectors; component-space cm.
    const auto& InverseBind=Body->GetSkinnedAsset()->GetRefBasesInvMatrix();
    const auto& Pose=Body->GetComponentSpaceTransforms();
    FString Palette;
    for(int32 I=0;I<Ref.GetNum() && InverseBind.IsValidIndex(I) && Pose.IsValidIndex(I);++I)
    {
        const FMatrix44f Skin=InverseBind[I]*FMatrix44f(Pose[I].ToMatrixWithScale());
        Palette+=Ref.GetBoneName(I).ToString();
        for(int32 Row=0;Row<4;++Row)
            for(int32 Col=0;Col<3;++Col) Palette+=FString::Printf(TEXT(",%.9g"),Skin.M[Row][Col]);
        Palette+=LINE_TERMINATOR;
    }
    FFileHelper::SaveStringToFile(Palette,*(Directory/TEXT("bone-palette.csv")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    for(int32 I=0;I<VertexCount;++I)
    {
        const FVector3f Bind=Positions.VertexPosition(I);
        const FVector3f Skin=USkinnedMeshComponent::GetSkinnedVertexPosition(Body,I,Mesh,*Weights);
        const FVector World=Body->GetComponentTransform().TransformPosition(FVector(Skin));
        FVector2D Pixel;
        FSceneView::ProjectWorldToScreen(World,Projection.GetConstrainedViewRect(),ViewProjection,Pixel,true);
        const float Values[]={Bind.X,Bind.Y,Bind.Z,Skin.X,Skin.Y,Skin.Z,float(Pixel.X),float(Pixel.Y),float(FVector::Distance(Eye,World))};
        File->Serialize(const_cast<float*>(Values),sizeof(Values));
        int32 Section=0,LocalVertex=0;
        Mesh.GetSectionFromVertexIndex(I,Section,LocalVertex);
        for(int32 J=0;J<4;++J)
        {
            uint16 Bone=0,Weight=0;
            if(J<Weights->GetMaxBoneInfluences())
            {
                const int32 LocalBone=Weights->GetBoneIndex(I,J);
                Weight=Weights->GetBoneWeight(I,J);
                if(Mesh.RenderSections[Section].BoneMap.IsValidIndex(LocalBone)) Bone=Mesh.RenderSections[Section].BoneMap[LocalBone];
            }
            *File << Bone << Weight;
        }
    }
    for(int32 I=0;I<IndexCount;++I)
    {
        uint32 Vertex=Indices->Get(I);
        *File << Vertex;
    }
    File->Close();
    UE_LOG(LogTemp,Display,TEXT("BOSSLAB surface probe: %s | %d vertices, %d triangles"),*Directory,VertexCount,IndexCount/3);
}
#endif

#if WITH_EDITOR
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "StaticMeshResources.h"
#include "DynamicMesh/DynamicMesh3.h"
#include "Spatial/MeshAABBTree3.h"

// Offline study only. Query the complete weapon mesh against the rendered skin;
// separate normal finger/haft contact from cloth, torso and forearm intersections.
void WardenAuditBellMesh(UPoseableMeshComponent* Body, UStaticMeshComponent* Hammer, int Move, int Age, const FVector& Forward)
{
    using namespace UE::Geometry;
    static const bool Enabled = FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_BELL_AUDIT")) == TEXT("1");
    if (!Enabled) return;
    const UStaticMesh* Asset = Hammer->GetStaticMesh();
    const auto* Skin = Body->GetSkeletalMeshRenderData();
    if (!Asset || !Asset->GetRenderData() || !Skin || !Skin->LODRenderData.IsValidIndex(0)) return;
    static FDynamicMesh3 Weapon;
    static TUniquePtr<TMeshAABBTree3<FDynamicMesh3>> Tree;
    static TWeakObjectPtr<const UStaticMesh> Cached;
    if (!Tree || Cached.Get() != Asset)
    {
        Weapon.Clear();
        const auto& L = Asset->GetRenderData()->LODResources[0];
        const auto& Positions = L.VertexBuffers.PositionVertexBuffer;
        const auto Indices = L.IndexBuffer.GetArrayView();
        if (!Positions.GetVertexData() || Indices.Num() == 0) return;
        for(int Z=142; Z<=312; Z+=10)
        {
            FBox Section(ForceInit);
            for(uint32 I=0; I<Positions.GetNumVertices(); ++I)
            {
                const FVector P(Positions.VertexPosition(I));
                if(FMath::Abs(P.Z-Z)<4.) Section+=P;
            }
            if(Section.IsValid) UE_LOG(LogTemp,Display,TEXT("BOSSLAB imported shaft section %d centre %s extent %s"),
                Z,*Section.GetCenter().ToCompactString(),*Section.GetExtent().ToCompactString());
        }
        // Independent triangles also preserve non-manifold faces from the imported asset.
        for (int I=0; I+2<Indices.Num(); I+=3)
        {
            const int A=Weapon.AppendVertex(FVector(Positions.VertexPosition(Indices[I])));
            const int B=Weapon.AppendVertex(FVector(Positions.VertexPosition(Indices[I+1])));
            const int C=Weapon.AppendVertex(FVector(Positions.VertexPosition(Indices[I+2])));
            Weapon.AppendTriangle(A,B,C);
        }
        Tree=MakeUnique<TMeshAABBTree3<FDynamicMesh3>>(&Weapon);
        Cached=Asset;
    }
    const int LOD=Body->GetPredictedLODLevel();
    if (!Skin->LODRenderData.IsValidIndex(LOD)) return;
    const auto& Mesh=Skin->LODRenderData[LOD];
    auto* Weights=Body->GetSkinWeightBuffer(LOD);
    const auto* Idx=Mesh.MultiSizeIndexContainer.GetIndexBuffer();
    if (!Idx || !Weights || !Weights->GetDataVertexBuffer()->GetWeightData()) return;
    TArray<FMatrix44f> Matrices;
    Body->GetCurrentRefToLocalMatrices(Matrices,LOD);
    if (Matrices.IsEmpty()) return;
    const FTransform ToWeapon=Body->GetComponentTransform().GetRelativeTransform(Hammer->GetComponentTransform());
    TArray<FVector> V; V.SetNumUninitialized(Mesh.GetNumVertices());
    for(int I=0; I<V.Num(); ++I)
        V[I]=ToWeapon.TransformPosition(FVector(USkinnedMeshComponent::GetSkinnedVertexPosition(Body,I,Mesh,*Weights,Matrices)));
    // Actual skinned boot vertices, independent of the joint-height proxy.
    // Keep the same bind-space sole region as the mesh moves through a stride.
    const auto& Bind=Mesh.StaticVertexBuffers.PositionVertexBuffer;
    double BootLeft=DBL_MAX,BootRight=DBL_MAX;
    for(int I=0; I<V.Num(); ++I)
    {
        const FVector3f Rest=Bind.VertexPosition(I);
        if(Rest.Z>8.f) continue;
        const double Height=Hammer->GetComponentTransform().TransformPosition(V[I]).Z;
        double& Boot=(Rest.X>0.f) ? BootLeft : BootRight;
        Boot=FMath::Min(Boot,Height);
    }
    if(BootLeft!=DBL_MAX && BootRight!=DBL_MAX)
        UE_LOG(LogTemp,Display,TEXT("BOSSLAB sole move=%d age=%d left=%.2f right=%.2f"),Move,Age,BootLeft,BootRight);
    int Torso=0,Head=0,Upper=0,Forearm=0,Hand=0,Leg=0,LeftHand=0,RightHand=0,ForearmL=0,ForearmR=0;
    // Actual intersecting skin triangles on the handle. Report separately for
    // the thumb, four fingers and palm so a palm brushing one face of the
    // shaft cannot be mistaken for a wrapped grip.
    uint8 TouchDigits[2]={},TouchSectors[2]={};
    float MinForearm=MAX_flt, MaxForearm=-MAX_flt;
    const FBox Box=Asset->GetBoundingBox();
    float MinCore=MAX_flt,MaxCore=-MAX_flt;
    static const bool SearchClearance=FPlatformMisc::GetEnvironmentVariable(TEXT("BOSSLAB_BELL_SHIFT"))==TEXT("1");
    const bool SampleShift=SearchClearance && Age%12<2;
    constexpr int Candidates=13;
    bool Blocked[Candidates]={};
    const FVector Shift=Hammer->GetComponentTransform().InverseTransformVector(Forward*10.);
    for(int I=0; I+2<Idx->Num(); I+=3)
    {
        const int A=Idx->Get(I),B=Idx->Get(I+1),C=Idx->Get(I+2);
        const auto& P=V[A]; const auto& Q=V[B]; const auto& R=V[C];
        const FBox Bounds(P.ComponentMin(Q).ComponentMin(R),P.ComponentMax(Q).ComponentMax(R));
        const bool Touch=Box.Intersect(Bounds) && Tree->TestIntersection(FTriangle3d(P,Q,R));
        if (!Touch && !SampleShift) continue;
        int Section,LocalId;
        Mesh.GetSectionFromVertexIndex(A,Section,LocalId);
        const auto& Bones=Mesh.RenderSections[Section].BoneMap;
        int MaxWeight=-1, MainBone=0;
        for(int J=0; J<Weights->GetMaxBoneInfluences(); ++J)
        {
            int Weight=Weights->GetBoneWeight(A,J);
            if(Weight>MaxWeight) { MainBone=Bones[Weights->GetBoneIndex(A,J)]; MaxWeight=Weight; }
        }
        const FString Bone=Body->GetSkinnedAsset()->GetRefSkeleton().GetBoneName(MainBone).ToString();
        if(SampleShift && (Bone.StartsWith(TEXT("spine")) || Bone.StartsWith(TEXT("pelvis")) ||
            Bone.StartsWith(TEXT("thigh")) || Bone.StartsWith(TEXT("calf")) ||
            Bone.StartsWith(TEXT("head")) || Bone.StartsWith(TEXT("neck")) || Bone==TEXT("root")))
            for(int J=0;J<Candidates;++J)
            {
                const FVector Delta=Shift*J;
                if(!Blocked[J] && Box.Intersect(Bounds.ShiftBy(-Delta)))
                    Blocked[J]=Tree->TestIntersection(FTriangle3d(P-Delta,Q-Delta,R-Delta));
            }
        if(!Touch) continue;
        if(Bone.StartsWith(TEXT("lowerarm")))
        {
            ++Forearm;
            ForearmL+=Bone.EndsWith(TEXT("_l")); ForearmR+=Bone.EndsWith(TEXT("_r"));
            const float Z=(P.Z+Q.Z+R.Z)/3;
            MinForearm=FMath::Min(MinForearm,Z); MaxForearm=FMath::Max(MaxForearm,Z);
        }
        else if(Bone.StartsWith(TEXT("upperarm")) || Bone.StartsWith(TEXT("clavicle"))) ++Upper;
        else if(Bone.StartsWith(TEXT("head")) || Bone.StartsWith(TEXT("neck"))) ++Head;
        else if(Bone.StartsWith(TEXT("thigh")) || Bone.StartsWith(TEXT("calf")) || Bone.StartsWith(TEXT("foot")) || Bone.StartsWith(TEXT("ball"))) ++Leg;
        else if(Bone.StartsWith(TEXT("spine")) || Bone.StartsWith(TEXT("pelvis")) || Bone==TEXT("root")) ++Torso;
        else
        {
            ++Hand;
            const bool Left=Bone.EndsWith(TEXT("_l"));
            LeftHand+=Left; RightHand+=Bone.EndsWith(TEXT("_r"));
            const FVector Mid=(P+Q+R)/3.;
            if(Mid.Z>=220 && Mid.Z<=320)
            {
                const int Side=Left ? 0 : 1;
                static const TCHAR* Digits[]={TEXT("thumb_"),TEXT("index_"),TEXT("middle_"),TEXT("ring_"),TEXT("pinky_")};
                for(int Finger=0;Finger<5;++Finger)
                    if(Bone.StartsWith(Digits[Finger])) TouchDigits[Side]|=uint8(1<<Finger);
                // Measured centreline of this bowed portion of the handle.
                const double Depth=FMath::Clamp(Mid.Z-230.,-100.,80.);
                const double Theta=FMath::Atan2(Mid.Y-(5.9+.145*Depth),Mid.X-(-6.7-.085*Depth));
                const int Sector=FMath::Clamp(FMath::FloorToInt((Theta+PI)*(4./PI)),0,7);
                TouchSectors[Side]|=uint8(1<<Sector);
            }
            continue;
        }
        const float Along=(P.Z+Q.Z+R.Z)/3;
        MinCore=FMath::Min(MinCore,Along); MaxCore=FMath::Max(MaxCore,Along);
    }
    UE_LOG(LogTemp,Display,TEXT("BOSSLAB grip coverage move=%d age=%d digits_l=%u digits_r=%u sectors_l=%u sectors_r=%u"),
        Move,Age,uint32(TouchDigits[0]),uint32(TouchDigits[1]),uint32(TouchSectors[0]),uint32(TouchSectors[1]));
    if(SampleShift)
    {
        int J=0;
        while(J<Candidates && Blocked[J]) ++J;
        UE_LOG(LogTemp,Display,TEXT("BOSSLAB armour clearance move=%d age=%d forward_cm=%d"), Move,Age,J==Candidates ? -1 : J*10);
    }
    const FQuat Rotation=Body->GetComponentQuat().Inverse()*Hammer->GetComponentQuat();
    UE_LOG(LogTemp,Display,TEXT("BOSSLAB bellmesh move=%d age=%d torso=%d head=%d upper=%d forearm=%d hand=%d leg=%d zmin=%.1f zmax=%.1f left=%d right=%d fl=%d fr=%d flo=%.1f fhi=%.1f quat=%.5f,%.5f,%.5f,%.5f"),
        Move,Age,Torso,Head,Upper,Forearm,Hand,Leg,MinCore==MAX_flt ? -1.f : MinCore,MaxCore==-MAX_flt ? -1.f : MaxCore,LeftHand,RightHand,ForearmL,ForearmR,Forearm ? MinForearm : -1.f,Forearm ? MaxForearm : -1.f,Rotation.X,Rotation.Y,Rotation.Z,Rotation.W);
}
#endif
