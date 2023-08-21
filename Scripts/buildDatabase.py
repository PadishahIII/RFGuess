import random
from unittest import TestCase

from Commons.DatabaseLayer import *
from Parser import PIIDataTypes
from Parser.PIIParsers import *
from Parser.PIIPreprocessor import PIIPreprocessor
from Scripts import Utils as DatabaseUtils
from Parser.GeneralPIIParsers import *


class BuildDatabase(TestCase):
    """Build datatables
    Scripts to build datatables

    """

    def buildPwRepresentationTable(self):
        """
        Build `pwrepresentation` table based on `pii` dataset.
        Parse all representations of password and store in `pwrepresentation` datatable.
        """
        processor = PIIPreprocessor(initDataset=PIIDataTypes.PIIDataSet(), start=0, limit=-1)
        processor.preprocess()
        dataset = processor.getDataSet()
        # for unit in iter(dataset):
        #     print(str(unit))
        print(f"Total: {dataset.row}")
        print(f"keyList:{dataset.keyList}")

        transformer = PwRepresentationTransformer.getInstance()
        transformer.queryMethods.DeleteAll()

        datasetIter: typing.Iterable[PIIDataUnit] = iter(dataset)
        i = 0
        repCount = 0
        updateCount = 0
        exceptionCount = 0
        for unit in datasetIter:
            pii = unit.pii
            piiParser = PIIStructureParser(pii)
            piiStructure = piiParser.getPwPIIStructure(pwStr=unit.password)
            for rep in piiStructure.piiRepresentationList:
                pr = PwRepresentationTransformer.getPwRepresentation(pwStr=unit.password, rep=rep)
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

        transformer:GeneralPwRepresentationTransformer = GeneralPwRepresentationTransformer.getInstance()
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
                pr = transformer.transformParseunitToBaseunit(pwStr=unit.password,rep=rep)
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
        self.buildPwRepresentationTable()

    def test_build_general(self):
        self.buildGeneralPwRepresentationTable()

    def test_read_pwrep(self):
        queryMethods = RepresentationMethods()
        repParser = PIITagRepresentationStrParser()
        units: list[PwRepresentation] = queryMethods.QueryWithLimit(offset=0, limit=10)
        for unit in units:
            pwStr = unit.pwStr
            rep: PIIRepresentation = PwRepresentationTransformer.getRepresentation(unit)
            repStr = repParser.representationToStr(rep)
            print(f"pw:{pwStr},rep:{repStr}")

    def test_read_pwrep_general(self):
        transformer:GeneralPwRepresentationTransformer = GeneralPwRepresentationTransformer.getInstance()
        repParser:GeneralPIIRepresentationStrParser = GeneralPIIRepresentationStrParser.getInstance()
        units: list[GeneralPwRepUnit] = transformer.read(offset=0,limit=10)
        for unit in units:
            pwStr = unit.pwStr
            rep:GeneralPIIRepresentation = unit.rep
            repStruc:GeneralPIIRepresentation = unit.repStructure
            repStr = repParser.representationToStr(rep)
            repStrucStr = repParser.representationToStr(repStruc)
            print(f"pw:{pwStr},rep:{repStr},repStructure:{repStrucStr}")

    def test_build_unique(self):
        resolver: PIIRepresentationResolver = PIIRepresentationResolver.getInstance()
        transformer: PwRepUniqueTransformer = PwRepUniqueTransformer.getInstance()

        transformer.queryMethods.DeleteAll()

        exceptionCount = 0
        i = 0

        pwRepDict: dict[str, RepUnit] = resolver.resolve()
        _len = len(pwRepDict)
        print(f"Resolved:{_len}")

        for pwStr, repUnit in pwRepDict.items():
            unit: PwRepUniqueUnit = DatabaseUtils.getIntermediateFromRepUnit(pwStr, repUnit)
            try:
                transformer.Insert(unit)
            except Exception as e:
                print(f"Exception occur: {str(e)}, pwStr: {pwStr}, RepUnit:{str(repUnit)}")
                exceptionCount += 1
            i += 1
            if i % 100 == 0:
                print(f"Progress:{i}/{_len} ({(i / _len * 100):.2f}%)")
        print(f"Completed! Total:{i}, total exception:{exceptionCount}")

    def test_read_unique(self):
        transformer: PwRepUniqueTransformer = PwRepUniqueTransformer.getInstance()
        parser: PIITagRepresentationStrParser = PIITagRepresentationStrParser()

        for i in range(10):
            id = random.randint(1, 129300)
            unit: PwRepAndStructureUnit = transformer.getParseunitWithId(id)
            rep: PIIRepresentation = unit.rep
            repStructure: PIIRepresentation = unit.repStructure
            repStr = parser.representationToStr(rep)
            repStructureStr = parser.representationToStr(repStructure)
            print(f"pw:{unit.pwStr} representation:{repStr}structure:{repStructureStr}")
