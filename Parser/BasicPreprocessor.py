import os
from abc import ABCMeta, abstractmethod

from Parser import BasicDataTypes

'''
Preprocessor: read from file, Output a dataset with uniform data unit
Functions:
    1. filter: eliminate unsupported characters for every unit
    2. formatting: format every unit, like doing strip, or length cutting
    3. eliminate duplicate: delete duplicates  
'''


class BasicPreProcessor(metaclass=ABCMeta):
    def __init__(self, initDataset, datasetFile: str, savePath: str, start: int = 0, limit: int = -1) -> None:
        super().__init__()
        self.dataset: BasicDataTypes.DataSet = initDataset
        self.titleList = list()

        self.filePath = datasetFile
        self.savePath = savePath
        self.start = start  # start line
        self.limit = limit  # line limit, -1 for no limit
        self.charset = set(
            "1234567890-=!@#$%^&*()_+qwertyuiop[]\\QWERTYUIOP{}|asdfghjkl;'ASDFGHJKL:\"zxcvbnm,./ZXCVBNM<>?")

        self.lines = list()

    @abstractmethod
    def filterLine(self, line: str) -> str:
        pass

    @abstractmethod
    def formatUnit(self, unit: BasicDataTypes.DataUnit) -> BasicDataTypes.DataUnit:
        pass

    def isVaildCharacter(self, ch: str) -> bool:
        if ch in self.charset:
            return True
        else:
            return False
            # raise PreprocessorException(f"Unsupported character: {ch}")

    def loadFromFile(self):
        if self.filePath is None or not os.path.exists(self.filePath):
            raise PreprocessorException(f"{self.filePath} not exists")
        with open(self.filePath, "r", encoding="utf-8", errors="ignore") as f:
            # read title
            title = self.readCsvLine(f.readline())
            self.titleList = [x.strip() for x in title if len(x) > 0]
            # ignore starting lines
            for i in range(self.start):
                f.readline()
            # read lines with limit number
            self.lines = list()
            if self.limit > 0:
                for i in range(int(self.limit)):
                    self.lines.append(f.readline())
            else:
                line = f.readline()
                while line:
                    self.lines.append(line)
                    line = f.readline()

    def readCsvLine(self, line: str) -> list:
        if len(line) <= 0:
            return []
        l = line.split(",")
        ll = list()
        for i in l:
            ii = i.strip()
            if len(ii) > 0:
                ll.append(ii)
        return ll

    def preprocess(self):
        self.loadFromFile()  # build self.lines
        # self.dataset = BasicDataTypes.DataSet(self.titleList)
        self.dataset.setKeyList(keylist=self.titleList)
        # walk through
        for line in self.lines:
            newline = self.filterLine(line)  # filter here
            d = dict()
            # build data unit
            if len(newline) > 0:
                l = newline.split(",")
                unit = self.dataset.createUnit(l)
                newUnit = self.formatUnit(unit)  # format unit here
                self.dataset.push(newUnit)
        # eliminate duplicate
        self.eliminateDuplicate()
        # save to file
        self.save()

    def save(self):
        def unit2line(u: BasicDataTypes.DataUnit) -> str:
            return ",".join(u.values()) + "\n"

        with open(self.savePath,"w", encoding="utf-8", errors="ignore") as f:
            datasetIter = iter(self.dataset)
            f.write(",".join(self.titleList) + "\n")
            i = 0
            for unit in datasetIter:
                f.write(unit2line(unit))
                i += 1
        print(f"Save preprocessed dataset to file {self.savePath}, total: {i}")

    def eliminateDuplicate(self):
        l = self.dataset.getUnitList()
        s = set(l)
        newList = list(s)
        self.dataset.resetUnitList(newList)


class PreprocessorException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
