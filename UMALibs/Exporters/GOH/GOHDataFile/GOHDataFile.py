class GOHDataFile:
    def __init__(self, Key:str, Value:str|None, ChildList:list):
        self.Key = Key
        self.Value = Value
        self.ChildList = ChildList

    @staticmethod
    def GetFirstObject(InputString):
        InDoubleQuote = False
        InSingleQuote = False
        for CharID in range(len(InputString)):
            if InputString[CharID] == '"':
                InDoubleQuote = (not InDoubleQuote)
            elif InputString[CharID] == "'":
                InSingleQuote = (not InSingleQuote)
            elif InputString[CharID] == "{":
                if (not InDoubleQuote) and (not InSingleQuote):
                    startID = CharID
                    break
        else:
            raise ValueError("Found No Object in input string!")
        
        InDoubleQuote = False
        InSingleQuote = False
        BraceCount = 1
        for CharID in range(startID+1, len(InputString)):
            if InputString[CharID] == '"':
                InDoubleQuote = (not InDoubleQuote)
            elif InputString[CharID] == "'":
                InSingleQuote = (not InSingleQuote)
            elif InputString[CharID] == "{":
                if (not InDoubleQuote) and (not InSingleQuote):
                    BraceCount += 1
            elif InputString[CharID] == "}":
                if (not InDoubleQuote) and (not InSingleQuote):
                    BraceCount -= 1
                    if BraceCount == 0:
                        endID = CharID + 1
                        break
        else:
            raise ValueError("Object not ended in input string!")
        
        return (startID, endID)

    @staticmethod
    def initFromMTLStr(MTLStr:str):
        MTLStr = "\n".join([line for line in MTLStr.split("\n") if not line.startswith(';')])
        MTLStr = MTLStr.strip()
        # Check Format
        if not MTLStr.startswith("{") and MTLStr.endswith("}"):
            raise NotImplementedError("An subobject do not starts with '{' and ends with '}'!")
        # Trim '{' and '}'
        MTLStr = MTLStr[1:-1].strip()
        # Seperate strings
        MTL_KVPair_Str = MTLStr.split("{", maxsplit=1)[0]
        MTL_Childs_Str = MTLStr[len(MTL_KVPair_Str):]

        MTL_KVPair_Str = MTL_KVPair_Str.strip()
        MTL_Childs_Str = MTL_Childs_Str.strip()
        
        # K-V
        # for seperator in {' ', '\t', '\n'}:
        Seperator_HeaderLen_list = [(len(MTL_KVPair_Str.split(seperator, maxsplit=1)[0]), seperator) for seperator in {' ', '\t', '\n'}]
        UsingSeperator = sorted(Seperator_HeaderLen_list, key=lambda x:x[0])[0][1]


        if UsingSeperator in MTL_KVPair_Str:
            Init_Key, Init_Value = MTL_KVPair_Str.split(UsingSeperator, maxsplit=1)
            Init_Key = Init_Key.strip()
            Init_Value = Init_Value.strip()
        else:
            Init_Key = MTL_KVPair_Str.strip()
            Init_Value = None
        
        # Children
        Init_ChildList = list()
        if "{" in MTL_Childs_Str:
            while "{" in MTL_Childs_Str:
                ChildStart, ChildEnd = GOHDataFile.GetFirstObject(MTL_Childs_Str)
                Init_ChildList.append(GOHDataFile.initFromMTLStr(MTL_Childs_Str[ChildStart: ChildEnd]))
                MTL_Childs_Str = MTL_Childs_Str[ChildEnd:].strip()
            if MTL_Childs_Str != "":
                raise ValueError("MTL_Childs string is not empty after extracting all childs!")
        
        return GOHDataFile(Init_Key, Init_Value, Init_ChildList)

    def GetChildByName(self, ChildName:str):
        ReturnList = list()
        if self.ChildList != None:
            for Child in self.ChildList:
                if Child.Key == ChildName:
                    ReturnList.append(Child)
        if len(ReturnList) > 1:
            raise ValueError("Multiple Children with Same Key!")
        elif len(ReturnList) == 1:
            return ReturnList[0]
        else:
            return None

    def AddChild(self, Child):
        self.ChildList.append(Child)
    
    def HasChild(self, Key):
        return self.GetChildByName(Key) != None

    def SetChildValue(self, Key, Value):
        TargetChild = self.GetChildByName(Key)
        if TargetChild != None:
            TargetChild.Value = Value
        else:
            self.AddChild(GOHDataFile(Key, Value, []))

    def ToMTLString(self, IndentLevel = 0):
        OutputString = (("\t" * IndentLevel) + "{" + self.Key)
        if self.Value is not None:
            OutputString += (" " + self.Value)
        if not self.ChildList:
            OutputString += "}\n"
        else:
            OutputString += "\n"
            for Child in self.ChildList:
                OutputString += Child.ToMTLString(IndentLevel = IndentLevel + 1)
            OutputString += (("\t" * IndentLevel) + "}\n")
        
        return OutputString
