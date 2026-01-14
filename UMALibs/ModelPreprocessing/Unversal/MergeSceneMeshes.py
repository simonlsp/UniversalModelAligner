import bpy

def MergeMeshes(MeshList):
    with bpy.context.temp_override(
        active_object = MeshList[0],
        selected_objects = MeshList,
        selected_editable_objects = MeshList,
    ):
        bpy.ops.object.join()

class Operator():
    def Execute(self):
        MergeMeshes([obj for obj in bpy.data.objects if obj.type == 'MESH'])