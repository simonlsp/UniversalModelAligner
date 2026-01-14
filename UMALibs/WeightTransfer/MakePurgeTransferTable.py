import bpy
import numpy as np
from copy import deepcopy

def FirstParentInTransferTable(InputBone, TransferTable):
    CurrentBone = InputBone
    while CurrentBone != None:
        for LineID, (SourceBoneList, TargetBoneList) in enumerate(TransferTable):
            if CurrentBone.name in SourceBoneList:
                return LineID
        else:
            CurrentBone = CurrentBone.parent
    raise ValueError(f"At least one bone is not purgeable: [{InputBone.name}]")

def MakePurgeTransferTable(ArmatureObject, TransferTable, WhiteListPrefix):
    PurgeTable = deepcopy(TransferTable)
    SourceBoneSet = {SourceBoneName for SourceBoneList, TargetBoneList in TransferTable for SourceBoneName in SourceBoneList}
    TargetBoneSet = {TargetBoneName for SourceBoneList, TargetBoneList in TransferTable for TargetBoneName, TargetBoneWeight in TargetBoneList}

    for TargetBoneName in TargetBoneSet:
        if not TargetBoneName.startswith(WhiteListPrefix):
            raise ValueError(f"PurgeTable could not be created: TargetBone [{TargetBoneName}] Do not have WhiteListPrefix [{WhiteListPrefix}].")

    # Record initial scene status
    InitialActiveObject = bpy.context.active_object
    InitialActiveMode = bpy.context.object.mode if bpy.context.object else 'OBJECT'

    # Switch context armature edit mode
    bpy.context.view_layer.objects.active = ArmatureObject
    ArmatureObject.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')

    # Get Current Bone List for purging
    for CurrentEditBone in list(ArmatureObject.data.edit_bones):
        if CurrentEditBone.name.startswith(WhiteListPrefix):
            continue # Whitelist
        elif CurrentEditBone in SourceBoneSet:
            continue # Already Purged
        else:
            AddingLineID = FirstParentInTransferTable(CurrentEditBone, PurgeTable)
            PurgeTable[AddingLineID][0].append(CurrentEditBone.name)
            
    # Restore
    bpy.context.view_layer.objects.active = InitialActiveObject
    bpy.ops.object.mode_set(mode=InitialActiveMode)

    return PurgeTable