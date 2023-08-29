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
        # newRepList:list[GeneralPIIRepresentation] = self.eliminateDuplicateRep(generalRepList)
        return GeneralPIIStructure(pwStr, generalRepList)

    def eliminateDuplicateRep(self, l: list[GeneralPIIRepresentation]) -> list[GeneralPIIRepresentation]:
        """Remove duplicates
        """
        nl = list(set(l))
        return nl

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
        matchSet: list[RepUnit] = copy(self.repPriorityList)
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


'''
Factories
'''


class CharacterSectionFactory(Singleton):

    def __init__(self) -> None:
        super().__init__()
        self.cp: CharacterParser = CharacterParser.getInstance()
        self.kp: KeyboardParser = KeyboardParser.getInstance()
        self.lp: LabelParser = LabelParser.getInstance()
        self.charVectorFactory: CharacterVectorFactory = CharacterVectorFactory.getInstance()

    def getBeginSection(self) -> CharacterSection:
        return CharacterSection("", type=CharacterType.BeginSymbol, serialNum=CharacterType.BeginSymbol.value,
                                keyboardPos=KeyboardPosition(0, 0))

    def getEndSection(self) -> CharacterSection:
        return CharacterSection("", type=CharacterType.EndSymbol, serialNum=CharacterType.EndSymbol.value,
                                keyboardPos=KeyboardPosition(0, 0))

    def isBeginSection(self, s: CharacterSection) -> bool:
        return s.type == CharacterType.BeginSymbol

    def isEndSection(self, s: CharacterSection) -> bool:
        return s.type == CharacterType.EndSymbol

    def createFromCh(self, ch: str) -> CharacterSection:
        """
        Create section from single character string

        """
        vector: CharacterVector = self.charVectorFactory.createFromCh(ch)
        return self.createFromCharacterVector(vector)

    def createFromCharacterVector(self, vector: CharacterVector) -> CharacterSection:
        return CharacterSection(ch=vector.getStr(), type=vector.type, serialNum=vector.serialNum,
                                keyboardPos=vector.keyboardPos)

    def createFromInt(self, i: int) -> CharacterSection:
        if i == 0:
            return self.getBeginSection()
        elif i < 0:
            return self.getEndSection()

        c: str = self.lp.decodeCh(i)
        if len(c) > 1 or len(c) <= 0:
            raise CharacterSectionFactoryException(f"Error: decode serial number fail: {str(i)}")
        type: CharacterType = Utils.parseType(c)
        keyPos: KeyboardPosition = self.kp.parseCh(c)
        return CharacterSection(ch=c, type=type, serialNum=i, keyboardPos=keyPos)


