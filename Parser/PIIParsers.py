import datetime
from enum import Enum

from Commons import Exceptions
from Commons.BasicTypes import PIIType
from Commons.Modes import Singleton
from Parser.BasicParsers import BasicParser, BasicParserException
from Parser.PIIDataTypes import *
from Scripts import Utils as DatabaseUtils
from Scripts.databaseInit import *

CONTEXT = None

'''
pii => parse pii tags from every pii field into respective PII types, get pii tag list 
    for every pwStr => parse all representations of pwStr, get a list of representations
                    => choose one representation of pwStr, convert it into Password
                    => walk through and convert the Password into Datagrams
        

'''

'''
Data Structures
'''


class Tag:
    """
    An intermediate within the process of parsing pii data into pii vector
    Specified piitype
    """

    def __init__(self, t: BasicTypes.PIIType, value: int, s: str):
        self.piitype = t
        self.piivalue = value
        self.s = s

    @classmethod
    def create(cls, type: BasicTypes.PIIType, s: str):
        """
        Create a Tag.
        When value < 0(default), use PIIType's value as Tag's value;
        When value > 0(LDS tag), use param value as Tag's value.

        """
        if isinstance(type, BasicTypes.PIIType.BaseTypes):
            # LDS Tag
            _len = len(s)
            return Tag(type, _len, s)
        else:
            # PII Tag
            return Tag(type, type.value, s)


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

    def getTagDict(self):
        return self._tagDict

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

    def filter(self, s: str) -> str:
        """Remove special characters, ensure string only have digit, alpha and space character
        """
        ss = ''
        for c in s:
            if c.isdigit() or c.isalpha() or c.isspace():
                ss += c
        return ss

    def filterDigit(self, s: str) -> str:
        """Retain only digit
        """
        ss = ''
        for c in s:
            if c.isdigit() or c.isspace():
                ss += c
        return ss

    def _buildTagDict(self):
        name = self.filter(self._pii.name)
        firstName = self.filter(self._pii.firstName)
        givenName = self.filter(self._pii.givenName)
        # if len(name) < 1:
        #     name = BasicTypes.DefaultPII.name
        # if len(firstName) < 1:
        #     firstName = BasicTypes.DefaultPII.firstName
        # if len(givenName) < 1:
        #     givenName = BasicTypes.DefaultPII.givenName

        if self._nameFuzz is True:
            for tu in Fuzzers.fuzzName(name, firstName, givenName):
                d = PIIToTagParser.parseNameToTagDict(tu[0], tu[1], tu[2])
                self.updateDict(d)
        else:
            d = PIIToTagParser.parseNameToTagDict(name, firstName, givenName)
            self.updateDict(d)

        birthday = self.filterDigit(self._pii.birthday)
        d = PIIToTagParser.parseBirthdayToTagDict(birthday)
        self.updateDict(d)

        d = PIIToTagParser.parseAccountToTagDict(self._pii.account)
        self.updateDict(d)

        d = PIIToTagParser.parseEmailToTagDict(self._pii.email)
        self.updateDict(d)

        phoneNum = self.filterDigit(self._pii.phoneNum)
        d = PIIToTagParser.parsePhoneNumToTagDict(phoneNum)
        self.updateDict(d)

        idCard = self.filter(self._pii.idcardNum)
        d = PIIToTagParser.parseIdCardNumToTagDict(idCard)
        self.updateDict(d)

    def _buildTagList(self):
        for k, v in self._tagDict.items():
            if not isinstance(v, list):
                raise Exceptions.PIIParserException(f"Parse TagDict Error: Expected list, given: {type(v)}")
            for i in v:
                t = Tag.create(k, i)
                self._tagList.append(t)


'''
PII Parser
'''


