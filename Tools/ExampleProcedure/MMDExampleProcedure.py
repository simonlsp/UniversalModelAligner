import sys
import os
import bpy


if __name__ == "__main__":
    # Get arguments after "--"
    argv = sys.argv
    try:
        # Find the index of "--"
        idx = argv.index("--")
        # Get everything after "--"
        script_args = argv[idx + 1:]
    except ValueError:
        script_args = []
    if len(script_args) != 2:
        raise ValueError("Failed to get args!")
    
    NVTTE_Path = r"C:\Program Files\NVIDIA Corporation\NVIDIA Texture Tools\nvtt_export.exe"
    ScriptRoot = r"D:\Develop\UniversalModelAligner"
    if ScriptRoot not in sys.path:
        sys.path.append(ScriptRoot)


class UMAProcedure:
    def __init__(self):
        # NameDistributor
        from UMALibs.NameDistributor.Increment import NameDistributor as IncrementNameDistributor
        self.NameDistributor = IncrementNameDistributor(Prefix="Model")
        # FileImporter
        from UMALibs.FileLoader.MMD import LoadFile as MMDLoadFile
        self.FileImporter = MMDLoadFile
        # ---------- Preprocessing ----------
        from UMALibs.ModelPreprocessing.MMD.RemoveRigid import Operator as RemoveRigidOperator
        from UMALibs.ModelPreprocessing.Unversal.MergeSceneMeshes import Operator as MergeSceneMeshesOperator
        from UMALibs.ModelPreprocessing.Unversal.RemoveShapeKeys import Operator as RemoveShapeKeysOperator
        from UMALibs.ModelPreprocessing.Unversal.RemoveConstrains import Operator as RemoveConstrainsOperator
        from UMALibs.ModelPreprocessing.Unversal.BoneSimplification import Operator as BoneSimplificationOperator
        from UMALibs.CoreBoneSets.MMD import CoreBoneSet as MMDCoreBoneSet
        from UMALibs.ModelPreprocessing.MMD.MergeDBones import Operator as MergeDBonesOperator
        self.PreprocessProcedure = [
            RemoveRigidOperator(RemoveJoints=True, RemoveRigidBodies=True),
            MergeSceneMeshesOperator(),
            RemoveShapeKeysOperator(),
            MergeDBonesOperator(),
            BoneSimplificationOperator(CoreBoneSet=MMDCoreBoneSet),
            RemoveConstrainsOperator(),
        ]
        # ---------- Alignment ----------
        from UMALibs.SkeletonReference.AddReferenceBones import Operator as AddReferenceBoneOperator
        from UMALibs.SkeletonReference.ReferenceDicts.GOH.Gan_V2_Ref import RefDict as GOHGANV2RefDict
        from UMALibs.SkeletonAlignment.GOH import Opreator as GOHSkeletonAlignmentOpreator
        from UMALibs.JointDicts.MMD_JointDict import JointDict as MMDJointDict
        self.AlignmentProcedure = [
            AddReferenceBoneOperator(GOHGANV2RefDict),
            GOHSkeletonAlignmentOpreator(MMDJointDict)
        ]
        # ---------- Weight Transfer ----------
        from UMALibs.WeightTransfer.WeightTransferTables.MMD_TO_GOH import TransferTable as MMD_GOHTranfserTable
        self.GOHBonePrefix = r"GFA_MWT_SKE_"
        self.WeightTransferTable = MMD_GOHTranfserTable
        # ---------- Exporting ----------
        from UMALibs.Exporters.GOH.GOHExporter import Exporter as GOHExporter
        from UMALibs.BlenderTools.RemoveSkeletonPrefix import Operator as RemoveSkeletonPrefixOperator
        from UMALibs.BlenderTools.RemoveSkeletonPrefix import RemoveRefDictPrefix

        SkeletonPrefix = "GAN_"
        self.Exporter = GOHExporter(RemoveRefDictPrefix(GOHGANV2RefDict, self.GOHBonePrefix), NVTTE_Path, MaterialMode="MMD", TargetShader="Vallina", AddingSkeletonPrefix=SkeletonPrefix)
        self.GOHBonePrefixRemover = RemoveSkeletonPrefixOperator(self.GOHBonePrefix)
    
    def Execute(self, InputModelPath, ExportBaseDir):
        from UMALibs.BlenderTools.BlenderTools import RemoveAllObjects
        from UMALibs.BlenderTools.BoneWeightTransfer import TransferBoneWeights
        from UMALibs.WeightTransfer.MakePurgeTransferTable import MakePurgeTransferTable
        # Clear Current Scene
        RemoveAllObjects()
        # Get Model Name
        CurrentModelName = self.NameDistributor.GetName(InputModelPath)
        # Load Model File
        self.FileImporter(InputModelPath)
        # ---------- Preprocessing ----------
        for Opreator in self.PreprocessProcedure:
            Opreator.Execute()
        # ---------- You could make a save here ----------

        # ---------- Alignment ----------
        for Opreator in self.AlignmentProcedure:
            Opreator.Execute()
        # ---------- You could make a save here ----------
        
        # ---------- Weight Transfer ----------
        SceneObjects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        assert len(SceneObjects) == 1, "There should be only one mesh in the scene upon aligning!"
        MeshObject = SceneObjects[0]
        # Find armature from modifier
        for mod in MeshObject.modifiers:
            if mod.type == 'ARMATURE' and mod.object:
                ArmatureObject = mod.object
                break
        else:
            raise ValueError("Error: No armature found on mesh")
        WeightPurgeTable = MakePurgeTransferTable(ArmatureObject, self.WeightTransferTable, self.GOHBonePrefix)
        TransferBoneWeights(MeshObject, WeightPurgeTable, PurgeVertGroupWitoutBone=True)
        # ---------- You could make a save here ----------

        # ---------- Export ----------
        self.GOHBonePrefixRemover.Execute()
        self.Exporter.Export(MeshObject, ExportBaseDir, CurrentModelName)

if __name__ == "__main__":
    Procedure = UMAProcedure()
    InputFile = script_args[0]
    OutputDir = script_args[1]
    Procedure.Execute(InputFile, OutputDir)