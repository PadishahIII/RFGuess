# from Parser.PasswordParsers import PasswordParsers.Segment,PasswordParsers.Datagram,Password
import base64
import pickle

import Commons.BasicTypes

PARSERS = False
if PARSERS is False:
    from Parser import PasswordParsers

    PARSERS = True
from Parser.CommonParsers import *


# Parse the type of character ch: Digit, Upper/Lower Case Letter, Special Characters
def parseType(ch: str) -> CharacterType:
    if len(ch) > 1 or len(ch) <= 0:
        raise ParseException(f"{ch} must be a single character")
    if str.isdigit(ch):
        return CharacterType.Digit
    elif str.isalpha(ch):
        if str.isupper(ch):
            return CharacterType.UpperCaseLetter
        elif str.islower(ch):
            return CharacterType.LowerCaseLetter
    else:
        return CharacterType.SpecialCharacter
    return None


# Transfer the begin/end symbol into that in CharacterType
def parseSymbol(c: int) -> CharacterType:
    if c == CharacterParser.BeginSymbol:
        return CharacterType.BeginSymbol
    elif c == CharacterParser.EndSymbol:
        return CharacterType.EndSymbol
    else:
        raise ParseException(f"Unknown symbol with value '{str(c)}'")


# Split a string into several Segments. Continuous characters with identical CharacterType belong to the same PasswordParsers.Segment
def parseSegment(s: str) -> typing.List[Commons.BasicTypes.Segment]:
    segList = list()
    curType = parseType(s[0])
    i = 1
    l = len(s)
    start = 0
    while i < l:
        tmpType = parseType(s[i])
        if tmpType == curType:
            pass
        else:
            segList.append(Commons.BasicTypes.Segment(curType, start, i))
            curType = tmpType
            start = i
        i += 1
    segList.append(Commons.BasicTypes.Segment(curType, start, i))
    return segList


# Get the PasswordParsers.Segment substring of s
def getSegmentStr(seg: Commons.BasicTypes.Segment, s: str) -> str:
    return s[seg.start: seg.end]


def getSegmentStrList(segList: typing.List[Commons.BasicTypes.Segment], s: str) -> typing.List[str]:
    return [s[x.start: x.end] for x in segList]


# transfer datagram to 26-dimension vector
# which can directly input to Decision Tree
def parseStandardVector(datagram: PasswordParsers.Datagram) -> typing.List[int]:
    l = datagram._tovector()
    for i in l:
        if not isinstance(i, int):
            raise ParseException(f"PasswordParsers.Datagram invail field: not a integer: {type(i)}:{i}")
    s = len(l)
    if s != 26:
        raise ParseException(f"parsing PasswordParsers.Datagram error: Invaild PasswordParsers.Datagram dimension: {s}")
    return l


# transfer datagram to 26-dimension vector
# which can directly input to Decision Tree
def parseStandardVectorByPassword(password: PasswordParsers.Password) -> typing.List[typing.List[int]]:
    dl = password.datagramList
    resList = list()
    for datagram in dl:
        resList.append(parseStandardVector(datagram))
    return resList


# Used in password-generation period, build prefix to be appended
# transfer a raw password string into 26-dim vector
def parseStandardVectorByStr(passwordStr: str) -> typing.List[int]:
    p = PasswordParsers.Password(passwordStr)
    datagram = p.datagramList[-1]
    # print(json.dumps(datagram._tojson(), indent=2))
    return parseStandardVector(datagram)


# Get the label of a PasswordParsers.Datagram
def getLabel(datagram: PasswordParsers.Datagram) -> int:
    return datagram.label


def getLabelByPassword(password: PasswordParsers.Password) -> typing.List[int]:
    dl = password.datagramList
    resList = list()
    for datagram in dl:
        resList.append(getLabel(datagram))
    return resList


def parseStrToDatagram(s: str) -> PasswordParsers.Datagram:
    p = PasswordParsers.Password(s)
    d = p.datagramList[-1]
    return d


class translation:
    def __init__(self, fromDict: dict, toDict: dict) -> object:
        """

        Args:
            fromDict: A hash map of the character list to be translated
            toDict:
        """
        self.fromDict: dict = fromDict
        self.toDict: dict = toDict

    @classmethod
    def makeTrans(cls, fromList: list, toList: list):
        """*translation* class factory

        Args:
            fromList:
            toList:

        Returns:

        """
        if len(fromList) != len(toList):
            raise TranslationException(f"Error: fromList's length({len(fromList)}) not equal to toList({len(toList)})")
        fromDict = {}
        toDict = {}
        for f in fromList:
            h = hash(f)
            fromDict[h] = f
        for t in toList:
            h = hash(t)
            toDict[h] = t
        return translation(fromDict, toDict)

    def translate(self, fromObj):
        h = hash(fromObj)
        try:
            fromIndex = list(self.fromDict.keys()).index(h)
            if fromIndex >= 0:
                toObj = list(self.toDict.values())[fromIndex]
                return toObj
            else:
                raise TranslationException(f"Error: {fromObj} with hash {h} not in the translation dictionary")
        except:
            raise TranslationException(f"Error: {fromObj} with hash {h} not in the translation dictionary")


class TranslationException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


from Scripts.databaseInit import PIIUnit
from Commons.BasicTypes import PII


def parsePIIUnitToPIIAndPwStr(unit: PIIUnit) -> (PII, str):
    """
    Convert PIIUnit into PII and password string

    Args:
        unit: input PIIUnit

    Returns:
        PII: PII object
        str: password string
    """

    def getFirstName(name: str):
        l = name.split()
        n = l[0]
        return n.strip()

    def getGivenName(name: str):
        l = name.partition(" ")
        n = l[2]
        if len(n) <= 0:
            n = l[1]
        return n.strip()

    def getBirthday(idCard: str):
        return idCard[-12:-4]

    d = dict()

    d['email'] = unit.email
    d['account'] = unit.account
    d['name'] = unit.name
    d['firstName'] = getFirstName(unit.fullName)
    d['givenName'] = getGivenName(unit.fullName)
    d['birthday'] = getBirthday(unit.idCard)
    d['phoneNum'] = unit.phoneNum
    d['idcardNum'] = unit.idCard
    pii = PII(**d)

    return pii, unit.password


class Serializer:
    """
    Serializer. Base64 encode the serialized bytes
    """

    @classmethod
    def serialize(obj) -> str:
        objSe = pickle.dumps(obj)
        s = base64.b64encode(objSe).decode("utf-8")
        return s

    def deserialize(s: str) -> object:
        obj = pickle.loads(base64.b64decode(s.encode("utf-8")))
        return obj
