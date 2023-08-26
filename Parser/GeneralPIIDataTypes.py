from Commons.BasicTypes import *
from Parser.PIIDataTypes import *

'''
Foreground analyzing phase datastructures
'''


class CharacterVector(StrProperty):
    """Denoting a character
    4-dimension vector data used in model input and Output which is more representative than PIISection
    Attributes:
        ch (str): character string
        type (CharacterType): type of character
        serialNum (PIIType): serial number of character
        keyboardPos (KeyboardPos): keyboard position
    """

    def __init__(self, ch: str, type: CharacterType, serialNum: int, keyboardPos: KeyboardPosition, ) -> None:
        super().__init__(ch)
        self.type: CharacterType = type
        self.serialNum: int = serialNum
        self.keyboardPos: KeyboardPosition = keyboardPos

    def __hash__(self):
        return hash((self.type, self.serialNum, self.keyboardPos.row, self.keyboardPos.col))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __copy__(self):
        return CharacterVector(self.getStr(), self.type, self.serialNum, self.keyboardPos)

    def _tojson(self):
        return {
            "CharacterType": str(self.type.name),
            "CharacterStr": self.getStr(),
            "SerialNum": self.serialNum,
            "KeyboardPos": f"{self.keyboardPos.row}:{self.keyboardPos.col}"
        }


class GeneralPIIVector(StrProperty):
    """
    A *Unit* object of `PIIVector` and `CharacterVector`
    Attributes:
        isPIIVector (bool): pii vector for True and CharacterVector for False
        vectorObj (PIIVector or CharacterVector): vector object
    """

    def __init__(self, vector: StrProperty, isPIIVector: bool, ) -> None:
        super().__init__(vector.getStr())
        self.isPIIVector = isPIIVector
        self.vectorObj = vector

    def __hash__(self):
        return hash((self.isPIIVector, self.vectorObj))

    def __eq__(self, other):
        return self.isPIIVector == other.isPIIVector and self.vectorObj == other.vectorObj

    def __copy__(self):
        newVector = copy(self.vectorObj)
        return GeneralPIIVector(newVector, self.isPIIVector)

    def _tojson(self):
        return self.vectorObj._tojson()


class GeneralPIIRepresentation:
    """
    A representation of password string, compose of a `GeneralPIIVector` list
    """

    def __init__(self, l: list[GeneralPIIVector]) -> None:
        self.vectorList: list[GeneralPIIVector] = l
        self.len = len(self.vectorList)

    def __len__(self):
        return self.len

    def __hash__(self):
        t = tuple(self.vectorList)
        return hash(t)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __copy__(self):
        newVectorList = list()
        for vector in self.vectorList:
            newVector = copy(vector)
            newVectorList.append(newVector)
        return GeneralPIIRepresentation(newVectorList)

    def _tojson(self):
        l = list()
        for vector in self.vectorList:
            if vector is not None:
                l.append(vector._tojson())
        return {
            "vector number": self.len,
            "vectors": l
        }


class GeneralPIIStructure:
    """
    All representations of password string, compose of `GeneralPIIRepresentation` in different length

    """

    def __init__(self, pwStr: str, repList: list[GeneralPIIRepresentation]) -> None:
        self.repList: list[GeneralPIIRepresentation] = repList
        self.num = len(self.repList)
        self.pwStr = pwStr

    def __len__(self):
        return self.num

    def _tojson(self):
        l = [x._tojson() for x in self.repList]
        return {
            "pwStr": self.pwStr,
            "representation number": self.num,
            "representations": l
        }


'''
GeneralPwRepresentation resolver datastructures
'''


class GeneralRepUnit(RepUnit):
    """
    A unit of representationStructure,repStructure hash and frequency
    Comparable, hashable
    """

    def __hash__(self):
        return self._hash

    def __eq__(self, o: object) -> bool:
        return self._hash == o._hash

    @classmethod
    def create(cls, repStr: str, repHash: str, frequency: int):
        return GeneralRepUnit(repStr, repHash, frequency)


