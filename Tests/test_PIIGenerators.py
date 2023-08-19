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
