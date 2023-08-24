from unittest import TestCase

import joblib
from sklearn import tree

from Generators.GeneralPIIGenerators import *
from Generators.PasswordGuessGenerator import *
from Parser.Factory import *


class GeneralPIITrainMain(TestCase):
    def test_train_general(self):
        piiFactory = GeneralPIIFactory.getInstance()
        piiFactory.process()
        print(
            f"Train data build Finished.\nSize of featureList:{len(piiFactory.getFeatureList())} LabelList:{len(piiFactory.getLabelList())}")
        print(f"\nStart Training...")
        trainner = PIIRFTrainner(piiFactory.getFeatureList(), piiFactory.getLabelList())
        trainner.train()
        savePath = "../../save_general.clf"
        joblib.dump(trainner.getClf(), savePath)
        print(f"Train finish, saved to {savePath}")

    def test_generate_pattern(self):
        generator: GeneralPIIPatternGenerator = GeneralPIIPatternGenerator.getInstance("../../save_general.clf")
        l, pl = generator.generatePattern()
        print(f"Generate complete: {len(l)}:{len(pl)}")
        sl: list[str] = [generator.datagramFactory.parseGeneralPIIDatagramToStr(dg) for dg in l]

        with open("../patterns_general.txt", "w") as f:
            for i in range(len(sl)):
                f.write(f"{sl[i]}\n")

    def test_generate_guess(self):
        pii = BasicTypes.PII(account="yhang0607",
                             name="yhangzhongjie",
                             firstName="yhang",
                             givenName="zhong jie",
                             birthday="19820607",
                             phoneNum="13222245678",
                             email="3501111asd11@qq.com",
                             idcardNum="1213213213")

        generator: GeneralPasswordGenerator = GeneralPasswordGenerator.getInstance(
            patternFile="../patterns_general.txt",
            outputFile="../passwords_general.txt",
            pii=pii,
            nameFuzz=True)
        generator.run()

    def test_output_clf(self):
        generator: GeneralPIIPatternGenerator = GeneralPIIPatternGenerator.getInstance("../../save_general.clf")
        # export_graphviz(generator.clf.getClf().estimators_[0],out_file="./graph.dot")
        # graph = graphviz.Source(dot_data)
        text = tree.export_text(generator.clf.getClf().estimators_[0])
        with open("../Tests/tree_text.txt", "w") as f:
            f.write(text)


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
        piiS: PIIStructure = piiParser.getPwPIIStructure(pw1)

        piiStrParser: PIITagRepresentationStrParser = PIITagRepresentationStrParser.getInstance()
        for rep in piiS.piiRepresentationList:
            print(f"{piiStrParser.representationToStr(rep)}\n")

