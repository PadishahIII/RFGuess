import queue

from Classifiers.PIIRFTrainner import PIIRFTrainner
from Parser.PIIParsers import *

'''
Generators: use trained model to generate password guessing
'''


class PIIPatternGenerator:
    """PIIPatternGenerator
    Generate password patterns utilizing classifier
    Input a structure prefix like "N1A2", output the whole structure string
    In every classification, get several results with possibility. Change this variable to adjust the size of dictionary
    Pattern Transformation: "N1A2"(input string) => PIIDatagram

    Parse the result of classifier into `PIISection`
    """

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

    def getMultiClassifyResultFromPIIDatagram(self, dgSeed: PIIDatagram, n: int, maxDgSize:int=9) -> list[PIIDatagram]:
        """Get top-n labels at every step
        Input a PIIDatagram seed, output all PIIDatagrams classified.

        Args:
            maxDgSize (int): max datagram size(length of vector list)
        """
        resDgList: list[PIIDatagram] = list()
        # q = queue.Queue()
        # q.put(dgSeed)
        q :list[PIIDatagram]= list()
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


class PIIPatternGeneratorException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
