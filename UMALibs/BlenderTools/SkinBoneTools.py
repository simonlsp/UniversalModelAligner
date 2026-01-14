import bpy
import numpy as np

def GetArmatureObject(MeshObject):
    for mod in MeshObject.modifiers:
        if mod.type == 'ARMATURE' and mod.object:
            return mod.object
    else:
        raise ValueError("Error: No armature found on mesh")

def ApplyPose(MeshObject):
    # Record initial scene status
    InitialActiveObject = bpy.context.active_object
    InitialActiveMode = bpy.context.object.mode if bpy.context.object else 'OBJECT'
    
    for mod in MeshObject.modifiers:
        if mod.type == 'ARMATURE' and mod:
            ArmatureModifier = mod
            break
    else:
        raise ValueError("Error: No armature found on mesh")
    ArmatureObject = ArmatureModifier.object
    ArmatureModName = ArmatureModifier.name
    
    # Duplicate Modifier
    bpy.context.view_layer.objects.active = MeshObject
    MeshObject.select_set(True)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.modifier_copy(modifier=ArmatureModName)
    NewModifier = MeshObject.modifiers[list(MeshObject.modifiers).index(ArmatureModifier) + 1]
    bpy.context.view_layer.update()

    # Apply Original Modifier
    bpy.ops.object.make_single_user(object=True, obdata=True)
    bpy.ops.object.modifier_apply(modifier=ArmatureModName)
    NewModifier.name = ArmatureModName
    bpy.context.view_layer.update()

    # Set Rest Pose
    bpy.context.view_layer.objects.active = ArmatureObject
    ArmatureObject.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.armature_apply()
    bpy.context.view_layer.update()

    # Restore Status
    bpy.context.view_layer.objects.active = InitialActiveObject
    bpy.ops.object.mode_set(mode=InitialActiveMode)