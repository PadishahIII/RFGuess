import typing
from copy import copy

from Commons import BasicTypes, Utils
from Commons.Property import StrProperty
from Parser import BasicDataTypes

'''
Foreground analyzing phase datastructures
'''


class PIIVector(StrProperty):
    """
    4-dimension vector data used in model input and Output which is more representative than PIISection
    Attributes:
        str (str): section string
        piitype (PIIType): specified pii type, like "PIIType.FullName"
        piitypevalue (int): enum value of pii type
        piivalue (int): value of type, identical to `piitype.value` for pii vector and denotes length of segment in terms of LDS vector
    """

    def __init__(self, s: str, piitype: BasicTypes.PIIType, piivalue: int):
        super().__init__(s)
        self.piitype: BasicTypes.PIIType = piitype
        self.piitypevalue: int = self.piitype.value
        self.piivalue: int = piivalue
        self.row = 0
        self.col = 0

    def __hash__(self):
        return hash((self.piitype.__class__, self.piivalue, self.piitypevalue, self.row, self.col))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __copy__(self):
        return PIIVector(s=self.str, piitype=self.piitype, piivalue=self.piivalue)

    def _tojson(self):
        obj = {
            "PIIType": str(self.piitype) + f" {self.piitype.name}",
            "s": self.str
        }
        return obj


class PIIRepresentation:
    """
    A representation of password string, compose of several PIIVectors(containing LDS)
    """

    def __init__(self, l: typing.List[PIIVector]):
        self.piiVectorList: typing.List[PIIVector] = l
        self.len = len(self.piiVectorList)

    def __len__(self):
        return self.len

    def __copy__(self):
        newVectorList = list()
        for vector in self.piiVectorList:
            newVector = copy(vector)
            newVectorList.append(newVector)
        return PIIRepresentation(newVectorList)

    def _tojson(self):
        l = list()
        for vector in self.piiVectorList:
            if vector != None:
                l.append(vector._tojson())
        return {
            "vector number": self.len,
            "vectors": l
        }

    def __str__(self) -> str:
        pass


class PIIStructure:
    """
    All representations of password string, compose of PIIRepresentations in different length
    """

    def __init__(self, s: str, l: typing.List[PIIRepresentation]):
        self.piiRepresentationList: typing.List[PIIRepresentation] = l
        self.num = len(self.piiRepresentationList)
        self.s = s

    def __len__(self):
        return self.num

    def _tojson(self):
        l = [x._tojson() for x in self.piiRepresentationList if x != None and len(x) > 0]
        return {
            "password string": self.s,
            "representation number": self.num,
            "representations": l
        }


'''
PwRepresentation resolver datastructures
'''


class RepUnit:
    """
    A unit of representationStructure,repStructure hash and frequency
    Comparable, hashable
    """

    def __init__(self, repStructureStr: str, repStructureHash: str, frequency: int):
        self.repStr = repStructureStr
        self.repHash = repStructureHash
        self.frequency = frequency
        self._hash = Utils.md5(self.repHash)

    def __hash__(self):
        return self._hash

    def __eq__(self, o: object) -> bool:
        return self._hash == o._hash

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def create(cls, repStr: str, repHash: str, frequency: int):
        return RepUnit(repStr, repHash, frequency)


class PwRepAndStructureUnit:
    """
    A password string and its unique representation and representationStructure
    A unit of pwStr, representation and structure

    """

    def __init__(self, pwStr: str, rep: PIIRepresentation, repStructure: PIIRepresentation):
        self.pwStr = pwStr
        self.rep: PIIRepresentation = rep
        self.repStructure: PIIRepresentation = repStructure

    @classmethod
    def create(cls, pwStr: str, rep: PIIRepresentation, repStructure: PIIRepresentation):
        return PwRepAndStructureUnit(pwStr, rep, repStructure)


'''
Preprocessor datastructures
'''


class PIIDataUnit(BasicDataTypes.DataUnit):
    """
    PIIDataUnit stores a PII object and a password string corresponding to PIIUnit fields


    """

    def __init__(self, pii: BasicTypes.PII, pwStr: str) -> None:
        """
        Overwrite __init__ of DataUnit. Input a PII and password string.
        Args:
            pii: PII to store
            pwStr: password string
        """
        super().__init__(**(pii.__dict__))
        self.password = pwStr
        self.pii = pii
        self.properties['password'] = self.password

    def getPII(self) -> BasicTypes.PII:
        """
        Get PII object

        Returns:
            PII: PII object
        """
        return self.pii

    def getPassword(self) -> str:
        """
        Get the password string

        Returns:
            str: password string
        """
        return self.password


