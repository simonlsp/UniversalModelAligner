import bpy
import numpy as np
import math
from mathutils import Matrix, Vector
from ..BlenderTools.SkinBoneTools import ApplyPose

def GetBBOX(ObjMesh):
    """
    Uses bounding box - faster but gives approximate values.
    """
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = ObjMesh.evaluated_get(depsgraph)
    
    # Get world-space bounding box corners
    bbox_world = [ObjMesh.matrix_world @ Vector(corner) for corner in eval_obj.bound_box]
    return {
        "X": {"Min": min(v.x for v in bbox_world), "Max": max(v.x for v in bbox_world)},
        "Y": {"Min": min(v.y for v in bbox_world), "Max": max(v.y for v in bbox_world)},
        "Z": {"Min": min(v.z for v in bbox_world), "Max": max(v.z for v in bbox_world)},
    }

def GetProjectedRotationOfPos(Pos1, Pos2, Plane):
    # This function is not designed to get precise rotation.
    # It is used to generate nearest rotation only to align the projection in specific axis
    DirectonVec = Pos2 - Pos1
    if Plane == "XY":
        angle = math.degrees(math.atan2(DirectonVec.y, DirectonVec.x))
    elif Plane == "YZ":
        angle = math.degrees(math.atan2(DirectonVec.z, DirectonVec.y))
    elif Plane == "XZ":
        angle = math.degrees(math.atan2(DirectonVec.z, DirectonVec.x))
    else:
        raise ValueError("Plane should be one of 'XY', 'YZ' or 'XZ', Input value is "+Plane+"!")
    
    if angle < 0:
        angle += 360
    
    return angle

def GetWorldPos(TargetArmature, BoneName):
    TargetBone = TargetArmature.pose.bones[BoneName]
    return TargetArmature.matrix_world @ TargetBone.head

def GetProjectedRotation(TargetArmature, PoseBone1, PoseBone2, Plane):
    return GetProjectedRotationOfPos(GetWorldPos(TargetArmature, PoseBone1), GetWorldPos(TargetArmature, PoseBone2), Plane)

def GetMeanPosFromNodeNameList(TargetArmature, InputNodeNameList):
    NodePosList = list()
    for NodeName in InputNodeNameList:
        NodePosList.append(GetWorldPos(TargetArmature, NodeName))
    return Vector(np.mean(np.array(NodePosList), axis = 0))

def GetVectorMainAxis(TargetArmature, StartNodeNameList, EndNodeNameList):
    InputVector = GetMeanPosFromNodeNameList(TargetArmature, EndNodeNameList) - GetMeanPosFromNodeNameList(TargetArmature, StartNodeNameList)
    MaxAxisID = np.argmax(np.abs(InputVector))
    if InputVector[MaxAxisID] >= 0:
        return("+", "XYZ"[MaxAxisID])
    else:
        return("-", "XYZ"[MaxAxisID])

def ApplyTranlsationOnWorldAxis(TargetArmature, BoneName, WorldOffset):
    TargetBone = TargetArmature.pose.bones[BoneName]
    # Current world matrix
    WorldMatrix = TargetArmature.matrix_world @ TargetBone.matrix
    # Create rotation around Bone position (pivot point)
    TranslationMatrix = Matrix.Translation(WorldOffset)
    NewWorldMatrix = TranslationMatrix @ WorldMatrix
    TargetBone.matrix = TargetArmature.matrix_world.inverted() @ NewWorldMatrix
    bpy.context.view_layer.update() # Always apply on any update before update children

def ApplyScaleOnWorldAxis(TargetArmature, BoneName, Scale):
    '''
    * Blender do not support shearing in bones
    * **So the result is approximated to a nearby axis**
    '''
    TargetBone = TargetArmature.pose.bones[BoneName]
    # Current world matrix
    WorldMatrix = TargetArmature.matrix_world @ TargetBone.matrix
    # Current world pivot
    Translation = WorldMatrix.translation.copy()
    # World-space scale matrix
    ScaleMatrix = Matrix.Diagonal((*Scale, 1.0))
    Location, Rotation, CurrentScale = WorldMatrix.decompose()
    new_world_matrix = (
        Matrix.Translation(Translation) @ 
        ScaleMatrix @ 
        Matrix.Translation(-Translation) @ 
        WorldMatrix
    )
    # Convert back to bone's local space
    TargetBone.matrix = TargetArmature.matrix_world.inverted() @ new_world_matrix

def ApplyRotationOnWorldAxis(TargetArmature, BoneName, Angle, Axis):
    TargetBone = TargetArmature.pose.bones[BoneName]
    # Recore head position
    WorldPos = TargetArmature.matrix_world @ TargetBone.head
    # Current world matrix
    WorldMatrix = TargetArmature.matrix_world @ TargetBone.matrix
    # Create rotation around Bone position (pivot point)
    Translation = Matrix.Translation(WorldPos)
    TranslationInv = Matrix.Translation(-WorldPos)
    RotationMatrix = Matrix.Rotation(math.radians(Angle), 4, Axis)
    NewWorldMatrix = Translation @ RotationMatrix @ TranslationInv @ WorldMatrix
    TargetBone.matrix = TargetArmature.matrix_world.inverted() @ NewWorldMatrix
    bpy.context.view_layer.update()

