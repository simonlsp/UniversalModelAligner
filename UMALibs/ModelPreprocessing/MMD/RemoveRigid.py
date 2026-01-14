from ...BlenderTools.BlenderTools import RemoveObjectsWithNameContainsSubStr

class Operator():
    def __init__(self, RemoveJoints=True, RemoveRigidBodies=True):
        self.RemovingSubStr = set()
        if RemoveJoints:
            self.RemovingSubStr.add('joints')
        if RemoveRigidBodies:
            self.RemovingSubStr.add('rigidbodies')

    def Execute(self):
        RemoveObjectsWithNameContainsSubStr(self.RemovingSubStr)