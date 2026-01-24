import bpy
import os
import subprocess
from .GOHDataFile.GOHDataFile import GOHDataFile
from .PlyFormat.PlyFile import GOHPLYFile
from .GOHDataFile.MDLForBone import GetMDLForBone
from .GOHDataFile.DEFForModel import GenerateDEF
from .GOHDataFile.MTLFile import MTLFile
from ...MaterialTools.UMAMaterial import UMAMaterial
import numpy as np

def AutoSeperateMesh(MeshObject, TargetVertCount = 49152):
    # Record initial scene status
    InitialActiveObject = bpy.context.active_object
    InitialActiveMode = bpy.context.object.mode if bpy.context.object else 'OBJECT'

    # Record original material mapping    
    bpy.context.view_layer.objects.active = MeshObject
    bpy.ops.object.mode_set(mode='EDIT')
    OriginalMatrialList = list(MeshObject.data.materials)

    # Seperate Objects
    bpy.context.view_layer.objects.active = MeshObject
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.separate(type='MATERIAL')
    bpy.ops.object.mode_set(mode='OBJECT')

    result_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    resultObjectGroups = [[[result_objects[0]], len(result_objects[0].data.vertices)]]
    # Regroup seperated objects
    for CurrentObject in result_objects[1:]:
        CurrentObjectVertCount = len(CurrentObject.data.vertices)
        CurrentGroupVertCount = resultObjectGroups[-1][1]
        if CurrentObjectVertCount + CurrentGroupVertCount > TargetVertCount:
            resultObjectGroups.append([[CurrentObject],CurrentObjectVertCount])
        else:
            resultObjectGroups[-1][0].append(CurrentObject)
            resultObjectGroups[-1][1] += CurrentObjectVertCount
            
    # Join seperated objects
    for resultObjectGroup, VertCount in resultObjectGroups:
        if len(resultObjectGroup) > 1:
            with bpy.context.temp_override(
                active_object = resultObjectGroup[0],
                selected_objects = resultObjectGroup,
                selected_editable_objects = resultObjectGroup,
            ):
                bpy.ops.object.join()
    JoinedObjects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    
    # Restore original material mapping
    for CurrentPart in JoinedObjects:
        bpy.context.view_layer.objects.active = CurrentPart
        bpy.ops.object.mode_set(mode='OBJECT')
        # Get MaterialID Casting for polygons
        MatCastingDict = dict()
        for MatID, CurrentMat in enumerate(CurrentPart.data.materials):
            MatCastingDict[MatID] = OriginalMatrialList.index(CurrentMat)
        ResoredMaterialID = list()
        # Generate ID list BEFORE clearing materials, It will also affect material ID!
        for CurrentPoly in list(CurrentPart.data.polygons):
            ResoredMaterialID.append(MatCastingDict[CurrentPoly.material_index])
        # Restore original Material slots
        CurrentPart.data.materials.clear()
        for AddingMat in OriginalMatrialList:
            CurrentPart.data.materials.append(AddingMat)
        # Restore original MaterialID
        bpy.context.view_layer.objects.active = CurrentPart
        print("CastingDict Length:")
        print(len(MatCastingDict))
        print("Polygon Count:")
        print(len(CurrentPart.data.polygons))
        print(str(MatCastingDict))
        for PolyID, CurrentPoly in enumerate(CurrentPart.data.polygons):
            CurrentPoly.material_index = ResoredMaterialID[PolyID]
        CurrentPart.data.update()
        
    # Restore
    bpy.context.view_layer.objects.active = InitialActiveObject
    bpy.ops.object.mode_set(mode=InitialActiveMode)
    return [obj for obj in bpy.data.objects if obj.type == 'MESH']

def GetObjectMaterials(MeshObject, MaterialMode):
    result = {}
    if MaterialMode == "XNALARA":
        for mat_id, mat_slot in enumerate(MeshObject.material_slots):
            result[mat_id] = UMAMaterial.FromXnalaraNode(mat_slot.material)
    elif MaterialMode == "MMD":
        for mat_id, mat_slot in enumerate(MeshObject.material_slots):
            result[mat_id] = UMAMaterial.FromMMDNode(mat_slot.material)
    else:
        raise NotImplementedError(f"Unknown Material Mode: [{MaterialMode}]")
    return result