class CharacterSectionFactoryException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class GeneralPIISectionFactory(Singleton):

    def __init__(self) -> None:
        self.piiSectionFactory: PIISectionFactory = PIISectionFactory.getInstance()
        self.charSectionFactory: CharacterSectionFactory = CharacterSectionFactory.getInstance()
        self.charVectorFactory: CharacterVectorFactory = CharacterVectorFactory.getInstance()

    def getEmptySection(self) -> GeneralPIISection:
        s: PIISection = self.piiSectionFactory.getEmptySection()
        return GeneralPIISection(vector=s, isPII=True)

    def getBeginSection(self) -> GeneralPIISection:
        s: PIISection = self.piiSectionFactory.getBeginSection()
        return GeneralPIISection(vector=s, isPII=True)

    def getEndSection(self) -> GeneralPIISection:
        """
        Use PIISection as end section

        """
        s = self.piiSectionFactory.getEndSection()
        return GeneralPIISection(vector=s, isPII=True)

    def isBeginSection(self, section: GeneralPIISection) -> bool:
        if section.isPII:
            s: PIISection = section.vector
            return self.piiSectionFactory.isBeginSection(s)
        else:
            s: CharacterSection = section.vector
            return s.type == CharacterType.BeginSymbol

    def isEndSection(self, section: GeneralPIISection) -> bool:
        if section.isPII:
            s: PIISection = section.vector
            return self.piiSectionFactory.isEndSection(s)
        else:
            s: CharacterSection = section.vector
            return s.type == CharacterType.EndSymbol

    def createFromGeneralPIIVector(self, vector: GeneralPIIVector) -> GeneralPIISection:
        if vector.isPIIVector:
            v: PIIVector = vector.vectorObj
            s: PIISection = self.piiSectionFactory.createFromPIIVector(v)
            return GeneralPIISection(s, True)
        else:
            v: CharacterVector = vector.vectorObj
            s: CharacterSection = self.charSectionFactory.createFromCharacterVector(v)
            return GeneralPIISection(s, False)

    def createFromInt(self, i: int) -> GeneralPIISection:
        """
        4002 => PIISection or serial number => CharacterSection

        """
        if i < 1e3:
            # Character Section
            isPII = False
            vector = self.charSectionFactory.createFromInt(i)
        else:
            isPII = True
            vector = self.piiSectionFactory.createFromInt(i)

        return GeneralPIISection(vector, isPII)

    def createFromStr(self, s: str) -> GeneralPIISection:
        """
        For PIISection, string must be surrounded by "<>", like "<N1>"
        For CharacterSection, just the character itself
        """
        if len(s) < 1:
            raise GeneralPIISectionFactoryException(f"Error: invalid input string: {s}")
        if len(s) == 1:
            # Character section
            v: CharacterVector = self.charVectorFactory.createFromCh(s)
            section: CharacterSection = self.charSectionFactory.createFromCharacterVector(v)
            return GeneralPIISection(section, False)
        # PIISection
        m = re.match(r"<(\w{2,3})>", s)
        if not m:
            raise GeneralPIISectionFactoryException(f"Format error: string '{s}' must in '<xx>' format")
        ss = m.group(1)  # N1
        section: PIISection = self.piiSectionFactory.createFromStr(ss)
        return GeneralPIISection(section, True)

    def createFromCharacterSection(self, section: CharacterSection) -> GeneralPIISection:
        return GeneralPIISection(section, False)

    def createFromPIISection(self, section: PIISection) -> GeneralPIISection:
        return GeneralPIISection(section, True)

    def parseGeneralPIISectionToStr(self, section: GeneralPIISection) -> str:
        """
        Parse GeneralPIISection to string like "<N1>"(for PIISection) or character
        """
        if section.isPII:
            s = self.piiSectionFactory.parsePIISectionToStr(section.vector)
            return f"<{s}>"
        else:
            v: CharacterSection = section.vector
            return v.ch


class GeneralPIISectionFactoryException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class GeneralPIILabelFactory(Singleton):

    def __init__(self) -> None:
        super().__init__()

    def createFromPIILabel(self, label: PIILabel) -> GeneralPIILabel:
        return GeneralPIILabel(label, True)

    def createFromCharacterLabel(self, label: CharacterLabel) -> GeneralPIILabel:
        return GeneralPIILabel(label, False)

    def createFromGeneralPIISection(self, section: GeneralPIISection) -> GeneralPIILabel:
        if section.isPII:
            l: PIILabel = PIILabel.create(section.vector)
            return GeneralPIILabel(l, True)
        else:
            l: CharacterLabel = CharacterLabel(section.vector)
            return GeneralPIILabel(l, False)


