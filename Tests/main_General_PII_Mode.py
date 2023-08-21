import json
from unittest import TestCase

from Parser.GeneralPIIParsers import *


class TestGeneralPIIStructureParser(TestCase):
    def test_parse_all_general_vector_recursive(self):
        pii = BasicTypes.PII(account="yhang0607",
                             name="yhangzhongjie",
                             firstName="yhang",
                             givenName="zhong jie",
                             birthday="19820607",
                             phoneNum="13222245678",
                             email="3501111asd11@qq.com",
                             idcardNum="1213213213")
        pw1 = "qwe123ryhang0607yuiyzj123wqer!@#"
        parser = GeneralPIIStructureParser(pii)
        piiParser = PIIStructureParser(pii)

        s: GeneralPIIStructure = parser.getGeneralPIIStructure(pw1)
        # print(f"{json.dumps(s._tojson(),indent=2)}")

        strParser: GeneralPIIRepresentationStrParser = GeneralPIIRepresentationStrParser.getInstance()
        for rep in s.repList:
            print(f"{strParser.representationToStr(rep)}\n")

        print(f"\nPIIParser:\n")
        piiS:PIIStructure = piiParser.getPwPIIStructure(pw1)

        piiStrParser:PIITagRepresentationStrParser = PIITagRepresentationStrParser.getInstance()
        for rep in piiS.piiRepresentationList:
            print(f"{piiStrParser.representationToStr(rep)}\n")

