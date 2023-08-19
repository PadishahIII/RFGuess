import os

import joblib

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
        if not os.path.exists(clfPath):
            raise PIIPatternGeneratorException(f"Error: invalid classifier path: {clfPath}")
        clf = joblib.load(clfPath)
        t = PIIRFTrainner.getInstance()
        t.setClf(clf)
        return PIIPatternGenerator(model=t)

    def getClassifyResultFromStrList(self, dgSeedList:list[str])->list[str]:
        """
        Input a list of PIIDatagram string, output the final classification result

        """
        resList = list()
        for s in dgSeedList:
            resList.append(self.getClassifyResultFromStr(s))
        return resList


    def getClassifyResultFromStr(self, dgSeedStr:str)->str:
        """
        Input a PIIDatagram str, output the whole classification result in string format

        """
        dg = self.datagramFactory.createFromStr(dgSeedStr)
        resDg = self.getClassifyResultFromPIIDatagram(dg)
        s = self.datagramFactory.parsePIIDatagramToStr(resDg)
        return s



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

    def classifyFromPIIDatagram(self, dg: PIIDatagram) -> PIISection:
        """
        Input a PIIDatagram, return the classification result in PIISection format

        """
        dg = self.datagramFactory.tailorPIIDatagram(dg)
        labelInt = self.clf.classifyPIIDatagram(dg)
        section: PIISection = self.sectionFactory.createFromInt(labelInt)
        return section


class PIIPatternGeneratorException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
