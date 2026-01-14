from ...BlenderTools.BoneWeightTransfer import TransferBoneWeights
import bpy

class Operator():
    def Execute(self):
        # Get object
        SceneObjects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        assert len(SceneObjects) == 1, "There should be only one mesh in the scene when calling RemoveDBones Operator!"
        MeshObject = SceneObjects[0]
        # Get TransferTable
        TransferTable = [
            [["LegD_L"], [("Leg_L", 1.0)]],
            [["KneeD_L"], [("Knee_L", 1.0)]],
            [["AnkleD_L"], [("Ankle_L", 1.0)]],
            [["LegTipEX_L"], [("ToeTip_L", 1.0)]],
            
            [["LegD_R"], [("Leg_R", 1.0)]],
            [["KneeD_R"], [("Knee_R", 1.0)]],
            [["AnkleD_R"], [("Ankle_R", 1.0)]],
            [["LegTipEX_R"], [("ToeTip_R", 1.0)]],
            
        ]
        # Execute
        TransferBoneWeights(MeshObject, TransferTable)