from unittest import TestCase

from Commons.DatabaseLayer import *
from Parser.PIIDataTypes import *
from Parser.PIIPreprocessor import PIIPreprocessor


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

    def test_build(self):
        self.buildPwRepresentationTable()

    def test_read_pwrep(self):
        queryMethods = RepresentationMethods()
        repParser = PIITagRepresentationStrParser()
        units: list[PwRepresentation] = queryMethods.QueryWithLimit(offset=0, limit=10)
        for unit in units:
            pwStr = unit.pwStr
            rep: PIIRepresentation = PwRepresentationTransformer.getRepresentation(unit)
            repStr = repParser.representationToStr(rep)
            print(f"pw:{pwStr},rep:{repStr}")

    def test_read_frequency(self):
        pass
