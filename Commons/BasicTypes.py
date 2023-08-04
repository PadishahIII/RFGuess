import typing
from enum import Enum

from Commons.Exceptions import ParseException


class PIIType(Enum):
    Name = 0
    Username = 1
    Birthday = 2


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
    def __init__(self, username: str = None, name: str = None, birthday: str = None, phoneNum: str = None):
        self.username = username
        self.name = name
        self.birthday = birthday
        self.phoneNum = phoneNum


class Segment:
    def __init__(self, _type: CharacterType, start: int, end: int) -> None:
        self.type = _type
        self.start = start
        self.end = end
