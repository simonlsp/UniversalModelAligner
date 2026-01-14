from .GOHDataFile import GOHDataFile

def GenerateDEF(ExportName):
    CurrentMDL = GOHDataFile("game_entity", None, [])
    CurrentMDL.SetChildValue("Extension", f'"{ExportName + ".mdl"}"')
    return CurrentMDL