import bpy

def RemoveAllObjects():
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    for collection in bpy.data.collections:
        bpy.data.collections.remove(collection)

def EnsureAddon(addon_name):
    """Check and enable a specific addon if available."""    
    # Check if already enabled
    if addon_name in bpy.context.preferences.addons:
        return True
    
    # Try to enable it
    try:
        bpy.ops.preferences.addon_enable(module=addon_name)
        return True
    except Exception:
        return False

def IsNameContainsSubStr(InputObject, TargetSubstrSet):
    for TargetSubstr in TargetSubstrSet:
        if TargetSubstr in InputObject.name:
            return True
    return False

def HasParentWithNameContainsSubStr(InputObject, TargetSubstrSet):
    CurrentObject = InputObject
    while CurrentObject != None:
        if IsNameContainsSubStr(CurrentObject, TargetSubstrSet):
            return True
        else:
            CurrentObject = CurrentObject.parent
    return False

def RemoveObjectsWithNameContainsSubStr(TargetSubstrSet):
    """
    Deletes objects with any parent in TargetNameSet
    """
    RemovingObjects = list()
    for obj in bpy.data.objects:
        if HasParentWithNameContainsSubStr(obj, TargetSubstrSet):
            RemovingObjects.append(obj)

    for obj in RemovingObjects:
        bpy.data.objects.remove(obj, do_unlink=True)