from unittest import TestCase

from Commons import Utils
from Commons.BasicTypes import PIIType
from Scripts.databaseInit import PIIUnit

class Testtranslation(TestCase):
    def test_make_trans(self):
        fromList = [PIIType.NameType, PIIType.BirthdayType, PIIType.AccountType, PIIType.IdCardNumberType,
                    PIIType.EmailPrefixType, PIIType.BaseTypes.L, PIIType.BaseTypes.D, PIIType.BaseTypes.S]
        toList = ["N", "B", "A", "I", "E", "L", "D", "S"]
        trans = Utils.translation.makeTrans(fromList, toList)
        for o in fromList:
            print(trans.translate(o))

        def raiseException():
            trans.translate(1)

        self.assertRaises(Utils.TranslationException, raiseException)

    def test_translate(self):
        self.fail()

    def test_parsePIIUnitToPII(self):
        unit = PIIUnit(email="274667266@qq.com",
                       account="6837605",
                       idCard="332522198705040011",
                       phoneNum="15068860664",
                       name="郑一峰",
                       password="z6837605",
                       fullName="zheng yi feng")
        pii, pwStr = Utils.parsePIIUnitToPIIAndPwStr(unit)
        print(pii.__dict__)
        print(f"pw:{pwStr}")
