from enum import IntFlag

class D3DFVF(IntFlag):
    """
    Direct3D 9 Flexible Vertex Format Flags
    
    These flags describe the components present in each vertex.
    Multiple flags can be combined to describe complex vertex formats.
    """
    # Position formats (mutually exclusive within position mask)
    # XXXX XXXX XXXX [XXXX]
    XYZ = 0x0002          # 0010 x, y, z position (3 floats)
    XYZRHW = 0x0004       # 0100 Transformed position with RHW (4 floats)
    XYZB1 = 0x0006        # 0110 Position + 1 blend weight
    XYZB2 = 0x0008        # 1000 Position + 2 blend weights
    XYZB3 = 0x000A        # 1010 Position + 3 blend weights
    XYZB4 = 0x000C        # 1100 Position + 4 blend weights
    XYZB5 = 0x000E        # 1110 Position + 5 blend weights
    XYZW = 0x4002         # 0100 .... 0010 Position with W component (4 floats)
    
    # Other vertex components
    # XXXX XXXX [XXXX] XXXX
    NORMAL = 0x0010       # 0001 Normal vector (3 floats)
    PSIZE = 0x0020        # 0010 Point size (1 float)
    DIFFUSE = 0x0040      # 0100 Diffuse color (4 bytes ARGB)
    SPECULAR = 0x0080     # 1000 Specular color (4 bytes ARGB)
    
    # Texture coordinate counts (bits 8-11)
    # XXXX [XXXX] XXXX XXXX
    TEX0 = 0x0000         # 0000 No texture coordinates
    TEX1 = 0x0100         # 0001 1 texture coordinate set
    TEX2 = 0x0200         # 0010 2 texture coordinate sets
    TEX3 = 0x0300         # 0011 3 texture coordinate sets
    TEX4 = 0x0400         # 0100 4 texture coordinate sets
    TEX5 = 0x0500         # 0101 5 texture coordinate sets
    TEX6 = 0x0600         # 0110 6 texture coordinate sets
    TEX7 = 0x0700         # 0111 7 texture coordinate sets
    TEX8 = 0x0800         # 1000 8 texture coordinate sets
    
    # Beta (blend) data format
    # [XXXX] XXXX XXXX XXXX
    LASTBETA_UBYTE4 = 0x1000    # 0001 Last blend weight is UBYTE4 (bone indices)
    LASTBETA_D3DCOLOR = 0x8000  # 1000 Last blend weight is D3DCOLOR
    
    # Masks for extracting specific fields
    POSITION_MASK = 0x400E      # 0100 .... 1110 Mask to extract position format
    TEXCOUNT_MASK = 0x0F00      # Mask to extract texture coordinate count
    TEXCOUNT_SHIFT = 8          # Bits to shift for texture count
    
    @staticmethod
    def Add_FVF(FVF_1:int|None, FVF_2:int|None):
        if FVF_1 == None:
            return FVF_2
        elif FVF_2 == None:
            return FVF_1
        else:
            NEW_FVF_WithOut_TexCount = (FVF_1 | FVF_2) & (0xFFFF ^ D3DFVF.TEXCOUNT_MASK)
            old_texcount = FVF_1 & D3DFVF.TEXCOUNT_MASK
            new_texcount = FVF_2 & D3DFVF.TEXCOUNT_MASK
            
            if old_texcount > new_texcount:
                return NEW_FVF_WithOut_TexCount | old_texcount
            else:
                return NEW_FVF_WithOut_TexCount | new_texcount

    @staticmethod
    def VertexDataStructureToFVF(VertexDataStructure):
        VertexDataNames = [DataName for DataName, DataLength in VertexDataStructure]
        assert "POSXYZ" in VertexDataNames, "Position must exist in Output Vertex structure!"
        assert "BONEWEIGHT" in VertexDataNames, "BoneWeight must exist in Output Vertex structure!"
        assert "MatrixIndices" in VertexDataNames, "MatrixIndices must exist in Output Vertex structure!"
        ReturnFVF = 0
        # Flag 1
        # BoneCount Must be added by 1 for MatrixIndices used 1 position
        WeightPerVertex = VertexDataStructure[VertexDataNames.index("BONEWEIGHT")][1]
        if WeightPerVertex == 1:
            ReturnFVF |= D3DFVF.XYZB2
        elif WeightPerVertex == 2:
            ReturnFVF |= D3DFVF.XYZB3
        elif WeightPerVertex == 3:
            ReturnFVF |= D3DFVF.XYZB4
        elif WeightPerVertex == 4:
            ReturnFVF |= D3DFVF.XYZB5
        # Flag 2
        if 'NORMAL' in VertexDataNames:
            ReturnFVF |= D3DFVF.NORMAL
        if 'PSIZE' in VertexDataNames:
            ReturnFVF |= D3DFVF.PSIZE
        if 'DIFFUSE' in VertexDataNames:
            ReturnFVF |= D3DFVF.DIFFUSE
        if 'SPECULAR' in VertexDataNames:
            ReturnFVF |= D3DFVF.SPECULAR
        # Flag 3
        ReturnFVF |= D3DFVF.TEX1 # We support and only support 1 UV channel per mat.
        # Flag4
        ReturnFVF |= D3DFVF.LASTBETA_UBYTE4 # MatrixIndices must exist in Output Vertex structure.

        return ReturnFVF

    @staticmethod
    def GetVertexDataStructure(GlobalFVF, VertexSize):
        # cls, ply: PlyFile, forced_bump: bool = False
        """Parse FVF flags to determine vertex format components"""
        # fvf = ply.global_fvf
        # flags = ply.global_flags

        VertexDataStructure = list()
        assert GlobalFVF != None, "No mesh detect in this file before VERT tag, could not resolv vertex format!"
        # Position
        if GlobalFVF & D3DFVF.POSITION_MASK:
            VertexDataStructure.append(("POSXYZ", 3))
            # ply.has_position = True
            # unknown_size -= 12
            PositionMaskedFormat = GlobalFVF & D3DFVF.POSITION_MASK

            if PositionMaskedFormat == D3DFVF.XYZRHW:
                VertexDataStructure.append(("POSRHW", 1))
            elif PositionMaskedFormat == D3DFVF.XYZW:
                VertexDataStructure.append(("POSW", 1))
            elif PositionMaskedFormat == D3DFVF.XYZB1:
                VertexDataStructure.append(("BONEWEIGHT", 1))
            elif PositionMaskedFormat == D3DFVF.XYZB2:
                VertexDataStructure.append(("BONEWEIGHT", 2))
            elif PositionMaskedFormat == D3DFVF.XYZB3:
                VertexDataStructure.append(("BONEWEIGHT", 3))
            elif PositionMaskedFormat == D3DFVF.XYZB4:
                VertexDataStructure.append(("BONEWEIGHT", 4))
            elif PositionMaskedFormat == D3DFVF.XYZB5:
                VertexDataStructure.append(("BONEWEIGHT", 5))
            else:
                raise AssertionError("Unknown PositionMaskedFormat!")
                
        if GlobalFVF & D3DFVF.LASTBETA_UBYTE4:
            assert VertexDataStructure[-1][0] == "BONEWEIGHT", "Matrix indice detected in an non-boneweighted vertex mapping."
            VertexDataStructure[-1] = (VertexDataStructure[-1][0], VertexDataStructure[-1][1]-1)
            VertexDataStructure.append(("MatrixIndices", 1))
        elif GlobalFVF & D3DFVF.LASTBETA_D3DCOLOR:
            assert VertexDataStructure[-1][0] != "BONEWEIGHT", AssertionError("No matrix indice found in an bone-weighted vertex mapping!")
        
        if GlobalFVF & D3DFVF.NORMAL:
            VertexDataStructure.append(("NORMAL", 3))
        
        if GlobalFVF & D3DFVF.PSIZE:
            VertexDataStructure.append(("PSIZE", 1))
        
        if GlobalFVF & D3DFVF.DIFFUSE:
            VertexDataStructure.append(("DIFFUSE", 1))
        
        if GlobalFVF & D3DFVF.SPECULAR:
            VertexDataStructure.append(("SPECULAR", 1))
        
        if GlobalFVF & D3DFVF.TEXCOUNT_MASK:
            UVWCoordsCount = (GlobalFVF & D3DFVF.TEXCOUNT_MASK) >> D3DFVF.TEXCOUNT_SHIFT
            if UVWCoordsCount > 1:
                raise AssertionError("Multiple UVW on a same vert?")
            VertexDataStructure.append(("UVW", 2))
        
        ## NO MESH BUMP ALLOWED

        UnknownSize = VertexSize
        for DataName, DataLength in VertexDataStructure:
            UnknownSize -= (DataLength * 4)
        
        assert UnknownSize == 0, f"Vertex format parsing failed, {UnknownSize} bytes are unknown!"
        return VertexDataStructure