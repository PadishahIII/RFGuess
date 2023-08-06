import typing
from abc import abstractmethod, ABCMeta

from Commons import BasicTypes


# Password: a set of 26-dim vectors expressed by several Datagrams
#   Datagram: a 26-dim vector expressed by several Sections
#       Section: a 4-dim vector expressed by (type,value,row,col)


class Section(metaclass=ABCMeta):
    def __init__(self, type, value, keyboardPos: BasicTypes.KeyboardPosition):
        super().__init__()
        self.type = type
        self.value = value
        self.keyboardPos = keyboardPos


    def _tovector(self) -> list[int, int, int, int]:
        return [
            int(self.type.value),
            int(self.value),
            int(self.keyboardPos.row),
            int(self.keyboardPos.col)
        ]

    def _tojson(self):
        return {
            "section type": self.type.name,
            "section value": self.value,
            "row": self.keyboardPos.row,
            "col": self.keyboardPos.col
        }


class Datagram(metaclass=ABCMeta):
    def __init__(self, sectionList: list[Section], label: typing.Any, offsetInPassword: int, offsetInSegment: int,
                 pwStr: str):
        super().__init__()
        self.pwStr = pwStr  # whole password string

        self.offsetInPassword = offsetInPassword  # index of the last character of subPwStr in pwStr
        self.offsetInSegment = offsetInSegment
        self.sectionList: list[Section] = sectionList
        self.label = label

    def _tojson(self):
        return {
            "section number": len(self.sectionList),
            "section list": [x._tojson() for x in self.sectionList if x is not None],
            "label": str(self.label),
            "offsetInPassword": self.offsetInPassword,
            "offsetInSegment": self.offsetInSegment
        }

    def _tovector(self):
        vector = []
        for section in self.sectionList:
            sectionVector = section._tovector()
            vector += sectionVector
        vector += [self.offsetInPassword, self.offsetInSegment]
        return vector


class Password(metaclass=ABCMeta):
    def __init__(self, pwStr: str, datagramList: list[Datagram]):
        super().__init__()
        self.datagramList: list[Datagram] = datagramList
        self.pwStr = pwStr

    def _tojson(self):
        return {
            "pwStr": self.pwStr,
            "datagramNum": len(self.datagramList),
            "datagrams": [x._tojson() for x in self.datagramList if x is not None]
        }
