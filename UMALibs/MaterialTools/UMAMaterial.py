import bpy

class UMAMaterial:
    def __init__(
        self,
        BlendMethod,
        DiffuseTexture,
        NormalTexture,
        SpecularTexture,
    )-> None:
        self.BlendMethod = BlendMethod
        self.DiffuseTexture = DiffuseTexture
        self.NormalTexture = NormalTexture
        self.SpecularTexture = SpecularTexture
    
    @staticmethod
    def FromXnalaraNode(InputMaterial):
        CurrentSurfaceShaderNode = InputMaterial.node_tree.nodes["Material Output"].inputs['Surface'].links[0].from_node

        try:
            BlendMethod = InputMaterial.blend_method
        except:
            BlendMethod = "OPAQUE"
        try:
            DiffuseTexture = bpy.path.abspath(CurrentSurfaceShaderNode.inputs['Diffuse'].links[0].from_node.image.filepath)
        except Exception:
            DiffuseTexture = None
            
        try:
            NormalTexture = bpy.path.abspath(CurrentSurfaceShaderNode.inputs['Bump Map'].links[0].from_node.image.filepath)
        except Exception:
            NormalTexture = None

        try:
            SpecularTexture = bpy.path.abspath(CurrentSurfaceShaderNode.inputs['Specular'].links[0].from_node.image.filepath)
        except Exception:
            SpecularTexture = None
        
        return UMAMaterial(BlendMethod, DiffuseTexture, NormalTexture, SpecularTexture)
        
    @staticmethod
    def FromMMDNode(InputMaterial):
        CurrentSurfaceShaderNode = InputMaterial.node_tree.nodes["Material Output"].inputs['Surface'].links[0].from_node
        
        try:
            BlendMethod = InputMaterial.blend_method
        except:
            BlendMethod = "OPAQUE"

        try:
            DiffuseTexture = bpy.path.abspath(CurrentSurfaceShaderNode.inputs['Base Tex'].links[0].from_node.image.filepath)
        except Exception:
            DiffuseTexture = None
        
        NormalTexture = None
        SpecularTexture = None
        
        return UMAMaterial(BlendMethod, DiffuseTexture, NormalTexture, SpecularTexture)

    @staticmethod
    def IsSimilar(MaterialA, MaterialB):
        return (
            (MaterialA.BlendMethod == MaterialB.BlendMethod) &
            (MaterialA.DiffuseTexture == MaterialB.DiffuseTexture) &
            (MaterialA.NormalTexture == MaterialB.NormalTexture) &
            (MaterialA.SpecularTexture == MaterialB.SpecularTexture)
        )