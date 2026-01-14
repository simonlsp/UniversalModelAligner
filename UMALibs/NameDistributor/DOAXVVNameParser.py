import os

class NameDistributor:
    def __init__(self):
        pass
    
    def GetName(self, InputPath):
        InputDirName = os.path.basename(os.path.dirname(InputPath))
        ReturnName = InputDirName.split("-",maxsplit=1)[0].strip().lower() + "_"
        ReturnName = ReturnName[0].upper() + ReturnName[1:]
        for Block in InputDirName.split("-",maxsplit=1)[1].split("(",maxsplit=1)[0].strip().lower().split(" "):
            AddingBlock = Block.strip()
            AddingBlock = AddingBlock[0].upper() + AddingBlock[1:]
            ReturnName += AddingBlock
        return ReturnName