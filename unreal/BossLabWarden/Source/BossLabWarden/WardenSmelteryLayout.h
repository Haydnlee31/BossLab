#pragma once
#include "CoreMinimal.h"
#include "Dom/JsonObject.h"

// A2 only: no inferred coordinates, silent light truncation or fallback room.
namespace WardenSmelteryLayout
{
struct FLayout
{
    FVector2D HalfSize=FVector2D(800,900);
    FVector Spawn=FVector(400,-400,95);
    FRotator Entry=FRotator(-12,113.96249f,0);
    bool bOuterCamera=false;
    TArray<FVector> StudyStops;
};
inline bool Vector(const TSharedPtr<FJsonObject>& O,const TCHAR* Key,FVector& Out)
{
    const TArray<TSharedPtr<FJsonValue>>* A=nullptr;
    if(!O.IsValid() || !O->TryGetArrayField(Key,A) || A->Num()!=3)return false;
    double N[3];for(int32 I=0;I<3;++I)if(!(*A)[I].IsValid() || !(*A)[I]->TryGetNumber(N[I]) || !FMath::IsFinite(N[I]))return false;
    Out=FVector(N[0],N[1],N[2]);return true;
}
// Exact slab test in a rotated proxy's local space; expand for swept sphere/capsule envelope.
inline bool SegmentHitsProxy(const FVector& A,const FVector& B,const FVector& Centre,const FVector& Extent,double Yaw,const FVector& Expansion)
{
    const FRotator R(0,Yaw,0);const FVector P=R.UnrotateVector(A-Centre),D=R.UnrotateVector(B-A),E=Extent+Expansion;
    double Lo=0,Hi=1;
    for(int32 I=0;I<3;++I)
    {
        if(FMath::Abs(D[I])<1.e-8){if(FMath::Abs(P[I])>E[I])return false;continue;}
        double U=(-E[I]-P[I])/D[I],V=(E[I]-P[I])/D[I];if(U>V)Swap(U,V);
        Lo=FMath::Max(Lo,U);Hi=FMath::Min(Hi,V);if(Lo>Hi)return false;
    }
    return true;
}
inline bool Validate(const TSharedPtr<FJsonObject>& O,FLayout& Result,FString& Error)
{
    auto Fail=[&](const TCHAR* Why){Error=Why;return false;};
    if(!O.IsValid())return Fail(TEXT("Missing layout object"));
    double Version=0,Pitch=0;FString Scene,Space;
    if(!O->TryGetNumberField(TEXT("schema_version"),Version)||Version!=2 ||
       !O->TryGetStringField(TEXT("scene_id"),Scene)||Scene!=TEXT("hearth-a2") ||
       !O->TryGetStringField(TEXT("coordinate_space"),Space)||Space!=TEXT("unreal_cm"))return Fail(TEXT("Expected schema 2 hearth-a2 in unreal_cm"));
    const TArray<TSharedPtr<FJsonValue>>* Size=nullptr; double Width=0,Length=0;
    if(!O->TryGetArrayField(TEXT("walkable_cm"),Size)||Size->Num()!=2 ||
       !(*Size)[0]->TryGetNumber(Width)||!(*Size)[1]->TryGetNumber(Length)||Width!=1600 || Length!=1800)
        return Fail(TEXT("A2 approved walkable floor must be 1600 x 1800 cm"));
    FLayout Candidate;Candidate.HalfSize=FVector2D(Width/2,Length/2);FVector Target;
    if(!Vector(O,TEXT("spawn_cm"),Candidate.Spawn)||!Vector(O,TEXT("entry_target_cm"),Target)||
       !O->TryGetNumberField(TEXT("entry_pitch_deg"),Pitch)||!FMath::IsFinite(Pitch)||Pitch < -30 || Pitch > 10 ||
       FMath::Abs(Candidate.Spawn.X)>Width/2-100 || FMath::Abs(Candidate.Spawn.Y)>Length/2-100 ||
       FMath::Abs(Candidate.Spawn.Z-95)>0.01 || (Target-Candidate.Spawn).Size2D()<100)
        return Fail(TEXT("Invalid spawn or entry camera"));
    Candidate.Entry=FRotator(Pitch,(Target-Candidate.Spawn).Rotation().Yaw,0);
    FString CameraMode=TEXT("field");O->TryGetStringField(TEXT("camera_boundary_mode"),CameraMode);
    if(CameraMode!=TEXT("field") && CameraMode!=TEXT("outer_proxies"))return Fail(TEXT("Unknown camera boundary mode"));
    Candidate.bOuterCamera=CameraMode==TEXT("outer_proxies");
    const FVector Eye=Candidate.Spawn+Candidate.Entry.RotateVector(FVector(-500,45,100));
    if((!Candidate.bOuterCamera && (FMath::Abs(Eye.X)>Width/2-16 || FMath::Abs(Eye.Y)>Length/2-16)) || Eye.Z<50)
        return Fail(TEXT("Default 500cm camera/probe would start outside clear field"));
    const TArray<TSharedPtr<FJsonValue>> *Instances=nullptr,*Lights=nullptr,*Boxes=nullptr;
    if(!O->TryGetArrayField(TEXT("instances"),Instances)||Instances->IsEmpty()||Instances->Num()>256)return Fail(TEXT("Expected 1..256 instances"));
    for(const auto& V:*Instances)
    {
        if(!V.IsValid()||V->Type!=EJson::Object)return Fail(TEXT("Instance must be an object"));
        auto Item=V->AsObject();FString Asset;FVector P,R,S;
        if(!Item.IsValid()||!Item->TryGetStringField(TEXT("asset"),Asset)||!Asset.StartsWith(TEXT("/Game/BossLab/HearthA2/"))||Asset.Contains(TEXT(".."))||
           !Vector(Item,TEXT("location_cm"),P)||!Vector(Item,TEXT("rotation_deg"),R)||!Vector(Item,TEXT("scale"),S)||S.GetMin()<=0 || S.GetMax()>100)
            return Fail(TEXT("Invalid A2 asset or transform"));
    }
    if(!O->TryGetArrayField(TEXT("lights"),Lights)||Lights->Num()>6)return Fail(TEXT("Expected at most six explicit lights"));
    int32 ShadowCount=0;
    for(const auto& V:*Lights)
    {
        if(!V.IsValid()||V->Type!=EJson::Object)return Fail(TEXT("Light must be an object"));
        auto Item=V->AsObject();FString Type,Fixture;FVector P,C,T;double Power=0,Radius=0,Inner=0,Outer=0;bool Shadows=false;
        if(!Item.IsValid()||!Item->TryGetStringField(TEXT("type"),Type)||(Type!=TEXT("point")&&Type!=TEXT("spot"))||
           !Item->TryGetStringField(TEXT("fixture_id"),Fixture)||Fixture.IsEmpty()||
           !Vector(Item,TEXT("location_cm"),P)||!Vector(Item,TEXT("color_rgb"),C)||C.GetMin()<0||C.GetMax()>1||
           !Item->TryGetNumberField(TEXT("intensity_lumens"),Power)||!FMath::IsFinite(Power)||Power<0||Power>80000||
           !Item->TryGetNumberField(TEXT("attenuation_radius_cm"),Radius)||!FMath::IsFinite(Radius)||Radius<100||Radius>4000||
           !Item->TryGetBoolField(TEXT("casts_shadows"),Shadows))return Fail(TEXT("Invalid light or missing fixture provenance"));
        for(const TCHAR* Key:{TEXT("source_radius_cm"),TEXT("soft_source_radius_cm")})
        {
            double RadiusValue=0;
            if(Item->HasField(Key) && (!Item->TryGetNumberField(Key,RadiusValue)||!FMath::IsFinite(RadiusValue)||RadiusValue<0||RadiusValue>250))return Fail(TEXT("Invalid light source radius"));
        }
        if(Type==TEXT("spot") && (!Vector(Item,TEXT("target_cm"),T)||(T-P).Size()<1||
           !Item->TryGetNumberField(TEXT("inner_angle_deg"),Inner)||!Item->TryGetNumberField(TEXT("outer_angle_deg"),Outer)||
           !FMath::IsFinite(Inner)||!FMath::IsFinite(Outer)||Inner<0||Inner>Outer||Outer<1||Outer>80))return Fail(TEXT("Invalid spotlight cone or target"));
        if(Shadows && (Type!=TEXT("spot") || ++ShadowCount>1))return Fail(TEXT("Only one shadowed window spot is budgeted"));
    }
    if(!O->TryGetArrayField(TEXT("camera_collision"),Boxes)||Boxes->Num()>64)return Fail(TEXT("Expected explicit camera collision array"));
    for(const auto& V:*Boxes){if(!V.IsValid()||V->Type!=EJson::Object)return Fail(TEXT("Camera proxy must be an object"));FVector P,E;if(!Vector(V->AsObject(),TEXT("location_cm"),P)||!Vector(V->AsObject(),TEXT("extent_cm"),E)||E.GetMin()<=0)return Fail(TEXT("Invalid camera proxy"));}
    if(Candidate.bOuterCamera && Boxes->Num()<4)return Fail(TEXT("Outer camera mode requires explicit enclosing proxies"));
    const TArray<TSharedPtr<FJsonValue>>* Props=nullptr;
    if(!O->TryGetArrayField(TEXT("prop_collision"),Props)||Props->Num()>64)return Fail(TEXT("Expected explicit prop collision array"));
    const TArray<TSharedPtr<FJsonValue>>* Stops=nullptr;
    if(!O->TryGetArrayField(TEXT("study_waypoints_cm"),Stops)||Stops->Num()<2||Stops->Num()>32)return Fail(TEXT("Expected 2..32 explicit study waypoints"));
    for(const auto& V:*Stops)
    {
        const TArray<TSharedPtr<FJsonValue>>* A=nullptr;
        if(!V.IsValid()||!V->TryGetArray(A)||A->Num()!=3)return Fail(TEXT("Invalid study waypoint"));
        double N[3];for(int32 I=0;I<3;++I)if(!(*A)[I]->TryGetNumber(N[I])||!FMath::IsFinite(N[I]))return Fail(TEXT("Invalid study coordinate"));
        const FVector P(N[0],N[1],N[2]);
        if(FMath::Abs(P.X)>Width/2-70||FMath::Abs(P.Y)>Length/2-70||FMath::Abs(P.Z-95)>.01)return Fail(TEXT("Study waypoint outside clear pawn envelope"));
        Candidate.StudyStops.Add(P);
    }
    for(int32 I=0;I<Candidate.StudyStops.Num();++I)
        if(FVector::Dist2D(Candidate.StudyStops[I],Candidate.StudyStops[(I+1)%Candidate.StudyStops.Num()])<150)return Fail(TEXT("Study waypoints too close to prove movement"));
    for(const auto& V:*Props)
    {
        if(!V.IsValid()||V->Type!=EJson::Object)return Fail(TEXT("Prop collider must be an object"));
        const auto Item=V->AsObject();FString Cluster;FVector P,E;double Yaw=0;
        if(!Item->TryGetStringField(TEXT("cluster_id"),Cluster)||Cluster.IsEmpty()||
           !Vector(Item,TEXT("location_cm"),P)||!Vector(Item,TEXT("extent_cm"),E)||E.GetMin()<=0||E.GetMax()>2000||
           !Item->TryGetNumberField(TEXT("yaw_deg"),Yaw)||!FMath::IsFinite(Yaw))return Fail(TEXT("Invalid prop cluster collider"));
        const FVector Local=FRotator(0,Yaw,0).UnrotateVector(Candidate.Spawn-P);
        if(FMath::Abs(Local.X)<E.X+34 && FMath::Abs(Local.Y)<E.Y+34 && FMath::Abs(Local.Z)<E.Z+90)
            return Fail(TEXT("Prop collider overlaps initial player capsule envelope"));
        if(SegmentHitsProxy(Candidate.Spawn,Eye,P,E,Yaw,FVector(16)))return Fail(TEXT("Prop collider intersects default entry camera sweep"));
        FVector From=Candidate.Spawn;
        for(int32 I=0;I<=Candidate.StudyStops.Num();++I)
        {
            const FVector To=Candidate.StudyStops[I%Candidate.StudyStops.Num()];
            if(SegmentHitsProxy(From,To,P,E,Yaw,FVector(50,50,90)))return Fail(TEXT("Study segment intersects expanded prop collider; provide clear detour"));
            From=To;
        }
    }
    Result=Candidate;Error.Empty();return true;
}
}
