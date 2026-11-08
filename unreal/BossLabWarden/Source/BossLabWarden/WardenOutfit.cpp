// Original Ashbound Knight polygon model. Units are centimeters; no imported art.
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

namespace Ashbound
{
struct FFace { int32 A,B,C,Material; };
struct FShape
{
    TArray<FVector> V; TArray<FFace> F;
    int32 Point(FVector P) { return V.Add(P); }
    void Tri(int32 A,int32 B,int32 C,int32 M) { F.Add({A,B,C,M}); }
    void Quad(int32 A,int32 B,int32 C,int32 D,int32 M) { Tri(A,B,C,M); Tri(A,C,D,M); }
    // Ring-loft supports shaped plate cross sections, not scaled engine primitives.
    void Loft(const TArray<FVector>& Centers,const TArray<FVector2D>& Radii,FVector U,FVector W,int32 M,int32 N=24)
    {
        const int32 Base=V.Num(), FirstFace=F.Num();
        for(int32 J=0;J<Centers.Num();++J)
            for(int32 I=0;I<N;++I)
            {
                const float A=I*2*PI/N;
                Point(Centers[J]+U*(Radii[J].X*FMath::Cos(A))+W*(Radii[J].Y*FMath::Sin(A)));
            }
        for(int32 J=0;J<Centers.Num()-1;++J) for(int32 I=0;I<N;++I)
            Quad(Base+J*N+I,Base+J*N+(I+1)%N,Base+(J+1)*N+(I+1)%N,Base+(J+1)*N+I,M);
        const int32 Bottom=Point(Centers[0]),Top=Point(Centers.Last());
        for(int32 I=0;I<N;++I) { Tri(Bottom,Base+(I+1)%N,Base+I,M); Tri(Top,Base+(Centers.Num()-1)*N+I,Base+(Centers.Num()-1)*N+(I+1)%N,M); }
        if(FVector::DotProduct(FVector::CrossProduct(U,W),Centers.Last()-Centers[0])<0)
            for(int32 I=FirstFace;I<F.Num();++I) Swap(F[I].B,F[I].C);
    }
    void Vertical(FVector C,const TArray<FVector>& Profile,int32 M,int32 N=24)
    {
        TArray<FVector> Centers; TArray<FVector2D> Radii;
        for(auto P:Profile) { Centers.Add(C+FVector(0,0,P.Z)); Radii.Add(FVector2D(P.X,P.Y)); }
        Loft(Centers,Radii,FVector::ForwardVector,FVector::RightVector,M,N);
    }
    void Tube(FVector A,FVector B,float R0,float R1,int32 M,int32 N=8)
    {
        const FVector Axis=(B-A).GetSafeNormal();
        FVector U=FVector::CrossProduct(Axis,FVector::UpVector).GetSafeNormal();
        if(U.IsNearlyZero()) U=FVector::ForwardVector;
        Loft({A,B},{{R0,R0},{R1,R1}},U,FVector::CrossProduct(Axis,U),M,N);
    }
    void Ring(FVector C,FVector U,FVector W,float Radius,float Thickness,float Start,float End,int32 M)
    {
        for(int32 I=0;I<24;++I)
        {
            const float A=FMath::Lerp(Start,End,I/24.f), B=FMath::Lerp(Start,End,(I+1)/24.f);
            Tube(C+(U*FMath::Cos(A)+W*FMath::Sin(A))*Radius,C+(U*FMath::Cos(B)+W*FMath::Sin(B))*Radius,Thickness,Thickness,M,6);
        }
    }
};
FVector ToMesh(FVector P) { return FVector(-P.Y,P.X,P.Z); }
FVector FromMesh(FVector P) { return FVector(P.Y,-P.X,P.Z); }
}

