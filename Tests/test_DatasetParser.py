from unittest import TestCase

from Parser.DatasetParser import CsvDatasetLoader, ShortBarDatasetLineParser
from Scripts.Utils import CsvHelper


class TestCsvDatasetLoader(TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.loader = CsvDatasetLoader()

    def test_load_dataset(self):
        self.loader.clear_and_load_dataset("test_dataset.txt")

    def test(self):
        lineparser = ShortBarDatasetLineParser()
        result_keys = ['email', 'account', 'name', 'idCard', 'password', 'phoneNum']
        results = list()
        _progress = 0
        _total = 0
        print("Reading...")
        with open("E:\\datasets\\2014\\2014.12-12306-13m-txt\\12306dataset.txt", "r", encoding="gbk", errors="ignore") as f:
            lines = f.readlines()
            for line in lines:
                unit = lineparser.parseline(line)
                results.append(unit)
                _total += 1
        print("Writing...")
        with open("12306_11m.txt", "w", encoding="gbk", errors="ignore") as f:
            f.write(CsvHelper.listToCsvLine(result_keys) + "\n")
            for unit in results:
                line = list()
                line.append(unit.email)
                line.append(unit.account)
                line.append(unit.name)
                line.append(unit.idCard)
                line.append(unit.password)
                line.append(unit.phoneNum)
                s = CsvHelper.listToCsvLine(line)
                f.write(s + "\n")
                _progress += 1
                if _progress % 5000 == 0:
                    print(f"Progress: {_progress}/{_total}, {(_progress / _total):.2f}%")
        print(f"Finished. total:{_total}")
