from Classifiers.PIIRFTrainner import PIIRFTrainner
from Parser.PIIParsers import *

'''
Generators: use trained model to generate password guessing
'''


class PIICharacterSet(Singleton):
    """
    All symbols occur in PII mode.

    """

    def __init__(self) -> None:
        self.translator = Utils.PIISectionTypeTranslation.getInstance()
        self.sectionFactory: PIISectionFactory = PIISectionFactory.getInstance()
        self.charsetInt: list[int] = list()
        self.charsetPIISection: list[PIISection] = list()

        self._ldsMaxLen = 10

        self._buildCharset()

    def _buildCharset(self):
        for baseType in self.translator.toList:
            piiType = self.translator.translatorBaseTypeToPIIType(baseType)
            i = baseType.value + piiType.value
            self.charsetInt.append(i)
            section: PIISection = self.sectionFactory.createFromInt(i)
            self.charsetPIISection.append(section)

        for ldsType in [BasicTypes.PIIType.BaseTypes.L, BasicTypes.PIIType.BaseTypes.D, BasicTypes.PIIType.BaseTypes.S]:
            for i in range(self._ldsMaxLen + 1):
                v = ldsType.value + i
                self.charsetInt.append(v)
                section: PIISection = self.sectionFactory.createFromInt(v)
                self.charsetPIISection.append(section)

        v = BasicTypes.PIIType.BaseTypes.EndSymbol.value
        self.charsetInt.append(v)
        section: PIISection = self.sectionFactory.createFromInt(v)
        self.charsetPIISection.append(section)

    def getCharsetInt(self) -> list[int]:
        return self.charsetInt

    def getCharsetPIISection(self) -> list[PIISection]:
        return self.charsetPIISection


