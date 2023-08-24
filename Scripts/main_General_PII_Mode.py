import time
from unittest import TestCase

import joblib
from sklearn import tree

from Generators.GeneralPIIGenerators import *
from Generators.PasswordGuessGenerator import *
from Parser.Factory import *
from Parser.PIIPreprocessor import *


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


class BuildDatabase(TestCase):
    def test_rebuild(self):
        """Rebuild all datatables
        """
        print(f"Start addressing dataset...")
        self.test_build()
        print(f"Finish addressing dataset")
        print(f"Start generating datatables...")
        time.sleep(1)
        self.test_generate_frequency_tables()
        print(f"Finish generating datatables")
        print(f"Start resolving representations and build unique datatable...")
        time.sleep(1)
        self.test_build_general_unique()
        print(f"\nRebuild complete!")

    def buildGeneralPwRepresentationTable(self):
        """
        Build `pwrepresentation_general` table based on `pii` dataset.
        Parse all representations of password and store in `pwrepresentation_general` datatable.
        """
        processor = PIIPreprocessor(initDataset=PIIDataTypes.PIIDataSet(), start=0, limit=-1)
        processor.preprocess()
        dataset = processor.getDataSet()
        # for unit in iter(dataset):
        #     print(str(unit))
        print(f"Total: {dataset.row}")
        print(f"keyList:{dataset.keyList}")

        transformer: GeneralPwRepresentationTransformer = GeneralPwRepresentationTransformer.getInstance()
        transformer.queryMethods.DeleteAll()
        datasetIter: typing.Iterable[PIIDataUnit] = iter(dataset)
        i = 0
        repCount = 0
        updateCount = 0
        exceptionCount = 0
        for unit in datasetIter:
            pii = unit.pii
            piiParser = GeneralPIIStructureParser(pii)
            piiStructure = piiParser.getGeneralPIIStructure(pwStr=unit.password)
            for rep in piiStructure.repList:
                pr = transformer.transformParseunitToBaseunit(pwStr=unit.password, rep=rep)
                try:
                    transformer.Insert(pr)
                    repCount += 1
                except Exception as e:
                    print(f"Exception occur: {str(e)}, pr: {str(pr)}")
                    exceptionCount += 1
            i += 1
            if i % 100 == 0:
                print(f"Progress:{i}/{dataset.row} ({(i / dataset.row * 100):.2f}%)")
        print(
            f"Completed! Total password:{i}, total item;{repCount}, update item:{updateCount}, total exception:{exceptionCount}")

    def test_build(self):
        self.buildGeneralPwRepresentationTable()

    def test_generate_frequency_tables(self):
        """Generate three datatable: `representation_frequency_base_general`, `pwrepresentation_frequency_general`, `representation_frequency_general`
        """
        transformers = list()
        transformers.append(GeneralRepFrequencyBaseTransformer.getInstance())
        transformers.append(GeneralRepFrequencyTransformer.getInstance())
        transformers.append(GeneralPwRepFrequencyTransformer.getInstance())
        for t in transformers:
            t.rebuild()
        print(f"Re-generate Complete")

    def test_build_general_unique(self):
        """Build unique datatable
        """
        resolver: GeneralPIIRepresentationResolver = GeneralPIIRepresentationResolver.getInstance()
        transformer: GeneralPwRepUniqueTransformer = GeneralPwRepUniqueTransformer.getInstance()

        transformer.queryMethods.DeleteAll()

        exceptionCount = 0
        i = 0

        pwRepDict: dict[str, RepUnit] = resolver.resolve()
        _len = len(pwRepDict)
        print(f"Resolved:{_len}")

        for pwStr, repUnit in pwRepDict.items():
            try:
                unit: PwRepUniqueUnit = DatabaseUtils.getGeneralIntermediateFromRepUnit(pwStr, repUnit)
                transformer.Insert(unit)
            except Exception as e:
                print(f"Exception occur: {str(e)}, pwStr: {pwStr}, RepUnit:{str(repUnit)}")
                exceptionCount += 1
            i += 1
            if i % 100 == 0:
                print(f"Progress:{i}/{_len} ({(i / _len * 100):.2f}%)")
        print(f"Completed! Total:{i}, total exception:{exceptionCount}")


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