def ApplyRotationOnWorldPlane(TargetArmature, BoneName, Angle, Plane):
    RotationAxisSet = {"X", "Y", "Z"} - set(Plane)
    if len(RotationAxisSet) != 1:
        raise ValueError("Plane should be one of 'XY', 'YZ' or 'XZ', Input value is '"+ str(Plane) +"'!")
    RotationAxis = RotationAxisSet.pop()
    if RotationAxis == "Y":
        ApplyRotationOnWorldAxis(TargetArmature, BoneName, -Angle, RotationAxis)
    else:
        ApplyRotationOnWorldAxis(TargetArmature, BoneName, Angle, RotationAxis)

def ApplyScaleOnLocalAxis(TargetArmature, ScalingBoneName, ScaleRatio, MainLocalAxis, OtherAxisScaleFactor = 0.5):
    TargetBone = TargetArmature.pose.bones[ScalingBoneName]
    MainScale = ScaleRatio
    if ScaleRatio >=0:
        OtherScale = ScaleRatio ** OtherAxisScaleFactor
    else:
        OtherScale = -((-ScaleRatio) ** OtherAxisScaleFactor)

    if MainLocalAxis == "X":
        TargetBone.scale = Vector((TargetBone.scale.x * MainScale, TargetBone.scale.y * OtherScale, TargetBone.scale.z * OtherScale))
    elif MainLocalAxis == "Y":
        TargetBone.scale = Vector((TargetBone.scale.x * OtherScale, TargetBone.scale.y * MainScale, TargetBone.scale.z * OtherScale))
    elif MainLocalAxis == "Z":
        TargetBone.scale = Vector((TargetBone.scale.x * OtherScale, TargetBone.scale.y * OtherScale, TargetBone.scale.z * MainScale))
    else:
        raise ValueError("MainLocalAxis should be one of 'X', 'Y' or 'Z', Input value is '"+MainLocalAxis+"'!")

    bpy.context.view_layer.update()

def AutoRotateFinger(TargetArmature, FingerBoneChain, RotatingWorldAxis, RotationAng):
    for FingerBone in FingerBoneChain:
        RotationAxisDir, RotationAxisName = RotatingWorldAxis
        if RotationAxisDir == "+":
            ApplyRotationOnWorldAxis(TargetArmature, FingerBone, RotationAng, RotationAxisName)
            ApplyRotationOnWorldAxis(TargetArmature, FingerBone, RotationAng, RotationAxisName)
        elif RotationAxisDir == "-":
            ApplyRotationOnWorldAxis(TargetArmature, FingerBone, -RotationAng, RotationAxisName)
        else:
            raise ValueError("RotationAxisDir is not + nor - !")
        
def AlignBoneLength(TargetArmature, ScalingBone, TargetBone, MainLocalAxis, LengthRatioToTarget = 1.0, OtherAxisScaleFactor = 0.5):
    ScalingBoneVector = GetWorldPos(TargetArmature, ScalingBone[1]) - GetWorldPos(TargetArmature, ScalingBone[0])
    TargetBoneVector = GetWorldPos(TargetArmature, TargetBone[1]) - GetWorldPos(TargetArmature, TargetBone[0])
    LengthRatio = (TargetBoneVector.length / ScalingBoneVector.length) * LengthRatioToTarget
    ApplyScaleOnLocalAxis(TargetArmature, ScalingBone[0], LengthRatio, MainLocalAxis, OtherAxisScaleFactor = OtherAxisScaleFactor)
    
def AlignBoneRotationOnWorldPlane(TargetArmature, RotatingBone, TargetBone, Plane):
    RotatingBoneProjectedRotation = GetProjectedRotation(TargetArmature, RotatingBone[0], RotatingBone[1], Plane)
    TargetBoneProjectedRotation = GetProjectedRotation(TargetArmature, TargetBone[0], TargetBone[1], Plane)
    RotationDiff = TargetBoneProjectedRotation - RotatingBoneProjectedRotation
    ApplyRotationOnWorldPlane(TargetArmature, RotatingBone[0], RotationDiff, Plane)

def AlignBoneRotationOnWorldPlaneBySequence(TargetArmature, RotatingBone, TargetBone, PlaneSeq):
    for Plane in PlaneSeq:
        AlignBoneRotationOnWorldPlane(TargetArmature, RotatingBone, TargetBone, Plane)


