import base64
import json
import pickle
from unittest import TestCase

import clipboard
import joblib

# from PasswordParser import *
from Generators.PIIGenerators import *
from Generators.PasswordGuessGenerator import *
from Parser.Factory import *


class PIITrainTest(TestCase):
    def test_train(self):
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

    def test_generate_pattern(self):
        generator: PIIPatternGenerator = PIIPatternGenerator.getInstance("../save.clf")
        l, pl = generator.generatePattern()
        sl: list[str] = [generator.datagramFactory.parsePIIDatagramToStr(dg) for dg in l]

        with open("../patterns.txt", "w") as f:
            for i in range(len(sl)):
                f.write(f"{sl[i]}  {pl[i]}\n")

    def test_label(self):
        piiFactory = GeneralPIIFactory.getInstance()
        sectionFactory: GeneralPIISectionFactory = GeneralPIISectionFactory.getInstance()
        dgFactory: GeneralPIIDatagramFactory = GeneralPIIDatagramFactory.getInstance()
        tagParser: GeneralPIIRepresentationStrParser = GeneralPIIRepresentationStrParser.getInstance()
        piiFactory.process()

        labelSet = set(piiFactory.getLabelList())
        lp: LabelParser = LabelParser.getInstance()
        labelS = ""
        sectionList: list[GeneralPIISection] = list()
        for i in labelSet:
            section: GeneralPIISection = sectionFactory.createFromInt(i)
            sectionList.append(section)
        dg: GeneralPIIDatagram = dgFactory.createGeneralPIIDatagramOnlyWithFeature(sectionList, 0, 0)
        labelS = dgFactory.parseGeneralPIIDatagramToStr(dg)
        cLabels = list()
        for i in labelSet:
            if i < 1000:
                cLabels.append(i)

        print(
            f"{len(piiFactory.getLabelList())}:{len(labelSet)},maxLabel:{max(labelSet)},max char label:{max(cLabels)}")
        print(f"{labelS}")
        print(f"{labelS.__contains__('`')}")
        print(f"{labelS.__contains__('U')}")


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


    def test_pii_container(self):
        pii = BasicTypes.PII(account="ty763699438",
                             name="tianyu",
                             firstName="#yhang",
                             givenName="%zhong jie",
                             birthday=".a19820607",
                             phoneNum="15051401132",
                             email="763699438@qq.com",
                             idcardNum="429004199008100018")
        pw = "qq763699438"

        parser:PIIFullTagParser = PIIFullTagParser(pii,nameFuzz=True)
        parser.parseTag()
        tagList:list[Tag]=parser.getTagContainer().getTagList()
        for tag in tagList:
            print(tag.__dict__)

    def test_pii_structure_parser(self):
        piiUnit:PIIUnit = PIIUnit(email="190466944@qq.com",
                                  account="131312",
                                  name="罗小浩",
                                  idCard="42098419921012047X",
                                  phoneNum="13189817093",
                                  password="luo131312",
                                  fullName="luo xiao hao")
        pii,pwStr = Utils.parsePIIUnitToPIIAndPwStr(piiUnit)
        print(pii.__dict__)
        # pw = "qq763699438"
        # pw = "ty333763699438"
        # pw = "haijing0325"
        pw = pwStr

        parser:GeneralPIIStructureParser = GeneralPIIStructureParser(pii=pii)
        struct:GeneralPIIStructure = parser.getGeneralPIIStructure(pw)
        repParser:GeneralPIIRepresentationStrParser = GeneralPIIRepresentationStrParser.getInstance()

        tagParser:PIIFullTagParser = PIIFullTagParser(pii,nameFuzz=True)
        tagParser.parseTag()
        tagList:list[Tag] = tagParser.getTagContainer().getTagList()
        for tag in tagList:
            print(f"{tag.__dict__}")

        print(f"Rep:")

        for rep in struct.repList:
            s = repParser.representationToStr(rep)
            print(f"{s}")
