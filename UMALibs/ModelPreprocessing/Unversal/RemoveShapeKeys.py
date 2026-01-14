import bpy

class Operator():
    def Execute(self):
        # Record initial scene status
        InitialActiveObject = bpy.context.active_object
        InitialActiveMode = bpy.context.object.mode if bpy.context.object else 'OBJECT'

        # Get object
        SceneObjects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        assert len(SceneObjects) == 1, "There should be only one mesh in the scene when calling RemoveShapeKeys Operator!"
        MeshObject = SceneObjects[0]
    
        # Switch context armature pose mode
        bpy.context.view_layer.objects.active = MeshObject
        MeshObject.select_set(True)
        bpy.ops.object.mode_set(mode='OBJECT')

        MeshObject.shape_key_clear()
                    
        # Restore Status
        bpy.context.view_layer.objects.active = InitialActiveObject
        bpy.ops.object.mode_set(mode=InitialActiveMode)