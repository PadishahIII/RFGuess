import datetime
import re
import typing

from Commons import BasicTypes
from Commons import Exceptions
from Context.Context import BasicContext

CONTEXT = None


# class PIIExtended(BasicTypes.PII):
#     def __init__(self, account: str = None, name: str = None, birthday: str = None, phoneNum: str = None):
#         super().__init__(account=account, name=name, birthday=birthday, phoneNum=phoneNum)


class PIIVector:
    def __init__(self, s: str, piitype: BasicTypes.PIIType, piivalue: int):
        self.str: str = s
        self.piitype: BasicTypes.PIIType = piitype
        self.piivalue: int = piivalue
        self.row = 0
        self.col = 0


class Tag:
    def __init__(self, t: BasicTypes.PIIType, s: str):
        self.piitype = t
        self.s = s


# contain all tags for a PII
class PIITagContainer:

    def __init__(self, pii: BasicTypes.PII, nameFuzz=False):
        self._tagDict: typing.Dict[BasicTypes.PIIType, list] = dict()
        self._tagList: typing.List[Tag] = list()
        self._pii = pii
        self._nameFuzz = nameFuzz

    def setNameFuzz(self, b: bool):
        self._nameFuzz = b

    def getTagList(self):
        return self._tagList

    def parse(self):
        self._buildTagDict()
        self._buildTagList()

    def updateDict(self, d: dict):
        for k, l in d.items():
            if k in self._tagDict.keys():
                pre: list = self._tagDict[k]
                ll = pre + l
                s = set(ll)
                self._tagDict[k] = list(s)
            else:
                self._tagDict[k] = l

    def _buildTagDict(self):
        if self._nameFuzz is True:
            for tu in Fuzzers.fuzzName(self._pii.name, self._pii.firstName, self._pii.givenName):
                d = PIIToTagParser.parseNameToTagDict(tu[0], tu[1], tu[2])
                self.updateDict(d)
        else:
            d = PIIToTagParser.parseNameToTagDict(self._pii.name, self._pii.firstName, self._pii.givenName)
            self.updateDict(d)

        d = PIIToTagParser.parseBirthdayToTagDict(self._pii.birthday)
        self.updateDict(d)

        d = PIIToTagParser.parseAccountToTagDict(self._pii.account)
        self.updateDict(d)

        d = PIIToTagParser.parseEmailToTagDict(self._pii.email)
        self.updateDict(d)

        d = PIIToTagParser.parsePhoneNumToTagDict(self._pii.phoneNum)
        self.updateDict(d)

        d = PIIToTagParser.parseIdCardNumToTagDict(self._pii.idcardNum)
        self.updateDict(d)

    def _buildTagList(self):
        for k, v in self._tagDict.items():
            if not isinstance(v, list):
                raise Exceptions.PIIParserException(f"Parse TagDict Error: Expected list, given: {type(v)}")
            for i in v:
                t = Tag(k, i)
                self._tagList.append(t)


class Datagram(BasicContext):
    pass


class Password(BasicContext):
    pass


class Fuzzers:
    @classmethod
    def swapFirstCase(cls, s: str):
        f = s
        if s[0].islower():
            f = f[0].capitalize() + f[1:]
        else:
            f = f[0].lower() + f[1:]
        return f

    @classmethod
    def fuzzBirthday(cls, data_obj: datetime.datetime) -> dict:
        pass

    @classmethod
    def fuzzName(cls, name: str, firstName: str, givenName: str) -> typing.List[tuple]:
        l = list()
        l.append((name, firstName, givenName))

        n = name
        f = firstName
        g = givenName
        # swap first character's capital
        f = Fuzzers.swapFirstCase(firstName)
        g = Fuzzers.swapFirstCase(givenName)
        l.append((n, f, g))

        f = firstName.lower()
        g = givenName.lower()
        l.append((n, f, g))
        return l


class LDSStepper:
    @classmethod
    def checkLDSType(cls, s: str) -> BasicTypes.PIIType:
        c = s[0]
        if s.isdigit():
            return BasicTypes.PIIType.D
        elif s.isalpha():
            return BasicTypes.PIIType.L
        else:
            return BasicTypes.PIIType.S

    @classmethod
    def getAllSegment(cls, s: str) -> typing.List[BasicTypes.LDSSegment]:
        l = list()
        limit = len(s)
        start = 0
        i = 1
        curType = LDSStepper.checkLDSType(s[0])
        while i < limit:
            t = LDSStepper.checkLDSType(s[i])
            if t == curType:
                i += 1
            else:
                seg = BasicTypes.LDSSegment(curType, i - start, s[start:i])
                l.append(seg)
                start = i
                i += 1
                curType = t
        seg = BasicTypes.LDSSegment(curType, i - start, s[start:i])
        l.append(seg)

        return l


