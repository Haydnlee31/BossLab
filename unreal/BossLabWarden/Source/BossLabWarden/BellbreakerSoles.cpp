#include "BellbreakerSoles.h"
#include "Components/PoseableMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "Rendering/SkeletalMeshLODRenderData.h"
#include "Rendering/SkinWeightVertexBuffer.h"

void FBellbreakerSoles::Fit(UPoseableMeshComponent* Body)
{
    Samples.Reset();
    const auto* Data=Body->GetSkeletalMeshRenderData();
    if(!Data || !Data->LODRenderData.IsValidIndex(0)) return;
    const auto& LOD=Data->LODRenderData[0];
    const auto& Positions=LOD.StaticVertexBuffers.PositionVertexBuffer;
    const auto* Weights=Body->GetSkinWeightBuffer(0);
    if(!Weights || !Weights->GetDataVertexBuffer()->GetWeightData() || !Positions.GetVertexData()) return;

    FBox Box(ForceInit);
    for(uint32 I=0;I<Positions.GetNumVertices();++I)
    {
        const FVector P(Positions.VertexPosition(I));
        if(P.Z<=8.) Box+=P;
    }
    if(!Box.IsValid) return;
    // Both soles occupy the lowest eight bind-space centimetres. Cover toe,
    // midsole, heel and edges so a tilted boot can rock onto its tread.
    constexpr int Cols=12, Rows=10;
    int32 Index[Rows*Cols];
    for(int32& Cell:Index) Cell=INDEX_NONE;
    for(uint32 I=0;I<Positions.GetNumVertices();++I)
    {
        const FVector P(Positions.VertexPosition(I));
        if(P.Z>8.) continue;
        const int X=FMath::Clamp(int((P.X-Box.Min.X)*Cols/FMath::Max(1.,Box.GetSize().X)),0,Cols-1);
        const int Y=FMath::Clamp(int((P.Y-Box.Min.Y)*Rows/FMath::Max(1.,Box.GetSize().Y)),0,Rows-1);
        int32& Best=Index[Y*Cols+X];
        if(Best==INDEX_NONE || P.Z<Positions.VertexPosition(Best).Z) Best=I;
    }
    const auto& Ref=Body->GetSkinnedAsset()->GetRefSkeleton();
    const int32 Left=Ref.FindBoneIndex(TEXT("thigh_l")), Right=Ref.FindBoneIndex(TEXT("thigh_r"));
    TArray<FTransform> Bind=Ref.GetRefBonePose();
    for(int I=1;I<Bind.Num();++I) Bind[I]*=Bind[Ref.GetParentIndex(I)];
    for(const int32 I:Index)
    {
        if(I==INDEX_NONE) continue;
        int Section,LocalIndex;
        LOD.GetSectionFromVertexIndex(I,Section,LocalIndex);
        const auto& Bones=LOD.RenderSections[Section].BoneMap;
        FSample Sample;
        float Total=0;
        for(int J=0;J<Weights->GetMaxBoneInfluences();++J)
        {
            const float Weight=Weights->GetBoneWeight(I,J);
            if(Weight<=0) continue;
            const int Bone=Bones[Weights->GetBoneIndex(I,J)];
            Sample.Influences.Add({Bone,Weight,Bind[Bone].InverseTransformPosition(FVector(Positions.VertexPosition(I)))});
            Total+=Weight;
        }
        if(Total<=0) continue;
        float LeftWeight=0,RightWeight=0;
        for(auto& Entry:Sample.Influences)
        {
            Entry.Weight/=Total;
            int32 Ancestor=Entry.Bone;
            while(Ancestor>=0 && Ancestor!=Left && Ancestor!=Right) Ancestor=Ref.GetParentIndex(Ancestor);
            if(Ancestor>=0 && Ancestor==Left) LeftWeight+=Entry.Weight;
            if(Ancestor>=0 && Ancestor==Right) RightWeight+=Entry.Weight;
        }
        if(LeftWeight>.5f) Sample.Thigh=Left;
        if(RightWeight>.5f) Sample.Thigh=Right;
        Samples.Add(MoveTemp(Sample));
    }
}

bool FBellbreakerSoles::Lowest(const TArray<FTransform>& Pose,double& Height,int32 Thigh) const
{
    Height=DBL_MAX;
    for(const auto& Sample:Samples)
    {
        if(Thigh!=INDEX_NONE && Thigh!=Sample.Thigh) continue;
        double Z=0;
        for(const auto& Entry:Sample.Influences)
            Z+=Entry.Weight*Pose[Entry.Bone].TransformPosition(Entry.Point).Z;
        Height=FMath::Min(Height,Z);
    }
    return Height<DBL_MAX;
}