class GeneralPwRepAndStructureUnit(PwRepAndStructureUnit):
    """
    A password string and its unique representation and representationStructure
    A unit of pwStr, representation and structure

    """

    def __init__(self, pwStr: str, rep: GeneralPIIRepresentation, repStructure: GeneralPIIRepresentation):
        super().__init__(pwStr, rep, repStructure)
        self.rep: GeneralPIIRepresentation
        self.repStructure: GeneralPIIRepresentation

    @classmethod
    def create(cls, pwStr: str, rep: GeneralPIIRepresentation, repStructure: GeneralPIIRepresentation):
        return GeneralPwRepAndStructureUnit(pwStr, rep, repStructure)


'''
General PII/Character data types extend BasicDataTypes
'''


class CharacterSection(BasicDataTypes.Section):
    """
    Attributes:
        ch (str): character
        type (BasicTypes.CharacterType): like `Digit`, `SpecialCharacter`...
        value (int): serial number
    """

    def __init__(self, ch: str, type: BasicTypes.CharacterType, serialNum, keyboardPos: BasicTypes.KeyboardPosition):
        super().__init__(type, serialNum, keyboardPos)
        self.ch = ch

    def __copy__(self):
        return CharacterSection(self.ch, self.type, self.value, self.keyboardPos)

    def __eq__(self, other):
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()

    def _tojson(self):
        return {
            "character": self.ch,
            "characterType": str(self.type.name),
            "serial number": str(self.value),
            "keyboardpos": f"r{self.keyboardPos.row}:c{self.keyboardPos.col}"
        }

    def _tovector(self) -> list[int, int, int, int]:
        return [
            int(self.type.value),
            int(self.value),
            int(self.keyboardPos.row),
            int(self.keyboardPos.col)
        ]


class GeneralPIISection(BasicDataTypes.Section):
    """
    Store either a `PIISection` or `CharacterSection`
    Attributes:
        isPIIVector (bool): True for PIIVector else for CharacterVector
        vector (PIIVector or CharacterVector): vector object

    """

    def __init__(self, vector: BasicDataTypes.Section, isPII: bool):
        super().__init__(vector.type, vector.value, vector.keyboardPos)
        self.isPII = isPII
        self.vector = vector

    def __copy__(self):
        newVector = copy(self.vector)
        return GeneralPIISection(newVector, self.isPII)

    def __eq__(self, other):
        return self.vector.__eq__(other.vector)

    def __hash__(self):
        return self.vector.__hash__()

    def _tojson(self):
        return {
            "isPII:": self.isPII,
            "vector": self.vector._tojson()
        }

    def _tovector(self) -> list[int, int, int, int]:
        return self.vector._tovector()


class CharacterLabel(BasicDataTypes.Label):
    def __init__(self, section: CharacterSection) -> None:
        super().__init__()
        from Parser.CommonParsers import LabelParser
        self.lp: LabelParser = LabelParser.getInstance()
        self.section: CharacterSection = section

    def toInt(self):
        return self.lp.encodeCh(self.section.ch)


class GeneralPIILabel(BasicDataTypes.Label):
    """
    Store either a PIILabel or CharacterLabel

    """

    def __init__(self, label: BasicDataTypes.Label, isPIILabel: bool) -> None:
        """
        Args:
            label: PIILabel or CharacterLabel
            isPIILabel: True for PIILable and False for CharacterLabel
        """
        super().__init__()
        self.label: BasicDataTypes.Label = label

    def toInt(self):
        return self.label.toInt()


class GeneralPIIDatagram(BasicDataTypes.Datagram):
    """
    Hashable, comparable
    """

    def __init__(self, sectionList: list[GeneralPIISection], label: GeneralPIILabel, offsetInPassword: int,
                 offsetInSegment: int,
                 pwStr: str):
        super().__init__(sectionList, label, offsetInPassword, offsetInSegment, pwStr)
        self.sectionList: list[GeneralPIISection]
        self.label: GeneralPIILabel

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return super().__eq__(other)

    def __copy__(self):
        newList: list[GeneralPIISection] = list()
        for section in self.sectionList:
            newSection = copy(section)
            newList.append(newSection)
        return GeneralPIIDatagram(newList, self.label, self.offsetInPassword, self.offsetInSegment, self.pwStr)


class GeneralPIIPassword(BasicDataTypes.Password):
    def __init__(self, pwStr: str, datagramList: list[GeneralPIIDatagram]):
        super().__init__(pwStr, datagramList)
