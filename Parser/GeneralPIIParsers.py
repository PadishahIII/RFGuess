from Parser.GeneralPIIDataTypes import *
from Parser.PIIParsers import *
from Commons import  Utils
from

'''
Foreground PII parse.
'''
class CharacterVectorFactory(Singleton):
    """
    Factory of `CharacterVector`
    """

    def __init__(self) -> None:
        super().__init__()

    def createFromCh(self,ch:str)->CharacterVector:
        cp:

        type = Utils.parseType(ch)
        value =


class GeneralPIIVectorFactory(Singleton):
    """
    Factory of `GeneralPIIVector`
    """

    def __init__(self) -> None:
        super().__init__()

    def createFromCharacterVector(self,vector:CharacterVector)->GeneralPIIVector:
        return GeneralPIIVector(vector,False)

    def createFromPIIVector(self,vector:PIIVector)->GeneralPIIVector:
        return GeneralPIIVector(vector,True)

class GeneralFactoryException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class GeneralPIIStructureParser:
    """(Foreground) Parse a pwStr into GeneralPIIStructure containing all representations
    Bound a pii data, parse password string into all possible representation
    """

    def __init__(self, pii:BasicTypes.PII) -> None:
        self.pii = pii

    def getGeneralPIIStructure(self, pwStr:str)->GeneralPIIStructure:
        """
        Given a password string, output the GeneralPIIStructure which contains all representation about this password

        """
        pass

    def parseAllGeneralVectorRecursive(self, tagList: list[Tag], pwStr: str, curVectors:list[GeneralPIIVector],
                                outputList: list[GeneralPIIRepresentation],
                                ):
        """Get all representations of a password string

        Args:
            tagList: list of tags to match
            pwStr: password string
            curTags: current tag list, denote a building representation
            outputList: *(output)*list of representations
            ldsType: current LDS type
            ldsStr: current LDS string

        Returns:
            a list of representations(denoting by `list[GeneralPIIRepresentation]`)
        """
        if len(pwStr) <= 0:
            # flush the last LDS segment
            if ldsType is not None:
                tag = Tag.create(ldsType, ldsStr)
                curTags.append(tag)
            outputList.append(curTags)
            return
        candidates: typing.List[Tag] = list()
        for tag in tagList:
            if pwStr.startswith(tag.s):
                candidates.append(tag)
        if len(candidates) <= 0:
            # parse current character
            newLdsType = LDSStepper.checkLDSType(pwStr[0])
            if ldsType is not None and newLdsType != ldsType:
                # LDS type changed, push old segment into curTags
                tag = Tag.create(ldsType, ldsStr)
                curTags.append(tag)
                ldsStr = ""
            ldsStr += pwStr[0]
            newPwStr = pwStr[1:]
            newCurTag = copy(curTags)
            parseAllPIITagRecursive(tagList, pwStr=newPwStr, curTags=newCurTag, outputList=outputList,
                                    # ldsStepNum=ldsStepNum,
                                    ldsType=newLdsType,
                                    ldsStr=ldsStr)
        else:
            # flush LDS stepper when meet pii segment
            if ldsType is not None:
                tag = Tag.create(ldsType, ldsStr)
                curTags.append(tag)
                ldsType = None
                ldsStr = ""
            for tag in candidates:
                s = len(tag.s)
                newPwStr = pwStr[s:]  # remove tag prefix
                newCurTag = copy(curTags)
                newCurTag.append(tag)
                parseAllPIITagRecursive(tagList, pwStr=newPwStr, curTags=newCurTag, outputList=outputList,
                                        ldsType=ldsType,
                                        ldsStr=ldsStr)





