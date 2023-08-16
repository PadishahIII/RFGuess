from random import random
from unittest import TestCase

from Commons.DatabaseLayer import *
from Parser.PIIParsers import *


class TestTag(TestCase):
    def test_create(self):
        tag1 = Tag.create(PIIType.BaseTypes.L, "asd")
        tag2 = Tag.create(PIIType.NameType.FullName, "jason")
        print(tag1.__dict__)
        print(tag2.__dict__)


class TestPIIRepresentationResolver(TestCase):
    def test_get_instance(self):
        resolver = PIIRepresentationResolver.getInstance()
        print(f"pwList:{len(resolver.pwList)}\n{resolver.pwList[:10]}")
        print(f"pwAllRepDict:{len(resolver.pwAllRepDict)}\n{resolver.pwAllRepDict[resolver.pwList[0]]}")
        for k, v in resolver.pwAllRepDict.items():
            assert v is not None and isinstance(v, list) and len(v) > 0
        print(
            f"repPriorityList:{len(resolver.repPriorityList)}\n{list(map(lambda x: x.frequency, resolver.repPriorityList[:10]))}")

    def test_check_pw_rep_match(self):
        self.fail()

    def test_resolve(self):
        self.fail()

    def test_short_match(self):
        resolver: PIIRepresentationResolver = PIIRepresentationResolver.getInstance()
        transformer: PwRepFrequencyTransformer = PwRepFrequencyTransformer.getInstance()
        parser: PIITagRepresentationStrParser = PIITagRepresentationStrParser()
        s = "xww123123"
        repList: list[PIIRepresentation] = list()
        for unit in resolver.pwAllRepDict[s]:
            rep: PIIRepresentation = transformer.getRepresentation(unit)
            repList.append(rep)
        for i in range(len(repList)):
            ss = parser.representationToStr(repList[i])
            print(f"{i}:{ss}\n")
        unit: RepUnit = resolver.shortMatch(s)
        rep: PIIRepresentation = Serializer.deserialize(unit.repStr)
        reps = parser.representationToStr(rep)
        print(f"shortest:\n{reps}")

    def test_resolve(self):
        resolver: PIIRepresentationResolver = PIIRepresentationResolver.getInstance()
        transformer: PwRepFrequencyTransformer = PwRepFrequencyTransformer.getInstance()
        pwList = copy(resolver.pwList)
        pwRepDict: dict[str, RepUnit] = resolver.resolve()
        assert len(pwList) == len(pwRepDict)

        randIndexList = list()
        for i in range(4):
            randIndexList.append(int(random() * len(pwList)))
        # for index in randIndexList:
        #     pw = pwList[index]
        #     rep: RepUnit = pwRepDict[pw]
        #     repExpected: RepUnit = resolver.shortMatch(pw)
        #     assert rep == repExpected


class TestPIIToTagParser(TestCase):
    def test_parse_account_to_tag_dict(self):
        account = "p9p9p9p9"
        d = PIIToTagParser.parseAccountToTagDict(account)
        print(d)
