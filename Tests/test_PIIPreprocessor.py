from unittest import TestCase

from Parser import PIIDataTypes
from Parser.PIIPreprocessor import PIIPreprocessor


class TestPIIPreprocessor(TestCase):
    def test_filter_line(self):
        processor = PIIPreprocessor(initDataset=PIIDataTypes.PIIDataSet(), start=0, limit=10)
        processor.preprocess()
        dataset = processor.getDataSet()
        for unit in iter(dataset):
            print(str(unit))
        print(f"Total: {dataset.row}")
        print(f"keyList:{dataset.keyList}")
        unit:PIIDataTypes.PIIDataUnit = next(iter(dataset))
        print(f"unit pii:{str(unit.pii)}, pw:{unit.password}")


    def test_format_unit(self):
        self.fail()