class PIIDataSet(BasicDataTypes.DataSet):
    """
    Notes:
        - The `keyList` of PIIDataSet must match the fields of PII class plus an additional *password* field

    """

    def createUnit(self, valueList: list) -> PIIDataUnit:
        """
        This method would extract PII and password string through `keyList` and param `valueList`.

        Args:
            valueList (list): values in the order of `keyList`

        Returns:
            PIIDataUnit: bound to a PII and password string

        Examples:
            dataset = PIIDataSet()
            dataset.generateKeyList(pii)
            unit = dataset.createUnit(dataset.getValueList(pii,pwStr))
            dataset.push(unit)
            for u in iter(dataset):
                print(str(u))
        """
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
        pwStr = d['password']
        del d['password']
        pii = BasicTypes.PII(**d)
        unit = PIIDataUnit(pii, pwStr)
        return unit

    def checkUnit(self, unit: PIIDataUnit) -> bool:
        return True

    def generateKeyList(self, pii: BasicTypes.PII):
        """
        Set keyList automatically using PII object given.
        Append 'password' into keyList due to PII class do not include 'password' field.

        Args:
            pii: input PII object
        """
        l = self._parseKeyList(pii)
        l.append("password")
        self.keyList = l

    def _parseKeyList(self, pii: BasicTypes.PII) -> list:
        """
        Parse keyList from PII object

        Args:
            pii: input PII object

        Returns:
            list of PII fields
        """
        return list(pii.__dict__.keys())

    def getValueList(self, pii: BasicTypes.PII, pwStr: str) -> list:
        """
        Get the value list of given pii according to keyList excluding 'password' field.

        Args:
            pii: input pii
            pwStr: password string

        Returns:
            list of values correspond to keyList
        """
        l = list()
        kl = copy(self.keyList)
        kl.remove("password")
        for key in kl:
            value = getattr(pii, key, None)
            if value is None:
                raise PIIDataSetException(f"getValueList Error: no match for key {key} in PII object {pii.__dict__}")
            l.append(value)
        l.append(pwStr)
        return l


class PIIDataSetException(BasicDataTypes.DatasetException):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


'''
PII data types extend BasicDataTypes
'''


class PIISection(BasicDataTypes.Section):
    """

    Attributes:
        type (PIIType.BaseTypes): like `Name`, `Account`,...
        value (PIIType or int): like `NameType.FullName`
    Notes:
        `value` field store either `PIIType` or int, LDS section use int value and pii sections use corresponding Enum type for value

    """

    def __init__(self, type: BasicTypes.PIIType.BaseTypes, value: BasicTypes.PIIType):
        super().__init__(type, value, BasicTypes.KeyboardPosition(0, 0))

    def __copy__(self):
        return PIISection(self.type, self.value)

    def __eq__(self, other):
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()

    def getIntValue(self) -> int:
        if isinstance(self.value, int):
            return self.value
        else:
            return self.value.value

    def _tojson(self):
        return {
            "PII Type:": str(self.type) + f" {self.type.name}",
            "PII value": self.value if isinstance(self.value, int) else str(self.value) + f" {self.value.name}",
        }

    def _tovector(self) -> list[int, int, int, int]:
        return [
            int(self.type.value),
            int(self.getIntValue()),
            int(self.keyboardPos.row),
            int(self.keyboardPos.col)
        ]


class PIILabel(BasicDataTypes.Label):

    def __init__(self, section: PIISection) -> None:
        super().__init__()
        self.section: PIISection = section

    @classmethod
    def create(cls, section: PIISection):
        return PIILabel(section)

    def toInt(self):
        return self.section.type.value + self.section.getIntValue()


class PIILabelException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class PIIDatagram(BasicDataTypes.Datagram):
    """
    Hashable, comparable
    """

    def __init__(self, sectionList: list[PIISection], label: PIILabel, offsetInPassword: int, offsetInSegment: int,
                 pwStr: str):
        super().__init__(sectionList, label, offsetInPassword, offsetInSegment, pwStr)

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return super().__eq__(other)

    def __copy__(self):
        newList: list[PIISection] = list()
        for section in self.sectionList:
            newSection = copy(section)
            newList.append(newSection)
        return PIIDatagram(newList, self.label, self.offsetInPassword, self.offsetInSegment, self.pwStr)


class PIIPassword(BasicDataTypes.Password):
    def __init__(self, pwStr: str, datagramList: list[PIIDatagram]):
        super().__init__(pwStr, datagramList)
