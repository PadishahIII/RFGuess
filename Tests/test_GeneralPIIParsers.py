from unittest import TestCase
from Parser.GeneralPIIParsers import *
from Commons.DatabaseLayer import *

class TestGeneralPIIParser(TestCase):
    def test_build_datagram_list(self):
        transformer:GeneralPwRepUniqueTransformer = GeneralPwRepUniqueTransformer.getInstance()
        l:list[GeneralPwRepAndStructureUnit] = transformer.readAsParseUnit(offset=1300,limit=10)
        tagParser:GeneralPIIRepresentationStrParser = GeneralPIIRepresentationStrParser.getInstance()
        for unit in l:
            rep:GeneralPIIRepresentation = unit.rep
            parser:GeneralPIIParser = GeneralPIIParser(None,unit.pwStr,rep)
            parser.parse()
            featureList = parser.getFeatureList()
            labelList = parser.getLabelList()
            print(f"rep:{tagParser.representationToStr(rep)}")
            print(f"feature({len(featureList)}):{featureList}\nlabel({len(labelList)}):{labelList}\n")


