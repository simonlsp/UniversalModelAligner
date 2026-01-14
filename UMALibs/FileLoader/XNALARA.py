import bpy
from ..BlenderTools.BlenderTools import EnsureAddon

def LoadFile(InputPath):
    EnsureAddon("XNALaraMesh") # Check and Enable addon

    # Import file
    try:
        bpy.ops.xps_tools.import_model(
            filepath=InputPath,
            filter_glob="*.ascii;*.mesh;*.xps",

            uvDisplX=0,
            uvDisplY=0,

            joinMeshRips=False,
            joinMeshParts=False,
            markSeams=True,
            vColors=True,
            importNormals=True,

            impDefPose=False,
            connectBones=False,
            autoIk=False,
            )
        print(f"Successfully imported: {InputPath}")
    except Exception as e:
        print(f"Error importing XNALARA model: {e}")
        return False
