# 3dsmax Ref to RefDict
from pymxs import runtime as rt
for i in rt.selection:
    TransformStr = "[" + "], [".join([", ".join([str(value) for value in vector]) for vector in i.transform]) + "]"
    if i.parent:
        ParStr = i.parent.name
    else:
        ParStr = "None"
    print('"'+i.name + '":[[' + TransformStr + "],'" + ParStr + "'],")