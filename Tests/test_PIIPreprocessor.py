from unittest import TestCase

from Parser import PIIDataTypes
from Parser.PIIPreprocessor import PIIPreprocessor


class TestPIIPreprocessor(TestCase):
    def test_filter_line(self):
        processor = PIIPreprocessor(initDataset=PIIDataTypes.PIIDataSet(), datasetFile="../Datasets/testdataset1.txt",
                                    savePath="../Datasets/save1.txt", start=0, limit=1000)
        processor.preprocess()

    def test_format_unit(self):
        self.fail()
