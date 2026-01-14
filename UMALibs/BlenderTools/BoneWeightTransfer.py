import bpy
import numpy as np

def TransferBoneWeights(MeshObject, TransferTable, NormalizeTransferTable = True, NormalizeOutput = True, PurgeVertGroupWitoutBone = False):
    """
    Transfer weights from bone1 to bone2, then delete bone1.
    
    Args:
        mesh_obj: Skinned mesh object
        bone_name1: Source bone (will be deleted)
        bone_name2: Target bone (receives weights)
    
    Returns:
        bool: Success status
    """
    # Record initial scene status
    InitialActiveObject = bpy.context.active_object
    InitialActiveMode = bpy.context.object.mode if bpy.context.object else 'OBJECT'

    # Switch context to OBJECT mode
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Find armature from modifier
    for mod in MeshObject.modifiers:
        if mod.type == 'ARMATURE' and mod.object:
            ArmatureObject = mod.object
            break
    else:
        raise ValueError("Error: No armature found on mesh")
    
    # Switch context armature edit mode
    bpy.context.view_layer.objects.active = ArmatureObject
    ArmatureObject.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Validate mesh object
    if MeshObject is None or MeshObject.type != 'MESH':
        raise ValueError("Error: Invalid mesh object")
    
    # Verify Bones
    SourceBoneSet = {SourceBoneName for SourceBoneList, TargetBoneList in TransferTable for SourceBoneName in SourceBoneList}
    TargetBoneSet = {TargetBoneName for SourceBoneList, TargetBoneList in TransferTable for TargetBoneName, TargetBoneWeight in TargetBoneList}
    for TargetBoneName in TargetBoneSet:
        if TargetBoneName not in ArmatureObject.data.bones:
            raise ValueError(f"Error: At least one target bone is not in armature: [{TargetBoneName}].")
    
    # Add Bones to VertexGroup if needed
    for TargetBoneName in TargetBoneSet:
        if MeshObject.vertex_groups.get(TargetBoneName) is None:
            MeshObject.vertex_groups.new(name=TargetBoneName)
    
    # Get current weights and remove all verts from group
    CurrentWeight = np.zeros((len(MeshObject.data.vertices), len(MeshObject.vertex_groups)), dtype=float)
    VertGroupNameToID = dict()
    VertGroupIDToName = dict()
    for Vert in list(MeshObject.data.vertices):
        for VertGroup in list(Vert.groups):
            CurrentWeight[Vert.index, VertGroup.group] = VertGroup.weight
    
    # Remove all VertGroups
    for VertGroup in list(MeshObject.vertex_groups):
        VertGroupNameToID[VertGroup.name] = VertGroup.index
        VertGroupIDToName[VertGroup.index] = VertGroup.name
        
    for RemovingVertGroup in list(MeshObject.vertex_groups):
        MeshObject.vertex_groups.remove(RemovingVertGroup)
    # Transfer weights
    for SourceBoneList, TargetBoneList in TransferTable:
        SourceBoneIDList = [VertGroupNameToID[SourceBoneName] for SourceBoneName in SourceBoneList if SourceBoneName in VertGroupNameToID]
        
        SourceSumWeight = np.sum(CurrentWeight[:, SourceBoneIDList], axis=-1)
        CurrentWeight[:, SourceBoneIDList] = 0

        # Normalize weights
        if NormalizeTransferTable:
            TargetBoneWeightSum = sum([TargetBoneWeight for TargetBoneName, TargetBoneWeight in TargetBoneList])
            TargetBoneList = [(TargetBoneName, TargetBoneWeight / TargetBoneWeightSum) for TargetBoneName, TargetBoneWeight in TargetBoneList]

        for TargetBoneName, TargetBoneWeight in TargetBoneList:
            CurrentWeight[:, VertGroupNameToID[TargetBoneName]] += (SourceSumWeight * TargetBoneWeight)

    if PurgeVertGroupWitoutBone:
        for vertexGroupName, vertexGroupID in VertGroupNameToID.items():
            if vertexGroupName not in ArmatureObject.data.bones:
                CurrentWeight[:, vertexGroupID] = 0
                

    # Remove small weights and normalize weights
    if not NormalizeOutput:
        OriginalWeightSum = np.sum(CurrentWeight, axis=-1, keepdims=True)
    
    CurrentWeight[CurrentWeight < 1e-10] = 0
    CurrentWeight /= np.sum(CurrentWeight, axis=-1, keepdims=True)
    
    if not NormalizeOutput:
        CurrentWeight *= OriginalWeightSum
    
    # Add verts back
    for VertGroupID in range(CurrentWeight.shape[1]):
        CurrentGroupVertWeights = CurrentWeight[:, VertGroupID]
        WeightMask = CurrentGroupVertWeights >= 1e-10
        if WeightMask.any():
            print(f"Added: {VertGroupIDToName[VertGroupID]}")
            CurrentVertGroup = MeshObject.vertex_groups.new(name=VertGroupIDToName[VertGroupID])
            for VertID in np.where(WeightMask)[0]:
                CurrentVertGroup.add([int(VertID)], CurrentGroupVertWeights[VertID], "REPLACE")

    # Remove Bones
    for CurrentEditBone in list(ArmatureObject.data.edit_bones): # Copy list first
        if CurrentEditBone.name in SourceBoneSet:
            CurrentBoneParent = CurrentEditBone.parent
            for CurrentBoneChild in list(CurrentEditBone.children): # Copy list first
                CurrentBoneChild.parent = CurrentBoneParent
            ArmatureObject.data.edit_bones.remove(CurrentEditBone)

    # Restore
    bpy.context.view_layer.objects.active = InitialActiveObject
    bpy.ops.object.mode_set(mode=InitialActiveMode)