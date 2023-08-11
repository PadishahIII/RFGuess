from Commons import Utils
from Parser import BasicDataTypes, BasicPreprocessor, PIIDataTypes
from Scripts.databaseInit import *


class PIIPreprocessor(BasicPreprocessor.DatabasePreProcessor):

    def __init__(self, initDataset: PIIDataTypes.PIIDataSet, start: int = 0, limit: int = -1) -> None:
        super().__init__(initDataset, start, limit)
        self.dataset: PIIDataTypes = initDataset

    def formatUnit(self, unit: BasicDataTypes.DataUnit) -> BasicDataTypes.DataUnit:
        from copy import copy
        newUnit: BasicDataTypes.DataUnit = copy(unit)
        for k, v in unit.items():
            newUnit.set(k, v.strip())
        return newUnit

    def baseUnit2DataUnit(self, baseUnit: PIIUnit) -> PIIDataTypes.PIIDataUnit:
        pii, pwStr = Utils.parsePIIUnitToPIIAndPwStr(baseUnit)
        unit = self.dataset.createUnit(self.dataset.getValueList(pii, pwStr))
        return unit

    def setKeyList(self):
        firstunit: PIIUnit = self.baseUnitList[0]
        pii, pwStr = Utils.parsePIIUnitToPIIAndPwStr(firstunit)
        self.dataset.generateKeyList(pii)

    def loadFromDatabase(self):
        offset = 0
        limit = 1e6
        if self.start >= 0:
            offset = self.start
        if self.limit > 0:
            limit = self.limit

        gen = UnitGenerator(offset, limit)
        while True:
            try:
                piiUnit: PIIUnit = next(gen)
                self.baseUnitList.append(piiUnit)
            except StopIteration:
                break

    def eliminateDuplicate(self):
        pass

    def getDataSet(self) -> BasicDataTypes.DataSet:
        return super().getDataSet()


class PIIPreprocessorException(BasicPreprocessor.PreprocessorException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
