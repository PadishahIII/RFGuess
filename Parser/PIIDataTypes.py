import typing

from Commons import BasicTypes
from Parser import BasicDataTypes


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
