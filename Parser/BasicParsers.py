from abc import ABCMeta, abstractmethod

from Context.Context import BasicContext
from Parser import BasicDataTypes


# Parser: convert single data unit of dataset into feature vector and label

# Given a password string, Output a feature vector list which contains 26-dim vectors
# and a label list, simply input (featureList,labelList) to model
class BasicParser(BasicContext, metaclass=ABCMeta):
    def __init__(self, ctx, pwStr: str):
        super().__init__()
        self.context = ctx
        self.pwStr = pwStr
        self.plen = len(pwStr)
        self.featureList: list[list] = list()
        self.labelList = list()

        self.datagramList: list[BasicDataTypes.Datagram] = list()

    # do some check here
    @abstractmethod
    def beforeParse(self):
        # if self.context is None:
        #     raise BasicParserException(f"context cannot be None")
        if self.pwStr is None or len(self.pwStr) <= 0:
            raise BasicParserException(f"pwStr cannot be empty")

    @abstractmethod
    def afterParse(self):
        pass

    def parse(self):
        self.beforeParse()
        self.buildDatagramList()
        self.buildFeatureList()
        self.buildLabelList()
        self.afterParse()

    # fill datagram list of pwStr
    @abstractmethod
    def buildDatagramList(self):
        pass

    @abstractmethod
    def buildFeatureList(self):
        pass

    # fill label list
    @abstractmethod
    def buildLabelList(self):
        pass

    def getFeatureList(self):
        return self.featureList

    def getLabelList(self):
        return self.labelList


class BasicParserException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