class EmailParser:

    # return prefix, None means not in email format
    @classmethod
    def parseEmailPrefix(cls, s: str) -> str:
        m = re.match(r"([^@\.]+)@[^@]+", s)
        if m is None:
            return None
        return m.group(1)


class PIIFullTagParser:
    def __init__(self, pii: BasicTypes.PII, nameFuzz=False):
        self._pii = pii
        self._tagContainer = None
        self._nameFuzz = nameFuzz

    def parseTag(self):
        self._tagContainer = PIITagContainer(self._pii, nameFuzz=self._nameFuzz)
        self._tagContainer.parse()

    def getTagContainer(self):
        return self._tagContainer


class PIIToTagParser:
    # parse pii into tags
    # pii with birthday = 19820607 => BirthdayType:value
    # dict key: PIIType, value: list of candidates
    # such as BirthdayType.Date can be expressed by 67 or 0607
    @classmethod
    def parsePIIToTagDict(cls, pii: BasicTypes.PII) -> typing.Dict[typing.Any, list]:
        pass

    # given a name, get all tags
    # givenName must in format that can split by space, like "zhong jie"
    # dict key: NameType, value: list of candidates
    @classmethod
    def parseNameToTagDict(cls, name: str, firstName: str, givenName: str) -> typing.Dict[
        BasicTypes.PIIType.NameType, list]:
        d = dict()
        d[BasicTypes.PIIType.NameType.FullName] = name
        _l = givenName.split()
        l = [x for x in _l if len(x) > 0]
        givenNameWithoutSpace = ''.join(l)
        d[BasicTypes.PIIType.NameType.AbbrName] = firstName[0] + ''.join(x[0] for x in l if len(x) > 0)
        d[BasicTypes.PIIType.NameType.FamilyName] = firstName
        d[BasicTypes.PIIType.NameType.GivenName] = givenName
        d[BasicTypes.PIIType.NameType.GivenName1stPlusFamilyName] = givenName[0] + firstName
        d[BasicTypes.PIIType.NameType.FamilyName1stPlusGivenName] = firstName[0] + givenNameWithoutSpace
        d[BasicTypes.PIIType.NameType.FamilyNameCapitalized] = firstName[0].capitalize() + firstName[1:]

        for k, v in d.items():
            d[k] = [v, ]
        return d

    @classmethod
    def parseBirthdayToTagDict(cls, birthday: str) -> typing.Dict[BasicTypes.PIIType.BirthdayType, list]:
        try:
            date_obj = datetime.datetime.strptime(birthday, "%Y%m%d")
            d = dict()
            last2digitsofyear = str(date_obj.year)[-2:]
            d[BasicTypes.PIIType.BirthdayType.FullYMD] = [datetime.datetime.strftime(date_obj, "%Y%m%d"), ]
            d[BasicTypes.PIIType.BirthdayType.FullMDY] = [datetime.datetime.strftime(date_obj, "%m%d%Y"), ]
            d[BasicTypes.PIIType.BirthdayType.FullDMY] = [datetime.datetime.strftime(date_obj, "%d%m%Y"), ]
            d[BasicTypes.PIIType.BirthdayType.Date] = [datetime.datetime.strftime(date_obj, "%m%d"), ]
            d[BasicTypes.PIIType.BirthdayType.Year] = [datetime.datetime.strftime(date_obj, "%Y"), ]
            d[BasicTypes.PIIType.BirthdayType.YM] = [datetime.datetime.strftime(date_obj, "%Y%m"), ]
            d[BasicTypes.PIIType.BirthdayType.MY] = [datetime.datetime.strftime(date_obj, "%m%Y"), ]
            d[BasicTypes.PIIType.BirthdayType.Year2lastdigitsPlusDateMD] = [
                last2digitsofyear + datetime.datetime.strftime(date_obj, "%m%d"), ]
            d[BasicTypes.PIIType.BirthdayType.DateMDPlusYear2lastdigits] = [
                datetime.datetime.strftime(date_obj, "%m%d") + last2digitsofyear, ]
            d[BasicTypes.PIIType.BirthdayType.DateDMPlusYear2lastdigits] = [
                datetime.datetime.strftime(date_obj, "%d%m") + last2digitsofyear, ]

            return d
        except Exception as e:
            print(e)
            raise Exceptions.PIIParserException(f"Invaild birthday format {birthday}")

    @classmethod
    def parseAccountToTagDict(cls, account: str) -> typing.Dict[BasicTypes.PIIType.AccountType, list]:
        segList = LDSStepper.getAllSegment(account)
        d = dict()
        d[BasicTypes.PIIType.AccountType.Full] = [account, ]
        letterSegment = None
        digitSegment = None
        for seg in segList:
            if seg.type == BasicTypes.PIIType.L:
                if letterSegment is None:
                    letterSegment = seg
            elif seg.type == BasicTypes.PIIType.D:
                if digitSegment is None:
                    digitSegment = seg
        if letterSegment is None and digitSegment is None:
            raise Exceptions.PIIParserException("parse Account error")
        if letterSegment is not None:
            d[BasicTypes.PIIType.AccountType.LetterSegment] = [letterSegment.s, ]
        if digitSegment is not None:
            d[BasicTypes.PIIType.AccountType.DigitSegment] = [digitSegment.s, ]
        return d

    @classmethod
    def parseEmailToTagDict(cls, email: str) -> typing.Dict[BasicTypes.PIIType.EmailPrefixType, list]:
        prefix = EmailParser.parseEmailPrefix(email)
        if prefix is None:
            raise Exceptions.PIIParserException(f"Invaild email : {email}")
        d = dict()
        d[BasicTypes.PIIType.EmailPrefixType.FullPreix] = [prefix, ]
        d[BasicTypes.PIIType.EmailPrefixType.LetterSegment] = []
        d[BasicTypes.PIIType.EmailPrefixType.DigitSegment] = []
        segList = LDSStepper.getAllSegment(prefix)
        letterSeg = None
        digitSeg = None
        for seg in segList:
            if seg.type == BasicTypes.PIIType.L:
                if letterSeg is None:
                    letterSeg = seg
            elif seg.type == BasicTypes.PIIType.D:
                if digitSeg is None:
                    digitSeg = seg
        if letterSeg is None and digitSeg is None:
            raise Exceptions.PIIParserException("Parse Email Error")
        if letterSeg is not None:
            d[BasicTypes.PIIType.EmailPrefixType.LetterSegment] = [letterSeg.s, ]
        if digitSeg is not None:
            d[BasicTypes.PIIType.EmailPrefixType.DigitSegment] = [digitSeg.s, ]

        return d

    @classmethod
    def parsePhoneNumToTagDict(cls, phoneNum: str) -> typing.Dict[BasicTypes.PIIType.PhoneNumber, list]:
        if not phoneNum.isdigit():
            raise Exceptions.PIIParserException(f"Invaild phone nubmer: {phoneNum}")
        d = dict()
        d[BasicTypes.PIIType.PhoneNumberType.FullNumber] = [phoneNum, ]
        d[BasicTypes.PIIType.PhoneNumberType.FirstThreeDigits] = [phoneNum[:3], ]
        d[BasicTypes.PIIType.PhoneNumberType.LastFourDigits] = [phoneNum[-4:], ]

        return d

    @classmethod
    def parseIdCardNumToTagDict(cls, idCardNum: str) -> typing.Dict[BasicTypes.PIIType.IdCardNumberType, list]:
        if not idCardNum.isdigit():
            raise Exceptions.PIIParserException(f"Invail id card number: {idCardNum}")
        d = dict()
        d[BasicTypes.PIIType.IdCardNumberType.Last4Digits] = [idCardNum[-4:], ]
        d[BasicTypes.PIIType.IdCardNumberType.First3Digits] = [idCardNum[:3], ]
        d[BasicTypes.PIIType.IdCardNumberType.First6Digits] = [idCardNum[:6], ]

        return d


