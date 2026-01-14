from ...BlenderTools.BlenderTools import RemoveObjectsWithNameContainsSubStr

class Operator():
    def __init__(self, RemoveCellphone=True, RemoveStick=True, RemoveFacePaint=True, Malfunction=False):
        self.RemovingSubStr = set()
        if RemoveCellphone:
            self.RemovingSubStr.add('+cellphone')
        if RemoveStick:
            self.RemovingSubStr.add('+stick')
        if RemoveFacePaint:
            self.RemovingSubStr.add('face paint')
        if Malfunction:
            self.RemovingSubStr.add('+switch malfunction')
        else:
            self.RemovingSubStr.add('-switch malfunction')

    def Execute(self):
        RemoveObjectsWithNameContainsSubStr(self.RemovingSubStr)