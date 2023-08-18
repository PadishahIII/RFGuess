from abc import  ABCMeta, abstractmethod
from Parser import  BasicDataTypes
from Parser import BasicParsers
from Parser.PIIParsers import PIIParser
from Commons.DatabaseLayer import *

'''
Factory: given a dataset, Output feature list and label list, toppest layer
Require:
    1. a Preprocessor to read file and preprocess dataset 
    2. a Parser to tackle every single data unit of the dataset  
'''
class BasicFactory(metaclass=ABCMeta):

    def __init__(self, transformer:DatabaseTransformer,parser:BasicParsers.BasicParser) -> None:
        super().__init__()
        self.transformer = transformer
        self.parser = parser
        self.featureList:list[list] = list()
        self.labelList:list[int] = list()

    def getFeatureList(self):
        return self.featureList

    def getLabelList(self):
        return self.labelList


    @abstractmethod
    def process(self):
        pass



class PIIFactory(BasicFactory):

    def __init__(self, transformer: DatabaseTransformer,
                 offset:int=0,
                 limit:int=1e6) -> None:
        super().__init__(transformer, parser)
        self.transformer:PwRepUniqueTransformer = transformer
        self.parser:PIIParser = parser
        self.limit = limit
        self.offset = offset

    @classmethod
    def getInstance(cls,offset:int=0,limit=1e6):
        return PIIFactory(transformer=PwRepUniqueTransformer.getInstance(),
                          parser=PIIParser(),
                          offset=offset,
                          limit=limit)

    def process(self):
        l:list[PwRepAndStructureUnit]= self.transformer.readAsParseUnit(offset=self.offset,limit=self.limit)
        for unit in l:
            pwStr = unit.pwStr
            rep:PIIRepresentation = unit.rep


