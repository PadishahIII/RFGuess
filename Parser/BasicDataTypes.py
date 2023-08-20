import typing
from abc import abstractmethod, ABCMeta
from copy import copy

from Commons import BasicTypes

"""
Dataset: a bunch of Dataunit
   Dataunit: a single item in dataset, e.g. (pwStr) in trawling mode and (pwStr,pii) in PII mode

Password: a set of 26-dim vectors expressed by several Datagrams
   Datagram: a 26-dim vector expressed by several Sections
       Section: a 4-dim vector expressed by (type,value,row,col)
       Label: abstract label class which can be transformed to Integer
"""


class Label(metaclass=ABCMeta):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def toInt(self):
        """
        Get Integer label

        """
        pass


class Section(metaclass=ABCMeta):
    """
    a 4-dim vector expressed by (type,value,row,col)
    """

    def __init__(self, type, value, keyboardPos: BasicTypes.KeyboardPosition):
        super().__init__()
        self.type = type
        self.value = value
        self.keyboardPos = keyboardPos

    def __copy__(self):
        return Section(self.type, self.value, self.keyboardPos)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(self.type) ^ hash(self.value) + hash(self.keyboardPos.row) + hash(self.keyboardPos.col)

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
    """
    a 26-dim vector expressed by several Sections
    """

    def __init__(self, sectionList: list[Section], label: typing.Any, offsetInPassword: int, offsetInSegment: int,
                 pwStr: str):
        super().__init__()
        self.pwStr = pwStr  # whole password string

        self.offsetInPassword = offsetInPassword  # index of the last character of subPwStr in pwStr
        self.offsetInSegment = offsetInSegment
        self.sectionList: list[Section] = sectionList
        self.label = label

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        h = hash(self.offsetInSegment)
        h ^= hash(self.pwStr)
        h ^= hash(self.offsetInPassword)
        for s in self.sectionList:
            h ^= hash(s)
        h ^= hash(self.label)
        return h

    def __copy__(self):
        """
        Copy section list
        """
        newSectionList = list()
        for s in self.sectionList:
            newSection = copy(s)
            newSectionList.append(newSection)
        return Datagram(newSectionList, self.label, self.offsetInPassword, self.offsetInSegment, self.pwStr)

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
    """
    a set of 26-dim vectors expressed by several Datagrams
    """

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


class DataUnit(metaclass=ABCMeta):
    """
    DataUnit stores a property dict.
    DataUnit is comparable, hashable, printable.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.properties = kwargs

    def __eq__(self, o: object) -> bool:
        return self.__hash__() == hash(o)

    def get(self, key: str):
        return self.properties.get(key)

    def set(self, key: str, value):
        self.properties[key] = value

    def keys(self):
        return self.properties.keys()

    def items(self):
        return self.properties.items()

    def values(self):
        return self.properties.values()

    def __str__(self) -> str:
        return str(self.properties)

    def __hash__(self):
        h = hash(tuple(self.values()))
        return h


class DataSet(metaclass=ABCMeta):
    """

    DataSet is a set of unit, provides methods to build the dataset and is iterable.


    Notes:
        - Build a DataSet use `push` method
        - Get units in DataSet use `iter(dataset)`

    Attributes:
        keyList (list): name of attributes in the unit
        unitList (list): list of units
        row (int): number of units
        col (int): dimension of unit

    Methods:
        - `setKeyList(key-list)`: set name of properties
        - `createUnit(value-list)`: input a value list, combine keyList, return a unit which contains a dict
        - `push(DataUnit)`: push a unit into dataset
        - `checkUnit(DataUnit)`: check before push a unit
        - `resetUnitList(list)`: clear current dataset and re-push every unit in param
    Raises:
        DatasetException
    """

    def __init__(self) -> None:
        super().__init__()
        self.keyList = list()
        self.unitList: list[DataUnit] = []
        self.row = 0
        self._col = len(self.keyList)

    def setKeyList(self, keylist: list):
        self.keyList = keylist

    def __len__(self):
        return self.row

    @property
    def col(self):
        return self._col

    @col.setter
    def col(self, c):
        self._col = c

    def push(self, unit: DataUnit):
        """
        Push a unit into dataset

        Args:
            unit (DataUnit): input unit
        """
        if not self.checkUnit(unit):
            raise DatasetException(f"Invaild Unit: {unit}")
        self.unitList.append(unit)
        self.row += 1

    def getUnitList(self):
        return self.unitList

    def resetUnitList(self, unitlist: list[DataUnit]):
        """
        Clear current dataset and re-push every unit in param

        Args:
            unitlist (list[DataUnit]): units to re-push
        """
        self.unitList.clear()
        self.row = 0
        for unit in unitlist:
            self.push(unit)

    @abstractmethod
    def createUnit(self, valueList: list) -> DataUnit:
        """
        Input a value list, combine keyList, return a unit which contains a dict

        Args:
            valueList (list): list of values in order of keyList
        """
        pass

    @abstractmethod
    def checkUnit(self, unit: DataUnit) -> bool:
        """
        Check before push a unit

        Args:
            unit (DataUnit): input
        """
        pass

    def __iter__(self):
        return iter(self.unitList)


class DatasetException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
