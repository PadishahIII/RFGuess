from Parser.CommonParsers import *
from Parser.GeneralPIIDataTypes import *
from Parser.PIIParsers import *

'''
Foreground PII parse.
'''


class PIIVectorFactory(Singleton):
    """
    Factory of `PIIVector`
    """

    def __init__(self) -> None:
        super().__init__()
        self.translatorPIIType = Utils.PIISectionTypeTranslation.getInstance()

    def createFromTag(self, tag: Tag) -> PIIVector:
        piiType = tag.piitype  # specified type, e.g. FullName
        piiTypeValue = piiType.value
        value = piiTypeValue
        return PIIVector(s=tag.s, piitype=piiType, piivalue=value)


class CharacterVectorFactory(Singleton):
    """
    Factory of `CharacterVector`
    """

    def __init__(self) -> None:
        super().__init__()

    def createFromCh(self, ch: str) -> CharacterVector:
        cp: CharacterParser = CharacterParser.getInstance()
        kp: KeyboardParser = KeyboardParser.getInstance()
        type = Utils.parseType(ch)
        value = cp.encodeCh(ch)
        keyboardPos = kp.parseCh(ch)
        return CharacterVector(ch, type, value, keyboardPos)


class GeneralPIIVectorFactory(Singleton):
    """
    Factory of `GeneralPIIVector`
    """

    def __init__(self) -> None:
        super().__init__()

    def createFromCharacterVector(self, vector: CharacterVector) -> GeneralPIIVector:
        return GeneralPIIVector(vector, False)

    def createFromPIIVector(self, vector: PIIVector) -> GeneralPIIVector:
        return GeneralPIIVector(vector, True)


class GeneralFactoryException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class GeneralPIIStructureParser:
    """(Foreground) Parse a pwStr into GeneralPIIStructure containing all representations
    Bound a pii data, parse password string into all possible representation
    """

    def __init__(self, pii: BasicTypes.PII) -> None:
        self.pii = pii
        self.generalRepList: list[GeneralPIIRepresentation] = list()

        self.tagList: list[Tag] = list()  # tags extracted from pii
        self.piivectorFactory: PIIVectorFactory = PIIVectorFactory.getInstance()
        self.charvectorFactory: CharacterVectorFactory = CharacterVectorFactory.getInstance()
        self.generalvectorFactory: GeneralPIIVectorFactory = GeneralPIIVectorFactory.getInstance()

        self._init()

    def _init(self):
        tagParser = PIIFullTagParser(self.pii)
        tagParser.parseTag()
        self.tagList = tagParser.getTagContainer().getTagList()

    def getGeneralPIIStructure(self, pwStr: str) -> GeneralPIIStructure:
        """
        Given a password string, output the GeneralPIIStructure which contains all representation about this password

        """

        generalRepList: list[GeneralPIIRepresentation] = list()
        self.parseAllGeneralVectorRecursive(pwStr, list(), generalRepList)
        return GeneralPIIStructure(pwStr, generalRepList)

    def parseAllGeneralVectorRecursive(self, pwStr: str, curVectors: list[GeneralPIIVector],
                                       outputList: list[GeneralPIIRepresentation]
                                       ):
        """Get all representations of a password string

        Args:
            tagList (list[Tag]) : list of tags to match
            pwStr (str) : password string
            curVectors (list[GeneralPIIVector]) : current tag list, denote a building representation
            outputList (list[GeneralPIIRepresentation]) : *(output)*list of representations

        Returns:
            a list of representations(denoting by `list[GeneralPIIRepresentation]`)
        """
        if len(pwStr) <= 0:
            outputList.append(GeneralPIIRepresentation(curVectors))
            return
        candidates: list[Tag] = list()
        for tag in self.tagList:
            if pwStr.startswith(tag.s):
                candidates.append(tag)
        if len(candidates) <= 0:
            # parse current character
            ch = pwStr[0]
            chVector: CharacterVector = self.charvectorFactory.createFromCh(ch)
            vector: GeneralPIIVector = self.generalvectorFactory.createFromCharacterVector(chVector)
            newCurVectors = copy(curVectors)
            newCurVectors.append(vector)
            newPwStr = pwStr[1:]
            self.parseAllGeneralVectorRecursive(pwStr=newPwStr, curVectors=newCurVectors, outputList=outputList)
        else:
            for tag in candidates:
                s = len(tag.s)
                newPwStr = pwStr[s:]  # remove tag prefix
                newCurVectors = copy(curVectors)
                piiVector: PIIVector = self.piivectorFactory.createFromTag(tag)
                vector: GeneralPIIVector = self.generalvectorFactory.createFromPIIVector(piiVector)
                newCurVectors.append(vector)
                self.parseAllGeneralVectorRecursive(pwStr=newPwStr, curVectors=newCurVectors, outputList=outputList)


