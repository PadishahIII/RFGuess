import typing
from Core.Decorators import Bean
from Commons.BasicTypes import KeyboardPosition, CharacterType
from Commons.Exceptions import ParseException
from Commons.Modes import Singleton

# Encode character into serial number, single-direction map
# Employ a One-to-one map from charset and (CharacterType, Serial number)
# Must signal Serial number with CharacterType
@Bean
class CharacterParser(Singleton):
    BeginSymbol = 0
    EndSymbol = -1

    def __init__(self) -> None:
        # Map character to serial number, not one-to-one!
        self.map = dict()
        # self.reMap = dict()
        # self.charset = "1234567890-=`~!@#$%^&*()_+qwertyuiop[]\\QWERTYUIOP{}|asdfghjkl;'ASDFGHJKL:\"zxcvbnm,./ZXCVBNM<>?"

        # letters
        ii = 1
        for i in range(ord("a"), ord("z") + 1):
            self.map[chr(i)] = ii
            ii += 1
        for i in range(ord("A"), ord("Z") + 1):
            self.map[chr(i)] = ii
            ii += 1

        # digits
        ii = 1
        for i in range(ord("1"), ord("9") + 1):
            self.map[chr(i)] = ii
            ii += 1
        self.map["0"] = 10

        # special characters
        ii = 1
        for i in "!@#$%^&*()_+-=[]\{}|;':\",./<>?`~":
            self.map[i] = ii
            ii += 1

        # get reverse mapping
        # self.reMap = {v: k for k, v in self.map.items()}

        # self._check()

    def encodeCh(self, ch: str)->int:
        if len(ch) > 1 or len(ch) < -1:
            raise ParseException(f"{ch} must be a single character")
        if ch not in self.map.keys():
            raise ParseException(f"{ch} must in a-z and 0-9")
        return self.map.get(ch)

    def encodeStr(self, s: str) -> typing.List[int]:
        l = list()
        for c in s:
            l.append(self.encodeCh(c))
        return l


@Bean
class KeyboardParser(Singleton):
    def __init__(self) -> None:
        self.map = dict()
        row = 1
        col = 1
        for l in ["`1234567890-=", "qwertyuiop[]\\", "asdfghjkl;'", "zxcvbnm,./"]:
            col = 1
            for c in l:
                self.map[c] = KeyboardPosition(row, col)
                col += 1
            row += 1
        row = 1
        col = 1
        for l in ["~!@#$%^&*()_+", r"QWERTYUIOP{}|", 'ASDFGHJKL:"', r"ZXCVBNM<>?"]:
            col = 1
            for c in l:
                self.map[c] = KeyboardPosition(row, col)
                col += 1
            row += 1

    def parseCh(self, ch: str) -> KeyboardPosition:
        if len(ch) > 1 or len(ch) < 0:
            raise ParseException(f"{ch} must be a single character")
        if ch not in self.map.keys():
            raise ParseException(f"{ch} not included")
        return self.map.get(ch)

    def parseStr(self, s: str) -> typing.List[KeyboardPosition]:
        l = list()
        for c in s:
            l.append(self.parseCh(c))
        return l


# Dependent from CharacterParser
# Encode/Decode between characters and serial number without CharacterType
# 0 and -1 is reserved for Begin/End Symbol
@Bean
class LabelParser(Singleton):
    def __init__(self) -> None:
        self.charset = "1234567890-=`~!@#$%^&*()_+qwertyuiop[]\\QWERTYUIOP{}|asdfghjkl;'ASDFGHJKL:\"zxcvbnm,./ZXCVBNM<>?"
        self.map = dict()
        self.reMap = dict()

        ii = 1
        for c in self.charset:
            self.map[c] = ii
            ii += 1
        self.reMap = {v: k for k, v in self.map.items()}
        self._check()

    def _check(self):
        s = set(self.map.keys())
        if len(s) != len(self.map.keys()):
            raise ParseException(f"Creating map error: duplicate key")
        ss = set(self.reMap.keys())
        if len(ss) != len(self.reMap.keys()):
            raise ParseException(f"Creating map error: duplicate key")
        if len(s) != len(ss):
            raise ParseException(f"Creating map error: not a one-to-one map")

    def encodeCh(self, ch: str):
        if len(ch) > 1 or len(ch) < -1:
            raise ParseException(f"{ch} must be a single character")
        if ch not in self.map.keys():
            raise ParseException(f"{ch} must in a-z and 0-9")
        return self.map.get(ch)

    def encodeStr(self, s: str) -> typing.List[int]:
        l = list()
        for c in s:
            l.append(self.encodeCh(c))
        return l

    def decodeCh(self, serial: int)->str:
        if not isinstance(serial, int):
            raise ParseException(f"{serial}({type(serial)}) must be a integer")
        if serial == CharacterParser.BeginSymbol:
            return f"<{CharacterType.BeginSymbol.name}>"
        if serial == CharacterParser.EndSymbol:
            return f"<{CharacterType.EndSymbol.name}>"
        if serial not in self.reMap.keys():
            raise ParseException(f"{serial} invaild serial number")
        return self.reMap.get(serial)

    def decodeList(self, serialList: typing.List[int]):
        s = ""
        for i in serialList:
            s += self.decodeCh(i)
        return s