# Fullname, Abbr, or None(abbr has nothing with name)
def checkPIINameType(name: str, abbr: str) -> BasicTypes.PIIType.NameType:
    ln = len(name)
    la = len(abbr)
    if ln < la:
        raise Exceptions.ParseException(f"Parse name type error : {name} and {abbr}")
    if ln == la:
        return BasicTypes.PIIType.NameType.FullName
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


# All PII structure representations of password s
#
def parseStrToPIIVector(pwStr: str, pii: BasicTypes.PII) -> typing.List[PIIVector]:
    parser = PIIFullTagParser(pii)
    parser.parseTag()
    tagList = parser._tagContainer.getTagList()
    representationList = list()
    gen = parseAllPIITagRecursive(tagList, pwStr, list())
    for l in gen:
        representationList.append(l)
    piiVectorlist = convertTagListToPIIVectorList(representationList)
    return piiVectorlist


def parseAllPIITagRecursive(tagList: typing.List[Tag], pwStr: str, curTags: typing.List[Tag]):
    if len(pwStr) <= 0:
        yield curTags
    candidates: typing.List[Tag] = list()
    for tag in tagList:
        if pwStr.startswith(tag.s):
            candidates.append(tag)
    for tag in candidates:
        s = len(tag.s)
        newPwStr = pwStr[s:]  # remove tag prefix
        curTags.append(tag)
        parseAllPIITagRecursive(tagList, pwStr=newPwStr, curTags=curTags)


def convertTagListToPIIVectorList(tagList: typing.List[Tag]) -> typing.List[PIIVector]:
    l = list()
    for tag in tagList:
        vector = PIIVector(tag.s, piitype=tag.piitype, piivalue=tag.piitype.value)
        l.append(vector)
    return l