void AWardenChallenger::DressAshbound()
{
    using namespace Ashbound;
    if(FindObject<UStaticMeshComponent>(this,TEXT("AshHelmet")))
    {
        // Reset recolors the underlayer without constructing duplicate meshes.
        auto* Existing=FindObject<UMaterialInstanceDynamic>(this,TEXT("AshUnderlayer"));
        if(Existing) for(int32 I=0;I<VisualBody->GetNumMaterials();++I) VisualBody->SetMaterial(I,Existing);
        return;
    }
    auto* Parent=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/BossLab/Materials/M_WardenSurface"));
    TArray<UMaterialInterface*> Materials;
    const FLinearColor Colors[]={FLinearColor(.30,.34,.37),FLinearColor(.25,.15,.055),FLinearColor(.11,.018,.023),FLinearColor(.52,.46,.34),FLinearColor(.018,.023,.028)};
    const TCHAR* Names[]={TEXT("AshSteel"),TEXT("AshBronze"),TEXT("AshOxblood"),TEXT("AshIvory"),TEXT("AshUnderlayer")};
    const float Roughness[]={.38f,.48f,.92f,.94f,.85f};
    for(int32 I=0;I<5;++I)
    {
        auto* Mat=UMaterialInstanceDynamic::Create(Parent,this,FName(Names[I]));
        Mat->SetVectorParameterValue(TEXT("Color"),Colors[I]); Mat->SetVectorParameterValue(TEXT("Glow"),FLinearColor::Black);
        Mat->SetScalarParameterValue(TEXT("Roughness"),Roughness[I]); Mat->SetScalarParameterValue(TEXT("Metallic"),I<2?.83f:0.f);
        Materials.Add(Mat);
    }
    for(int32 I=0;I<VisualBody->GetNumMaterials();++I) VisualBody->SetMaterial(I,Materials[4]);
    const auto& Ref=VisualBody->GetSkinnedAsset()->GetRefSkeleton();
    TArray<FTransform> CS=Ref.GetRefBonePose();
    for(int32 I=1;I<CS.Num();++I) CS[I]=CS[I]*CS[Ref.GetParentIndex(I)];
    auto Bone=[&](const TCHAR* Name) { const int32 I=Ref.FindBoneIndex(FName(Name)); check(I>=0); return FromMesh(CS[I].GetLocation()); };
    const bool Export=FParse::Param(FCommandLine::Get(),TEXT("BossLabExportOutfit"));
    FString Obj=TEXT("# BossLab original Ashbound Knight reference-pose assembly, centimeters, Z-up.\nmtllib ashbound.mtl\n");
    int32 ObjIndex=1;
    auto Add=[&](const TCHAR* Name,const TCHAR* Joint,FShape& Shape,bool Sword=false)
    {
        const int32 BoneIndex=Sword?0:Ref.FindBoneIndex(FName(Joint));
        const bool Cloth=FString(Name).StartsWith(TEXT("AshCape"));
        FMeshDescription Desc; FStaticMeshAttributes Attr(Desc); Attr.Register();
        auto Positions=Attr.GetVertexPositions(); auto Normals=Attr.GetVertexInstanceNormals();
        auto Tangents=Attr.GetVertexInstanceTangents(); auto Signs=Attr.GetVertexInstanceBinormalSigns();
        auto UV=Attr.GetVertexInstanceUVs(); UV.SetNumChannels(1);
        auto Color=Attr.GetVertexInstanceColors();
        TArray<FVertexID> Vertices;
        for(auto V:Shape.V) Vertices.Add(Desc.CreateVertex());
        for(int32 I=0;I<Shape.V.Num();++I) Positions[Vertices[I]]=FVector3f(Sword?Shape.V[I]:Cloth?Shape.V[I]-FromMesh(CS[BoneIndex].GetLocation()):CS[BoneIndex].InverseTransformPosition(ToMesh(Shape.V[I])));
        TMap<int32,FPolygonGroupID> Groups;
        for(const auto& Face:Shape.F)
        {
            if(!Groups.Contains(Face.Material))
            {
                const auto G=Desc.CreatePolygonGroup(); Groups.Add(Face.Material,G);
                Attr.GetPolygonGroupMaterialSlotNames()[G]=FName(Names[Face.Material]);
            }
            const FVector A(Positions[Vertices[Face.A]]),B(Positions[Vertices[Face.B]]),C(Positions[Vertices[Face.C]]);
            const FVector N=FVector::CrossProduct(B-A,C-A).GetSafeNormal();
            if(N.IsNearlyZero()) continue;
            TArray<FVertexInstanceID> Instances;
            // Unreal fronts use clockwise winding; retain the outward normal.
            for(int32 K:{Face.A,Face.C,Face.B})
            {
                const auto Id=Desc.CreateVertexInstance(Vertices[K]); Instances.Add(Id);
                Normals[Id]=FVector3f(N); Tangents[Id]=FVector3f((B-A).GetSafeNormal()); Signs[Id]=1;
                UV.Set(Id,0,FVector2f(Shape.V[K].Y*.02,Shape.V[K].Z*.02)); Color[Id]=FVector4f(1,1,1,1);
            }
            Desc.CreatePolygon(Groups[Face.Material],Instances);
        }
        auto* Mesh=NewObject<UStaticMesh>(this,FName(FString(Name)+TEXT("Mesh")));
        for(int32 I=0;I<5;++I)
        {
            FStaticMaterial Slot(Materials[I],FName(Names[I]));
            Slot.UVChannelData=FMeshUVChannelInfo(50.f); // .02 UV/cm; no texture maps in this pass.
            Mesh->GetStaticMaterials().Add(Slot);
        }
        // Editor InitResources resolves section indices through this map. Populate it
        // before fast-build so single-material cloth cannot silently become slot zero.
#if WITH_EDITOR
        for(auto Pair:Groups) { FMeshSectionInfo Info(Pair.Key); Info.bEnableCollision=false; Mesh->GetSectionInfoMap().Set(0,Pair.Value.GetValue(),Info); }
#endif
        Mesh->CreateBodySetup();
        Mesh->GetBodySetup()->CollisionTraceFlag=CTF_UseSimpleAsComplex;
        Mesh->GetBodySetup()->bNeverNeedsCookedCollisionData=true;
        UStaticMesh::FBuildMeshDescriptionsParams Params; Params.bAllowCpuAccess=true; Params.bFastBuild=true; Params.bBuildSimpleCollision=false; Params.bMarkPackageDirty=false; Params.bCommitMeshDescription=false;
        check(Mesh->BuildFromMeshDescriptions({&Desc},Params));
        auto* Part=NewObject<UStaticMeshComponent>(this,FName(Name)); Part->SetStaticMesh(Mesh);
        Part->ComponentTags.Add(TEXT("Ashbound")); Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Part->SetCanEverAffectNavigation(false); Part->SetupAttachment(Sword?SwordRoot.Get():VisualBody.Get(),Sword?NAME_None:FName(Joint));
        if(Cloth) Part->SetRelativeRotation(CS[BoneIndex].GetRotation().Inverse()*FRotator(0,90,0).Quaternion());
        Part->RegisterComponent(); AddInstanceComponent(Part);
        FWardenOutfitSupport Support; Support.Part=Part;
        for(auto Id:Vertices) Support.Vertices.Add(FVector(Positions[Id]));
        OutfitSupport.Add(MoveTemp(Support));
        OutfitTriangles+=Shape.F.Num();
        if(Export)
        {
            Obj+=FString::Printf(TEXT("o %s\n"),Name);
            for(auto P:Shape.V) { if(Sword) P+=FVector(85,0,35); Obj+=FString::Printf(TEXT("v %.5f %.5f %.5f\n"),P.X,P.Y,P.Z); }
            int32 Last=-1;
            for(auto F:Shape.F)
            {
                if(Last!=F.Material) { Last=F.Material; Obj+=FString::Printf(TEXT("usemtl %s\n"),Names[Last]); }
                Obj+=FString::Printf(TEXT("f %d %d %d\n"),ObjIndex+F.A,ObjIndex+F.B,ObjIndex+F.C);
            }
            ObjIndex+=Shape.V.Num();
        }
        return Part;
    };
    const FVector Head=Bone(TEXT("head")),Chest=Bone(TEXT("spine_05")),Waist=Bone(TEXT("pelvis"));
    FShape Helmet;
    Helmet.Vertical(Head,{{8,8,-2},{10,10,2},{10.8,10.2,8}},0,32);
    Helmet.Vertical(Head,{{11,10.4,10},{11.3,10.2,16},{8.8,8.2,22},{.6,.6,25}},0,32);
    Helmet.Tube(Head+FVector(11.4,0,11),Head+FVector(8.7,0,23),.7,.5,1);
    // Dark inset below brow reads as an eye slit; no glowing eye effect.
    Helmet.Tube(Head+FVector(10.5,-7,9),Head+FVector(10.5,7,9),.7,.7,4);
    Add(TEXT("AshHelmet"),TEXT("head"),Helmet);
    FShape Crest;
    for(int32 I=0;I<8;++I)
    {
        FVector P=Head+FVector(-4-I*.65,0,24-I*.6);
        Crest.Loft({P,P+FVector(-3,0,4),P+FVector(-7,0,1)},{{1.8,1.1},{1.4,.6},{.1,.1}},FVector::ForwardVector,FVector::RightVector,3,8);
    }
    Add(TEXT("AshCrest"),TEXT("head"),Crest);
    FShape Breast;
    Breast.Vertical(Chest,{{9.8,15,-14},{12.5,20,-7},{13.5,21,3},{10,16,13}},0,32);
    Breast.Tube(Chest+FVector(12.8,0,-12),Chest+FVector(14,0,6),.6,.6,1);
    Breast.Ring(Chest+FVector(12,0,9),FVector::RightVector,FVector::UpVector,3.3,.55,.3f,5.7f,1);
    for(int32 Side:{-1,1}) Breast.Tube(Chest+FVector(9,Side*13,10),Chest+FVector(13,Side*10,0),.65,.65,1);
    Add(TEXT("AshBreastplate"),TEXT("spine_05"),Breast);
    FShape Abdomen;
    const FVector Mid=Bone(TEXT("spine_01"));
    for(int32 I=0;I<3;++I) Abdomen.Vertical(Mid+FVector(0,0,I*5),{{10.8,14.8,-2},{11.6,16,0},{10.8,15,3.2}},0,24);
    Add(TEXT("AshAbdominalLames"),TEXT("spine_01"),Abdomen);
    FShape Belt; Belt.Vertical(Waist,{{10,15,0},{11.2,16.3,1},{11.2,16.3,6},{10,15,7}},4,28);
    Belt.Ring(Waist+FVector(11.5,0,3.5),FVector::RightVector,FVector::UpVector,2.2,.65,.3,5.8,1);
    Add(TEXT("AshBelt"),TEXT("pelvis"),Belt);
    FShape Mantle;
    // Sculpted tapered locks, merged into one mesh; no strand simulation/alpha overdraw.
    for(int32 I=0;I<32;++I)
    {
        const float A=.4f+I*(2*PI-.8f)/31;
        const FVector Radial(FMath::Cos(A),FMath::Sin(A),0);
        const FVector P=Chest+FVector(0,0,16)+Radial*FVector(11,18,1);
        const float Drop=5+(I%4)*1.8f;
        Mantle.Loft({P,P+Radial*3+FVector(0,0,-4),P+Radial*5+FVector(0,0,-Drop-6)},{{3.5,3},{3.3,2.4},{.12,.12}},Radial,FVector::CrossProduct(FVector::UpVector,Radial),3,8);
    }
    Add(TEXT("AshIvoryMantle"),TEXT("spine_05"),Mantle);
    for(int32 Side:{-1,1})
    {
        const bool Left=Side==-1; const TCHAR* Upper=Left?TEXT("upperarm_l"):TEXT("upperarm_r");
        const TCHAR* Lower=Left?TEXT("lowerarm_l"):TEXT("lowerarm_r"); const TCHAR* Hand=Left?TEXT("hand_l"):TEXT("hand_r");
        const TCHAR* Thigh=Left?TEXT("thigh_l"):TEXT("thigh_r"); const TCHAR* Calf=Left?TEXT("calf_l"):TEXT("calf_r"); const TCHAR* Foot=Left?TEXT("foot_l"):TEXT("foot_r");
        auto Sleeve=[&](const TCHAR* Name,const TCHAR* Joint,const TCHAR* End,float Start,float Finish,float R0,float R1)
        {
            const FVector A=Bone(Joint),B=Bone(End),Axis=(B-A).GetSafeNormal();
            const FVector U=FVector::VectorPlaneProject(FVector::ForwardVector,Axis).GetSafeNormal();
            const FVector V=FVector::CrossProduct(Axis,U);
            FShape S; S.Loft({FMath::Lerp(A,B,Start),FMath::Lerp(A,B,Start+.07f),FMath::Lerp(A,B,Finish-.05f),FMath::Lerp(A,B,Finish)},{{R0*.88f,R0*.88f},{R0,R0},{R1,R1},{R1*.88f,R1*.88f}},U,V,0,20);
            S.Tube(FMath::Lerp(A,B,Start+.1f)+U*R0,FMath::Lerp(A,B,Finish-.1f)+U*R1,.45,.35,1,6);
            Add(Name,Joint,S);
        };
        Sleeve(Left?TEXT("AshPauldronL"):TEXT("AshPauldronR"),Upper,Lower,-.03,.36,Left?10.4:9.6,8.7);
        Sleeve(Left?TEXT("AshVambraceL"):TEXT("AshVambraceR"),Lower,Hand,.12,.86,6.5,4.6);
        Sleeve(Left?TEXT("AshCuissesL"):TEXT("AshCuissesR"),Thigh,Calf,.13,.74,9.8,7.5);
        Sleeve(Left?TEXT("AshGreaveL"):TEXT("AshGreaveR"),Calf,Foot,.12,.91,7.2,4.9);
        FShape Knee; Knee.Vertical(Bone(Calf)+FVector(4,0,0),{{3,4,-5},{5,6,0},{3,4,5}},0,16);
        Add(Left?TEXT("AshKneeL"):TEXT("AshKneeR"),Calf,Knee);
        FShape Boot; Boot.Vertical(Bone(Foot)+FVector(5,0,-1),{{12,5.7,-3},{13.2,6.3,-1},{12,5.8,4},{7,4.8,9}},0,24);
        Add(Left?TEXT("AshBootL"):TEXT("AshBootR"),Foot,Boot);
        FShape Glove; const FVector H=Bone(Hand),Finger=Bone(Left?TEXT("middle_01_l"):TEXT("middle_01_r"));
        const FVector Axis=(Finger-H).GetSafeNormal(),U=FVector::VectorPlaneProject(FVector::UpVector,Axis).GetSafeNormal();
        Glove.Loft({H+Axis*1,H+Axis*3,H+Axis*7},{{2.7,3.9},{3,4.1},{2.5,3.7}},U,FVector::CrossProduct(Axis,U),0,12);
        Add(Left?TEXT("AshGauntletL"):TEXT("AshGauntletR"),Hand,Glove);
        // Short overlapping waist textile, divided at the legs for roll clearance.
        FShape Tasset; const FVector ThighOrigin=Bone(Thigh);
        Tasset.Vertical(ThighOrigin+FVector(0,0,-4),{{10,11,4},{10.8,11.5,-1},{10.5,11,-14},{8.8,9,-19}},2,20);
        Add(Left?TEXT("AshTassetL"):TEXT("AshTassetR"),Thigh,Tasset);
        FShape Cape;
        // Broad curved panel with three longitudinal folds and an uneven hem.
        const int32 Rows=9,Cols=10;
        for(int32 R=0;R<Rows;++R) for(int32 C=0;C<Cols;++C)
        {
            const float T=R/float(Rows-1),U0=C/float(Cols-1);
            const float Y=Side*(2+U0*(15+5*T));
            const float X=-13-7*T-1.1f*FMath::Sin(U0*PI*6)*T;
            const float Z=13-77*T-2.5f*FMath::Sin(U0*PI*3)*T*T;
            Cape.Point(Chest+FVector(X,Y,Z));
        }
        for(int32 R=0;R<Rows-1;++R) for(int32 C=0;C<Cols-1;++C) Cape.Quad(R*Cols+C,R*Cols+C+1,(R+1)*Cols+C+1,(R+1)*Cols+C,2);
        auto* Panel=Add(Left?TEXT("AshCapeL"):TEXT("AshCapeR"),TEXT("spine_05"),Cape);
        CapePanels.Add(Panel); CapeRest.Add(Panel->GetRelativeTransform());
    }
    FShape Blade;
    Blade.Loft({FVector(0,0,14),FVector(0,0,22),FVector(0,0,116),FVector(0,0,132),FVector(0,0,148)},{{5.25,1.25},{5.25,1.25},{4.4,1.25},{3.6,1},{.025,.025}},FVector::ForwardVector,FVector::RightVector,0,4);
    Add(TEXT("OathwakeBlade"),TEXT(""),Blade,true);
    FShape Hilt;
    Hilt.Tube(FVector(0,0,-24),FVector(0,0,7),2.1,2.1,4,12);
    for(int32 I=0;I<12;++I) Hilt.Ring(FVector(0,0,-23+I*2.4f),FVector::ForwardVector,FVector::RightVector,2.15,.18,0,2*PI,1);
    Hilt.Ring(FVector(0,0,7),FVector::ForwardVector,FVector::UpVector,9,.9,.18,PI-.18,1);
    Hilt.Tube(FVector(-16,0,7),FVector(16,0,7),1.2,1.2,1,12);
    Hilt.Vertical(FVector(0,0,-27),{{2,2,-4},{3.7,2.5,-1},{3.7,2.5,2},{2,2,4}},1,12);
    // Sparse bronze channel ornament, safely inside the original blade envelope.
    for(int32 Side:{-1,1}) for(int32 I=0;I<7;++I)
    {
        const float Z=27+I*12;
        Hilt.Tube(FVector(-.65,Side*1.28,Z),FVector(.65,Side*1.28,Z+4),.16,.16,1,6);
    }
    Add(TEXT("OathwakeHilt"),TEXT(""),Hilt,true);
    if(Export)
    {
        const FString Dir=FPaths::Combine(FPaths::ProjectSavedDir(),TEXT("AshboundModel")); IFileManager::Get().MakeDirectory(*Dir,true);
        FFileHelper::SaveStringToFile(Obj,*FPaths::Combine(Dir,TEXT("ashbound.obj")));
        FString Mtl;
        for(int32 I=0;I<5;++I) Mtl+=FString::Printf(TEXT("newmtl %s\nKd %.4f %.4f %.4f\nKs .3 .3 .3\nNs %.1f\n\n"),Names[I],Colors[I].R,Colors[I].G,Colors[I].B,(1-Roughness[I])*150);
        FFileHelper::SaveStringToFile(Mtl,*FPaths::Combine(Dir,TEXT("ashbound.mtl")));
    }
    UE_LOG(LogTemp,Display,TEXT("Ashbound original outfit: %d triangles, %d cape panels; contact geometry unchanged"),OutfitTriangles,CapePanels.Num());
}