class GeneralPIIRepresentationStrParser(Singleton):
    """Parse `GeneralPIIRepresentation` to readable string like "A1B2aaaa"

    """

    def __init__(self) -> None:
        super().__init__()
        self.piiVectorStrParser = PIITagRepresentationStrParser.getInstance()
        self.piiTypetoCharTranslator = self.piiVectorStrParser.translation
        self.piiCharToTypeTranslator = self.piiVectorStrParser.reTranslation

    def representationToStr(self, rep: GeneralPIIRepresentation) -> str:
        """Parse `GeneralPIIRepresentation` object into string like "A1B2aaa123"

        """
        l = list()
        vectorList: list[GeneralPIIVector] = rep.vectorList
        for vector in vectorList:
            s = self.vectorToStr(vector)
            l.append(s)
        ss = ",".join(l)
        prefix = f"{len(l)}:"
        first = prefix + ss
        second = "|".join(list(map(lambda x: x.getStr(), vectorList)))
        res = f"{first}\n{second}"
        return res

    def vectorToStr(self, vector: GeneralPIIVector) -> str:
        """Convert a `GeneralPIIVector` to string

        """
        if vector.isPIIVector:
            s = self.piiVectorStrParser.tagToStr(vector.vectorObj)
        else:
            charVector: CharacterVector = vector.vectorObj
            s = charVector.getStr()
        return s


'''
General representation resolver
'''


class GeneralPIIRepresentationResolver(Singleton):
    """
    select a representation of password
    """

    def __init__(self,
                 pwList: list[str],
                 pwAllRepDict: dict[str, list[RepUnit]],
                 repPriorityList: list[RepUnit],
                 ) -> None:
        self.pwList: list[str] = pwList  # all pwStr
        self.pwAllRepDict: dict[
            str, list[RepUnit]] = pwAllRepDict  # pwStr:list of all rep, password string and its all representation
        self.repPriorityList: list[RepUnit] = repPriorityList  # list of repUnit in frequency-descending order
        self.pwRepDict: dict[str, RepUnit] = dict()  # (output) password with its unique representation

    @classmethod
    def getInstance(cls):
        if super()._instances is not None:
            return super().getInstance()
        repPriorityList = DatabaseUtils.getGeneralRepStructurePriorityList()
        # print(f"PriorityList:{len(repPriorityList)}")
        pwList = DatabaseUtils.getGeneralAllPw()
        pwAllRepDict = dict()
        _len = len(pwList)
        _i = 0
        # print(f"PwList:{len(pwList)}")
        pwAllRepDict = DatabaseUtils.getGeneralAllRepStructureDict()
        # for pw in pwList:
        #     repList = DatabaseUtils.getAllRepStructureOfPw(pw)
        #     pwAllRepDict[pw] = repList
        #     _i += 1
        #     print(f"Progress:{(_i / _len) * 100:.2f}%")
        # print(f"PwRepDict:{len(pwAllRepDict.keys())}\n{list(pwAllRepDict.keys())[:10]}")

        return super().getInstance(pwList, pwAllRepDict, repPriorityList)

    def pwMatch(self, pwStr: str) -> tuple[RepUnit]:
        """
        Return all PII structure representations of pwStr

        """
        if pwStr not in self.pwAllRepDict.keys():
            raise ResolverException(f"Error: pwStr {pwStr} not in pwAllRepDict ")
        return tuple(self.pwAllRepDict[pwStr])

    def subtractFrequency(self, repUnitList: list[RepUnit]):
        """
        Subtract frequency of all representation structures in `repUnitList`

        """

        for unit in repUnitList:
            unit.frequency -= 1

    def shortMatch(self, pwStr: str) -> RepUnit:

        """
        Return the shortest representation structure of pwStr

        """
        if pwStr not in self.pwAllRepDict.keys():
            raise ResolverException(f"Error pwStr {pwStr} not in pwAllRepDict")
        repList: list[RepUnit] = self.pwAllRepDict[pwStr]
        min = 1e6
        min_i = 0
        i = 0
        _len = len(repList)
        while i < _len:
            rep: RepUnit = repList[i]
            l = DatabaseUtils.getRepLen(rep)
            if l < min:
                min_i = i
                min = l
            i += 1
        minRep: RepUnit = repList[min_i]
        return minRep

    def resolve(self) -> dict[str, RepUnit]:
        """
        Resolve the representations of all passwords
        `repPriorityList` and `pwList` will turn to empty after call
        `pwAllRepDict` will not change and `shortMatch` method can use as normal

        Take the frequency of representation structures as the primary consider, if pw's all representations have equal
         frequency, select the shortest structure.

        Returns:

        """
        matchSet: list[RepUnit] = self.repPriorityList
        _len = len(matchSet)
        item: RepUnit = matchSet.pop(0)
        while len(matchSet) > 0:
            print(
                f"Resolve Progress:{_len - len(matchSet)}/{_len}:{((_len - len(matchSet)) / _len * 100):.2f} pwList:{len(self.pwList)}")
            if item.frequency <= 1:
                item: RepUnit = matchSet.pop(0)
                continue
            for pw in self.pwList:
                matchPw: tuple[RepUnit] = self.pwMatch(pw)
                if item in matchPw:
                    self.pwRepDict[pw] = item
                    self.pwList.remove(pw)
                    for remainItem in matchPw:
                        remainItem.frequency -= 1
            item: RepUnit = matchSet.pop(0)

        while len(self.pwList) > 0:
            pw = self.pwList.pop()
            structure: RepUnit = self.shortMatch(pw)
            self.pwRepDict[pw] = structure
        return self.pwRepDict


class ResolverException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
