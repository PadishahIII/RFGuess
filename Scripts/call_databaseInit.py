from unittest import TestCase

from Scripts import databaseInit


class Test(TestCase):
    def test_load_dataset(self):
        databaseInit.LoadDataset(r"E:\datasets\2014\2014.12-12306-13m-txt\12306dataset.txt", start=0, limit=10, clear=True)
