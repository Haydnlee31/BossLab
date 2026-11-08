// Opt-in transfer of actual Blender V13 geometry. Rigid attachment trial, not a production skin/cloth rig.
#include "WardenPrototype.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "PhysicsEngine/BodySetup.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "MeshDescription.h"
#include "StaticMeshAttributes.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

namespace V13Trial
{
struct FMaterial { FString Name; FLinearColor Color; float Roughness,Metallic; };
struct FFace { int32 A,B,C,M; };
struct FPart { FString Name,Bone,Child; FVector Origin,Axis; bool ScaleLength=true; TArray<FVector> V,N; TArray<FVector2f> UV; TArray<FFace> F; };
struct FData { FString Hash; TArray<FMaterial> Materials; TArray<FPart> Parts; int32 Triangles=0; };
FVector ToMesh(FVector P) { return FVector(-P.Y,P.X,P.Z); }
FVector FromMesh(FVector P) { return FVector(P.Y,-P.X,P.Z); }
bool Number(const TSharedPtr<FJsonValue>& V,double& X) { return V.IsValid() && V->TryGetNumber(X) && FMath::IsFinite(X); }
bool Vector(const TSharedPtr<FJsonValue>& Value,FVector& Out)
{
    const TArray<TSharedPtr<FJsonValue>>* A=nullptr;
    double X,Y,Z;
    if(!Value.IsValid() || !Value->TryGetArray(A) || A->Num()!=3 || !Number((*A)[0],X) || !Number((*A)[1],Y) || !Number((*A)[2],Z)) return false;
    Out=FVector(X,Y,Z); return Out.GetAbsMax()<10000;
}
bool Load(const FString& Path,FData& Data,FString& Error)
{
    const int64 Bytes=IFileManager::Get().FileSize(*Path);
    if(Bytes<=0 || Bytes>64*1024*1024) { Error=TEXT("missing or oversized export"); return false; }
    FString Json; TSharedPtr<FJsonObject> Root;
    if(!FFileHelper::LoadFileToString(Json,*Path) || !FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Json),Root) || !Root.IsValid()) { Error=TEXT("invalid JSON"); return false; }
    double Schema=0; const TArray<TSharedPtr<FJsonValue>> *Materials=nullptr,*Parts=nullptr;
    if(!Root->TryGetNumberField(TEXT("schema"),Schema) || Schema!=1 || !Root->TryGetStringField(TEXT("source_scene_sha256"),Data.Hash) || Data.Hash.Len()!=64 || !Root->TryGetArrayField(TEXT("materials"),Materials) || Materials->IsEmpty() || Materials->Num()>32 || !Root->TryGetArrayField(TEXT("parts"),Parts) || Parts->IsEmpty() || Parts->Num()>64) { Error=TEXT("schema/material/part bounds"); return false; }
    for(const auto& Value:*Materials)
    {
        const TSharedPtr<FJsonObject>* O=nullptr; FVector Color; FMaterial M; double Roughness,Metallic;
        if(!Value->TryGetObject(O) || !(*O)->TryGetStringField(TEXT("name"),M.Name) || !Vector((*O)->TryGetField(TEXT("color")),Color) || !(*O)->TryGetNumberField(TEXT("roughness"),Roughness) || !(*O)->TryGetNumberField(TEXT("metallic"),Metallic) || !FMath::IsFinite(Roughness) || !FMath::IsFinite(Metallic)) { Error=TEXT("material record"); return false; }
        M.Color=FLinearColor(FMath::Clamp(float(Color.X),0.f,1.f),FMath::Clamp(float(Color.Y),0.f,1.f),FMath::Clamp(float(Color.Z),0.f,1.f));
        M.Roughness=FMath::Clamp(float(Roughness),.04f,1.f); M.Metallic=FMath::Clamp(float(Metallic),0.f,1.f); Data.Materials.Add(M);
    }
    int32 TotalVertices=0;
    for(const auto& Value:*Parts)
    {
        const TSharedPtr<FJsonObject>* O=nullptr; const TArray<TSharedPtr<FJsonValue>> *Vertices=nullptr,*Normals=nullptr,*UVs=nullptr,*Faces=nullptr; FPart P;
        if(!Value->TryGetObject(O) || !(*O)->TryGetStringField(TEXT("name"),P.Name) || !(*O)->TryGetStringField(TEXT("bone"),P.Bone) || !Vector((*O)->TryGetField(TEXT("source_origin")),P.Origin) || !Vector((*O)->TryGetField(TEXT("source_axis")),P.Axis) || !(*O)->TryGetArrayField(TEXT("vertices"),Vertices) || !(*O)->TryGetArrayField(TEXT("triangles"),Faces) || Vertices->IsEmpty() || Faces->IsEmpty()) { Error=TEXT("part record"); return false; }
        (*O)->TryGetStringField(TEXT("target_child"),P.Child); (*O)->TryGetBoolField(TEXT("scale_length"),P.ScaleLength);
        TotalVertices+=Vertices->Num(); Data.Triangles+=Faces->Num();
        if(TotalVertices>300000 || Data.Triangles>150000) { Error=TEXT("geometry budget"); return false; }
        for(const auto& V:*Vertices) { FVector X; if(!Vector(V,X)) { Error=TEXT("nonfinite vertex"); return false; } P.V.Add(X); }
        if((*O)->TryGetArrayField(TEXT("normals"),Normals) && Normals->Num()==Vertices->Num()) for(const auto& V:*Normals) { FVector X; if(!Vector(V,X)) { Error=TEXT("normal record"); return false; } P.N.Add(X.GetSafeNormal()); }
        if((*O)->TryGetArrayField(TEXT("uvs"),UVs) && UVs->Num()==Vertices->Num()) for(const auto& V:*UVs)
        {
            const TArray<TSharedPtr<FJsonValue>>* A=nullptr; double U,W;
            if(!V->TryGetArray(A) || A->Num()!=2 || !Number((*A)[0],U) || !Number((*A)[1],W)) { Error=TEXT("UV record"); return false; }
            P.UV.Add(FVector2f(U,W));
        }
        for(const auto& V:*Faces)
        {
            const TArray<TSharedPtr<FJsonValue>>* A=nullptr; double X[4];
            if(!V->TryGetArray(A) || A->Num()!=4) { Error=TEXT("face record"); return false; }
            for(int32 I=0;I<4;++I) if(!Number((*A)[I],X[I]) || X[I]!=FMath::FloorToDouble(X[I]) || X[I]<0 || X[I]>(I==3?Data.Materials.Num()-1:P.V.Num()-1)) { Error=TEXT("face index"); return false; }
            P.F.Add({int32(X[0]),int32(X[1]),int32(X[2]),int32(X[3])});
        }
        Data.Parts.Add(MoveTemp(P));
    }
    return true;
}
}

