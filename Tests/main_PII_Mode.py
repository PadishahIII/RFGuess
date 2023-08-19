import base64
import json
import pickle
from unittest import TestCase

import clipboard
import joblib

from Classifiers.PIIRFTrainner import PIIRFTrainner
from Parser.Factory import *
# from PasswordParser import *
from Parser.PIIParsers import *


class PIITrainTest(TestCase):
    piiFactory = PIIFactory.getInstance()
    piiFactory.process()
    print(
        f"Train data build Finished.\nSize of featureList:{len(piiFactory.getFeatureList())} LabelList:{len(piiFactory.getLabelList())}")
    print(f"\nStart Training...")
    trainner = PIIRFTrainner(piiFactory.getFeatureList(), piiFactory.getLabelList())
    trainner.train()
    savePath = "../save.clf"
    joblib.dump(trainner.getClf(), savePath)
    print(f"Train finish, saved to {savePath}")


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

        pii = BasicTypes.PII(account="yhang0607",
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
        # for tag in tagList:
        #     print(f"Tag id:{i}")
        #     print(f"\tType:{str(tag.piitype.__class__) + str(tag.piitype.name)}")
        #     print(f"\tValue:{tag.piitype.value}")
        #     print(f"\tString:{tag.s}")
        #     print("")
        #     i += 1
        piiStructureParser = PIIStructureParser(pii)
        piiStructure: PIIStructure = piiStructureParser.getPwPIIStructure(pw1)
        json_str = json.dumps(piiStructure._tojson(), indent=2)
        # print(f"pii structure:\n{json_str}")
        tagParser = PIITagRepresentationStrParser()
        print(f"Representations:")
        for rep in piiStructure.piiRepresentationList:
            print(tagParser.representationToStr(rep))

        rep = piiStructure.piiRepresentationList[1]
        vector = rep.piiVectorList[0]
        vectorSerialized = pickle.dumps(vector, )
        print(f"vector se: {vectorSerialized}")
        vectorSerializedB = base64.b64encode(vectorSerialized).decode("utf-8")
        print(f"vector seB: {vectorSerializedB}")
        vectorDe: PIIVector = pickle.loads(base64.b64decode(vectorSerializedB.encode("utf-8")))
        print(f"vector re: {json.dumps(vectorDe._tojson(), indent=2)}")

        def serialize(obj) -> str:
            objSe = pickle.dumps(obj)
            s = base64.b64encode(objSe).decode("utf-8")
            return s

        def deserialize(s: str) -> object:
            obj = pickle.loads(base64.b64decode(s.encode("utf-8")))
            return obj

        repS = serialize(rep)
        print(f"rep se: {repS}")
        clipboard.copy(repS)
        repRe = deserialize(repS)
        print(f"rep re: {json.dumps(repRe._tojson(), indent=2)}")

    def test_representationParse(self):
        s = "N1B2L3S4D4"
        pwStr = "zhangzhongjie06071982aaa!@#$1234"
        parser = PIITagRepresentationStrParser()
        rep: PIIRepresentation = parser.strToRepresentation(s)
        print(json.dumps(rep._tojson(), indent=2))
        repStr = parser.representationToStr(rep)
        print(f"rep str: {repStr}")

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