class Exporter:
    def __init__(self, BoneRef, NVTTEPath, MaterialMode, TargetShader, AddingSkeletonPrefix = ""):
        self.BoneRef = BoneRef
        self.NVTTEPath = NVTTEPath
        self.MaterialMode = MaterialMode
        self.TargetShader = TargetShader
        self.AddingSkeletonPrefix = AddingSkeletonPrefix
        self.PrefixWhiteList = ["Basis", "Skin", "None"]

    def Export(self, MeshObject, ExportBaseDir, ExportName):
        ExportRootDir = os.path.join(ExportBaseDir, ExportName)
        os.makedirs(ExportRootDir, exist_ok=True)
        UsingMatDict = GetObjectMaterials(MeshObject, self.MaterialMode)

        KeepingMateralIDSet = set()
        OldMatIDToKeepMatIDDict = dict()
        for MaterialID in UsingMatDict.keys():
            for KeepingMateralID in KeepingMateralIDSet:
                if UMAMaterial.IsSimilar(UsingMatDict[MaterialID], UsingMatDict[KeepingMateralID]):
                    OldMatIDToKeepMatIDDict[MaterialID] = KeepingMateralID
                    break
            else:
                KeepingMateralIDSet.add(MaterialID)
                OldMatIDToKeepMatIDDict[MaterialID] = MaterialID

        KeepMatIDToNewMatIDDict = dict()
        # DDS File & MTL File
        for NewMatID, KeepingMatID in enumerate(sorted(list(KeepingMateralIDSet), key=lambda x:int(x)), start=1):
            KeepMatIDToNewMatIDDict[KeepingMatID] = NewMatID
            MTLFile(UsingMatDict[KeepingMatID], self.NVTTEPath, self.TargetShader).ToGOHMTLFile(ExportRootDir, NewMatID)

        OldMatIDToNewMatIDDict = {int(OldMatID): KeepMatIDToNewMatIDDict[KeepMatID]for OldMatID, KeepMatID in OldMatIDToKeepMatIDDict.items()}

        # Ply File
        PlyFileNameList = list()
        if len(MeshObject.data.vertices) >= 57344:
            # The model is dangerous for INDX format, which only allows 65535 verticles, and verticle count could grow upon UV dividing.
            # We will try to seperate the mesh to multiple parts to avoid this problem
            SeperatedMeshObjectList = AutoSeperateMesh(MeshObject, TargetVertCount = 49152)
            for MeshPartID, MeshPartObject in enumerate(SeperatedMeshObjectList):
                PlyFileName = ExportName + f"_Part{MeshPartID}.ply"
                InputPlyFile = GOHPLYFile.FromBlenderScene(MeshPartObject, OldMatIDToNewMatIDDict, WeightPerVert=1, ScaleRatio = 0.5)
                InputPlyFile.ToPlyFile(os.path.join(ExportRootDir, PlyFileName), AddingSkePrefix=self.AddingSkeletonPrefix, SkePrefixWhiteList=self.PrefixWhiteList)
                PlyFileNameList.append(PlyFileName)

        else:
            # Standard Output
            PlyFileName = ExportName + ".ply"
            InputPlyFile = GOHPLYFile.FromBlenderScene(MeshObject, OldMatIDToNewMatIDDict, WeightPerVert=1, ScaleRatio = 0.5, )
            InputPlyFile.ToPlyFile(os.path.join(ExportRootDir, PlyFileName), AddingSkePrefix=self.AddingSkeletonPrefix, SkePrefixWhiteList=self.PrefixWhiteList)
            PlyFileNameList.append(PlyFileName)

        # MDL Export
        OutputMDL = GOHDataFile("Skeleton", None, [])
        OutputMDL.AddChild(GetMDLForBone(self.BoneRef, "Basis", PlyFileNameList, ScaleRatio = 0.5, AddingPrefix=self.AddingSkeletonPrefix, WhiteList=self.PrefixWhiteList))
        with open(os.path.join(ExportRootDir, f"{ExportName}.mdl"), "w") as OutMDLFile:
            OutMDLFile.write(OutputMDL.ToMTLString())

        # DEF Export
        with open(os.path.join(ExportRootDir, f"{ExportName}.def"), 'w') as OutDEFFile:
            OutDEFFile.write(GenerateDEF(ExportName).ToMTLString())