bool AWardenChallenger::DressV13()
{
    using namespace V13Trial;
    FString Path;
    if(!FParse::Value(FCommandLine::Get(),TEXT("BossLabV13="),Path)) return false;
    if(bV13Outfit) return true;
    static FString CachedPath; static TSharedPtr<FData> Cached;
    if(!Cached.IsValid() || CachedPath!=Path)
    {
        auto Candidate=MakeShared<FData>(); FString Error;
        if(!Load(Path,*Candidate,Error)) { UE_LOG(LogTemp,Warning,TEXT("V13 trial unavailable (%s): %s; original outfit retained"),*Error,*Path); return false; }
        Cached=Candidate; CachedPath=Path;
    }
    const FData& Data=*Cached;
    const auto& Ref=VisualBody->GetSkinnedAsset()->GetRefSkeleton();
    TArray<FTransform> CS=Ref.GetRefBonePose(); for(int32 I=1;I<CS.Num();++I) CS[I]=CS[I]*CS[Ref.GetParentIndex(I)];
    for(const auto& P:Data.Parts) if(P.Bone!=TEXT("sword") && (Ref.FindBoneIndex(FName(P.Bone))<0 || (!P.Child.IsEmpty() && Ref.FindBoneIndex(FName(P.Child))<0)))
    { UE_LOG(LogTemp,Warning,TEXT("V13 trial unknown bone %s/%s; original outfit retained"),*P.Bone,*P.Child); return false; }
    auto* Parent=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/BossLab/Materials/M_WardenSurface"));
    if(!Parent) return false;
    TArray<UMaterialInterface*> Materials;
    for(int32 I=0;I<Data.Materials.Num();++I)
    {
        const auto& M=Data.Materials[I]; auto* Material=UMaterialInstanceDynamic::Create(Parent,this,FName(FString::Printf(TEXT("V13Material%d"),I)));
        Material->SetVectorParameterValue(TEXT("Color"),M.Color); Material->SetVectorParameterValue(TEXT("Glow"),FLinearColor::Black);
        Material->SetScalarParameterValue(TEXT("Roughness"),M.Roughness); Material->SetScalarParameterValue(TEXT("Metallic"),M.Metallic); Materials.Add(Material);
    }
    TArray<UStaticMeshComponent*> Built;
    for(int32 PartIndex=0;PartIndex<Data.Parts.Num();++PartIndex)
    {
        const auto& P=Data.Parts[PartIndex]; const bool Sword=P.Bone==TEXT("sword"),Cape=P.Name.Contains(TEXT("cape"),ESearchCase::IgnoreCase);
        const int32 BI=Sword?0:Ref.FindBoneIndex(FName(P.Bone));
        const FVector Origin=Sword?FVector::ZeroVector:FromMesh(CS[BI].GetLocation());
        FQuat Align=FQuat::Identity; double LengthScale=1; const FVector Axis=P.Axis.GetSafeNormal();
        if(!Sword && !P.Child.IsEmpty())
        {
            const FVector BoneDelta=FromMesh(CS[Ref.FindBoneIndex(FName(P.Child))].GetLocation())-Origin;
            Align=FQuat::FindBetweenNormals(Axis,BoneDelta.GetSafeNormal());
            if(P.ScaleLength && P.Axis.Size()>.01) LengthScale=FMath::Clamp(BoneDelta.Size()/P.Axis.Size(),.5,2.);
        }
        auto Fit=[&](FVector V)
        {
            if(Sword) return V;
            FVector D=V-P.Origin; D+=Axis*(FVector::DotProduct(D,Axis)*(LengthScale-1));
            const FVector World=Origin+Align.RotateVector(D);
            return Cape?World-Origin:CS[BI].InverseTransformPosition(ToMesh(World));
        };
        auto FitNormal=[&](FVector N)
        {
            if(Sword) return N;
            N+=Axis*(FVector::DotProduct(N,Axis)*(1/LengthScale-1)); N=Align.RotateVector(N).GetSafeNormal();
            return Cape?N:CS[BI].InverseTransformVectorNoScale(ToMesh(N)).GetSafeNormal();
        };
        FMeshDescription Desc; FStaticMeshAttributes Attr(Desc); Attr.Register();
        auto Positions=Attr.GetVertexPositions(); auto Normals=Attr.GetVertexInstanceNormals(); auto Tangents=Attr.GetVertexInstanceTangents(); auto Signs=Attr.GetVertexInstanceBinormalSigns(); auto UV=Attr.GetVertexInstanceUVs(); UV.SetNumChannels(1); auto Colors=Attr.GetVertexInstanceColors();
        TArray<FVertexID> VIDs; FBox Bounds(ForceInit);
        for(auto V:P.V) { const auto ID=Desc.CreateVertex(); const FVector Fitted=Fit(V); Positions[ID]=FVector3f(Fitted); VIDs.Add(ID); Bounds+=Fitted; }
        TMap<int32,FPolygonGroupID> Groups;
        for(const auto& Face:P.F)
        {
            const FVector A(Positions[VIDs[Face.A]]),B(Positions[VIDs[Face.B]]),C(Positions[VIDs[Face.C]]);
            const FVector FaceNormal=FVector::CrossProduct(B-A,C-A).GetSafeNormal(); if(FaceNormal.IsNearlyZero()) continue;
            if(!Groups.Contains(Face.M)) { const auto G=Desc.CreatePolygonGroup(); Groups.Add(Face.M,G); Attr.GetPolygonGroupMaterialSlotNames()[G]=FName(FString::Printf(TEXT("V13Slot%d"),Face.M)); }
            TArray<FVertexInstanceID> Instances;
            for(int32 I:{Face.A,Face.C,Face.B})
            {
                const auto ID=Desc.CreateVertexInstance(VIDs[I]); Instances.Add(ID);
                FVector N=P.N.IsValidIndex(I)?FitNormal(P.N[I]):FaceNormal; if(N.IsNearlyZero()) N=FaceNormal;
                Normals[ID]=FVector3f(N); FVector T=FVector::CrossProduct(N,FVector::UpVector).GetSafeNormal(); if(T.IsNearlyZero()) T=FVector::ForwardVector;
                Tangents[ID]=FVector3f(T); Signs[ID]=1; Colors[ID]=FVector4f(1,1,1,1);
                UV.Set(ID,0,P.UV.IsValidIndex(I)?P.UV[I]:FVector2f(P.V[I].Y*.02,P.V[I].Z*.02));
            }
            Desc.CreatePolygon(Groups[Face.M],Instances);
        }
        const FName Name(FString::Printf(TEXT("V13_%02d_%s"),PartIndex,*P.Bone));
        auto* Mesh=NewObject<UStaticMesh>(this,FName(Name.ToString()+TEXT("Mesh")));
        for(int32 I=0;I<Materials.Num();++I) { FStaticMaterial Slot(Materials[I],FName(FString::Printf(TEXT("V13Slot%d"),I))); Slot.UVChannelData=FMeshUVChannelInfo(50.f); Mesh->GetStaticMaterials().Add(Slot); }
#if WITH_EDITOR
        for(auto Pair:Groups) { FMeshSectionInfo Info(Pair.Key); Info.bEnableCollision=false; Mesh->GetSectionInfoMap().Set(0,Pair.Value.GetValue(),Info); }
#endif
        Mesh->CreateBodySetup(); Mesh->GetBodySetup()->CollisionTraceFlag=CTF_UseSimpleAsComplex; Mesh->GetBodySetup()->bNeverNeedsCookedCollisionData=true;
        UStaticMesh::FBuildMeshDescriptionsParams Params; Params.bAllowCpuAccess=true; Params.bFastBuild=true; Params.bBuildSimpleCollision=false; Params.bMarkPackageDirty=false; Params.bCommitMeshDescription=false;
        if(!Mesh->BuildFromMeshDescriptions({&Desc},Params))
        {
            for(auto* C:Built) { C->DestroyComponent(); RemoveInstanceComponent(C); }
            CapePanels.Reset(); CapeRest.Reset(); OutfitSupport.Reset(); OutfitTriangles=0;
            UE_LOG(LogTemp,Warning,TEXT("V13 mesh build failed; original outfit retained")); return false;
        }
        auto* Part=NewObject<UStaticMeshComponent>(this,Name); Part->SetStaticMesh(Mesh); Part->SetCollisionEnabled(ECollisionEnabled::NoCollision); Part->SetCanEverAffectNavigation(false);
        Part->ComponentTags.Add(TEXT("V13Trial")); Part->ComponentTags.Add(FName(P.Name)); Part->SetupAttachment(Sword?SwordRoot.Get():VisualBody.Get(),Sword?NAME_None:FName(P.Bone));
        if(Cape) Part->SetRelativeRotation(CS[BI].GetRotation().Inverse()*FRotator(0,90,0).Quaternion());
        Part->RegisterComponent(); AddInstanceComponent(Part); Built.Add(Part);
        if(Cape) { CapePanels.Add(Part); CapeRest.Add(Part->GetRelativeTransform()); }
        FWardenOutfitSupport Support; Support.Part=Part;
        // Eight conservative box corners replace per-frame scans of ~120k imported vertices.
        for(int32 I=0;I<8;++I) Support.Vertices.Add(FVector((I&1)?Bounds.Max.X:Bounds.Min.X,(I&2)?Bounds.Max.Y:Bounds.Min.Y,(I&4)?Bounds.Max.Z:Bounds.Min.Z));
        OutfitSupport.Add(MoveTemp(Support)); OutfitTriangles+=P.F.Num();
    }
    bV13Outfit=true; V13SourceHash=Data.Hash;
    UE_LOG(LogTemp,Display,TEXT("V13 actual Blender trial loaded: source=%s parts=%d triangles=%d; rigid attachments, palette-only material transfer, no production cloth/rig"),*Data.Hash,Built.Num(),OutfitTriangles);
    return true;
}