class PIIParserException(BasicParserException):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class PIISectionFactory(Singleton):

    def __init__(self) -> None:
        self.translatorPIIType = Utils.PIISectionTypeTranslation.getInstance()
        self.translatorPIIValue = Utils.PIISectionValueTranslation.getInstance()
        self.translatorPIIStr = Utils.PIISectionStrTranslation.getInstance()

    def isBeginSection(self, section: PIISection) -> bool:
        return section.type == PIIType.BaseTypes.BeginSymbol

    def isEndSection(self, section: PIISection) -> bool:
        return section.type == PIIType.BaseTypes.EndSymbol

    def getEmptySection(self) -> PIISection:
        return PIISection(0, 0)

    def getBeginSection(self) -> PIISection:
        return PIISection(PIIType.BaseTypes.BeginSymbol, 0)

    def getEndSection(self) -> PIISection:
        return PIISection(PIIType.BaseTypes.EndSymbol, 0)

    def createFromPIIVector(self, vector: PIIVector) -> PIISection:
        enumCls = vector.piitype.__class__
        if enumCls in self.translatorPIIType.fromList:
            # pii section
            typeCls = self.translatorPIIType.translatePIITypeToBaseType(enumCls)
            valueCls = vector.piitype  # e.g. NameType.FullName
            section = PIISection(type=typeCls, value=valueCls)
            return section

        else:
            # LDS or begin/end section
            typeCls = vector.piitype
            value = vector.piivalue
            section = PIISection(type=typeCls, value=value)
            return section

    def createFromInt(self, i: int) -> PIISection:
        """
        4002 => PIISection

        """
        if i == 0:
            return self.getBeginSection()
        elif i < 0:
            return self.getEndSection()

        td = int(i // 1e3)
        if td > 0:
            typeValue = int(i // 1e3) * 1e3
            value = int(i % 1e3)

            baseType = self.translatorPIIValue.translateIntToEnumType(typeValue)
            sectionType = baseType
            if self.isLDSType(baseType):
                sectionValue = value
            else:
                piiType = self.translatorPIIType.translateBaseTypeToPIIType(baseType)
                v = Utils.getEnumTypeFromInt(piiType, value)
                if v == None:
                    raise PIISectionFactoryException(f"Error: cannot create PIISection, invalid value {value} in {i}")
                sectionValue = v

            if sectionType is None or sectionValue is None:
                raise PIISectionFactoryException(
                    f"Error: cannot create PIISection, invalid pii value:{typeValue}+{value} in {i}")
            return PIISection(sectionType, sectionValue)
        else:
            raise PIISectionFactoryException(f"Error: cannot create PIISection, invalid Integer:{i}")

    def createFromStr(self, s: str) -> PIISection:
        """
        Convert string like "A2" or "N1" or "L10" into `PIISection`

        """
        if len(s) < 2 or not s[0].isalpha() or not s[1:].isdigit():
            raise PIISectionFactoryException(f"Error: invalid tag str: {s}")
        ch = s[0]
        di = s[1:]
        baseCls = self.translatorPIIStr.translateStrToBaseType(ch)
        if self.isLDSType(baseCls):
            piiTypeCls = baseCls
            piiValue = int(di)
            return PIISection(type=piiTypeCls, value=piiValue)
        else:
            piiTypeCls = baseCls  # BaseTypes.Name
            piiCls = self.translatorPIIType.translateBaseTypeToPIIType(baseCls)  # NameType
            piiValue = piiCls._value2member_map_.get(int(di))  # FullName
            return PIISection(type=piiTypeCls, value=piiValue)

    def getAllPIISectionDict(self) -> dict[str, PIISection]:
        """Get pii sections with all PIIType and corresponding string
        E.g. "N1": PIISection with FullName
        """
        d = dict()
        baseClsList = self.translatorPIIType.fromList
        for cls in baseClsList:
            valueList: list[int] = list(cls._value2member_map_.keys())

            for i in valueList:
                specifiedCls = cls._value2member_map_[i]
                v = PIIVector(s="", piitype=specifiedCls, piivalue=i)
                section = self.createFromPIIVector(v)
                sectionStr = self.parsePIISectionToStr(section)
                d[sectionStr] = section
        return d

    def parsePIISectionToStr(self, section: PIISection) -> str:
        """
        Parse PIISection to string like "N1" or "A2" or "L10"

        """
        baseCls = section.type
        piiCls = section.value

        ch = self.translatorPIIStr.translateBaseTypeToStr(baseCls)
        di = ""
        if self.isLDSType(baseCls):
            v = int(piiCls)
            di = str(v)
        else:
            di = str(piiCls.value)
        return ch + di

    def isLDSType(self, t: BasicTypes.PIIType.BaseTypes) -> bool:
        """
        Input a type, check whether it's LDS type

        """
        if t in [BasicTypes.PIIType.BaseTypes.L, BasicTypes.PIIType.BaseTypes.D, BasicTypes.PIIType.BaseTypes.S]:
            return True
        else:
            return False


class PIIDatagramFactory(Singleton):
    from Parser import Config
    order = Config.pii_order

    def __init__(self) -> None:
        super().__init__()
        self.sectionFactory = PIISectionFactory.getInstance()

    def getAllBasicPIIDatagramsDict(self) -> dict[str, PIIDatagram]:
        """Get pii datagrams with all pii types
        like "N1"

        """
        d: dict[str, PIISection] = self.sectionFactory.getAllPIISectionDict()
        resDict: dict[str, PIIDatagram] = dict()
        for s, section in d.items():
            sectionList = [section, ]
            endSection: PIISection = self.sectionFactory.getEndSection()
            endLabel: PIILabel = PIILabel.create(endSection)
            dg = PIIDatagram(sectionList=sectionList, label=endLabel, offsetInSegment=0, offsetInPassword=1, pwStr="")
            resDict[s] = dg
        return resDict

    def tailorPIIDatagram(self, dg: PIIDatagram) -> PIIDatagram:
        """
        Tailor datagram to 26-dim, datagram must have 6 sections

        """
        sectionList = dg.sectionList
        newList = list()
        if len(sectionList) > self.order:
            newList = sectionList[-6:]
        else:
            n = self.order - len(sectionList)
            beginSection = self.sectionFactory.getBeginSection()
            for i in range(n):
                newList.append(beginSection)
            newList += sectionList
        return PIIDatagram(newList, dg.label, dg.offsetInPassword, dg.offsetInSegment, dg.pwStr)

    def createPIIDatagramOnlyWithFeature(self, sectionList: list[PIISection], offsetInSegment: int,
                                         offsetInPassword: int) -> PIIDatagram:
        """
        Create a PIIDatagram only with fields required by `_tovector` method
        The minimum object that can be passed to trainner
        """
        return PIIDatagram(sectionList, PIILabel(self.sectionFactory.getEmptySection()), offsetInPassword,
                           offsetInSegment, "")

    def createFromStr(self, s: str) -> PIIDatagram:
        """
        Convert string "N1A2" into PIIDatagram
        OffsetInSegment is set to 0 and offsetInPassword is set to len(sectionList)
        """
        sectionList: list[PIISection] = list()
        i = 0
        sub = ""
        while i < len(s):
            if s[i].isalpha():
                if sub != "":
                    section: PIISection = self.sectionFactory.createFromStr(sub)
                    sectionList.append(section)
                    sub = s[i]
                else:
                    sub += s[i]
            if s[i].isdigit():
                sub += s[i]
            i += 1
        if sub != "":
            section: PIISection = self.sectionFactory.createFromStr(sub)
            sectionList.append(section)

        offsetInSegment = 0
        offsetInPassword = len(sectionList)
        dg = self.createPIIDatagramOnlyWithFeature(sectionList, offsetInSegment, offsetInPassword)
        # dg_ = self.tailorPIIDatagram(dg)
        return dg

    def parsePIIDatagramToStr(self, dg: PIIDatagram) -> str:
        """
        Parse PIIDatagram to string like "A1L10N2"
        """
        s = ""
        for section in dg.sectionList:
            if section.type == BasicTypes.PIIType.BaseTypes.BeginSymbol:
                continue
            try:
                s += self.sectionFactory.parsePIISectionToStr(section)
            except Exception as e:
                raise PIIDatagramFactoryException(
                    f"Exception occur when parsing section:{section}, Original Exception is {e}")
        return s


class PIIDatagramFactoryException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class PIISectionFactoryException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class PIIParser(BasicParser):
    from Parser import Config
    order = Config.pii_order
    """

    Examples:
        parser :PIIParser = PIIParser(None,pwStr,rep)
        parser.parse()
        parser.getFeatureList()
        parser.getLabelList()
    """

    def __init__(self, ctx, pwStr: str, rep: PIIRepresentation):
        super().__init__(ctx, pwStr)
        self.rep: PIIRepresentation = rep
        self.plen = rep.len
        self.featureList: list[list]
        self.datagramList: list[PIIDatagram]
        self.labelList: list[int]

        self.translator = Utils.PIISectionTypeTranslation()
        self.sectionFactory = PIISectionFactory.getInstance()

    def beforeParse(self):
        super().beforeParse()

    def afterParse(self):
        super().afterParse()

    def buildDatagramList(self):
        sectionList: list[PIISection] = [self.sectionFactory.getBeginSection() for i in range(self.order)]
        beginVector: PIIVector = self.rep.piiVectorList[0]
        beginSection: PIISection = self.sectionFactory.createFromPIIVector(beginVector)
        beginLabel: PIILabel = PIILabel.create(beginSection)
        dg: PIIDatagram = PIIDatagram(sectionList=sectionList,
                                      label=beginLabel,
                                      offsetInPassword=0,
                                      offsetInSegment=0,
                                      pwStr=self.pwStr)
        self.datagramList.append(dg)

        for i in range(self.plen):
            sectionList = list()
            offsetInPassword = 0
            # offsetInSegment = len(self.rep.piiVectorList[i].str)
            offsetInSegment = 0
            if i < self.order:
                for n in range(self.order - i - 1):
                    sectionList.append(self.sectionFactory.getBeginSection())
            start = max(0, i - self.order + 1)
            end = i + 1
            for n in range(start, end):
                vector: PIIVector = self.rep.piiVectorList[n]
                section: PIISection = self.sectionFactory.createFromPIIVector(vector)
                sectionList.append(section)
                # offsetInPassword += len(vector.str)
                offsetInPassword += 1
            # resolve label
            if i < self.plen - 1:
                nextVector = self.rep.piiVectorList[i + 1]
                section = self.sectionFactory.createFromPIIVector(nextVector)
                label = PIILabel.create(section)
            else:
                # end symbol
                section = self.sectionFactory.getEndSection()
                label = PIILabel.create(section)
            dg = PIIDatagram(sectionList=sectionList,
                             label=label,
                             offsetInPassword=offsetInPassword,
                             offsetInSegment=offsetInSegment,
                             pwStr=self.pwStr)
            self.datagramList.append(dg)

    def buildFeatureList(self):
        for dg in self.datagramList:
            t = dg._tovector()
            self.featureList.append(t)

    def buildLabelList(self):
        for dg in self.datagramList:
            label = dg.label
            self.labelList.append(label.toInt())


'''
Parsers
'''


# generate extra data in common format
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
        if len(name) <=0 or len(firstName) <=0 or len(givenName) <=0:
            return list()
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


# a functional static class to parse LDS segments
class LDSStepper:
    @classmethod
    def checkLDSType(cls, s: str) -> BasicTypes.PIIType:
        c = s[0]
        if c.isdigit():
            return BasicTypes.PIIType.BaseTypes.D
        elif c.isalpha():
            return BasicTypes.PIIType.BaseTypes.L
        else:
            return BasicTypes.PIIType.BaseTypes.S

    # input a string, Output all LDS segments in order
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


# static email parser
class EmailParser:

    # return prefix, None means not in email format
    @classmethod
    def parseEmailPrefix(cls, s: str) -> str:
        m = re.match(r"([^@]+)@[^@]+", s)
        if m is None:
            return None
        return m.group(1)

    @classmethod
    def parseEmailSite(cls, s: str) -> str:
        """Extract email site like qq in qq.com
        Returns:
            site string or None
        """
        i = s.index("@")
        if i == len(s) - 1:
            return None
        sub = s[i + 1:]
        return sub.split('.')[0]


# (second layer)parse a pii data into pii tags
# nameFuzz: employ fuzz on certain pii types like birthday
# pii: input pii data
# employed by PIIStructure parser
class PIIFullTagParser:
    def __init__(self, pii: BasicTypes.PII, nameFuzz=False):
        self._pii = pii
        self._tagContainer = None
        self._nameFuzz = nameFuzz

    def parseTag(self):
        self._tagContainer = PIITagContainer(self._pii, nameFuzz=self._nameFuzz)
        self._tagContainer.parse()

    def getTagContainer(self) -> PIITagContainer:
        return self._tagContainer


class PIIToTagParser:
    """
    Parse pii string into pii tag
    e.g. 19820607 => dict[BirthdayType: list of all fuzz strings
        pii with birthday = 19820607 => BirthdayType:value
    dict key: PIIType, value: list of candidates
    such as BirthdayType.Date can be expressed by 67 or 0607
    """

    @classmethod
    def parsePIIToTagDict(cls, pii: BasicTypes.PII) -> typing.Dict[typing.Any, list]:
        pass

    @classmethod
    def parseNameToTagDict(cls, name: str, firstName: str, givenName: str) -> typing.Dict[
        BasicTypes.PIIType.NameType, list]:
        """
        Given a name, get all tags
        `givenName` must in format that can split by space, like "zhong jie"

        Args:
            name: Full name
            firstName:
            givenName:

        Returns:
            Dict: dict key: NameType, value: list of candidates

        """
        d = dict()
        if len(name) <= 0 or len(firstName) <= 0 or len(givenName) <= 0:
            return d
        d[BasicTypes.PIIType.NameType.FullName] = name.replace(" ", "").replace("\t", "")
        _l = givenName.split()
        l = [x for x in _l if len(x) > 0]
        givenNameWithoutSpace = ''.join(l)
        d[BasicTypes.PIIType.NameType.AbbrName] = firstName[0] + ''.join(x[0] for x in l if len(x) > 0)
        d[BasicTypes.PIIType.NameType.FamilyName] = firstName
        d[BasicTypes.PIIType.NameType.GivenName] = givenName.replace(" ", "").replace("\t", "")
        d[BasicTypes.PIIType.NameType.GivenName1stPlusFamilyName] = givenName[0] + firstName
        d[BasicTypes.PIIType.NameType.FamilyName1stPlusGivenName] = firstName[0] + givenNameWithoutSpace
        d[BasicTypes.PIIType.NameType.FamilyNameCapitalized] = firstName[0].capitalize() + firstName[1:]

        for k, v in d.items():
            d[k] = [v, ]

        d[BasicTypes.PIIType.NameType.FamilyName1st] = [firstName[0].upper(), firstName[0].lower()]
        givennameAbbr = ""  # zj
        gl = givenName.split()
        for c in gl:
            if c is not None and len(c) > 0:
                givennameAbbr += c[0]
        d[BasicTypes.PIIType.NameType.GivenNameAbbr] = [givennameAbbr]

        return d

    @classmethod
    def parseBirthdayToTagDict(cls, birthday: str) -> typing.Dict[BasicTypes.PIIType.BirthdayType, list]:
        try:
            d = dict()
            if len(birthday) <= 0:
                return d
            date_obj = datetime.datetime.strptime(birthday, "%Y%m%d")
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
            raise Exceptions.PIIParserException(f"Invalid birthday format {birthday}. Parent exception:{str(e)}")

    @classmethod
    def parseAccountToTagDict(cls, account: str) -> typing.Dict[BasicTypes.PIIType.AccountType, list]:
        d = dict()
        if len(account) <= 0:
            return d
        segList = LDSStepper.getAllSegment(account)
        d[BasicTypes.PIIType.AccountType.Full] = [account, ]
        letterSegmentList: list[BasicTypes.LDSSegment] = list()
        digitSegmentList: list[BasicTypes.LDSSegment] = list()
        for seg in segList:
            if seg.type == BasicTypes.PIIType.BaseTypes.L:
                letterSegmentList.append(seg)
            elif seg.type == BasicTypes.PIIType.BaseTypes.D:
                digitSegmentList.append(seg)
        if len(letterSegmentList) <= 0 and len(digitSegmentList) <= 0:
            raise Exceptions.PIIParserException("parse Account error")
        letterSegStrList = list(map(lambda x: x.s, letterSegmentList))
        digitSegStrList = list(map(lambda x: x.s, digitSegmentList))
        letterSegStrSet = set(letterSegStrList)  # remove duplicate
        digitSegStrSet = set(digitSegStrList)

        d[BasicTypes.PIIType.AccountType.LetterSegment] = list(letterSegStrSet)
        d[BasicTypes.PIIType.AccountType.DigitSegment] = list(digitSegStrSet)
        return d

    @classmethod
    def parseEmailToTagDict(cls, email: str) -> typing.Dict[BasicTypes.PIIType.EmailPrefixType, list]:
        d = dict()
        if len(email) <= 0:
            return d
        prefix = EmailParser.parseEmailPrefix(email)
        site = EmailParser.parseEmailSite(email)
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
            if seg.type == BasicTypes.PIIType.BaseTypes.L:
                if letterSeg is None:
                    letterSeg = seg
            elif seg.type == BasicTypes.PIIType.BaseTypes.D:
                if digitSeg is None:
                    digitSeg = seg
        if letterSeg is None and digitSeg is None:
            raise Exceptions.PIIParserException("Parse Email Error")
        if letterSeg is not None:
            d[BasicTypes.PIIType.EmailPrefixType.LetterSegment] = [letterSeg.s, ]
        if digitSeg is not None:
            d[BasicTypes.PIIType.EmailPrefixType.DigitSegment] = [digitSeg.s, ]
        if site is not None and len(site) > 0:
            d[BasicTypes.PIIType.EmailPrefixType.Site] = [site, ]

        return d

    @classmethod
    def parsePhoneNumToTagDict(cls, phoneNum: str) -> typing.Dict[BasicTypes.PIIType.BaseTypes.PhoneNumber, list]:
        if len(phoneNum) <= 0:
            return dict()
        if not phoneNum.isdigit():
            raise Exceptions.PIIParserException(f"Invaild phone nubmer: {phoneNum}")
        d = dict()
        d[BasicTypes.PIIType.PhoneNumberType.FullNumber] = [phoneNum, ]
        d[BasicTypes.PIIType.PhoneNumberType.FirstThreeDigits] = [phoneNum[:3], ]
        d[BasicTypes.PIIType.PhoneNumberType.LastFourDigits] = [phoneNum[-4:], ]

        return d

    @classmethod
    def parseIdCardNumToTagDict(cls, idCardNum: str) -> typing.Dict[BasicTypes.PIIType.IdCardNumberType, list]:
        d = dict()
        if len(idCardNum) <= 0:
            return d
        d[BasicTypes.PIIType.IdCardNumberType.Last4Digits] = [idCardNum[-4:], ]
        d[BasicTypes.PIIType.IdCardNumberType.First3Digits] = [idCardNum[:3], ]
        d[BasicTypes.PIIType.IdCardNumberType.First6Digits] = [idCardNum[:6], ]

        return d


class PIITagRepresentationStrParser(Singleton):
    """
    Parse PIIRepresentation to readable string like A1B2N3
    """

    def __init__(self):
        piiTypeList = [PIIType.NameType, PIIType.BirthdayType, PIIType.AccountType, PIIType.IdCardNumberType,
                       PIIType.EmailPrefixType, PIIType.BaseTypes.L, PIIType.BaseTypes.D, PIIType.BaseTypes.S,
                       PIIType.PhoneNumberType]
        piiCharList = ["N", "B", "A", "I", "E", "L", "D", "S", "P"]
        trans = Utils.translation.makeTrans(piiTypeList, piiCharList)
        self.translation = trans  # representation => str
        reTrans = Utils.translation.makeTrans(piiCharList, piiTypeList)
        self.reTranslation = reTrans  # str => representation

    def representationToStr(self, rep: PIIRepresentation) -> str:
        """
        Parse PIIRepresentation object into string like "N1B2L3S4D4'

        Args:
            rep:

        Returns:

        """
        l = []
        vectorList: list[PIIVector] = rep.piiVectorList
        for vector in vectorList:
            s = self.tagToStr(vector)
            l.append(s)
        ss = ",".join(l)
        prefix = f"({len(l)})"
        first = prefix + ss
        second = "|".join(list(map(lambda x: x.str, vectorList)))
        res = f"{first}\n{second}\n"
        return res

    def tagToStr(self, vector: PIIVector) -> str:
        """
        Convert a PIIVector into string

        Args:
            vector:

        Returns:

        """
        typeCls = vector.piitype.__class__
        _len = len(vector.str)
        if vector.piitype in (
                BasicTypes.PIIType.BaseTypes.L, BasicTypes.PIIType.BaseTypes.D, BasicTypes.PIIType.BaseTypes.S):
            _value = _len

        if isinstance(vector.piitype, BasicTypes.PIIType.BaseTypes):
            typeCls = vector.piitype
            _value = vector.piivalue
        else:
            _value = vector.piivalue

        s = self.translation.translate(typeCls)
        ss = s + str(_value)
        return ss

    def strToRepresentation(self, s: str) -> PIIRepresentation:
        """
        (Deprecated)
        Args:
            s:

        Returns:

        """
        if len(s) % 2 != 0:
            raise PIITagRepresentationStrParserException(f"Error: representation string must have even length, {s}")
        vectorList = list()
        for i in range(0, len(s), 2):
            vector = self.strToTag(s[i:i + 2])
            vectorList.append(vector)
        repr = PIIRepresentation(vectorList)
        return repr

    def strToTag(self, s: str) -> PIIVector:
        """
        (Deprecated)

        """
        if len(s) != 2 or not s[0].isalpha() or not s[1].isdigit():
            raise PIITagRepresentationStrParserException(f"Error: invaild tag str: {s}")
        ch = s[0]
        di = s[1]
        typeCls: Enum = self.reTranslation.translatePIITypeToBaseType(ch)
        if typeCls in (BasicTypes.PIIType.BaseTypes.L, BasicTypes.PIIType.BaseTypes.D, BasicTypes.PIIType.BaseTypes.S):
            piiTypeCls = typeCls
        else:
            piiTypeCls = typeCls._value2member_map_.get(int(di))

        piiValue = int(di)
        vector = PIIVector("", piiTypeCls, piiValue)
        return vector


class PIITagRepresentationStrParserException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class PIIStructureParser:
    """
    (top layer) bound a pii data, parse password string into PIIStructure
    constructor: given a pii data bounded to the parser
    getPwPIIStructure: given a password string, Output the PIIStructure which contains all vectors about this password
    """

    def __init__(self, pii: BasicTypes.PII):
        self._pii = pii

    def getPwPIIStructure(self, pwStr: str) -> PIIStructure:
        return parseStrToPIIStructure(pwStr, self._pii)


def checkPIINameType(name: str, abbr: str) -> BasicTypes.PIIType.NameType:
    """

    Check the type of `abbr` in terms of `name`. Including fullname, Abbr, or None(abbr has nothing with name)

    Args:
        name: full name base
        abbr: the abbr of `name` to detect

    Returns:
        `NameType`
    """
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


def parseStrToPIIStructure(pwStr: str, pii: BasicTypes.PII) -> PIIStructure:
    """
    Get all PII structure representations of password s(PII type contains LDS)

    Args:
        pwStr: password string for input
        pii: pii data

    Returns:
        PIIStructure
    """
    parser = PIIFullTagParser(pii)
    parser.parseTag()
    tagList = parser._tagContainer.getTagList()
    tagRepresentationList: typing.List[typing.List[Tag]] = list()
    # gen = parseAllPIITagRecursive(tagList, pwStr, list())
    # for l in gen:
    #     tagRepresentationList.append(l)
    parseAllPIITagRecursive(tagList, pwStr, list(), tagRepresentationList)
    piiRepresentationList = list()
    for l in tagRepresentationList:
        piiVectorList = convertTagListToPIIVectorList(l)
        representation = PIIRepresentation(piiVectorList)
        piiRepresentationList.append(representation)
    piiStructure = PIIStructure(pwStr, piiRepresentationList)
    return piiStructure


def parseAllPIITagRecursive(tagList: typing.List[Tag], pwStr: str, curTags: typing.List[Tag],
                            outputList: typing.List[typing.List[Tag]],
                            # ldsStepNum:int = 0,
                            ldsType: BasicTypes.PIIType = None,
                            ldsStr: str = ""):
    """Get all representations of a password string

    Args:
        tagList: list of tags to match
        pwStr: password string
        curTags: current tag list, denote a building representation
        outputList: *(output)*list of representations
        ldsType: current LDS type
        ldsStr: current LDS string

    Returns:
        a list of representations(denoting by `list[list[tag]]`)
    """
    if len(pwStr) <= 0:
        # flush the last LDS segment
        if ldsType is not None:
            tag = Tag.create(ldsType, ldsStr)
            curTags.append(tag)
        outputList.append(curTags)
        return
    candidates: typing.List[Tag] = list()
    for tag in tagList:
        if pwStr.startswith(tag.s):
            candidates.append(tag)
    if len(candidates) <= 0:
        # LDS stepper
        newLdsType = LDSStepper.checkLDSType(pwStr[0])
        if ldsType is not None and newLdsType != ldsType:
            # LDS type changed, push old segment into curTags
            tag = Tag.create(ldsType, ldsStr)
            curTags.append(tag)
            ldsStr = ""
        ldsStr += pwStr[0]
        newPwStr = pwStr[1:]
        newCurTag = copy(curTags)
        parseAllPIITagRecursive(tagList, pwStr=newPwStr, curTags=newCurTag, outputList=outputList,
                                # ldsStepNum=ldsStepNum,
                                ldsType=newLdsType,
                                ldsStr=ldsStr)
    else:
        # flush LDS stepper when meet pii segment
        if ldsType is not None:
            tag = Tag.create(ldsType, ldsStr)
            curTags.append(tag)
            ldsType = None
            ldsStr = ""
        for tag in candidates:
            s = len(tag.s)
            newPwStr = pwStr[s:]  # remove tag prefix
            newCurTag = copy(curTags)
            newCurTag.append(tag)
            parseAllPIITagRecursive(tagList, pwStr=newPwStr, curTags=newCurTag, outputList=outputList,
                                    ldsType=ldsType,
                                    ldsStr=ldsStr)


def convertTagListToPIIVectorList(tagList: typing.List[Tag]) -> typing.List[PIIVector]:
    """
    Convert tag list into vector list

    Args:
        tagList: list of `Tag`

    Returns:
        list of `PIIVector`
    """
    l = list()
    for tag in tagList:
        vector = PIIVector(tag.s, piitype=tag.piitype, piivalue=tag.piivalue)
        l.append(vector)
    return l


'''
Select a representation of password string
'''


class PIIRepresentationResolver(Singleton):
    """
    select a representation of password
    """

    def __init__(self,
                 pwList: list[str],
                 pwAllRepDict: dict[str, list[RepUnit]],
                 repPriorityList: list[RepUnit],
                 ) -> None:
        self.pwList: list[str] = pwList  # all pwStr
        self.pwAllRepDict: dict[
            str, list[RepUnit]] = pwAllRepDict  # pwStr:list of all rep, password string and its all representation
        self.repPriorityList: list[RepUnit] = repPriorityList  # list of repUnit in frequency-descending order
        self.pwRepDict: dict[str, RepUnit] = dict()  # (output) password with its unique representation

    @classmethod
    def getInstance(cls):
        repPriorityList = DatabaseUtils.getRepStructurePriorityList()
        # print(f"PriorityList:{len(repPriorityList)}")
        pwList = DatabaseUtils.getAllPw()
        pwAllRepDict = dict()
        _len = len(pwList)
        _i = 0
        # print(f"PwList:{len(pwList)}")
        pwAllRepDict = DatabaseUtils.getAllRepStructureDict()
        # for pw in pwList:
        #     repList = DatabaseUtils.getAllRepStructureOfPw(pw)
        #     pwAllRepDict[pw] = repList
        #     _i += 1
        #     print(f"Progress:{(_i / _len) * 100:.2f}%")
        # print(f"PwRepDict:{len(pwAllRepDict.keys())}\n{list(pwAllRepDict.keys())[:10]}")

        return super().getInstance(pwList, pwAllRepDict, repPriorityList)

    def checkPwRepMatch(self, pwStr: str, repUnit: RepUnit) -> bool:
        """
        Check whether `repUnit` is one of the representations of `pwStr`
        Args:
            pwStr:
            repUnit:

        Returns:

        """
        pass

    def pwMatch(self, pwStr: str) -> tuple[RepUnit]:
        """
        Return all PII structure representations of pwStr

        """
        if pwStr not in self.pwAllRepDict.keys():
            raise ResolverException(f"Error: pwStr {pwStr} not in pwAllRepDict ")
        return tuple(self.pwAllRepDict[pwStr])

    def subtractFrequency(self, repUnitList: list[RepUnit]):
        """
        Subtract frequency of all representation structures in `repUnitList`

        """

        for unit in repUnitList:
            unit.frequency -= 1

    def shortMatch(self, pwStr: str) -> RepUnit:

        """
        Return the shortest representation structure of pwStr

        """
        if pwStr not in self.pwAllRepDict.keys():
            raise ResolverException(f"Error pwStr {pwStr} not in pwAllRepDict")
        repList: list[RepUnit] = self.pwAllRepDict[pwStr]
        min = 1e6
        min_i = 0
        i = 0
        _len = len(repList)
        while i < _len:
            rep: RepUnit = repList[i]
            l = DatabaseUtils.getRepLen(rep)
            if l < min:
                min_i = i
                min = l
            i += 1
        minRep: RepUnit = repList[min_i]
        return minRep

    def resolve(self) -> dict[str, RepUnit]:
        """
        Resolve the representations of all passwords
        `repPriorityList` and `pwList` will turn to empty after call
        `pwAllRepDict` will not change and `shortMatch` method can use as normal

        Take the frequency of representation structures as the primary consider, if pw's all representations have equal
         frequency, select the shortest structure.

        Returns:

        """
        matchSet: list[RepUnit] = self.repPriorityList
        _len = len(matchSet)
        item: RepUnit = matchSet.pop(0)
        while len(matchSet) > 0:
            print(
                f"Progress:{_len - len(matchSet)}/{_len}:{((_len - len(matchSet)) / _len * 100):.2f} pwList:{len(self.pwList)}")
            if item.frequency <= 1:
                item: RepUnit = matchSet.pop(0)
                continue
            for pw in self.pwList:
                matchPw: tuple[RepUnit] = self.pwMatch(pw)
                if item in matchPw:
                    self.pwRepDict[pw] = item
                    self.pwList.remove(pw)
                    for remainItem in matchPw:
                        remainItem.frequency -= 1
            item: RepUnit = matchSet.pop(0)

        while len(self.pwList) > 0:
            pw = self.pwList.pop()
            structure: RepUnit = self.shortMatch(pw)
            self.pwRepDict[pw] = structure
        return self.pwRepDict


class ResolverException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
