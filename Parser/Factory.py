from Commons.DatabaseLayer import *
from Parser.GeneralPIIParsers import *

'''
Factory: given a dataset, Output feature list and label list, toppest layer
Require:
    1. a Preprocessor to read file and preprocess dataset 
    2. a Parser to tackle every single data unit of the dataset  
'''


class BasicFactory(metaclass=ABCMeta):

    def __init__(self, transformer: DatabaseTransformer) -> None:
        super().__init__()
        self.transformer = transformer
        self.featureList: list[list] = list()
        self.labelList: list[int] = list()

    def getFeatureList(self):
        return self.featureList

    def getLabelList(self):
        return self.labelList

    @abstractmethod
    def process(self):
        pass


class PIIFactoryException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class PIIFactory(BasicFactory):
    """
    Examples:

    """

    def __init__(self, transformer: PwRepUniqueTransformer,
                 offset: int = 0,
                 limit: int = 1e6) -> None:
        super().__init__(transformer)
        self.transformer: PwRepUniqueTransformer = transformer
        self.limit = limit
        self.offset = offset

        self.sectionFactory = PIISectionFactory.getInstance()

    @classmethod
    def getInstance(cls, offset: int = 0, limit=1e6):
        return PIIFactory(transformer=PwRepUniqueTransformer.getInstance(),
                          offset=offset,
                          limit=int(limit))

    def process(self):
        l: list[PwRepAndStructureUnit] = self.transformer.readAsParseUnit(offset=self.offset, limit=self.limit)
        for unit in l:
            try:
                pwStr = unit.pwStr
                rep: PIIRepresentation = unit.rep
                parser: PIIParser = PIIParser(None, pwStr, rep)
                parser.parse()
                featureList = parser.getFeatureList()
                labelList = parser.getLabelList()
                self.featureList += featureList
                self.labelList += labelList
            except Exception as e:
                raise PIIFactoryException(
                    f"Exception occur when addressing unit {str(unit.__dict__)}\nOriginal Exception: {e}")


class GeneralPIIFactory(BasicFactory):
    """
    Examples:

    """

    def __init__(self, transformer: GeneralPwRepUniqueTransformer,
                 proportion: float = 1) -> None:
        super().__init__(transformer)
        self.transformer: GeneralPwRepUniqueTransformer = transformer
        self.limit = 1e6
        self.offset = 0

        minId = self.transformer.getMinId()
        maxId = self.transformer.getMaxId()

        start = minId
        end = minId + int(proportion * (maxId - minId + 1))

        self.offset = 0
        self.limit = end - start

        self.sectionFactory = GeneralPIISectionFactory.getInstance()

    @classmethod
    def getInstance(cls, proportion: float = 1):
        return GeneralPIIFactory(transformer=GeneralPwRepUniqueTransformer.getInstance(),
                                 proportion=proportion)

    def process(self):
        l: list[GeneralPwRepAndStructureUnit] = self.transformer.readAsParseUnit(offset=self.offset, limit=self.limit)
        for unit in l:
            try:
                pwStr = unit.pwStr
                rep: GeneralPIIRepresentation = unit.rep
                parser: GeneralPIIParser = GeneralPIIParser(None, pwStr, rep)
                parser.parse()
                featureList = parser.getFeatureList()
                labelList = parser.getLabelList()
                self.featureList += featureList
                self.labelList += labelList
            except Exception as e:
                raise GeneralPIIFactoryException(
                    f"Exception occur when addressing unit {str(unit.__dict__)}\nOriginal Exception: {e}")


class GeneralPIIFactoryException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