class GeneralPIIDatagramFactory(Singleton):
    from Parser import Config
    order = Config.pii_order

    def __init__(self) -> None:
        super().__init__()
        self.sectionFactory = GeneralPIISectionFactory.getInstance()
        self.piidatagramFactory: PIIDatagramFactory = PIIDatagramFactory.getInstance()
        self.labelFactory: GeneralPIILabelFactory = GeneralPIILabelFactory.getInstance()
        self.charSectionFactory: CharacterSectionFactory = CharacterSectionFactory.getInstance()

    def createFromPIIDatagram(self, dg: PIIDatagram) -> GeneralPIIDatagram:
        sectionList: list[GeneralPIISection] = list()
        for section in dg.sectionList:
            sectionList.append(self.sectionFactory.createFromPIISection(section))
        newLabel = self.labelFactory.createFromPIILabel(dg.label)
        newDg = GeneralPIIDatagram(sectionList=sectionList, label=newLabel, offsetInSegment=dg.offsetInSegment,
                                   offsetInPassword=dg.offsetInPassword, pwStr=dg.pwStr)
        return newDg

    def getAllBasicGeneralPIIDatagramsDict(self) -> dict[str, GeneralPIIDatagram]:
        d: dict[str, PIIDatagram] = self.piidatagramFactory.getAllBasicPIIDatagramsDict()
        resDict: dict[str, GeneralPIIDatagram] = dict()
        for s, dg in d.items():
            generalDg: GeneralPIIDatagram = self.createFromPIIDatagram(dg)
            resDict[s] = generalDg
        return resDict

    def tailorGeneralPIIDatagram(self, dg: GeneralPIIDatagram) -> GeneralPIIDatagram:
        """
        Tailor datagram to 26-dim, datagram must have 6 sections

        """
        sectionList = dg.sectionList
        newList = list()
        if len(sectionList) > self.order:
            newList = sectionList[-6:]
        else:
            n = self.order - len(sectionList)
            beginSection = self.sectionFactory.getBeginSection()
            for i in range(n):
                newList.append(beginSection)
            newList += sectionList
        return GeneralPIIDatagram(newList, dg.label, dg.offsetInPassword, dg.offsetInSegment, dg.pwStr)

    def createGeneralPIIDatagramOnlyWithFeature(self, sectionList: list[GeneralPIISection], offsetInSegment: int,
                                                offsetInPassword: int) -> GeneralPIIDatagram:
        """
        Create a GeneralPIIDatagram only with fields required by `_tovector` method
        The minimum object that can be passed to trainner
        """
        emptySection: GeneralPIISection = self.sectionFactory.getEmptySection()
        label: GeneralPIILabel = self.labelFactory.createFromGeneralPIISection(emptySection)

        return GeneralPIIDatagram(sectionList, label, offsetInPassword,
                                  offsetInSegment, "")

    def createFromStr(self, s: str) -> GeneralPIIDatagram:
        """
        Convert string "<N1>aa123" into GeneralPIIDatagram
        OffsetInSegment is set to 0 and offsetInPassword is set to len(sectionList)
        """
        rst = re.compile(r"^(<\w{2,3}>)")
        sectionList: list[GeneralPIISection] = list()
        i = 0
        while i < len(s):
            begin = s[i:]
            m = rst.match(begin)
            if m is None:
                # character section
                section: CharacterSection = self.charSectionFactory.createFromCh(s[i])
                generalSection = self.sectionFactory.createFromCharacterSection(section)
                sectionList.append(generalSection)
                i += 1
            else:
                tag = m.group(1)
                section: GeneralPIISection = self.sectionFactory.createFromStr(tag)
                sectionList.append(section)
                i += len(tag)

        offsetInSegment = 0
        offsetInPassword = len(sectionList)
        dg = self.createGeneralPIIDatagramOnlyWithFeature(sectionList, offsetInSegment, offsetInPassword)
        # dg_ = self.tailorPIIDatagram(dg)
        return dg

    def parseGeneralPIIDatagramToStr(self, dg: GeneralPIIDatagram) -> str:
        """
        Parse GeneralPIIDatagram to string like "A1L10N2"
        """
        s = ""
        for section in dg.sectionList:
            section: GeneralPIISection
            if section.isPII and (
                    section.vector.type == BasicTypes.PIIType.BaseTypes.BeginSymbol or section.vector.type == BasicTypes.PIIType.BaseTypes.EndSymbol):
                continue
            elif not section.isPII and (
                    section.vector.type == CharacterType.BeginSymbol or section.vector.type == CharacterType.EndSymbol):
                continue

            try:
                s += self.sectionFactory.parseGeneralPIISectionToStr(section)
            except Exception as e:
                raise GeneralPIIDatagramFactoryException(
                    f"Exception occur when parsing section:{section}, Original Exception is {e}")

        return s


