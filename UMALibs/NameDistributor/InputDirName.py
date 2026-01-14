import os

class NameDistributor:
    def __init__(self):
        pass
    
    def GetName(self, InputPath):
        return os.path.basename(os.path.dirname(InputPath))