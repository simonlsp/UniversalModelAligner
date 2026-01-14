import os

class NameDistributor:
    def __init__(self, Prefix, StartID=0):
        self.Prefix = Prefix
        self.CurrentID = StartID - 1
        
    def GetName(self, InputPath):
        self.CurrentID += 1
        return self.Prefix + str(self.CurrentID)