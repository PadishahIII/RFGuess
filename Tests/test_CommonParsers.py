from unittest import TestCase
from Parser.CommonParsers import *
from Commons.BasicTypes import *
class TestCommonParsers(TestCase):
    def test_character_parser(self):
        self.fail()

    def test_keyboard_parser(self):
        self.fail()

    def test_label_parser(self):
        self.fail()


class TestLabelParser(TestCase):
    def test_decode_ch(self):
        lp:LabelParser = LabelParser.getInstance()
        kp:KeyboardParser = KeyboardParser.getInstance()
        cp:CharacterParser = CharacterParser.getInstance()
        s = "Uu"
        labelList = lp.encodeStr(s)
        cList = cp.encodeStr(s)
        keyPos:KeyboardPosition = kp.parseCh("u")
        keyPos1:KeyboardPosition = kp.parseCh("U")
        print(f"label: {labelList}\nserial: {cList}")

        print(f"{keyPos.__dict__}, {keyPos1.__dict__}")

    def test_serialnumber(self):
        cp:CharacterParser = CharacterParser.getInstance()
        print(f"{cp.map}")
        vList =cp.map.values()
        print(f"max:{max(vList)}")

    def test_q(self):
        lp:LabelParser = LabelParser.getInstance()
        kp:KeyboardParser = KeyboardParser.getInstance()

        qi = lp.encodeCh("q")
        k = kp.parseCh("q")
        print(f"{qi},{k.__dict__}")