class GeneralPIIDatagramFactoryException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


'''
Training data build
'''


class GeneralPIIParser(BasicParser):
    from Parser import Config
    order = Config.pii_order
    """

    Examples:
        parser :GeneralPIIParser = GeneralPIIParser(None,pwStr,rep)
        parser.parse()
        parser.getFeatureList()
        parser.getLabelList()
    """

    def __init__(self, ctx, pwStr: str, rep: GeneralPIIRepresentation):
        super().__init__(ctx, pwStr)
        self.rep: GeneralPIIRepresentation = rep
        self.plen = rep.len
        self.featureList: list[list]
        self.datagramList: list[GeneralPIIDatagram]
        self.labelList: list[int]

        # self.translator = Utils.PIISectionTypeTranslation()
        self.sectionFactory = GeneralPIISectionFactory.getInstance()
        self.labelFactory = GeneralPIILabelFactory.getInstance()

    def beforeParse(self):
        super().beforeParse()

    def afterParse(self):
        super().afterParse()

    def buildDatagramList(self):
        # 6 begin section
        beginSections = [self.sectionFactory.getBeginSection() for i in range(self.order)]
        beginVector: GeneralPIIVector = self.rep.vectorList[0]
        beginSection: GeneralPIISection = self.sectionFactory.createFromGeneralPIIVector(beginVector)
        beginLabel: GeneralPIILabel = self.labelFactory.createFromGeneralPIISection(beginSection)
        beginDg: GeneralPIIDatagram = GeneralPIIDatagram(sectionList=beginSections,
                                                         label=beginLabel,
                                                         offsetInSegment=0,
                                                         offsetInPassword=0,
                                                         pwStr="")
        self.datagramList.append(beginDg)

        for i in range(self.plen):
            sectionList = list()
            offsetInPassword = 0
            # offsetInSegment = len(self.rep.piiVectorList[i].str)
            offsetInSegment = 0
            if i < self.order:
                for n in range(self.order - i - 1):
                    sectionList.append(self.sectionFactory.getBeginSection())
            start = max(0, i - self.order + 1)
            end = i + 1
            for n in range(start, end):
                vector: GeneralPIIVector = self.rep.vectorList[n]
                section: GeneralPIISection = self.sectionFactory.createFromGeneralPIIVector(vector)
                sectionList.append(section)
                # offsetInPassword += len(vector.str)
                offsetInPassword += 1
            # resolve label
            if i < self.plen - 1:
                nextVector: GeneralPIIVector = self.rep.vectorList[i + 1]
                section: GeneralPIISection = self.sectionFactory.createFromGeneralPIIVector(nextVector)
                label: GeneralPIILabel = self.labelFactory.createFromGeneralPIISection(section)
            else:
                # end symbol
                section: GeneralPIISection = self.sectionFactory.getEndSection()
                label = self.labelFactory.createFromGeneralPIISection(section)
            dg = GeneralPIIDatagram(sectionList=sectionList,
                                    label=label,
                                    offsetInPassword=offsetInPassword,
                                    offsetInSegment=offsetInSegment,
                                    pwStr=self.pwStr)
            self.datagramList.append(dg)

    def buildFeatureList(self):
        for dg in self.datagramList:
            t = dg._tovector()
            self.featureList.append(t)

    def buildLabelList(self):
        for dg in self.datagramList:
            label = dg.label
            self.labelList.append(label.toInt())
