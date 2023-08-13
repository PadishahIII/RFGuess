import os
from abc import ABCMeta, abstractmethod

from Parser import BasicDataTypes
from Scripts.databaseInit import Base

'''
Preprocessor: read from file or database, Output a dataset with uniform data unit
Functions:
    1. filter: eliminate unsupported characters for every unit
    2. formatting: format every unit, like doing strip, or length cutting
    3. eliminate duplicate: delete duplicates  
'''


class BasicPreProcessor(metaclass=ABCMeta):
    """Ancestor of preprocessors

    Attributes:
        charset (set): set of supported characters
    """

    def __init__(self) -> None:
        super().__init__()
        self.charset = set(
            "1234567890-=!@#$%^&*()_+qwertyuiop[]\\QWERTYUIOP{}|asdfghjkl;'ASDFGHJKL:\"zxcvbnm,./ZXCVBNM<>?")

    @abstractmethod
    def preprocess(self):
        pass

    @abstractmethod
    def getDataSet(self) -> BasicDataTypes.DataSet:
        pass


class FilePreProcessor(BasicPreProcessor, metaclass=ABCMeta):
    """File preprocessor

    Read data from file and save the preprocessed data into another file.
    Dataset file format:
        First line for title list, quote separated, example:
        ```csv
        name,birthday,email
        JasonHarris, 1982-03-04, 350@qq.com
        JasonHarris, 1982-03-04, 350@qq.com~
        ```
    """

    def __init__(self, initDataset, datasetFile: str, savePath: str, start: int = 0, limit: int = -1) -> None:
        """

        Args:
            initDataset: input an initial DataSet object
            datasetFile: file to read
            savePath: path to save
            start: line number to start with
            limit: number of line limitation
        """
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

        with open(self.savePath, "w", encoding="utf-8", errors="ignore") as f:
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

    def getDataSet(self) -> BasicDataTypes.DataSet:
        return self.dataset


class DatabasePreProcessor(BasicPreProcessor, metaclass=ABCMeta):
    """Used to read and preprocess primitive dataset

    Facade api. Read from database and build `DataSet` object.
    Provide self-defined preprocess interface for every `DataUnit` in dataset.

    Notes:
        - Preprocessors only read database and simply transform units into `DataUnit` in dataset
        - If you require database manipulation or more flexible transformation api, consider `DatabaseTransformer`s in
        `Commons.DatabaseLayer`
    """

    def __init__(self, initDataset: BasicDataTypes.DataSet, start: int = 0, limit: int = -1) -> None:
        super().__init__()
        self.dataset: BasicDataTypes.DataSet = initDataset
        self.start = start
        self.limit = limit

        self.baseUnitList: list[Base] = list()  # raw unit from database

    @abstractmethod
    def baseUnit2DataUnit(self, baseUnit: Base) -> BasicDataTypes.DataUnit:
        """
        Convert database unit into DataUnit

        Args:
            baseUnit: the unit from database query result

        Returns:
            DataUnit: unit type in DataSet

        """
        pass

    @abstractmethod
    def formatUnit(self, unit: BasicDataTypes.DataUnit) -> BasicDataTypes.DataUnit:
        pass

    @abstractmethod
    def loadFromDatabase(self):
        """
        Build baseUnitList
        """
        pass

    @abstractmethod
    def setKeyList(self):
        """
        Build keyList of dataset
        """
        pass

    def preprocess(self):
        self.loadFromDatabase()  # build self.baseUnitList
        if len(self.baseUnitList) <= 0:
            raise PreprocessorException(f"Error: get none data from database")
        # set keyList
        self.setKeyList()
        # walk through
        for baseUnit in self.baseUnitList:
            # build data unit
            dataUnit: BasicDataTypes.DataUnit = self.baseUnit2DataUnit(baseUnit)
            newUnit = self.formatUnit(dataUnit)  # format unit here
            self.dataset.push(newUnit)
        # eliminate duplicate
        self.eliminateDuplicate()

    @abstractmethod
    def eliminateDuplicate(self):
        """
        Eliminate duplicate in dataset
        """
        pass

    def getDataSet(self) -> BasicDataTypes.DataSet:
        return self.dataset


class PreprocessorException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
