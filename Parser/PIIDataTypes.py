import typing
from copy import copy

from Commons import BasicTypes
from Parser import BasicDataTypes


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
