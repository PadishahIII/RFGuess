import os
from abc import  ABCMeta, abstractmethod
from Parser import  BasicDataTypes

'''
Preprocessor: read from file, output a dataset with uniform data unit
Functions:
    1. filter: eliminate unsupported characters for every unit
    2. formatting: format every unit, like doing strip, or length cutting
    3. eliminate duplicate: delete duplicates  
'''

class BasicPreProcessor(metaclass=ABCMeta):
    def __init__(self, file:str, start:int=0, limit:int=-1) -> None:
        super().__init__()
        self.dataset = None
        self.filePath = file
        self.start = start # start line
        self.limit = limit # line limit, -1 for no limit
        self.charset = "1234567890-=!@#$%^&*()_+qwertyuiop[]\\QWERTYUIOP{}|asdfghjkl;'ASDFGHJKL:\"zxcvbnm,./ZXCVBNM<>?"

        self.lines = list()


    @abstractmethod
    def filterLine(self,line:str)->str:
        pass

    @abstractmethod
    def formatUnit(self,unit:BasicDataTypes.DataUnit)->BasicDataTypes.DataUnit:
        pass

    def loadFromFile(self):
        if self.filePath is None or not os.path.exists(self.filePath):
            raise PreprocessorException(f"{self.filePath} not exists")
        with open(self.filePath, "r", encoding="utf-8", errors="ignore") as f:
            for i in range(self.start):
                f.readline()
            self.lines = list()
            if self.limit > 0:
                for i in range(int(self.limit)):
                    self.lines.append(f.readline())
            else:
                line = f.readline()
                while line:
                    self.lines.append(line)
                    line = f.readline()

    @abstractmethod
    def

    @abstractmethod
    def eliminateDuplicate(self):
        pass

class PreprocessorException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)