import typing
from enum import Enum

from Commons.Exceptions import ParseException


class LDSSegment:
    def __init__(self, t, length: int, s: str):
        self.type = t
        self.length = length
        self.s = s


class PIIType:
    class BaseTypes(Enum):
        Name = 1000
        Birthday = 2000
        Account = 3000
        Email = 4000
        PhoneNumber = 5000
        IdCardNumber = 6000
        L = 7000
        D = 8000
        S = 9000
        BeginSymbol = 0
        EndSymbol = -1

    class NameType(Enum):
        FullName = 1
        AbbrName = 2
        FamilyName = 3
        GivenName = 4
        GivenName1stPlusFamilyName = 5
        FamilyName1stPlusGivenName = 6
        FamilyNameCapitalized = 7  # Wang

    class BirthdayType(Enum):
        FullYMD = 1  # 19820607
        FullMDY = 2
        FullDMY = 3  # 07061982
        Date = 4  # 0607
        Year = 5
        YM = 6  # Year + Month 198206
        MY = 7  # Month + Year
        Year2lastdigitsPlusDateMD = 8  # the last two digits of year + date in MD 820607
        DateMDPlusYear2lastdigits = 9  # 060782 date in MD format + the last two digits of year
        DateDMPlusYear2lastdigits = 10

    class AccountType(Enum):
        Full = 1  # icemoon12
        LetterSegment = 2  # icemoon
        DigitSegment = 3  # 12

    class EmailPrefixType(Enum):
        FullPreix = 1  # loveu1314 from loveu1314@aa.com
        LetterSegment = 2  # loveu
        DigitSegment = 3  # 1314

    class PhoneNumberType(Enum):
        FullNumber = 1
        FirstThreeDigits = 2  # first three digits
        LastFourDigits = 3

    class IdCardNumberType(Enum):
        Last4Digits = 1
        First3Digits = 2
        First6Digits = 3


class CharacterType(Enum):
    Digit = 0
    UpperCaseLetter = 1
    LowerCaseLetter = 2
    SpecialCharacter = 3
    EndSymbol = -1
    BeginSymbol = -2


class KeyboardPosition:
    def __init__(self, row=0, col=0) -> None:
        self._row = row
        self._col = col

    @property
    def row(self) -> int:
        if self._row < 0:
            raise ParseException(f"keyboardPosition's row less than 0: {self._row}")
        return self._row

    @row.setter
    def row(self, r):
        if r < 0:
            raise ParseException(f"keyboardPosition's row less than 0: {self._row}")
        self._row = r

    @property
    def col(self) -> int:
        if self._col < 0:
            raise ParseException(f"keyboardPosition's col less than 0: {self._col}")
        return self._col

    @col.setter
    def col(self, c):
        if c < 0:
            raise ParseException(f"keyboardPosition's col less than 0: {self._col}")
        self._col = c

    def getTuple(self) -> typing.Tuple[int]:
        return (self._row, self._col)

    def __str__(self):
        return str(self.getTuple())

    def _tojson(self):
        return {"row": self.row, "col": self.col}


class PII:
    def __init__(self, account: str = None,
                 name: str = None,
                 firstName: str = None,
                 givenName: str = None,
                 birthday: str = None,
                 phoneNum: str = None,
                 email: str = None,
                 idcardNum=None):
        self.name = name  # full name in any format
        self.firstName = firstName  #
        self.givenName = givenName  # split by space "zhong jie"
        self.birthday = birthday  # YYYYMMDD format
        self.account = account
        self.email = email
        self.phoneNum = phoneNum
        self.idcardNum = idcardNum  # only digits

    def __str__(self):
        return str(self.__dict__)


DefaultPII = PII(account="account",
                 name="zhang san",
                 firstName="zhang",
                 givenName="san",
                 birthday="20000607",
                 email="defaultemail@email.com",
                 idcardNum="130528200006076060",
                 phoneNum="13222222222")


class Segment:
    def __init__(self, _type: CharacterType, start: int, end: int) -> None:
        self.type = _type
        self.start = start
        self.end = end