class PIIPatternGenerator:
    """PIIPatternGenerator
    Generate password patterns utilizing classifier
    Input a structure prefix like "N1A2", output the whole structure string
    In every classification, get several results with possibility. Change this variable to adjust the size of dictionary
    Pattern Transformation: "N1A2"(input string) => PIIDatagram

    Parse the result of classifier into `PIISection`
    """
    from Parser import Config
    order = Config.pii_order
    threshold = Config.generator_threshold

    def __init__(self, model: PIIRFTrainner) -> None:
        super().__init__()
        self.sectionFactory: PIISectionFactory = PIISectionFactory.getInstance()
        self.datagramFactory: PIIDatagramFactory = PIIDatagramFactory.getInstance()
        self.clf: PIIRFTrainner = model

    @classmethod
    def getInstance(cls, clfPath):
        t = PIIRFTrainner.loadFromFile(clfPath)
        return PIIPatternGenerator(model=t)

    def getClassifyResultFromStrList(self, dgSeedList: list[str]) -> list[str]:
        """
        Input a list of PIIDatagram string, output the final classification result

        """
        resList = list()
        for s in dgSeedList:
            resList.append(self.getClassifyResultFromStr(s))
        return resList

    def getMultiClassifyResultFromStrList(self, dgSeedList: list[str], n: int) -> list[str]:
        """Get top-n classes at every step
        Input a list of PIIDatagram string, output the final classification result

        """
        resList = list()
        for s in dgSeedList:
            resList += self.getMultiClassifyResultFromStr(s, n)
        return resList

    def getClassifyResultFromStr(self, dgSeedStr: str) -> str:
        """
        Input a PIIDatagram str, output the whole classification result in string format

        """
        dg = self.datagramFactory.createFromStr(dgSeedStr)
        resDg = self.getClassifyResultFromPIIDatagram(dg)
        s = self.datagramFactory.parsePIIDatagramToStr(resDg)
        return s

    def getMultiClassifyResultFromStr(self, dgSeedStr: str, n: int) -> list[str]:
        """Get top-n classes at every step
        Input a PIIDatagram str, output the list of classification result in string format

        """
        resStrList: list[str] = list()

        dg = self.datagramFactory.createFromStr(dgSeedStr)
        dgList: list[PIIDatagram] = self.getMultiClassifyResultFromPIIDatagram(dg, n)
        for dg in dgList:
            s = self.datagramFactory.parsePIIDatagramToStr(dg)
            resStrList.append(s)
        return resStrList

    def getMultiClassifyResultFromStrToProbaDict(self, dgSeedStr: str) -> dict[int, float]:
        """Get all classes to probability
        Input a str, return all classes with corresponding probability

        """
        dg = self.datagramFactory.createFromStr(dgSeedStr)
        return self.classifyMultiFromPIIDatagramToProbaDict(dg)

    def getClassifyResultFromPIIDatagram(self, dgSeed: PIIDatagram) -> PIIDatagram:
        """
        Input a PIIDatagram seed, output the whole PIIDatagram classified.

        """
        newSection: PIISection = self.classifyFromPIIDatagram(dgSeed)
        resDg: PIIDatagram = dgSeed
        while not self.sectionFactory.isEndSection(newSection):
            resDg.sectionList.append(newSection)
            newSection = self.classifyFromPIIDatagram(resDg)
        return resDg

    def getMultiClassifyResultFromPIIDatagram(self, dgSeed: PIIDatagram, n: int, maxDgSize: int = 9) -> list[
        PIIDatagram]:
        """Get top-n labels at every step
        Input a PIIDatagram seed, output all PIIDatagrams classified.

        Args:
            maxDgSize (int): max datagram size(length of vector list)
        """
        resDgList: list[PIIDatagram] = list()
        # q = queue.Queue()
        # q.put(dgSeed)
        q: list[PIIDatagram] = list()
        q.append(dgSeed)
        # while not q.empty():
        while len(q) > 0:
            # curDg: PIIDatagram = q.get()
            curDg: PIIDatagram = q.pop(0)
            newSectionList: list[PIISection] = self.classifyMultiFromPIIDatagram(curDg, n)
            for section in newSectionList:
                if not self.sectionFactory.isEndSection(section) and len(curDg.sectionList) < maxDgSize:
                    newDg: PIIDatagram = copy(curDg)
                    newDg.sectionList.append(section)
                    # q.put(newDg)
                    q.append(newDg)
                else:
                    resDgList.append(curDg)
        return resDgList

    def classifyFromPIIDatagram(self, dg: PIIDatagram) -> PIISection:
        """
        Input a PIIDatagram, return the classification result in PIISection format

        """
        dg = self.datagramFactory.tailorPIIDatagram(dg)
        labelInt = self.clf.classifyPIIDatagram(dg)
        section: PIISection = self.sectionFactory.createFromInt(labelInt)
        return section

    def classifyMultiFromPIIDatagram(self, dg: PIIDatagram, n: int) -> list[PIISection]:
        """Get top-n class labels
        Input a PIIDatagram, return the list of classification result in PIISection for top-n probability
        """
        dg = self.datagramFactory.tailorPIIDatagram(dg)
        labelList: list[int] = self.clf.classifyPIIDatagramProba(dg, n)
        sectionList: list[PIISection] = list()
        for i in labelList:
            section = self.sectionFactory.createFromInt(i)
            sectionList.append(section)
        return sectionList

    def classifyMultiFromPIIDatagramToProbaDict(self, dg: PIIDatagram) -> dict[int, float]:
        """Get all classes to probability
        Input a PIIDatagram, return all classes with corresponding probability

        """
        dg = self.datagramFactory.tailorPIIDatagram(dg)
        probaDict = self.clf.classifyPIIDatagramToProbaDict(dg)
        return probaDict

    def generatePattern(self) -> tuple[list[PIIDatagram], list[float]]:
        """
        Generate patterns using RF classifier
        Returns:
            list[PIIDatagram], list[float] : patternList and probability list in descending order

        """
        # charset:PIICharacterSet = PIICharacterSet.getInstance()
        patternList: list[PIIDatagram] = list()  # output
        probaList: list[float] = list()  # output, probability of pattern
        patternProbaDict: dict[PIIDatagram, float] = dict()  # output, pattern to probability
        prefixList: list[PIIDatagram] = list()  # current generated prefix
        probaDict: dict[PIIDatagram, float] = dict()  # currently generated prefix to probability

        sectionList = [self.sectionFactory.getBeginSection() for i in range(self.order)]
        beginDg = self.datagramFactory.createPIIDatagramOnlyWithFeature(sectionList, 0, 0)
        prefixList.append(beginDg)
        probaDict[beginDg] = 1
        _num_discarded = 0

        while len(prefixList) > 0:
            currentPrefix: PIIDatagram = prefixList.pop()
            pd: dict[int, float] = self.classifyMultiFromPIIDatagramToProbaDict(currentPrefix)
            for c, proba in pd.items():
                if proba == 0.0:
                    continue
                currentProba = probaDict[currentPrefix]
                newProba = currentProba * proba
                if newProba > self.threshold:
                    newSection: PIISection = self.sectionFactory.createFromInt(c)
                    newPrefix: PIIDatagram = copy(currentPrefix)
                    newPrefix.sectionList.append(newSection)
                    if self.sectionFactory.isEndSection(newSection):
                        # output
                        patternList.append(currentPrefix)
                        probaList.append(currentProba)
                        # patternProbaDict[currentPrefix] = currentProba
                    else:
                        prefixList.append(newPrefix)
                        probaDict[newPrefix] = newProba
                else:
                    _num_discarded += 1

        print(f"generatePattern:discarded:{_num_discarded}")
        pp = zip(patternList, probaList)
        pp_sorted = sorted(pp, key=lambda x: x[1], reverse=True)
        newPatternList = list(map(lambda x: x[0], pp_sorted))
        newProbaList = list(map(lambda x: x[1], pp_sorted))
        return newPatternList, newProbaList


class PIIPatternGeneratorException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
