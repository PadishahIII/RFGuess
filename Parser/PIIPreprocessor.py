from Parser import BasicDataTypes, BasicPreprocessor


class PIIPreprocessor(BasicPreprocessor.BasicPreProcessor):

    def __init__(self, initDataset, datasetFile: str, savePath: str, start: int = 0, limit: int = -1) -> None:
        super().__init__(initDataset, datasetFile, savePath, start, limit)

    def filterLine(self, line: str) -> str:
        newLine = ''.join([ch for ch in line if self.isVaildCharacter(ch)])
        return newLine

    def formatUnit(self, unit: BasicDataTypes.DataUnit) -> BasicDataTypes.DataUnit:
        from copy import copy
        newUnit: BasicDataTypes.DataUnit = copy(unit)
        for k, v in unit.items():
            newUnit.set(k, v.strip())
        return newUnit
