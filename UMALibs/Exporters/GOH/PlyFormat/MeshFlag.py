
class GOHPLYMeshFlag:
    TWO_SIDED = 0x0001    # 0 Render both front and back faces (no backface culling)
    USE_ALPHA = 0x0002    # 1 Enable alpha blending/transparency
    LIGHT = 0x0004        # 2 Enable lighting calculations
    PLCR = 0x0008         # 3 Player color (for customizable unit colors)
    SKINNED = 0x0010      # 4 Mesh is skinned to a skeleton (animated)
    SHADOW = 0x0020       # 5 Mesh casts shadows
    MIRRORED = 0x0040     # 6 Mesh has mirrored/flipped UVs
    BLENDTEX = 0x0080     # 7 Use texture blending
    BUMP = 0x0100         # 8 Has bump/normal mapping
    SPECULAR = 0x0200     # 9 Has specular highlights (followed by RGBA color)
    MATERIAL = 0x0400     # 10 Uses material properties
    SUBSKIN = 0x0800      # 11 Sub-skin data (bone subset for optimization)
    TWOTEX = 0x1000       # 12 Two texture coordinate sets
    USINGVD = 0x2000      # 13 Using vertex declaration
    LIGHTMAP = 0x4000     # 14 Has lightmap texture
    
    @staticmethod
    def GetDefaultMeshFlag():
        TargetMatFlag = 0
        TargetMatFlag |= GOHPLYMeshFlag.TWO_SIDED
        # TargetMatFlag |= GOHPLYMeshFlag.USE_ALPHA
        TargetMatFlag |= GOHPLYMeshFlag.LIGHT
        # TargetMatFlag |= GOHPLYMeshFlag.PLCR
        TargetMatFlag |= GOHPLYMeshFlag.SKINNED
        # TargetMatFlag |= GOHPLYMeshFlag.SHADOW
        # TargetMatFlag |= GOHPLYMeshFlag.MIRRORED
        # TargetMatFlag |= GOHPLYMeshFlag.BLENDTEX
        # TargetMatFlag |= GOHPLYMeshFlag.BUMP
        # TargetMatFlag |= GOHPLYMeshFlag.SPECULAR
        TargetMatFlag |= GOHPLYMeshFlag.MATERIAL
        TargetMatFlag |= GOHPLYMeshFlag.SUBSKIN
        # TargetMatFlag |= GOHPLYMeshFlag.TWOTEX
        # TargetMatFlag |= GOHPLYMeshFlag.USINGVD
        # TargetMatFlag |= GOHPLYMeshFlag.LIGHTMAP
        
        return TargetMatFlag
    
    @staticmethod
    def GetMeshFlagFromMaxMaterial(Material):
        from pymxs import runtime as rt
        TargetMatFlag = 0
        if rt.isProperty(Material, "twoSided"):
            if Material.twoSided:
                TargetMatFlag |= GOHPLYMeshFlag.TWO_SIDED
        if rt.isProperty(Material, "opacityMap"):
            if Material.opacityMap:
                TargetMatFlag |= GOHPLYMeshFlag.USE_ALPHA
        TargetMatFlag |= GOHPLYMeshFlag.LIGHT
        # TargetMatFlag |= GOHPLYMeshFlag.PLCR
        TargetMatFlag |= GOHPLYMeshFlag.SKINNED
        # TargetMatFlag |= GOHPLYMeshFlag.SHADOW
        # TargetMatFlag |= GOHPLYMeshFlag.MIRRORED
        # TargetMatFlag |= GOHPLYMeshFlag.BLENDTEX
        # TargetMatFlag |= GOHPLYMeshFlag.BUMP
        # TargetMatFlag |= GOHPLYMeshFlag.SPECULAR
        TargetMatFlag |= GOHPLYMeshFlag.MATERIAL
        TargetMatFlag |= GOHPLYMeshFlag.SUBSKIN
        # TargetMatFlag |= GOHPLYMeshFlag.TWOTEX
        # TargetMatFlag |= GOHPLYMeshFlag.USINGVD
        # TargetMatFlag |= GOHPLYMeshFlag.LIGHTMAP
        
        return TargetMatFlag
    
    def GetMeshFlagFromMaxSubMaterial(TargetMesh, MaterialID):
        from pymxs import runtime as rt
        MultiMaterial = TargetMesh.material
        if rt.classOf(MultiMaterial) != rt.Multimaterial:
            return GOHPLYMeshFlag.GetMeshFlagFromMaterial(MultiMaterial)
        # Material ID is 1-based, but MultiMaterial is 0-based!
        assert (MaterialID - 1) < len(MultiMaterial), "Mesh has material ID without matching sub material! Material ID: [" + str(MaterialID) + "]"
        return GOHPLYMeshFlag.GetMeshFlagFromMaterial(MultiMaterial[MaterialID - 1])
