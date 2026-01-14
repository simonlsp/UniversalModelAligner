

import os
import json
import subprocess
import struct
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, BinaryIO, Dict, Any
from .D3DFVF import D3DFVF
from .MeshFlag import GOHPLYMeshFlag

@dataclass
class GOHPLYMesh:
    VertexFormat: int = 0
    FirstFaceID: int = 0
    FaceCount: int = 0
    Flags: int = 0
    SpecularColor: int = 0
    TextureRawPath: str = ""
    SubskinBones: List[int] = field(default_factory=list)

class GOHPLYFile:
    def __init__(
        self,
        BindingBox,
        BoneNameList,
        MeshList,
        VertexDataStructure,
        VertexData,
        FaceCount,
        FaceData,
    ):
        self.BindingBox = BindingBox
        self.BoneNameList = BoneNameList
        self.MeshList = MeshList
        self.VertexDataStructure = VertexDataStructure
        self.VertexData = VertexData
        self.FaceCount = FaceCount
        self.FaceData = FaceData

    @staticmethod
    def FromPlyFile(FilePath):
        with open(FilePath, 'rb') as Inputfile:
            # Read file signture
            FileSignature = Inputfile.read(4).decode('ascii')
            assert FileSignature in ['EPLY'], f"Invalid PLY signature: {FileSignature}. Expected or EPLY (We do not support BPLY, as we use seperated mtl file)."

            PLY_Mesh_List = list()
            BoneNameList = list()
            GLOBAL_FVF = None
            VertexDataStructure = None
            VertexData = None
            FaceCount = None
            FaceData = None
            while True:
                section_id = Inputfile.read(4).decode('ascii').upper()
                if not section_id or len(section_id) < 4:
                    break

                # Binding Box
                if section_id == 'BNDS':
                    BindingBox = struct.unpack('<6f', Inputfile.read(24))
                
                # SKIN (Bones)
                elif section_id == 'SKIN':
                    BoneCount = struct.unpack('<I', Inputfile.read(4))[0]
                    for _ in range(BoneCount):
                        BoneNameLength = struct.unpack('<B', Inputfile.read(1))[0]
                        BoneName = Inputfile.read(BoneNameLength).decode('ascii')
                        BoneNameList.append(BoneName)

                # Mesh (Material)
                elif section_id == 'MESH':
                    CurrentMesh = GOHPLYMesh()
                    # Mesh Header
                    CurrentMesh.VertexFormat = struct.unpack('<I', Inputfile.read(4))[0]
                    CurrentMesh.FirstFaceID = struct.unpack('<I', Inputfile.read(4))[0]
                    CurrentMesh.FaceCount = struct.unpack('<I', Inputfile.read(4))[0]
                    CurrentMesh.Flags = struct.unpack('<I', Inputfile.read(4))[0]
                    # Parse Mesh Flags
                    if CurrentMesh.Flags & GOHPLYMeshFlag.SPECULAR:
                        CurrentMesh.SpecularColor = struct.unpack('<I', Inputfile.read(4))[0]
                    if CurrentMesh.Flags & GOHPLYMeshFlag.BUMP:
                        raise AssertionError("We are not expecting forced bump in this file.")
                    # Mesh Textures
                    TexturePathLen = struct.unpack('<B', Inputfile.read(1))[0] # Only one texture path is expected, as we only support EPLY, not BPLY
                    if TexturePathLen:
                        CurrentMesh.TextureRawPath = Inputfile.read(TexturePathLen).decode('ascii')
                    else:
                        CurrentMesh.TextureRawPath = ""
                        Inputfile.read(1)  # Skip null byte
                    # Mesh Subskin
                    if CurrentMesh.Flags & GOHPLYMeshFlag.SUBSKIN:
                        SubSkinBoneCount = struct.unpack('<B', Inputfile.read(1))[0]
                        CurrentMesh.SubskinBones = list(Inputfile.read(SubSkinBoneCount))
                    PLY_Mesh_List.append(CurrentMesh)
                    GLOBAL_FVF = D3DFVF.Add_FVF(GLOBAL_FVF, CurrentMesh.VertexFormat)
                
                # VERT (Vertex)
                elif section_id == 'VERT':
                    VertCount = struct.unpack('<I', Inputfile.read(4))[0]
                    VertSize = struct.unpack('<H', Inputfile.read(2))[0]
                    VertFlags = struct.unpack('<H', Inputfile.read(2))[0]
                    VertexDataStructure = D3DFVF.GetVertexDataStructure(GLOBAL_FVF, VertSize)

                    VertDataTotalLength = VertSize * VertCount
                    VertexData = Inputfile.read(VertDataTotalLength)

                # INDX(Face)
                elif section_id == 'INDX' or section_id == 'IND4':
                    FaceVertCount = struct.unpack('<I', Inputfile.read(4))[0]
                    FaceCount = FaceVertCount // 3
                    if section_id == 'INDX':
                        FaceData = struct.unpack(f'<{FaceVertCount}H', Inputfile.read(FaceVertCount * 2))
                    elif section_id == 'IND4':
                        ReadData = Inputfile.read(FaceVertCount * 4)
                        FaceData = struct.unpack(f'<{FaceVertCount}I', Inputfile.read(FaceVertCount * 4))
                else:
                    # Unknown section - try to continue but warn
                    pos = Inputfile.tell()
                    raise ValueError(f"Unknown section '{section_id}' at offset 0x{pos-4:X}")
                
            return GOHPLYFile(BindingBox,BoneNameList,PLY_Mesh_List,VertexDataStructure,VertexData,FaceCount,FaceData)
        
    @staticmethod
    def From3dsmaxScene(TargetMesh, MateraiIDCastDict, UVChannel = 1, WeightPerVert = 1, ScaleRatio = 0.5):
        from pymxs import runtime as rt
        # Checking and preparing
        assert rt.ClassOf(TargetMesh) == rt.Editable_mesh, "Target mesh should be an editable mesh!"
        if hasattr(TargetMesh, "skin") and TargetMesh.skin:
            TargetSkin = TargetMesh.skin
        else:
            raise AssertionError(f"TargetMesh [{TargetMesh.name}] Has no skin modifier, could not export.")

        rt.select(TargetMesh)
        rt.modPanel.setCurrentObject(TargetSkin)

        # File Header
        FileSignature = "EPLY"
        # assert WeightPerVert in {1,2,3,4}, "WeightPerVert must be an int in {1,2,3,4}!"
        assert WeightPerVert in {1}, "WeightPerVert must be an int in {1}!"
        VertexDataStructure = [('POSXYZ', 3), ('BONEWEIGHT', WeightPerVert), ('MatrixIndices', 1), ('NORMAL', 3), ('UVW', 2)]
        
        ## Binding Box
        BindingBox = (
            TargetMesh.min.x * ScaleRatio,
            TargetMesh.min.y * ScaleRatio,
            TargetMesh.min.z * ScaleRatio,
            TargetMesh.max.x * ScaleRatio,
            TargetMesh.max.y * ScaleRatio,
            TargetMesh.max.z * ScaleRatio
            )
        
        # SKIN (Bones)
        BoneNameList = list()
        for i in range(1, rt.skinOps.GetNumberBones(TargetSkin) + 1):
            BoneNameList.append(str(rt.skinOps.GetBoneName(TargetSkin, i, 0)).lower())
        BoneNameList += ["basis",]
        
        # Get UV Verts Casting
        NextNewVertID = 0
        NewVertDict = dict() # NewVertID: (RawVertID, (U, V))
        RawVertToNewVertDict = dict() # RawVertID: NewVertIDList
        UVVertToNewVertDict = dict() # UV_VertID: NewVertID
        for face_idx in range(1, rt.getNumFaces(TargetMesh) + 1):  # MaxScript uses 1-based indexing
            # Get face vertex indices (returns Point3)
            VertIDPoint3 = rt.getFace(TargetMesh, face_idx)
            UVVertIDPoint3 = rt.meshop.getMapFace(TargetMesh, UVChannel, face_idx)
            VertIDPoint3_INT = [int(VertIDPoint3.x), int(VertIDPoint3.y), int(VertIDPoint3.z)]
            UVVertIDPoint3_INT = [int(UVVertIDPoint3.x), int(UVVertIDPoint3.y), int(UVVertIDPoint3.z)]
            for UV_Vert_ID, Raw_Vert_ID in zip(UVVertIDPoint3_INT, VertIDPoint3_INT):
                UV_Value = rt.meshop.getMapVert(TargetMesh, UVChannel, UV_Vert_ID)
                # Add a new vert if brand new vert is being added
                if Raw_Vert_ID not in RawVertToNewVertDict:
                    RawVertToNewVertDict[Raw_Vert_ID] = list()

                for New_Vert_ID in RawVertToNewVertDict[Raw_Vert_ID]:
                    # Find a correct new vert to attach
                    NewVertUV = NewVertDict[New_Vert_ID][1]
                    UVDistance = ((NewVertUV[0] - UV_Value.x) ** 2.0 + (NewVertUV[1] - UV_Value.y) ** 2.0) ** 0.5
                    if UVDistance < 0.001:
                        UVVertToNewVertDict[UV_Vert_ID] = New_Vert_ID
                        break
                else:
                    # Need to add a new vert
                    AddingNewVertID = NextNewVertID
                    NextNewVertID += 1

                    NewVertDict[AddingNewVertID] = (Raw_Vert_ID, (UV_Value.x, UV_Value.y))
                    RawVertToNewVertDict[Raw_Vert_ID].append(AddingNewVertID)
                    UVVertToNewVertDict[UV_Vert_ID] = AddingNewVertID

        # Faces (Also pre-process Mesh!)
        FaceWithMatList = list()
        for face_idx in range(1, rt.getNumFaces(TargetMesh) + 1):  # MaxScript uses 1-based indexing
            # Get face vertex indices (returns Point3)
            UVVertIDPoint3 = rt.meshop.getMapFace(TargetMesh, UVChannel, face_idx)
            VertIDPoint3 = rt.getFace(TargetMesh, face_idx)
            # Get material ID for this face
            OldMaterialID = rt.getFaceMatID(TargetMesh, face_idx)
            MaterialID = MateraiIDCastDict[OldMaterialID]
            # USE XZY to invert R-hand to L-hand
            NewVertIDWithMatList = [UVVertToNewVertDict[UVVertIDPoint3.x], UVVertToNewVertDict[UVVertIDPoint3.z], UVVertToNewVertDict[UVVertIDPoint3.y]]
            FaceWithMatList.append((NewVertIDWithMatList[0], NewVertIDWithMatList[1], NewVertIDWithMatList[2], MaterialID))
        FaceWithMatSortedList = sorted(FaceWithMatList, key=lambda x: x[-1])
        ## Finished
        FaceCount = len(FaceWithMatList)
        FaceData = [VertID for FaceWithMat in FaceWithMatSortedList for VertID in FaceWithMat[:3]]

        # Mesh (Material)
        PLY_Mesh_List = list()
        MatSortedList = [FaceWithMat[-1] for FaceWithMat in FaceWithMatSortedList]
        UniqueSortedMat = sorted(list(set(MatSortedList)))
        for MaterialID in UniqueSortedMat:
            CurrentMesh = GOHPLYMesh()
            # Mesh Header
            CurrentMesh.FirstFaceID = MatSortedList.index(MaterialID)
            CurrentMesh.FaceCount = MatSortedList.count(MaterialID)
            CurrentMesh.VertexFormat = D3DFVF.VertexDataStructureToFVF(VertexDataStructure)
            CurrentMesh.Flags = GOHPLYMeshFlag.GetMeshFlagFromSubMaterial(TargetMesh, MaterialID)
            CurrentMesh.SpecularColor = 0 # Process later with vertex???
            CurrentMesh.TextureRawPath = f"Mat_{MaterialID}.mtl"
            CurrentMesh.SubskinBones = list(range(len(BoneNameList))) # Must we use subskin?
            PLY_Mesh_List.append(CurrentMesh)

        # VERT (Vertex)
        ## Get Real Normal
        Vert_Normal_Dict = dict()
        rt.addModifier(TargetMesh, rt.EditNormals())
        EditNorm = TargetMesh.modifiers[0]
        rt.select(TargetMesh)
        rt.setCommandPanelTaskMode(rt.name("modify"))
        rt.modPanel.setCurrentObject(EditNorm)
        print(EditNorm.GetNumFaces())
        for FaceID in range(1, EditNorm.GetNumFaces() + 1):
            for CornerID in range(1, EditNorm.GetFaceDegree(FaceID) + 1):
                VertID = EditNorm.GetVertexID(FaceID, CornerID)
                if VertID not in Vert_Normal_Dict:
                    Vert_Normal_Dict[VertID] = list()
                Vert_Normal_Dict[VertID].append(EditNorm.GetNormal(EditNorm.GetNormalID(FaceID, CornerID)))
        rt.deleteModifier(TargetMesh, EditNorm)
        for VertID in Vert_Normal_Dict.keys():
            SumNormal = sum(Vert_Normal_Dict[VertID])
            SumNormalLength = ((SumNormal.x ** 2) + (SumNormal.y ** 2) + (SumNormal.z ** 2)) ** 0.5
            Vert_Normal_Dict[VertID] = SumNormal / SumNormalLength

        ## Get Vert data
        VertexData = b""
        for NewVertID in range(NextNewVertID):
            RawVertexID, (VertU, VertV) = NewVertDict[NewVertID]
            # Flip VertV
            VertV = 1-VertV

            VertexBoneWeightCount = rt.skinOps.GetVertexWeightCount(TargetSkin, RawVertexID)
            BoneIDList = list()
            BoneWeightList = list()
            for i in range(1, VertexBoneWeightCount + 1):
                BoneID = rt.skinOps.GetVertexWeightBoneID(TargetSkin, RawVertexID, i)
                WeightValue = rt.skinOps.GetVertexWeight(TargetSkin, RawVertexID, i)
                BoneIDList.append(BoneID) # Change from 1-offset to 0-offset!
                BoneWeightList.append(WeightValue)
            
            # Sort by weight
            SortedOrder = [ID for ID, weight in sorted(list(enumerate(BoneWeightList)), key=lambda x: x[1], reverse=True)]
            BoneIDList = [BoneIDList[ID] for ID in SortedOrder]
            BoneWeightList = [BoneWeightList[ID] for ID in SortedOrder]
            
            # Trim Bone Group To WeightPerVert + 1
            if len(BoneIDList) < WeightPerVert + 1:
                BoneIDList += [0] * (WeightPerVert + 1-len(BoneIDList))
                BoneWeightList += [0.0] * (WeightPerVert + 1-len(BoneWeightList))
            elif len(BoneIDList) > WeightPerVert:
                BoneIDList = BoneIDList[:WeightPerVert + 1]
                BoneWeightList = BoneWeightList[:WeightPerVert + 1]

            ## Matrix is always 4 len (4*8)
            if len(BoneIDList) < 4:
                BoneIDList += [0] * (4-len(BoneIDList))
            ## Normalize weight
            BoneWeightListSum = sum(BoneWeightList)
            for i in range(len(BoneWeightList)):
                BoneWeightList[i] /= BoneWeightListSum
            ## Remove Last weight (Auto cacluated)
            BoneWeightList = BoneWeightList[:WeightPerVert]

            # Write Position
            VertPos = rt.getVert(TargetMesh, RawVertexID) * ScaleRatio
            VertexData += struct.pack('<3f', *[VertPos.x, VertPos.y, VertPos.z])
            # Write Boneweight
            VertexData += struct.pack(f'<{WeightPerVert}f', *BoneWeightList)
            # Write BoneMatrix
            VertexData += struct.pack(f'<4B', *BoneIDList)
            # Write Normal
            VertNrm = Vert_Normal_Dict[RawVertexID]
            VertexData += struct.pack('<3f', *[VertNrm.x, VertNrm.y, VertNrm.z])
            # Write UVW
            VertexData += struct.pack('<2f', *[VertU, VertV])

        return GOHPLYFile(BindingBox,BoneNameList,PLY_Mesh_List,VertexDataStructure,VertexData,FaceCount,FaceData)
    
    @staticmethod
    def FromBlenderScene(MeshObject, MaterialIDCastDict, WeightPerVert = 1, ScaleRatio = 0.5):
        import bpy
        from mathutils import Matrix, Vector

        # Find armature from modifier
        for mod in MeshObject.modifiers:
            if mod.type == 'ARMATURE' and mod.object:
                ArmatureObject = mod.object
                break
        else:
            raise ValueError("Error: No armature found on mesh")

        # Record initial scene status
        InitialActiveObject = bpy.context.active_object
        InitialActiveMode = bpy.context.object.mode if bpy.context.object else 'OBJECT'

        # Switch context to OBJECT mode
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Set Vertex Format
        assert WeightPerVert in {1}, "WeightPerVert must be an int in {1}!"
        VertexDataStructure = [('POSXYZ', 3), ('BONEWEIGHT', WeightPerVert), ('MatrixIndices', 1), ('NORMAL', 3), ('UVW', 2)]

        ## Binding Box
        EvalObject = MeshObject.evaluated_get(bpy.context.evaluated_depsgraph_get())
        bbox_world = [MeshObject.matrix_world @ Vector(corner) for corner in EvalObject.bound_box]
        BindingBox = (
            min(v.x for v in bbox_world) * ScaleRatio,
            min(v.y for v in bbox_world) * ScaleRatio,
            min(v.z for v in bbox_world) * ScaleRatio,
            max(v.x for v in bbox_world) * ScaleRatio,
            max(v.y for v in bbox_world) * ScaleRatio,
            max(v.z for v in bbox_world) * ScaleRatio
            )

        # SKIN (Bones)
        BoneNameList = [VertGroup.name.lower() for VertGroup in list(MeshObject.vertex_groups)] + ["basis",]

        # Get UV Verts Casting

        NextNewVertID = 0
        NewVertDict = dict() # NewVertID: (RawVertID, (U, V))
        RawVertToNewVertDict = dict() # RawVertID: NewVertIDList
        UVVertToNewVertDict = dict() # UV_VertID: NewVertID

        ActiveUVChannel = MeshObject.data.uv_layers.active.data
        for CurrentPoly in MeshObject.data.polygons:
            UVVertIDList = list(CurrentPoly.loop_indices)
            if len(UVVertIDList) != 3:
                raise ValueError("Some faces are not triangles!")
            VertIDList = [MeshObject.data.loops[LoopID].vertex_index for LoopID in UVVertIDList]
            UVValueList = [ActiveUVChannel[LoopID].uv for LoopID in UVVertIDList]
            for UV_Vert_ID, Raw_Vert_ID, UV_Value in zip(UVVertIDList, VertIDList, UVValueList):
                if Raw_Vert_ID not in RawVertToNewVertDict:
                    RawVertToNewVertDict[Raw_Vert_ID] = list()

                for New_Vert_ID in RawVertToNewVertDict[Raw_Vert_ID]:
                    # Find a correct new vert to attach
                    NewVertUV = NewVertDict[New_Vert_ID][1]
                    UVDistance = ((NewVertUV[0] - UV_Value.x) ** 2.0 + (NewVertUV[1] - UV_Value.y) ** 2.0) ** 0.5
                    if UVDistance < 0.001:
                        UVVertToNewVertDict[UV_Vert_ID] = New_Vert_ID
                        break

                else:
                    # Need to add a new vert
                    AddingNewVertID = NextNewVertID
                    NextNewVertID += 1

                    NewVertDict[AddingNewVertID] = (Raw_Vert_ID, (UV_Value.x, UV_Value.y))
                    RawVertToNewVertDict[Raw_Vert_ID].append(AddingNewVertID)
                    UVVertToNewVertDict[UV_Vert_ID] = AddingNewVertID

        # Faces (Also pre-process Mesh!)
        FaceWithMatList = list()
        for CurrentPoly in MeshObject.data.polygons:
            UVVertIDList = list(CurrentPoly.loop_indices)
            # Get material ID for this face
            OldMaterialID = CurrentPoly.material_index
            MaterialID = MaterialIDCastDict[OldMaterialID]
            # USE XZY to invert R-hand to L-hand
            InvertedNewVertIDList = [UVVertToNewVertDict[UVVertIDList[0]], UVVertToNewVertDict[UVVertIDList[2]], UVVertToNewVertDict[UVVertIDList[1]]]
            FaceWithMatList.append((InvertedNewVertIDList[0], InvertedNewVertIDList[1], InvertedNewVertIDList[2], MaterialID))
        FaceWithMatSortedList = sorted(FaceWithMatList, key=lambda x: x[-1])

        ## Finished
        FaceCount = len(FaceWithMatList)
        FaceData = [VertID for FaceWithMat in FaceWithMatSortedList for VertID in FaceWithMat[:3]]

        # Mesh (Material)
        PLY_Mesh_List = list()
        MatSortedList = [FaceWithMat[-1] for FaceWithMat in FaceWithMatSortedList]
        UniqueSortedMat = sorted(list(set(MatSortedList)))
        for MaterialID in UniqueSortedMat:
            CurrentMesh = GOHPLYMesh()
            # Mesh Header
            CurrentMesh.FirstFaceID = MatSortedList.index(MaterialID)
            CurrentMesh.FaceCount = MatSortedList.count(MaterialID)
            CurrentMesh.VertexFormat = D3DFVF.VertexDataStructureToFVF(VertexDataStructure)
            CurrentMesh.Flags = GOHPLYMeshFlag.GetDefaultMeshFlag()
            CurrentMesh.SpecularColor = 0 # Process later with vertex???
            CurrentMesh.TextureRawPath = f"Mat_{MaterialID}.mtl"
            CurrentMesh.SubskinBones = list(range(len(BoneNameList))) # Must we use subskin?
            PLY_Mesh_List.append(CurrentMesh)

        # VERT (Vertex)
        ## Normal
        MeshObject.data.calc_normals_split()
        Vert_Normal_Dict = dict()
        for loop in MeshObject.data.loops:
            VertID = loop.vertex_index
            if VertID not in Vert_Normal_Dict:
                Vert_Normal_Dict[VertID] = list()
                Vert_Normal_Dict[VertID].append(loop.normal)

        for VertID in Vert_Normal_Dict.keys():
            if len(Vert_Normal_Dict[VertID]) == 1:
                SumNormal = Vert_Normal_Dict[VertID][0]
            else:
                SumNormal = sum(Vert_Normal_Dict[VertID])
            Vert_Normal_Dict[VertID] = SumNormal / SumNormal.length

        ## Get Vert data
        VertexData = b""
        WorldMatrix = MeshObject.matrix_world
        for NewVertID in range(NextNewVertID):
            RawVertexID, (VertU, VertV) = NewVertDict[NewVertID]
            # Flip VertV
            VertV = 1-VertV

            BoneIDList = list()
            BoneWeightList = list()
            RawVertex = MeshObject.data.vertices[RawVertexID]
            for VertGroup in list(RawVertex.groups):
                BoneIDList.append(VertGroup.group + 1) # Blender Group starts from 0
                BoneWeightList.append(VertGroup.weight)
            
            # Sort by weight
            SortedOrder = [ID for ID, weight in sorted(list(enumerate(BoneWeightList)), key=lambda x: x[1], reverse=True)]
            BoneIDList = [BoneIDList[ID] for ID in SortedOrder]
            BoneWeightList = [BoneWeightList[ID] for ID in SortedOrder]
            
            # Trim Bone Group To WeightPerVert + 1
            if len(BoneIDList) < WeightPerVert + 1:
                BoneIDList += [0] * (WeightPerVert + 1-len(BoneIDList))
                BoneWeightList += [0.0] * (WeightPerVert + 1-len(BoneWeightList))
            elif len(BoneIDList) > WeightPerVert:
                BoneIDList = BoneIDList[:WeightPerVert + 1]
                BoneWeightList = BoneWeightList[:WeightPerVert + 1]

            ## Matrix is always 4 len (4*8)
            if len(BoneIDList) < 4:
                BoneIDList += [0] * (4-len(BoneIDList))
            ## Normalize weight
            BoneWeightListSum = sum(BoneWeightList)
            for i in range(len(BoneWeightList)):
                BoneWeightList[i] /= BoneWeightListSum
            ## Remove Last weight (Auto cacluated)
            BoneWeightList = BoneWeightList[:WeightPerVert]

            # Write Position
            VertPos = (WorldMatrix @ RawVertex.co) * ScaleRatio
            VertexData += struct.pack('<3f', *[VertPos.x, VertPos.y, VertPos.z])
            # Write Boneweight
            VertexData += struct.pack(f'<{WeightPerVert}f', *BoneWeightList)
            # Write BoneMatrix
            VertexData += struct.pack(f'<4B', *BoneIDList)
            # Write Normal
            VertNrm = WorldMatrix @ Vert_Normal_Dict[RawVertexID]
            VertexData += struct.pack('<3f', *[VertNrm.x, VertNrm.y, VertNrm.z])
            # Write UVW
            VertexData += struct.pack('<2f', *[VertU, VertV])

        # Restore
        bpy.context.view_layer.objects.active = InitialActiveObject
        bpy.ops.object.mode_set(mode=InitialActiveMode)
        return GOHPLYFile(BindingBox,BoneNameList,PLY_Mesh_List,VertexDataStructure,VertexData,FaceCount,FaceData)


    def ToPlyFile(self, FilePath, Use32BitFace=False):
        with open(FilePath, 'wb') as Outputfile:
            # FileSignature
            Outputfile.write('EPLY'.encode('ascii'))
            
            # BNDS (Binding box)
            Outputfile.write('BNDS'.encode('ascii'))
            Outputfile.write(struct.pack('<6f', *self.BindingBox))
            
            # SKIN (Bones)
            Outputfile.write('SKIN'.encode('ascii'))
            Outputfile.write(struct.pack('<I', len(self.BoneNameList)))
            for BoneName in self.BoneNameList:
                assert len(BoneName) < 255, "Length of all bone names must be smaller than 255, but current bone's name is [" + BoneName + "]!"
                Outputfile.write(struct.pack('<B', len(BoneName)))
                Outputfile.write(BoneName.encode('ascii'))

            # SKIN (Bones)
            for CurrentMesh in self.MeshList:
                Outputfile.write('MESH'.encode('ascii'))
                Outputfile.write(struct.pack('<I', CurrentMesh.VertexFormat))
                Outputfile.write(struct.pack('<I', CurrentMesh.FirstFaceID))
                Outputfile.write(struct.pack('<I', CurrentMesh.FaceCount))
                Outputfile.write(struct.pack('<I', CurrentMesh.Flags))
                if CurrentMesh.Flags & GOHPLYMeshFlag.SPECULAR:
                    Outputfile.write(struct.pack('<I', CurrentMesh.SpecularColor))
                if CurrentMesh.Flags & GOHPLYMeshFlag.BUMP:
                    raise AssertionError("We are not expecting forced bump in this file.")
                
                if CurrentMesh.TextureRawPath != "":
                    assert len(CurrentMesh.TextureRawPath) < 255, "Length of all texture paths must be smaller than 255, but current texture's path is [" + CurrentMesh.TextureRawPath + "]!"
                    Outputfile.write(struct.pack('<B', len(CurrentMesh.TextureRawPath)))
                    Outputfile.write(CurrentMesh.TextureRawPath.encode('ascii'))
                else:
                    Outputfile.write(struct.pack('<B', 0))
                    Outputfile.write(struct.pack('<B', 0))
                
                if CurrentMesh.Flags & GOHPLYMeshFlag.SUBSKIN:
                    SubskinBoneCount = len(CurrentMesh.SubskinBones)
                    Outputfile.write(struct.pack('<B', SubskinBoneCount))
                    Outputfile.write(struct.pack(f'<{SubskinBoneCount}B', *CurrentMesh.SubskinBones))
            
            # VERT (Vertex)
            Outputfile.write('VERT'.encode('ascii'))
            VertSize = sum([DataSize for DataName, DataSize in self.VertexDataStructure]) * 4
            VertCount = len(self.VertexData) // VertSize
            VertFlags = 0X07 # WHY? Is this Position format + 1??????
            Outputfile.write(struct.pack('<I', VertCount))
            Outputfile.write(struct.pack('<H', VertSize))
            Outputfile.write(struct.pack('<H', VertFlags))
            Outputfile.write(self.VertexData)

            # INDX / IND4 (Faces)
            if Use32BitFace:
                Outputfile.write('IND4'.encode('ascii'))
                Outputfile.write(struct.pack('<I', len(self.FaceData)))
                Outputfile.write(struct.pack(f'<{len(self.FaceData)}I', *self.FaceData))
            else:
                Outputfile.write('INDX'.encode('ascii'))
                Outputfile.write(struct.pack('<I', len(self.FaceData)))
                Outputfile.write(struct.pack(f'<{len(self.FaceData)}H', *self.FaceData))