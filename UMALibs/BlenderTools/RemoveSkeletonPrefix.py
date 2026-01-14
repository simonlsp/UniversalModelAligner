import bpy

def RemoveRefDictPrefix(InputRefDict, RemovingPrefix):
    RemovePrefixRefDict = dict()
    for BoneName, (BoneMatrix, ParentName) in InputRefDict.items():
        if BoneName.startswith(RemovingPrefix):
            NewBoneName = BoneName[len(RemovingPrefix):]
        else:
            NewBoneName = BoneName
        if ParentName.startswith(RemovingPrefix):
            NewParentName = ParentName[len(RemovingPrefix):]
        else:
            NewParentName = ParentName
        RemovePrefixRefDict[NewBoneName] = [BoneMatrix, NewParentName]
    return RemovePrefixRefDict

class Operator:
    def __init__(self, RemovingPrefix):
        self.RemovingPrefix = RemovingPrefix

    def Execute(self):
        SceneObjects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        assert len(SceneObjects) == 1, "There should be only one mesh in the scene upon Calling RemoveSkeletonPrefix!"
        MeshObject = SceneObjects[0]
        # Find armature from modifier
        for mod in MeshObject.modifiers:
            if mod.type == 'ARMATURE' and mod.object:
                ArmatureObject = mod.object
                break
        else:
            raise ValueError("Error: No armature found on mesh")
        
        # Record initial scene status
        InitialActiveObject = bpy.context.active_object
        InitialActiveMode = bpy.context.object.mode if bpy.context.object else 'OBJECT'

        # Switch context armature edit mode
        bpy.context.view_layer.objects.active = ArmatureObject
        ArmatureObject.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        
        for CurrentEditBone in ArmatureObject.data.edit_bones:
            if CurrentEditBone.name.startswith(self.RemovingPrefix):
                CurrentEditBone.name = CurrentEditBone.name[len(self.RemovingPrefix):]
        # Restore
        bpy.context.view_layer.objects.active = InitialActiveObject
        bpy.ops.object.mode_set(mode=InitialActiveMode)