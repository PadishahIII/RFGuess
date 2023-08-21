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
