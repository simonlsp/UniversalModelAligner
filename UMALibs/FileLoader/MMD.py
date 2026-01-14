import bpy
from ..BlenderTools.BlenderTools import EnsureAddon

def LoadFile(InputPath):
    EnsureAddon("mmd_tools") # Check and Enable addon
    
    # Import file
    try:
        bpy.ops.mmd_tools.import_model(
            filepath=InputPath,
            types={'MESH', 'ARMATURE', 'PHYSICS', 'DISPLAY', 'MORPHS'},
            scale=0.08,
            clean_model=True,
            remove_doubles=False,
            fix_IK_links=False,
            # ik_loop_factor=5,
            apply_bone_fixed_axis=False,
            rename_bones=True,
            use_underscore=False,
            dictionary='INTERNAL',
            use_mipmap=True,
            sph_blend_factor=1.0,
            spa_blend_factor=1.0,
            log_level='WARNING',
            save_log=False
        )
        print(f"Successfully imported: {InputPath}")
    except Exception as e:
        print(f"Error importing MMD model: {e}")
        return False