import typing

from Commons import BasicTypes
from Parser import BasicDataTypes


class PIIDataUnit(BasicDataTypes.DataUnit):
    pass


class PIIDataSet(BasicDataTypes.DataSet):

    def createUnit(self, valueList: list) -> PIIDataUnit:
        keys = self.keyList
        i = 0
        _keysLen = len(keys)
        d = dict()
        for value in valueList:
            if i >= _keysLen:
                raise PIIDataSetException(
                    f"createUnit Error: unit's dimension({len(valueList)}) not fit dataset's dimension({len(self.keyList)})")
            key = keys[i]
            d[key] = value
            i += 1
        unit = PIIDataUnit(**d)
        return unit

    def checkUnit(self, unit: PIIDataUnit) -> bool:
        return True


class PIIDataSetException(BasicDataTypes.DatasetException):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


# PII data types extend BasicDataTypes
class PIISection(BasicDataTypes.Section):

    def __init__(self, type: BasicTypes.PIIType, value):
        super().__init__(type, value, BasicTypes.KeyboardPosition(0, 0))

    def _tojson(self):
        return {
            "PII Type:": str(self.type) + f" {self.type.name}",
            "PII value": self.value,
        }


class PIIDatagram(BasicDataTypes.Datagram):

    def __init__(self, sectionList: list[PIISection], label: typing.Any, offsetInPassword: int, offsetInSegment: int,
                 pwStr: str):
        super().__init__(sectionList, label, offsetInPassword, offsetInSegment, pwStr)


class PIIPassword(BasicDataTypes.Password):
    def __init__(self, pwStr: str, datagramList: list[PIIDatagram]):
        super().__init__(pwStr, datagramList)
