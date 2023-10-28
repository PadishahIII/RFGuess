from unittest import TestCase

from Parser.DatasetParser import CsvDatasetLoader


class TestCsvDatasetLoader(TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.loader = CsvDatasetLoader()

    def test_load_dataset(self):
        self.loader.clear_and_load_dataset("test_dataset.txt")


