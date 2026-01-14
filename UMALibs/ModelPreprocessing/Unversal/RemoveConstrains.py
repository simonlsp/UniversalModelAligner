import bpy

class Operator():
    def Execute(self):
        # Record initial scene status
        InitialActiveObject = bpy.context.active_object
        InitialActiveMode = bpy.context.object.mode if bpy.context.object else 'OBJECT'

        # Get object
        SceneObjects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        assert len(SceneObjects) == 1, "There should be only one mesh in the scene when calling RemoveConstains Operator!"
        MeshObject = SceneObjects[0]
        for mod in MeshObject.modifiers:
            if mod.type == 'ARMATURE' and mod.object:
                ArmatureObject = mod.object
                break
        else:
            raise ValueError("Error: No armature found on mesh")
    
        # Switch context armature pose mode
        bpy.context.view_layer.objects.active = ArmatureObject
        ArmatureObject.select_set(True)
        bpy.ops.object.mode_set(mode='POSE')

        for bone in ArmatureObject.pose.bones:
            for constraint in bone.constraints:
                if constraint.type == 'IK':
                    bone.constraints.remove(constraint)
                    
        # Restore Status
        bpy.context.view_layer.objects.active = InitialActiveObject
        bpy.ops.object.mode_set(mode=InitialActiveMode)