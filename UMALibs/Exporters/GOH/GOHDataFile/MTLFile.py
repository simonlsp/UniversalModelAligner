from ....MaterialTools.UMAMaterial import UMAMaterial
from .GOHDataFile import GOHDataFile
import os, subprocess
import bpy
import numpy as np

def SaveChannelSwappedNrmPNG(NrmTex, OutputPath):
    NrmImg = bpy.data.images.load(NrmTex)
    NrmImgWidth, NrmImgHeight = NrmImg.size[0], NrmImg.size[1]
    NrmImgArr = np.array(NrmImg.pixels[:]).reshape((NrmImgHeight, NrmImgWidth, 4))
    NrmImgArr[:,:,3] = NrmImgArr[:,:,0]
    NrmImgArr[:,:,0] = 0.0
    NrmImg.pixels[:] = NrmImgArr.ravel()

    NrmImg.filepath_raw = OutputPath
    NrmImg.file_format = 'PNG'
    NrmImg.save()

class MTLFile:
    def __init__(self, InputUMAMat:UMAMaterial, NVTTEPath:str, TargetShader:str):
        self.InputUMAMat = InputUMAMat
        self.NVTTEPath = NVTTEPath
        self.TargetShader = TargetShader
        if TargetShader not in ["Vallina", "FedPBR", "FedToon"]:
            raise NotImplementedError(f"Unknown Target Shader: {self.TargetShader}")

    def ToGOHMTLFile(self, OutputDir, MatID):
        CurrentMatOutputName = f"Mat_{MatID}.mtl"
        CurrentMatMTL = GOHDataFile("material","bump", [])

        # Diffuse texture is same
        if self.InputUMAMat.DiffuseTexture and os.path.exists(str(self.InputUMAMat.DiffuseTexture)):
            DiffTexOutputName = f"Mat_{MatID}_diff.dds"
            subprocess.check_output([self.NVTTEPath, "-o", f"{os.path.join(OutputDir, DiffTexOutputName)}", "-f", "18", f'"{self.InputUMAMat.DiffuseTexture}"'])
            CurrentMatMTL.SetChildValue("diffuse", f'"{DiffTexOutputName}"')

        # Normal texture
        if self.TargetShader == "Vallina":
            if self.InputUMAMat.NormalTexture:
                pass # Vallina Shader has bug on normal map
        elif self.TargetShader == "FedPBR" or self.TargetShader == "FedToon":
            if self.InputUMAMat.NormalTexture and os.path.exists(str(self.InputUMAMat.NormalTexture)):
                NrmTexOutputName = f"Mat_{MatID}_nrm.dds"
                TempNrmTexPath = self.InputUMAMat.NormalTexture + "_TEMP.png"
                SaveChannelSwappedNrmPNG(self.InputUMAMat.NormalTexture, TempNrmTexPath)
                subprocess.check_output([self.NVTTEPath, "-o", f"{os.path.join(OutputDir, NrmTexOutputName)}", "-f", "18", f'"{TempNrmTexPath}"'])
                CurrentMatMTL.SetChildValue("bump", f'"{NrmTexOutputName}"')
                os.remove(TempNrmTexPath)
            else:
                CurrentMatMTL.SetChildValue("bump", '"$/dummyTex/normal"')
        
        # Specular Texture
        if self.InputUMAMat.SpecularTexture and os.path.exists(str(self.InputUMAMat.SpecularTexture)):
            DiffTexOutputName = f"Mat_{MatID}_spe.dds"
            subprocess.check_output([self.NVTTEPath, "-o", f"{os.path.join(OutputDir, DiffTexOutputName)}", "-f", "18", f'"{self.InputUMAMat.SpecularTexture}"'])
            CurrentMatMTL.SetChildValue("specular", f'"{DiffTexOutputName}"') # Original tex is used for all shaders
        elif self.TargetShader == "FedPBR" or self.TargetShader == "FedToon":
            CurrentMatMTL.SetChildValue("specular", '"$/dummyTex/black"') # A dummy tex is used for Fed Shaders.
        
        # Height Texture and full_specular mark
        if self.TargetShader == "FedToon":
            CurrentMatMTL.SetChildValue("height", '"$/envmap/env"')
            CurrentMatMTL.SetChildValue("full_specular", None)
            
        # BlendMode
        if self.InputUMAMat.BlendMethod == "OPAQUE":
            CurrentMatMTL.SetChildValue("blend", 'none')
        else:
            CurrentMatMTL.SetChildValue("alpharef", '127')
            CurrentMatMTL.SetChildValue("blend", 'test')
            CurrentMatMTL.SetChildValue('alphatocoverage', None)
            
        with open(os.path.join(OutputDir, CurrentMatOutputName), 'w') as MTLOutfile:
            MTLOutfile.write(CurrentMatMTL.ToMTLString())