void AWardenChallenger::UpdateAshbound(const FVector& Travel)
{
    if(bBoss || CapePanels.IsEmpty()) return;
    OutfitClock+=WardenRules::Step;
    const float Speed=FMath::Clamp(float(Travel.Size2D()*60/540),0.f,1.f);
    // Cosmetic only: short rigid cloth panels with restrained sway, not cloth physics.
    // Fold close during a roll/death so tails do not remain extended through the floor.
    const float Tuck=Fight.Action==EWardenAction::Dodge?FMath::Sin(PI*FMath::Clamp(Fight.Age/36.f,0.f,1.f)):!Fight.Alive()?1.f:0.f;
    for(int32 I=0;I<CapePanels.Num();++I)
    {
        FTransform T=CapeRest[I];
        const float Sway=FMath::Sin(OutfitClock*4.2f+I*.7f)*(1.3f+Speed*3);
        T.SetRotation(T.GetRotation()*FQuat(FVector::UpVector,FMath::DegreesToRadians(Sway)));
        T.SetScale3D(FVector(1,1,1-.85f*Tuck));
        CapePanels[I]->SetRelativeTransform(T);
    }
    if(Fight.Action==EWardenAction::Dodge || Fight.Action==EWardenAction::Dead)
    {
        // Exact authored outfit support on this flat arena. Only the presentation
        // moves during non-attacking roll/death; capsule, timing and damage stay fixed.
        float Lowest=MAX_flt;
        for(const auto& Support:OutfitSupport) if(auto* Part=Support.Part.Get())
        {
            Part->UpdateComponentToWorld();
            const FTransform Transform=Part->GetComponentTransform();
            for(const FVector& V:Support.Vertices) Lowest=FMath::Min(Lowest,float(Transform.TransformPosition(V).Z));
        }
        const float Floor=GetActorLocation().Z-95*GetActorScale3D().Z;
        if(Lowest<Floor)
        {
            VisualBody->AddWorldOffset(FVector(0,0,Floor-Lowest));
            VisualBody->UpdateComponentToWorld(); SwordRoot->UpdateComponentToWorld();
        }
    }
}
