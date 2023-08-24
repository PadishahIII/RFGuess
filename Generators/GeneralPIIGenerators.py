import numpy as np

from Classifiers.PIIRFTrainner import PIIRFTrainner
from Parser.GeneralPIIParsers import *
from Parser.GeneralPIIParsers import *


class GeneralPIIPatternGenerator:
    """GeneralPIIPatternGenerator
    Generate password patterns utilizing classifier
    Input a structure prefix like "<N1><A2>", output the whole structure string
    In every classification, get several results with possibility. Change this variable to adjust the size of dictionary
    Pattern Transformation: "<N1><A2>"(input string) => GeneralPIIDatagram

    Parse the result of classifier into `GeneralPIISection`

    Examples:
        generator:GeneralPasswordGenerator = GeneralPasswordGenerator.getInstance(patternFile="../patterns_general.txt",
                                                                                  outputFile="../passwords_general.txt",
                                                                                  pii=pii,
                                                                                  nameFuzz=True)
        generator.run()
    """
    from Parser import Config
    order = Config.pii_order
    threshold = Config.general_generator_threshold

    def __init__(self, model: PIIRFTrainner) -> None:
        super().__init__()
        self.sectionFactory: GeneralPIISectionFactory = GeneralPIISectionFactory.getInstance()
        self.datagramFactory: GeneralPIIDatagramFactory = GeneralPIIDatagramFactory.getInstance()
        self.clf: PIIRFTrainner = model

    @classmethod
    def getInstance(cls, clfPath):
        t = PIIRFTrainner.loadFromFile(clfPath)
        return GeneralPIIPatternGenerator(model=t)

    def getClassifyResultFromStrList(self, dgSeedList: list[str]) -> list[str]:
        """
        Input a list of GeneralPIIDatagram string, output the final classification result

        """
        resList = list()
        for s in dgSeedList:
            resList.append(self.getClassifyResultFromStr(s))
        return resList

    def getMultiClassifyResultFromStrList(self, dgSeedList: list[str], n: int) -> list[str]:
        """Get top-n classes at every step
        Input a list of GeneralPIIDatagram string, output the final classification result

        """
        resList = list()
        for s in dgSeedList:
            resList += self.getMultiClassifyResultFromStr(s, n)
        return resList

    def getClassifyResultFromStr(self, dgSeedStr: str) -> str:
        """
        Input a GeneralPIIDatagram str, output the whole classification result in string format

        """
        dg = self.datagramFactory.createFromStr(dgSeedStr)
        resDg = self.getClassifyResultFromGeneralPIIDatagram(dg)
        s = self.datagramFactory.parseGeneralPIIDatagramToStr(resDg)
        return s

    def getMultiClassifyResultFromStr(self, dgSeedStr: str, n: int) -> list[str]:
        """Get top-n classes at every step
        Input a GeneralPIIDatagram str, output the list of classification result in string format

        """
        resStrList: list[str] = list()

        dg = self.datagramFactory.createFromStr(dgSeedStr)
        dgList: list[GeneralPIIDatagram] = self.getMultiClassifyResultFromGeneralPIIDatagram(dg, n)
        for dg in dgList:
            s = self.datagramFactory.parseGeneralPIIDatagramToStr(dg)
            resStrList.append(s)
        return resStrList

    def getMultiClassifyResultFromStrToProbaDict(self, dgSeedStr: str) -> dict[int, float]:
        """Get all classes to probability
        Input a str, return all classes with corresponding probability

        """
        dg = self.datagramFactory.createFromStr(dgSeedStr)
        return self.classifyMultiFromGeneralPIIDatagramToProbaDict(dg)

    def getClassifyResultFromGeneralPIIDatagram(self, dgSeed: GeneralPIIDatagram) -> GeneralPIIDatagram:
        """
        Input a GeneralPIIDatagram seed, output the whole GeneralPIIDatagram classified.

        """
        newSection: GeneralPIISection = self.classifyFromGeneralPIIDatagram(dgSeed)
        resDg: GeneralPIIDatagram = dgSeed
        while not self.sectionFactory.isEndSection(newSection):
            resDg.sectionList.append(newSection)
            newSection = self.classifyFromGeneralPIIDatagram(resDg)
        return resDg

    def getMultiClassifyResultFromGeneralPIIDatagram(self, dgSeed: GeneralPIIDatagram, n: int, maxDgSize: int = 9) -> \
    list[
        GeneralPIIDatagram]:
        """Get top-n labels at every step
        Input a GeneralPIIDatagram seed, output all GeneralPIIDatagrams classified.

        Args:
            maxDgSize (int): max datagram size(length of vector list)
        """
        resDgList: list[GeneralPIIDatagram] = list()
        # q = queue.Queue()
        # q.put(dgSeed)
        q: list[GeneralPIIDatagram] = list()
        q.append(dgSeed)
        # while not q.empty():
        while len(q) > 0:
            # curDg: GeneralPIIDatagram = q.get()
            curDg: GeneralPIIDatagram = q.pop(0)
            newSectionList: list[GeneralPIISection] = self.classifyMultiFromGeneralPIIDatagram(curDg, n)
            for section in newSectionList:
                if not self.sectionFactory.isEndSection(section) and len(curDg.sectionList) < maxDgSize:
                    newDg: GeneralPIIDatagram = copy(curDg)
                    newDg.sectionList.append(section)
                    # q.put(newDg)
                    q.append(newDg)
                else:
                    resDgList.append(curDg)
        return resDgList

    def classifyFromGeneralPIIDatagram(self, dg: GeneralPIIDatagram) -> GeneralPIISection:
        """
        Input a GeneralPIIDatagram, return the classification result in GeneralPIISection format

        """
        dg = self.datagramFactory.tailorGeneralPIIDatagram(dg)
        labelInt = self.clf.classifyPIIDatagram(dg)
        section: GeneralPIISection = self.sectionFactory.createFromInt(labelInt)
        return section

    def classifyMultiFromGeneralPIIDatagram(self, dg: GeneralPIIDatagram, n: int) -> list[GeneralPIISection]:
        """Get top-n class labels
        Input a GeneralPIIDatagram, return the list of classification result in GeneralPIISection for top-n probability
        """
        dg: GeneralPIIDatagram = self.datagramFactory.tailorGeneralPIIDatagram(dg)
        labelList: list[int] = self.clf.classifyPIIDatagramProba(dg, n)
        sectionList: list[GeneralPIISection] = list()
        for i in labelList:
            section = self.sectionFactory.createFromInt(i)
            sectionList.append(section)
        return sectionList

    def classifyMultiFromGeneralPIIDatagramToProbaDict(self, dg: GeneralPIIDatagram) -> dict[int, float]:
        """Get all classes to probability
        Input a GeneralPIIDatagram, return all classes with corresponding probability

        """
        dg = self.datagramFactory.tailorGeneralPIIDatagram(dg)
        probaDict = self.clf.classifyPIIDatagramToProbaDict(dg)
        return probaDict

    def generatePattern(self) -> tuple[list[GeneralPIIDatagram], list[float]]:
        """
        Generate patterns using RF classifier
        Returns:
            list[GeneralPIIDatagram], list[float] : patternList and probability list in descending order

        """
        # charset:PIICharacterSet = PIICharacterSet.getInstance()
        patternList: list[GeneralPIIDatagram] = list()  # output
        probaList:list[float] = list() # output
        patternProbaDict: dict[GeneralPIIDatagram, float] = dict()  # output, pattern to probability
        prefixList: list[GeneralPIIDatagram] = list()  # current generated prefix
        probaDict: dict[GeneralPIIDatagram, float] = dict()  # currently generated prefix to probability

        sectionList = [self.sectionFactory.getBeginSection() for i in range(self.order)]
        beginDg: GeneralPIIDatagram = self.datagramFactory.createGeneralPIIDatagramOnlyWithFeature(sectionList, 0, 0)
        prefixList.append(beginDg)
        probaDict[beginDg] = 1
        _num_discarded = 0
        _i = 0
        probaStatisticList: list[float] = list()  # for statistic

        while len(prefixList) > 0:
            currentPrefix: GeneralPIIDatagram = prefixList.pop()
            pd: dict[int, float] = self.classifyMultiFromGeneralPIIDatagramToProbaDict(currentPrefix)
            for c, proba in pd.items():
                if proba == 0.0:
                    continue
                currentProba = probaDict[currentPrefix]
                newProba = currentProba * proba
                probaStatisticList.append(newProba)
                if newProba > self.threshold:
                    newSection: GeneralPIISection = self.sectionFactory.createFromInt(int(c))
                    newPrefix: GeneralPIIDatagram = copy(currentPrefix)
                    newPrefix.sectionList.append(newSection)
                    if self.sectionFactory.isEndSection(newSection):
                        # output
                        patternList.append(newPrefix)
                        probaList.append(currentProba) # exclude proba of EndSymbol
                        # patternProbaDict[currentPrefix] = currentProba
                    else:
                        prefixList.append(newPrefix)
                        probaDict[newPrefix] = newProba
                else:
                    _num_discarded += 1
                _i += 1
                if _i % 1000 == 0:
                    print(f"Progress: {_i}, remain prefix: {len(prefixList)}, current prefix len: {len(prefixList[-1].sectionList)}, completed: {len(patternList)}, discarded:{_num_discarded}")

        probaArray = np.array(probaStatisticList)
        m = np.average(probaArray)
        print(f"proba average({len(probaArray)}): {m}, min: {np.min(probaArray)}, max: {np.max(probaArray)}")

        print(f"generatePattern:discarded:{_num_discarded}")
        pp = zip(patternList, probaList)
        pp_sorted = sorted(pp, key=lambda x: x[1], reverse=True)
        newPatternList = list(map(lambda x: x[0], pp_sorted))
        newProbaList = list(map(lambda x: x[1], pp_sorted))
        return newPatternList, newProbaList


class GeneralPIIPatternGeneratorException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
