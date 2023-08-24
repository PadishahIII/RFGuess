import json
from unittest import TestCase

from Generators.PIIGenerators import *


class TestPIIPatternGenerator(TestCase):
    def test_create_section_from_int(self):
        generator = PIIPatternGenerator()
        s1: PIISection = generator.createSectionFromInt(1001)
        s2 = generator.createSectionFromInt(0)
        s3 = generator.createSectionFromInt(-1)
        s4: PIISection = generator.createSectionFromInt(2003)
        self.assertRaises(PIILabelException, generator.createSectionFromInt, 2011)

        print(f"s1:{json.dumps(s1._tojson())}")
        print(f"s2:{json.dumps(s2._tojson())}")
        print(f"s3:{json.dumps(s3._tojson())}")
        print(f"s4:{json.dumps(s4._tojson())}")
        self.assertRaises(PIILabelException, generator.createSectionFromInt, 100)


class TestPIIPatternGenerator(TestCase):
    def test_get_classify_result_from_str_list(self):
        generator: PIIPatternGenerator = PIIPatternGenerator.getInstance("../save.clf")
        seedList = ['N1', 'L1', "A1", "E1", "A2"]
        l = generator.getClassifyResultFromStrList(seedList)
        print(l)

    def test_multi_classify(self):
        generator: PIIPatternGenerator = PIIPatternGenerator.getInstance("../save.clf")
        seedList = ['N1', "A2", "E1", "L1", "S1", "D1", "B1", "B2"]
        resList = generator.getMultiClassifyResultFromStrList(seedList, n=2)
        print(f"seed list len:{len(seedList)}\nres list len:{len(resList)}\n{list(set(resList))}")


class TestPIIPatternGenerator(TestCase):
    def test_classify_multi_from_piidatagram_to_proba_dict(self):
        generator: PIIPatternGenerator = PIIPatternGenerator.getInstance("../save.clf")
        d = generator.getMultiClassifyResultFromStrToProbaDict("N1")
        print(d)

        d1: PIIDatagram = generator.datagramFactory.createFromStr("N1")
        d2 = copy(d1)
        pd = dict()
        pd[d1] = 1
        pd[d2] = 2
        print(pd)

        s1: PIISection = generator.sectionFactory.createFromInt(4001)
        s2 = copy(s1)
        s3: PIISection = generator.sectionFactory.createFromInt(4002)
        print(hash(s1))
        print(hash(s2))
        print(hash(s3))
        pd = dict()
        pd[s1] = 1
        pd[s2] = 2
        print(pd)

