import json
from unittest import TestCase

# from PasswordParser import *
from Parser.PIIParsers import *
from Parser.PasswordParsers import *


class TestPIIParsers(TestCase):

    def test_all(self):
        name = "abcdefg12345"
        a1 = "beg4"
        a2 = "ac4"
        a3 = "bg5"
        a4 = name
        a5 = "aeg5"
        a6 = "at5"
        a7 = "ag5t"

        pii = BasicTypes.PII(account="user123!@#",
                             name="yhangzhongjie",
                             firstName="yhang",
                             givenName="zhong jie",
                             birthday="19820607",
                             phoneNum="13222245678",
                             email="3501111asd11@qq.com",
                             idcardNum="1213213213")
        pw1 = "qwe123ryhang0607yuiyzj123wqer!@#"
        parser = PIIFullTagParser(pii, nameFuzz=True)
        parser.parseTag()
        tagContainer: PIITagContainer = parser.getTagContainer()
        tagList: typing.List[Tag] = tagContainer.getTagList()
        i = 1
        for tag in tagList:
            print(f"Tag id:{i}")
            print(f"\tType:{str(tag.piitype.__class__) + str(tag.piitype.name)}")
            print(f"\tValue:{tag.piitype.value}")
            print(f"\tString:{tag.s}")
            print("")
            i += 1
        piiStructureParser = PIIStructureParser(pii)
        piiStructure: PIIStructure = piiStructureParser.getPwPIIStructure(pw1)
        json_str = json.dumps(piiStructure._tojson(), indent=2)
        print(f"pii structure:\n{json_str}")

    def test_check_piiname_type(self):
        self.fail()

    def test_parse_str_to_piistructure(self):
        self.fail()

    def test_parse_all_piitag_recursive(self):
        self.fail()

    def test_convert_tag_list_to_piivector_list(self):
        self.fail()

    def test_piivector(self):
        self.fail()

    def test_piirepresentation(self):
        self.fail()

    def test_piistructure(self):
        self.fail()

    def test_tag(self):
        self.fail()

    def test_piitag_container(self):
        self.fail()

    def test_fuzzers(self):
        self.fail()

    def test_ldsstepper(self):
        self.fail()

    def test_email_parser(self):
        self.fail()

    def test_piifull_tag_parser(self):
        self.fail()

    def test_piito_tag_parser(self):
        self.fail()

    def test_piistructure_parser(self):
        self.fail()

    def test_datagram(self):
        self.fail()

    def test_piitrain_vector_builder(self):
        self.fail()
