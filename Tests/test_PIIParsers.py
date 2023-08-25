import json
import random
from unittest import TestCase

from Commons.DatabaseLayer import *
from Parser.GeneralPIIParsers import *


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


class TestPIIParser(TestCase):
    def test_build_datagram_list(self):
        transformer: PwRepUniqueTransformer = PwRepUniqueTransformer.getInstance()
        minId = 0
        maxId = 129300
        l: list[PwRepAndStructureUnit] = []
        for i in range(100):
            id = random.randint(minId, maxId)
            unit = transformer.getParseunitWithId(id)
            l.append(unit)

        repParser: PIITagRepresentationStrParser = PIITagRepresentationStrParser()
        for unit in l:
            parser: PIIParser = PIIParser(None, unit.pwStr, unit.rep)
            parser.parse()
            repStr = repParser.representationToStr(unit.rep)
            if len(unit.rep.piiVectorList) > 4:
                print(
                    f"{unit.pwStr}\n{repStr}feature:{len(parser.getFeatureList()[0])}{parser.getFeatureList()}\nlabel:{parser.getLabelList()}\n")

    def test_build_general_datagram_list(self):
        transformer: GeneralPwRepUniqueTransformer = GeneralPwRepUniqueTransformer.getInstance()
        minId = 154195
        maxId = 283494
        l: list[GeneralPwRepAndStructureUnit] = []
        for i in range(100):
            id = random.randint(minId, maxId)
            unit = transformer.getParseunitWithId(id)
            l.append(unit)

        repParser: GeneralPIIRepresentationStrParser = GeneralPIIRepresentationStrParser()
        for unit in l:
            parser: GeneralPIIParser = GeneralPIIParser(None, unit.pwStr, unit.rep)
            parser.parse()
            repStr = repParser.representationToStr(unit.rep)
            if len(unit.rep.vectorList) > 4:
                print(
                    f"{unit.pwStr}\n{repStr}feature:{len(parser.getFeatureList()[0])}{parser.getFeatureList()}\nlabel:{parser.getLabelList()}\n")


class TestPIISectionFactory(TestCase):
    def test_get_begin_section(self):
        self.fail()

    def test_get_end_section(self):
        self.fail()

    def test_create_from_piivector(self):
        factory: PIISectionFactory = PIISectionFactory.getInstance()
        # vector = PIIVector(s="jason",piitype=BasicTypes.PIIType.NameType.GivenName,piivalue=)
        transformer: PwRepUniqueTransformer = PwRepUniqueTransformer.getInstance()
        parser: PIITagRepresentationStrParser = PIITagRepresentationStrParser()

        unit: PwRepAndStructureUnit = transformer.getParseunitWithPw("w63844810")
        print(unit.rep.piiVectorList[1].__dict__)
        s1: PIISection = factory.createFromPIIVector(unit.rep.piiVectorList[0])
        s2: PIISection = factory.createFromPIIVector(unit.rep.piiVectorList[1])
        print(f"s1:{json.dumps(s1._tojson())}")
        print(f"s2:{json.dumps(s2._tojson())}")

    def test_create_from_int(self):
        factory: PIISectionFactory = PIISectionFactory.getInstance()
        s1: PIISection = factory.createFromInt(1001)
        s2 = factory.createFromInt(0)
        s3 = factory.createFromInt(-1)
        s4: PIISection = factory.createFromInt(7011)
        self.assertRaises(PIISectionFactoryException, factory.createFromInt, 2011)

        print(f"s1:{json.dumps(s1._tojson())}")
        print(f"s2:{json.dumps(s2._tojson())}")
        print(f"s3:{json.dumps(s3._tojson())}")
        print(f"s4:{json.dumps(s4._tojson())}")
        self.assertRaises(PIISectionFactoryException, factory.createFromInt, 100)

    def test_create_from_str(self):
        factory: PIISectionFactory = PIISectionFactory.getInstance()
        l: list[PIISection] = list()
        l.append(factory.createFromStr("N1"))
        l.append(factory.createFromStr("A2"))
        l.append(factory.createFromStr("L9"))
        l.append(factory.createFromStr("S11"))
        for s in l:
            print(f"{json.dumps(s._tojson())}")


def test_is_ldstype(self):
    self.fail()


class TestPIIDatagramFactory(TestCase):
    def test_create_from_str(self):
        factory: PIIDatagramFactory = PIIDatagramFactory.getInstance()
        dg1: PIIDatagram = factory.createFromStr("N1A2I3L10")
        dg2: PIIDatagram = factory.createFromStr("N1A2I3L1")
        dg3: PIIDatagram = factory.createFromStr("N1A2I3L1S10D9E1I2A3")
        print(f"{len(dg1._tovector())}:{json.dumps(dg1._tovector())}")
        print(f"{len(dg2._tovector())}:{json.dumps(dg2._tovector())}")
        print(f"{len(dg3._tovector())}:{json.dumps(dg3._tovector())}")
        print(f"{len(dg3._tovector())}:{json.dumps(dg3._tojson(), indent=2)}")


class TestPIISectionFactory(TestCase):
    def test_parse_piisection_to_str(self):
        factory: PIISectionFactory = PIISectionFactory.getInstance()
        l: list[PIISection] = list()
        l.append(factory.createFromStr("N1"))
        l.append(factory.createFromStr("L11"))
        l.append(factory.createFromStr("A3"))
        l.append(factory.createFromStr("I1"))
        for section in l:
            print(f"{factory.parsePIISectionToStr(section)}")


class TestPIIDatagramFactory(TestCase):
    def test_parse_piidatagram_to_str(self):
        factory: PIIDatagramFactory = PIIDatagramFactory.getInstance()
        l: list[PIIDatagram] = list()
        l.append(factory.createFromStr("N1A2I3L10"))
        l.append(factory.createFromStr("A1E3N2S3N1A2I3L10"))
        for dg in l:
            print(f"{factory.parsePIIDatagramToStr(dg)}")

    def test_parse_general_piidatagram_to_str(self):
        factory: GeneralPIIDatagramFactory = GeneralPIIDatagramFactory.getInstance()
        l: list[GeneralPIIDatagram] = list()
        l.append(factory.createFromStr("<N1><N2<>>asd123!#$N1<L10>"))
        for dg in l:
            print(f"{factory.parseGeneralPIIDatagramToStr(dg)}\n{json.dumps(dg._tojson(), indent=2)}")


class TestPIISectionFactory(TestCase):
    def test_get_all_piisection_dict(self):
        factory: PIISectionFactory = PIISectionFactory.getInstance()
        d = factory.getAllPIISectionDict()
        for s, section in d.items():
            print(f"{s}:{json.dumps(section._tojson())}")

    def test_get_all_piidatagram_dict(self):
        factory:PIIDatagramFactory = PIIDatagramFactory.getInstance()
        d = factory.getAllBasicPIIDatagramsDict()
        for s, dg in d.items():
            print(f"{s}:{json.dumps(dg._tojson())}")

