from unittest import TestCase

from Commons import Utils
from Commons.BasicTypes import PIIType


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