def AlignSkeleton(MeshObject, ArmatureObject, SourceJointDict, TargetJointDict, GameMode="GOH"):
    # Record initial scene status
    InitialActiveObject = bpy.context.active_object
    InitialActiveMode = bpy.context.object.mode if bpy.context.object else 'OBJECT'
    
    # Modify skeleton to make specific bones always use average scaling from parent
    bpy.context.view_layer.objects.active = ArmatureObject
    ArmatureObject.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for BoneName in [
        SourceJointDict["Shoulder_L"],
        SourceJointDict["Shoulder_R"],
        SourceJointDict["Neck"],
        SourceJointDict["Thigh_L"],
        SourceJointDict["Thigh_R"],
        SourceJointDict["Foot_L"],
        SourceJointDict["Foot_R"],
        SourceJointDict["Wrist_L"],
        SourceJointDict["Wrist_R"],
    ]:
        ArmatureObject.data.edit_bones[BoneName].inherit_scale = "AVERAGE"

    # Switch context armature pose mode
    bpy.context.view_layer.objects.active = ArmatureObject
    ArmatureObject.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')

    # Remove all constraints
    for bone in ArmatureObject.pose.bones:
        for constraint in list(bone.constraints):
            bone.constraints.remove(constraint)

    ## ==================== Axis Alignment ====================
    ### Head
    SourceHeadAxisDir, SourceHeadAxisName = GetVectorMainAxis(ArmatureObject, [SourceJointDict["Foot_L"], SourceJointDict["Foot_R"]], [SourceJointDict["Shoulder_L"], SourceJointDict["Shoulder_R"]])
    TargetHeadAxisDir, TargetHeadAxisName = GetVectorMainAxis(ArmatureObject, [TargetJointDict["Foot_L"], TargetJointDict["Foot_R"]], [TargetJointDict["Shoulder_L"], TargetJointDict["Shoulder_R"]])

    #### Align Head Axis
    if SourceHeadAxisName != TargetHeadAxisName:
        RotationAxis = ({"X", "Y", "Z"} - {SourceHeadAxisName, TargetHeadAxisName}).pop()
        ApplyRotationOnWorldAxis(ArmatureObject, SourceJointDict["Root"], 90, RotationAxis)
        SourceHeadAxisDir, SourceHeadAxisName = GetVectorMainAxis(ArmatureObject, [SourceJointDict["Foot_L"], SourceJointDict["Foot_R"]], [SourceJointDict["Shoulder_L"], SourceJointDict["Shoulder_R"]])
        TargetHeadAxisDir, TargetHeadAxisName = GetVectorMainAxis(ArmatureObject, [TargetJointDict["Foot_L"], TargetJointDict["Foot_R"]], [TargetJointDict["Shoulder_L"], TargetJointDict["Shoulder_R"]])
    #### Align Head Direction
    if SourceHeadAxisDir != TargetHeadAxisDir:
        RotationAxis = ({"X", "Y", "Z"} - {SourceHeadAxisName, TargetHeadAxisName}).pop()
        ApplyRotationOnWorldAxis(ArmatureObject, SourceJointDict["Root"], 180, RotationAxis)
        SourceHeadAxisDir, SourceHeadAxisName = GetVectorMainAxis(ArmatureObject, [SourceJointDict["Foot_L"], SourceJointDict["Foot_R"]], [SourceJointDict["Shoulder_L"], SourceJointDict["Shoulder_R"]])
        TargetHeadAxisDir, TargetHeadAxisName = GetVectorMainAxis(ArmatureObject, [TargetJointDict["Foot_L"], TargetJointDict["Foot_R"]], [TargetJointDict["Shoulder_L"], TargetJointDict["Shoulder_R"]])
    ### Shoulder
    SourceShoulderAxisDir, SourceShoulderAxisName = GetVectorMainAxis(ArmatureObject, [SourceJointDict["Shoulder_L"], ], [SourceJointDict["Shoulder_R"], ])
    TargetShoulderAxisDir, TargetShoulderAxisName = GetVectorMainAxis(ArmatureObject, [TargetJointDict["Shoulder_L"], ], [TargetJointDict["Shoulder_R"], ])
    #### Align Shoulder Axis
    if SourceShoulderAxisName != TargetShoulderAxisName:
        ApplyRotationOnWorldAxis(ArmatureObject, SourceJointDict["Root"], 90, SourceHeadAxisName)
        SourceShoulderAxisDir, SourceShoulderAxisName = GetVectorMainAxis(ArmatureObject, [SourceJointDict["Shoulder_L"], ], [SourceJointDict["Shoulder_R"], ])
        TargetShoulderAxisDir, TargetShoulderAxisName = GetVectorMainAxis(ArmatureObject, [TargetJointDict["Shoulder_L"], ], [TargetJointDict["Shoulder_R"], ])
    #### Align Shoulder Direction
    if SourceShoulderAxisDir != TargetShoulderAxisDir:
        ApplyRotationOnWorldAxis(ArmatureObject, SourceJointDict["Root"], 180, SourceHeadAxisName)

    ## ==================== Full body Pre-Alignment ====================
    ### Lower body rotation alignment
    #### UpperLeg Rotation (YZ -> XZ)
    UpperLegRotationSequence = ["YZ", "XZ"]
    SourceUpperLegLeft = [SourceJointDict["Thigh_L"], SourceJointDict["Knee_L"]]
    SourceUpperLegRight = [SourceJointDict["Thigh_R"], SourceJointDict["Knee_R"]]
    TargetUpperLegLeft = [TargetJointDict["Thigh_L"], TargetJointDict["Knee_L"]]
    TargetUpperLegRight = [TargetJointDict["Thigh_R"], TargetJointDict["Knee_R"]]
    AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, SourceUpperLegLeft, TargetUpperLegLeft, UpperLegRotationSequence)
    AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, SourceUpperLegRight, TargetUpperLegRight, UpperLegRotationSequence)

    #### LowerLeg Rotation (YZ -> XZ)
    LowerLegRotationSequence = ["YZ", "XZ"]
    SourceLowerLegLeft = [SourceJointDict["Knee_L"], SourceJointDict["Foot_L"]]
    SourceLowerLegRight = [SourceJointDict["Knee_R"], SourceJointDict["Foot_R"]]
    TargetLowerLegLeft = [TargetJointDict["Knee_L"], TargetJointDict["Foot_L"]]
    TargetLowerLegRight = [TargetJointDict["Knee_R"], TargetJointDict["Foot_R"]]
    AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, SourceLowerLegLeft, TargetLowerLegLeft, LowerLegRotationSequence)
    AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, SourceLowerLegRight, TargetLowerLegRight, LowerLegRotationSequence)

    ### Overall Scaling Alignment
    SourceShoulderHeight = GetMeanPosFromNodeNameList(ArmatureObject, [SourceJointDict["Shoulder_L"], SourceJointDict["Shoulder_R"]]).z
    SourceFootHeight = GetBBOX(MeshObject)["Z"]["Min"]
    TargetShoulderHeight = GetMeanPosFromNodeNameList(ArmatureObject, [TargetJointDict["Shoulder_L"], TargetJointDict["Shoulder_R"]]).z
    TargetFootHeight = 0
    OverallScale = (TargetShoulderHeight - TargetFootHeight) / (SourceShoulderHeight - SourceFootHeight)
    RootBone = ArmatureObject.pose.bones[SourceJointDict["Root"]]
    RootBone.scale = RootBone.scale * OverallScale
    bpy.context.view_layer.update()

    ### Overall Rotation Alignment
    BodyAlignmentPlane = "XZ"
    SourceFootCenter = GetMeanPosFromNodeNameList(ArmatureObject, [SourceJointDict["Foot_L"], SourceJointDict["Foot_R"]])
    SourceShoulderCenter = GetMeanPosFromNodeNameList(ArmatureObject, [SourceJointDict["Shoulder_L"], SourceJointDict["Shoulder_R"], SourceJointDict["Neck"], SourceJointDict["Neck"]])
    SourceBodyDirection = GetProjectedRotationOfPos(SourceFootCenter, SourceShoulderCenter, BodyAlignmentPlane)
    TargetFootCenter = GetMeanPosFromNodeNameList(ArmatureObject, [TargetJointDict["Foot_L"], TargetJointDict["Foot_R"]])
    TargetShoulderCenter = GetMeanPosFromNodeNameList(ArmatureObject, [TargetJointDict["Shoulder_L"], TargetJointDict["Shoulder_R"], TargetJointDict["Neck"], TargetJointDict["Neck"]])
    TargetBodyDirection = GetProjectedRotationOfPos(TargetFootCenter, TargetShoulderCenter, BodyAlignmentPlane)
    BodyDirectionDiff = TargetBodyDirection - SourceBodyDirection
    ApplyRotationOnWorldPlane(ArmatureObject, SourceJointDict["Root"], BodyDirectionDiff, BodyAlignmentPlane)
    ### Re-Align Legs Rotation
    ApplyRotationOnWorldPlane(ArmatureObject, SourceJointDict["Thigh_L"], -BodyDirectionDiff, BodyAlignmentPlane)
    ApplyRotationOnWorldPlane(ArmatureObject, SourceJointDict["Thigh_R"], -BodyDirectionDiff, BodyAlignmentPlane)
    
    ### Overall Position Alignment
    SourceFullBodyAlignmentPos = GetMeanPosFromNodeNameList(ArmatureObject, [SourceJointDict["Thigh_L"], SourceJointDict["Thigh_R"]])
    TargetFullBodyAlignmentPos = GetMeanPosFromNodeNameList(ArmatureObject, [TargetJointDict["Thigh_L"], TargetJointDict["Thigh_R"]])
    ApplyTranlsationOnWorldAxis(ArmatureObject, SourceJointDict["Root"], (TargetFullBodyAlignmentPos - SourceFullBodyAlignmentPos))

    ## ==================== Shoulder Alignment ====================
    ### Get Upper body scaling
    SourceShoulderHeight = GetMeanPosFromNodeNameList(ArmatureObject, [SourceJointDict["Shoulder_L"], SourceJointDict["Shoulder_R"]]).z
    SourceThighHeight = GetMeanPosFromNodeNameList(ArmatureObject, [SourceJointDict["Thigh_L"], SourceJointDict["Thigh_R"]]).z
    TargetShoulderHeight = GetMeanPosFromNodeNameList(ArmatureObject, [TargetJointDict["Shoulder_L"], TargetJointDict["Shoulder_R"]]).z
    TargetThighHeight = GetMeanPosFromNodeNameList(ArmatureObject, [TargetJointDict["Thigh_L"], TargetJointDict["Thigh_R"]]).z
    UpperBodyHeightScale = (TargetShoulderHeight - TargetThighHeight) / (SourceShoulderHeight - SourceThighHeight)

    SourceShoulderWidth = (GetMeanPosFromNodeNameList(ArmatureObject, [SourceJointDict["Shoulder_L"]]) - GetMeanPosFromNodeNameList(ArmatureObject, [SourceJointDict["Shoulder_R"]])).length
    TargetShoulderWidth = (GetMeanPosFromNodeNameList(ArmatureObject, [TargetJointDict["Shoulder_L"]]) - GetMeanPosFromNodeNameList(ArmatureObject, [TargetJointDict["Shoulder_R"]])).length
    UpperBodyWidthScale = TargetShoulderWidth / SourceShoulderWidth
    ApplyScaleOnWorldAxis(ArmatureObject, SourceJointDict["Root"], Vector(((UpperBodyWidthScale * UpperBodyHeightScale) ** 0.5, UpperBodyWidthScale, UpperBodyHeightScale)))
    
    ### Re Align Position
    SourceFullBodyAlignmentPos = GetMeanPosFromNodeNameList(ArmatureObject, [SourceJointDict["Thigh_L"], SourceJointDict["Thigh_R"]])
    TargetFullBodyAlignmentPos = GetMeanPosFromNodeNameList(ArmatureObject, [TargetJointDict["Thigh_L"], TargetJointDict["Thigh_R"]])
    ApplyTranlsationOnWorldAxis(ArmatureObject, SourceJointDict["Root"], (TargetFullBodyAlignmentPos - SourceFullBodyAlignmentPos))

    #### Shoulder Alignment
    ##### Align Midpoint
    ###### Rotation
    SourceUpperBodyCenter = GetMeanPosFromNodeNameList(ArmatureObject, [SourceJointDict["SpineLower"]])
    SourceShoulderCenter = GetMeanPosFromNodeNameList(ArmatureObject, [SourceJointDict["Shoulder_L"], SourceJointDict["Shoulder_R"], SourceJointDict["Neck"], SourceJointDict["Neck"]])
    SourceUpperBodyDirection = GetProjectedRotationOfPos(SourceUpperBodyCenter, SourceShoulderCenter, BodyAlignmentPlane)

    TargetUpperBodyCenter = GetMeanPosFromNodeNameList(ArmatureObject, [SourceJointDict["SpineLower"]])
    TargetShoulderCenter = GetMeanPosFromNodeNameList(ArmatureObject, [TargetJointDict["Shoulder_L"], TargetJointDict["Shoulder_R"], TargetJointDict["Neck"], TargetJointDict["Neck"]])
    TargetUpperBodyDirection = GetProjectedRotationOfPos(TargetUpperBodyCenter, TargetShoulderCenter, BodyAlignmentPlane)
    UpperBodyDirectionDiff = (TargetUpperBodyDirection - SourceUpperBodyDirection) * 0.67 # Use Translation to cover the rest 1/3 to avoid border situations.

    ApplyRotationOnWorldPlane(ArmatureObject, SourceJointDict["SpineLower"], UpperBodyDirectionDiff, BodyAlignmentPlane)
    ApplyRotationOnWorldPlane(ArmatureObject, SourceJointDict["Shoulder_L"], -UpperBodyDirectionDiff, BodyAlignmentPlane)
    ApplyRotationOnWorldPlane(ArmatureObject, SourceJointDict["Shoulder_R"], -UpperBodyDirectionDiff, BodyAlignmentPlane)
    ApplyRotationOnWorldPlane(ArmatureObject, SourceJointDict["Neck"], -UpperBodyDirectionDiff, BodyAlignmentPlane)

    SourceShoulderPos = GetMeanPosFromNodeNameList(ArmatureObject, [SourceJointDict["Shoulder_L"], SourceJointDict["Shoulder_R"], SourceJointDict["Neck"]])
    TargetShoulderPos = GetMeanPosFromNodeNameList(ArmatureObject, [TargetJointDict["Shoulder_L"], TargetJointDict["Shoulder_R"], TargetJointDict["Neck"]])
    ShoulderOffset = TargetShoulderPos - SourceShoulderPos
    ApplyTranlsationOnWorldAxis(ArmatureObject, SourceJointDict["SpineLower"], ShoulderOffset * 0.1)
    ApplyTranlsationOnWorldAxis(ArmatureObject, SourceJointDict["SpineUpper"], ShoulderOffset * 0.4)
    ApplyTranlsationOnWorldAxis(ArmatureObject, SourceJointDict["Clavicle_L"], ShoulderOffset * 0.5)
    ApplyTranlsationOnWorldAxis(ArmatureObject, SourceJointDict["Clavicle_R"], ShoulderOffset * 0.5)
    ApplyTranlsationOnWorldAxis(ArmatureObject, SourceJointDict["Neck"], ShoulderOffset * 0.5)
    ##### Align Seperate
    ###### L
    SourceLeftShoulderPos = GetMeanPosFromNodeNameList(ArmatureObject, [SourceJointDict["Shoulder_L"]])
    TargetLeftShoulderPos = GetMeanPosFromNodeNameList(ArmatureObject, [TargetJointDict["Shoulder_L"]])
    LeftShoulderOffset = TargetLeftShoulderPos - SourceLeftShoulderPos
    ApplyTranlsationOnWorldAxis(ArmatureObject, SourceJointDict["Clavicle_L"], LeftShoulderOffset * 0.6)
    ApplyTranlsationOnWorldAxis(ArmatureObject, SourceJointDict["Shoulder_L"], LeftShoulderOffset * 0.4)
    ###### R
    SourceRightShoulderPos = GetMeanPosFromNodeNameList(ArmatureObject, [SourceJointDict["Shoulder_R"]])
    TargetRightShoulderPos = GetMeanPosFromNodeNameList(ArmatureObject, [TargetJointDict["Shoulder_R"]])
    RightShoulderOffset = TargetRightShoulderPos - SourceRightShoulderPos
    ApplyTranlsationOnWorldAxis(ArmatureObject, SourceJointDict["Clavicle_R"], RightShoulderOffset * 0.6)
    ApplyTranlsationOnWorldAxis(ArmatureObject, SourceJointDict["Shoulder_R"], RightShoulderOffset * 0.4)
    ###### Neck
    SourceNeckPos = GetMeanPosFromNodeNameList(ArmatureObject, [SourceJointDict["Neck"]])
    TargetNeckPos = GetMeanPosFromNodeNameList(ArmatureObject, [TargetJointDict["Neck"]])
    NeckOffset = TargetNeckPos - SourceNeckPos
    ApplyTranlsationOnWorldAxis(ArmatureObject, SourceJointDict["Neck"], NeckOffset * 0.4)

    ## ==================== Leg Alignment ====================
    ### UpperLeg Scaling
    UpperLegScalingAxis = "Y"
    AlignBoneLength(ArmatureObject, [SourceJointDict["Thigh_L"], SourceJointDict["Knee_L"]], [TargetJointDict["Thigh_L"], TargetJointDict["Knee_L"]], UpperLegScalingAxis, OtherAxisScaleFactor=(1/3))
    AlignBoneLength(ArmatureObject, [SourceJointDict["Thigh_R"], SourceJointDict["Knee_R"]], [TargetJointDict["Thigh_R"], TargetJointDict["Knee_R"]], UpperLegScalingAxis, OtherAxisScaleFactor=(1/3))
    ### LowerLeg Scaling
    LowerLegScalingAxis = "Y"
    LowerLegExpectedHeight = GetMeanPosFromNodeNameList(ArmatureObject, [SourceJointDict["Knee_L"], SourceJointDict["Knee_R"]]).z
    LowerLegCurrentHeight = LowerLegExpectedHeight - GetBBOX(MeshObject)["Z"]["Min"]
    LowerLegScaling = LowerLegExpectedHeight / LowerLegCurrentHeight
    ApplyScaleOnLocalAxis(ArmatureObject, SourceJointDict["Knee_L"], LowerLegScaling, LowerLegScalingAxis, OtherAxisScaleFactor = (1/3))
    ApplyScaleOnLocalAxis(ArmatureObject, SourceJointDict["Knee_R"], LowerLegScaling, LowerLegScalingAxis, OtherAxisScaleFactor = (1/3))
    ### UpperLeg Re-Rotation To Match Foot Pos
    SourceFullLegLeft = [SourceJointDict["Thigh_L"], SourceJointDict["Foot_L"]]
    SourceFullLegRight = [SourceJointDict["Thigh_R"], SourceJointDict["Foot_R"]]
    TargetFullLegLeft = [TargetJointDict["Thigh_L"], TargetJointDict["Foot_L"]]
    TargetFullLegRight = [TargetJointDict["Thigh_R"], TargetJointDict["Foot_R"]]
    AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, SourceFullLegLeft, TargetFullLegLeft, UpperLegRotationSequence)
    AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, SourceFullLegRight, TargetFullLegRight, UpperLegRotationSequence)
    
    ## ==================== Arm Alignment ====================
    ### UpperArm
    UpperArmScalingAxis = "Y"
    UpperArmRotationSequence = ["XY", "YZ"]
    SourceUpperArmLeft = [SourceJointDict["Shoulder_L"], SourceJointDict["Elbow_L"]]
    SourceUpperArmRight = [SourceJointDict["Shoulder_R"], SourceJointDict["Elbow_R"]]
    TargetUpperArmLeft = [TargetJointDict["Shoulder_L"], TargetJointDict["Elbow_L"]]
    TargetUpperArmRight = [TargetJointDict["Shoulder_R"], TargetJointDict["Elbow_R"]]
    AlignBoneLength(ArmatureObject, SourceUpperArmLeft, TargetUpperArmLeft, UpperArmScalingAxis)
    AlignBoneLength(ArmatureObject, SourceUpperArmRight, TargetUpperArmRight, UpperArmScalingAxis)
    AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, SourceUpperArmLeft, TargetUpperArmLeft, UpperArmRotationSequence)
    AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, SourceUpperArmRight, TargetUpperArmRight, UpperArmRotationSequence)
    ### LowerArm
    LowerArmScalingAxis = "Y"
    LowerArmRotationSequence = ["XY", "YZ"]
    SourceLowerArmLeft = [SourceJointDict["Elbow_L"], SourceJointDict["Wrist_L"]]
    SourceLowerArmRight = [SourceJointDict["Elbow_R"], SourceJointDict["Wrist_R"]]
    TargetLowerArmLeft = [TargetJointDict["Elbow_L"], TargetJointDict["Wrist_L"]]
    TargetLowerArmRight = [TargetJointDict["Elbow_R"], TargetJointDict["Wrist_R"]]
    AlignBoneLength(ArmatureObject, SourceLowerArmLeft, TargetLowerArmLeft, LowerArmScalingAxis)
    AlignBoneLength(ArmatureObject, SourceLowerArmRight, TargetLowerArmRight, LowerArmScalingAxis)
    AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, SourceLowerArmLeft, TargetLowerArmLeft, LowerArmRotationSequence)
    AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, SourceLowerArmRight, TargetLowerArmRight, LowerArmRotationSequence)
    ### ArmFinal
    SourceFinalArmLeft = [SourceJointDict["Shoulder_L"], SourceJointDict["Wrist_L"]]
    SourceFinalArmRight = [SourceJointDict["Shoulder_R"], SourceJointDict["Wrist_R"]]
    TargetFinalArmLeft = [TargetJointDict["Shoulder_L"], TargetJointDict["Wrist_L"]]
    TargetFinalArmRight = [TargetJointDict["Shoulder_R"], TargetJointDict["Wrist_R"]]
    AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, SourceFinalArmLeft, TargetFinalArmLeft, UpperArmRotationSequence)
    AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, SourceFinalArmRight, TargetFinalArmRight, UpperArmRotationSequence)
    
    ### Arm Further offset for specific game
    if GameMode == "GOH":
        ApplyRotationOnWorldPlane(ArmatureObject, SourceJointDict["Shoulder_L"], 2.0, "YZ")
        ApplyRotationOnWorldPlane(ArmatureObject, SourceJointDict["Shoulder_R"], -2.0, "YZ")
    else:
        raise NotImplementedError("Input GameMode not implemented")

    ## ==================== Finger Alignment ====================
    if GameMode == "GOH":
        ### Rotate Thumb
        GOH_ThumbRotation = 10
        LeftThumbWorldRotateAxis = ["+", "Y"]
        RightThumbWorldRotateAxis = ["+", "Y"]
        AutoRotateFinger(ArmatureObject, [SourceJointDict["Thumb_L1"], SourceJointDict["Thumb_L2"], SourceJointDict["Thumb_L3"],], LeftThumbWorldRotateAxis, GOH_ThumbRotation)
        AutoRotateFinger(ArmatureObject, [SourceJointDict["Thumb_R1"], SourceJointDict["Thumb_R2"], SourceJointDict["Thumb_R3"],], RightThumbWorldRotateAxis, GOH_ThumbRotation)
        ### Align Other fingers to hand pose
        FingerAlignmentSequence = ["XY", "YZ"]
        AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, [SourceJointDict["IndexFinger_L1"], SourceJointDict["IndexFinger_L2"]], SourceLowerArmLeft, FingerAlignmentSequence)
        AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, [SourceJointDict["IndexFinger_L2"], SourceJointDict["IndexFinger_L3"]], SourceLowerArmLeft, FingerAlignmentSequence)
        AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, [SourceJointDict["MiddleFinger_L1"], SourceJointDict["MiddleFinger_L2"]], SourceLowerArmLeft, FingerAlignmentSequence)
        AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, [SourceJointDict["MiddleFinger_L2"], SourceJointDict["MiddleFinger_L3"]], SourceLowerArmLeft, FingerAlignmentSequence)
        AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, [SourceJointDict["LittleFinger_L1"], SourceJointDict["LittleFinger_L2"]], SourceLowerArmLeft, FingerAlignmentSequence)
        AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, [SourceJointDict["LittleFinger_L2"], SourceJointDict["LittleFinger_L3"]], SourceLowerArmLeft, FingerAlignmentSequence)
        AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, [SourceJointDict["RingFinger_L1"], SourceJointDict["RingFinger_L2"]], SourceLowerArmLeft, FingerAlignmentSequence)
        AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, [SourceJointDict["RingFinger_L2"], SourceJointDict["RingFinger_L3"]], SourceLowerArmLeft, FingerAlignmentSequence)

        AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, [SourceJointDict["IndexFinger_R1"], SourceJointDict["IndexFinger_R2"]], SourceLowerArmRight, FingerAlignmentSequence)
        AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, [SourceJointDict["IndexFinger_R2"], SourceJointDict["IndexFinger_R3"]], SourceLowerArmRight, FingerAlignmentSequence)
        AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, [SourceJointDict["MiddleFinger_R1"], SourceJointDict["MiddleFinger_R2"]], SourceLowerArmRight, FingerAlignmentSequence)
        AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, [SourceJointDict["MiddleFinger_R2"], SourceJointDict["MiddleFinger_R3"]], SourceLowerArmRight, FingerAlignmentSequence)
        AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, [SourceJointDict["LittleFinger_R1"], SourceJointDict["LittleFinger_R2"]], SourceLowerArmRight, FingerAlignmentSequence)
        AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, [SourceJointDict["LittleFinger_R2"], SourceJointDict["LittleFinger_R3"]], SourceLowerArmRight, FingerAlignmentSequence)
        AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, [SourceJointDict["RingFinger_R1"], SourceJointDict["RingFinger_R2"]], SourceLowerArmRight, FingerAlignmentSequence)
        AlignBoneRotationOnWorldPlaneBySequence(ArmatureObject, [SourceJointDict["RingFinger_R2"], SourceJointDict["RingFinger_R3"]], SourceLowerArmRight, FingerAlignmentSequence)
        ### Rotate Other fingers    
        LeftHandWorldRotateAxis = ["-", "X"]
        RightHandWorldRotateAxis = ["+", "X"]
        GOH_FingerRotation = 15 # ?

        AutoRotateFinger(ArmatureObject, [SourceJointDict["IndexFinger_L1"], SourceJointDict["IndexFinger_L2"], SourceJointDict["IndexFinger_L3"],], LeftHandWorldRotateAxis, GOH_FingerRotation)
        AutoRotateFinger(ArmatureObject, [SourceJointDict["MiddleFinger_L1"], SourceJointDict["MiddleFinger_L2"], SourceJointDict["MiddleFinger_L3"],], LeftHandWorldRotateAxis, GOH_FingerRotation * 1.3)
        AutoRotateFinger(ArmatureObject, [SourceJointDict["RingFinger_L1"], SourceJointDict["RingFinger_L2"], SourceJointDict["RingFinger_L3"],], LeftHandWorldRotateAxis, GOH_FingerRotation * 1.4)
        AutoRotateFinger(ArmatureObject, [SourceJointDict["LittleFinger_L1"], SourceJointDict["LittleFinger_L2"], SourceJointDict["LittleFinger_L3"],], LeftHandWorldRotateAxis, GOH_FingerRotation * 1.375)

        AutoRotateFinger(ArmatureObject, [SourceJointDict["IndexFinger_R1"], SourceJointDict["IndexFinger_R2"], SourceJointDict["IndexFinger_R3"],], RightHandWorldRotateAxis, GOH_FingerRotation)
        AutoRotateFinger(ArmatureObject, [SourceJointDict["MiddleFinger_R1"], SourceJointDict["MiddleFinger_R2"], SourceJointDict["MiddleFinger_R3"],], RightHandWorldRotateAxis, GOH_FingerRotation * 1.3)
        AutoRotateFinger(ArmatureObject, [SourceJointDict["RingFinger_R1"], SourceJointDict["RingFinger_R2"], SourceJointDict["RingFinger_R3"],], RightHandWorldRotateAxis, GOH_FingerRotation * 1.4)
        AutoRotateFinger(ArmatureObject, [SourceJointDict["LittleFinger_R1"], SourceJointDict["LittleFinger_R2"], SourceJointDict["LittleFinger_R3"],], RightHandWorldRotateAxis, GOH_FingerRotation * 1.375)
        
        # Finalize Hand Rotation
        ApplyRotationOnWorldPlane(ArmatureObject, SourceJointDict["Wrist_L"], -35, "XY")
        ApplyRotationOnWorldPlane(ArmatureObject, SourceJointDict["Wrist_R"], 35, "XY") 
        
        ApplyRotationOnWorldPlane(ArmatureObject, SourceJointDict["Wrist_L"], 5, "YZ")
        ApplyRotationOnWorldPlane(ArmatureObject, SourceJointDict["Wrist_R"], -5, "YZ")
        
        ApplyRotationOnWorldPlane(ArmatureObject, SourceJointDict["Wrist_L"], -15, "XZ")
        ApplyRotationOnWorldPlane(ArmatureObject, SourceJointDict["Wrist_R"], -15, "XZ")
    else:
        raise NotImplementedError("Input GameMode not implemented")

    ApplyPose(MeshObject)
    # Restore Status
    bpy.context.view_layer.objects.active = InitialActiveObject
    bpy.ops.object.mode_set(mode=InitialActiveMode)


class Opreator():
    def __init__(self, SourceJointDict):
        self.SourceJointDict = SourceJointDict

    def Execute(self):
        SceneObjects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        assert len(SceneObjects) == 1, "There should be only one mesh in the scene upon aligning!"
        MeshObject = SceneObjects[0]
        for mod in MeshObject.modifiers:
            if mod.type == 'ARMATURE' and mod.object:
                ArmatureObject =  mod.object
                break
        else:
            raise ValueError("Error: No armature found on mesh")
        
        from ..JointDicts.GOH_JointDict import JointDict as GOH_JointDict
        
        AlignSkeleton(MeshObject, ArmatureObject, self.SourceJointDict, GOH_JointDict, GameMode="GOH")