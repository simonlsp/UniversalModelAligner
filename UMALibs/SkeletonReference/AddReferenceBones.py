import bpy
import mathutils

class Operator:
    def __init__(self, ReferenceBoneDict):
        self.ReferenceBoneDict = ReferenceBoneDict

    def Execute(self):
        SceneObjects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        assert len(SceneObjects) == 1, "There should be only one mesh in the scene to add reference bones!"
        MeshObject = SceneObjects[0]

        for mod in MeshObject.modifiers:
            if mod.type == 'ARMATURE' and mod.object:
                ArmatureObject = mod.object
                break
        else:
            raise ValueError("Error: No armature found on mesh")
        
        # Record initial scene status
        InitialActiveObject = bpy.context.active_object
        InitialActiveMode = bpy.context.object.mode if bpy.context.object else 'OBJECT'

        ChildrenMap = dict()
        for BoneName, (BoneTrans, BoneParent) in self.ReferenceBoneDict.items():
            if BoneParent != "None":
                if BoneParent not in ChildrenMap:
                    ChildrenMap[BoneParent] = list()
                ChildrenMap[BoneParent].append(BoneName)
        
        # Create armature datablock and object
        bpy.context.view_layer.objects.active = ArmatureObject
        ArmatureObject.select_set(True)
        # Enter edit mode to create bones
        bpy.ops.object.mode_set(mode='EDIT')

        ArmatureData = ArmatureObject.data
        EditBones = ArmatureData.edit_bones

        # --- First Pass: Create all bones ---
        for BoneName, (BoneTrans, BoneParent) in self.ReferenceBoneDict.items():
            BoneTrans44 = [
                BoneTrans[0] + [0],
                BoneTrans[1] + [0],
                BoneTrans[2] + [0],
                BoneTrans[3] + [1],
            ]
            AddingBone = EditBones.new(BoneName)
            AddingBone.use_connect = False # Do not Snap to parent bone!
            AddingBone.head = (0,0,0)
            AddingBone.tail = (0,0,1)
            AddingBone.matrix = mathutils.Matrix(BoneTrans44).transposed()

        # --- Second Pass: Set parent relationships ---
        for ParentName, ChildList in ChildrenMap.items():
            for ChildName in ChildList:
                if ParentName and ChildName in EditBones:
                    EditBones[ChildName].parent = EditBones[ParentName]
        
        
        bpy.context.view_layer.objects.active = InitialActiveObject
        bpy.ops.object.mode_set(mode=InitialActiveMode)