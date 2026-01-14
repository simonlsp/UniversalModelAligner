import bpy
from ...BlenderTools.BoneWeightTransfer import TransferBoneWeights

def GetFirstParentInSet(EditBone, BoneNameSet):
    if not EditBone.parent:
        return None
    elif EditBone.name in BoneNameSet:
        return None
    elif EditBone.parent.name in BoneNameSet:
        return EditBone.parent
    else:
        return GetFirstParentInSet(EditBone.parent, BoneNameSet)

def GetSimplificationTable(MeshObject, CoreBoneSet):
    SimplificationTable = list()
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
    
    for CurrentEditBone in ArmatureObject.data.edit_bones:
        CurrentBoneCoreParent = GetFirstParentInSet(CurrentEditBone, CoreBoneSet)
        if CurrentBoneCoreParent:
            SimplificationTable.append([[CurrentEditBone.name, ], [(CurrentBoneCoreParent.name, 1.0)]])

    # Restore
    bpy.context.view_layer.objects.active = InitialActiveObject
    bpy.ops.object.mode_set(mode=InitialActiveMode)

    return SimplificationTable

class Operator():
    def __init__(self, CoreBoneSet):
        self.CoreBoneSet = CoreBoneSet

    def Execute(self):
        # Get object
        SceneObjects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        assert len(SceneObjects) == 1, "There should be only one mesh in the scene when calling BoneSimplification Operator!"
        MeshObject = SceneObjects[0]
        # Get TransferTable
        SimplificationTable = GetSimplificationTable(MeshObject, self.CoreBoneSet)
        # Execute
        TransferBoneWeights(MeshObject, SimplificationTable)
        