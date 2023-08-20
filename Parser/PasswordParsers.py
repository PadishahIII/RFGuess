"""Password Parsers

```plaintext
Parse password string into a set of 26-dimension vectors
class Password: [{Bs,Bs,Bs,Bs,Bs,Bs|a},{Bs,Bs,Bs,Bs,Bs,a|b}...{a,b,c,1,2,3|Es}]
                   |                |
                   V                V
            Character Vector       label
           (4-dimension vector)
                |______________________|
                       Datagram
```
"""

import Parser.PasswordParsers
from Context.Context import BasicContext
# UTILS = False
# if UTILS is False:
#     from Commons import Utils
#
#     UTILS = True
from Parser.CommonParsers import *

CONTEXT = None


# 4-dimensional vector for a single character.
class CharacterVector(BasicContext):
    def __init__(self, ch, ctx=None) -> None:
        super().__init__()
        self.context = Parser.PasswordParsers.CONTEXT
        from Commons import Utils
        if type(ch) == str:
            cp = self.context.getBean(CharacterParser)
            kp = self.context.getBean(KeyboardParser)
            self._ch = ch
            self.type = Utils.parseType(ch)
            self.serialNum = cp.encodeCh(ch)
            self.keyboardPos: KeyboardPosition = kp.parseCh(ch)
            self.check()
        elif type(ch) == int:
            self._ch = ch
            self.type = Utils.parseSymbol(ch)
            self.serialNum = ch
            self.keyboardPos = KeyboardPosition(0, 0)

    def check(self):
        if self.serialNum < 0 or self.keyboardPos.row <= 0 or self.keyboardPos.col <= 0:
            raise ParseException("Invail CharacterVector")

    def getTuple(self) -> tuple[int, int, int, int]:
        return (
            int(self.type.value),
            int(self.serialNum),
            int(self.keyboardPos.row),
            int(self.keyboardPos.col),
        )

    def _tojson(self):
        return {
            "characterType": self.type.name,
            "characterValue": self._ch,
            "serialNum": self.serialNum,
            "keyboardRow": self.keyboardPos.row,
            "keyboardCol": self.keyboardPos.col,
        }

    def _tovector(self):
        return list(self.getTuple())


# 26-dimensional vector (4*6+2) as Feature,following character(CharacterParser-encoded) as Label
# standard vector format: {4-dimension(CharacterVector)}{4-dimension}{4-dimension}{4-dimension}{2-dimension for offsetInPassword and offsetInSegment}
# 6-order set: 6 CharacterVectors regarding to 6 character in prefix
class Datagram(BasicContext):
    from Parser import Config
    order = Config.pii_order  # n-gram model

    def __init__(self, index: int, passwordStr: str, ctx=None) -> None:
        """
        Datagram

        Args:
            index:
            passwordStr:
            ctx:
        """
        super().__init__()
        self.context = Parser.PasswordParsers.CONTEXT
        self._cp = self.context.getBean(CharacterParser)
        self._lp = self.context.getBean(LabelParser)
        self._plen = -1  # password len
        self._password = passwordStr
        self._sub = ""
        self.index = index # equal to offsetInPassword
        self._validFeatureLen = -1  # number of characters not begin or end symbol

        self.featureList: typing.List[
            CharacterVector
        ] = list()  # 6-dimension vector of every character in prefix
        self.nextCh: str = ""  # character after prefix
        self.label: int = -1  # label, serial number of nextCh

        self._offsetInPassword = -1
        self._offsetInSegment = -1

        self._parse()

    @property
    def offsetInPassword(self) -> int:
        return self._offsetInPassword

    @offsetInPassword.setter
    def offsetInPassword(self, offset: int):
        self._offsetInPassword = offset

    @property
    def offsetInSegment(self) -> int:
        return self._offsetInSegment

    @offsetInSegment.setter
    def offsetInSegment(self, offset: int):
        self._offsetInSegment = offset

    def _parse(self):
        self._plen = len(self._password)
        if self.index < 0 or self.index >= self._plen:
            raise ParseException(f"Invail index : {self.index}")

        if self.index == self._plen - 1:
            self.nextCh = ""
            self.label = CharacterParser.EndSymbol
        else:
            self.nextCh = self._password[self.index + 1]
            # self.label = self._cp.encodeCh(self.nextCh)
            self.label = self._lp.encodeCh(self.nextCh)  # TODO:

        self._sub = self._password[max(self.index - 6 + 1, 0): self.index + 1]
        # if len(sub) < Datagram.order:
        # i = Datagram.order - len(sub)
        # vector = CharacterVector(CharacterType.)
        # self.featureList.append()
        for i in range(Datagram.order - len(self._sub)):
            vector = CharacterVector(CharacterParser.BeginSymbol, ctx=self.context)
            vector.context = self.context
            self.featureList.append(vector)

        for c in self._sub:
            vector = CharacterVector(c, ctx=self.context)
            self.featureList.append(vector)
        self._validFeatureLen = len(self.featureList)

    def _tojson(self):
        return {
            "passwordSub": self._sub,
            "index": self.index,
            "label": self.label,
            "labelCh": self._lp.decodeCh(self.label),
            "nextCh": self.nextCh,
            "offsetInPassword": self.offsetInPassword,
            "offsetInSegment": self.offsetInSegment,
            "validVectorNum": self._validFeatureLen,
            "vectors": [x._tojson() for x in self.featureList],
        }

    def _tovector(self):
        l = list()
        for i in self.featureList:
            ll = i._tovector()
            l += ll
        if self.offsetInPassword < 0 or self.offsetInSegment < 0:
            raise ParseException(f"Uninit error: Datagram offset cannot less than 0")
        l += [self.offsetInPassword, self.offsetInSegment]
        return l


# a Password can produce n=len(Password) number Datagram
class Password(BasicContext):
    def __init__(self, passwordStr: str, ctx=None) -> None:
        super().__init__()
        self.context = Parser.PasswordParsers.CONTEXT
        # Parser.PasswordParsers.CONTEXT = ctx
        from Commons import Utils
        self.datagramList: typing.List[Datagram] = list()
        self._password = passwordStr
        self._plen = len(self._password)
        self._segmentList = Utils.parseSegment(self._password)
        # self._ctx = ctx

        self._parseDatagramList()

    def _parseDatagramList(self):
        for i in range(0, len(self._password)):
            dg = Datagram(i, self._password)
            # dg.context = self.context
            offset, _ = self.segmentOffset(i)
            dg.offsetInSegment = offset
            dg.offsetInPassword = i
            self.datagramList.append(dg)

    # In which segment passowrd[index] falls
    def segmentOffset(self, index) -> (int, int):
        segIndex = 0
        l = len(self._segmentList)
        seg = self._segmentList[segIndex]

        while segIndex < l and not (index >= seg.start and index < seg.end):
            segIndex += 1
            if segIndex >= l:
                break
            seg = self._segmentList[segIndex]
        if index >= seg.start and index < seg.end:
            return index - seg.start, segIndex
        else:
            raise ParseException(f"error not found segment for index={index}")

    def _tojson(self):
        return {
            "password": self._password,
            "len": self._plen,
            "datagramNum": len(self.datagramList),
            "datagrams": [x._tojson() for x in self.datagramList],
        }
