import typing

from Commons import BasicTypes
from Context.Context import BasicContext
from Commons import  Exceptions

CONTEXT = None

class PIIExtended(BasicTypes.PII):
    def __init__(self,username: str = None, name: str = None, birthday: str = None, phoneNum: str = None):
        super().__init__(username=username,name=name,birthday=birthday,phoneNum= phoneNum)





class PIIVector:
    def __init__(self, s: str, piitype: BasicTypes.PIIType, piivalue: int):
        self.str: str = s
        self.piitype: BasicTypes.PIIType = piitype
        self.piivalue: int = piivalue
        self.row = 0
        self.col = 0


class Datagram(BasicContext):
    pass

class Password(BasicContext):
    pass


# All PII structure representations of password s
def parseStrToPIIVector(s: str, pii:BasicTypes.PII) -> typing.List[PIIVector]:
    pass


# Fullname, Abbr, or None(abbr has nothing with name)
def parseNameType(name:str, abbr:str)->BasicTypes.NameType:
    ln = len(name)
    la = len(abbr)
    if ln < la:
        raise Exceptions.ParseException(f"Parse name type error : {name} and {abbr}")
    if ln == la:
        return BasicTypes.NameType.FullName
    ni = 0
    ai = 0
    while ni < ln and ai < la:
        ac = abbr[ai]
        nc = name[ni]
        if ac == nc:
            ni += 1
            ai += 1
        else:
            ni += 1
    if ai >= la:
        return BasicTypes.NameType.AbbrName
    if ni >= ln:
        return None




