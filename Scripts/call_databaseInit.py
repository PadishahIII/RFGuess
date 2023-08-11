from unittest import TestCase

from Scripts import databaseInit


class Test(TestCase):
    def test_load_dataset(self):
        databaseInit.LoadDataset(r"E:\datasets\2014\2014.12-12306-13m-txt\12306dataset.txt", start=0, limit=-1,
                                 clear=True, update=False)
    def test_query(self):
        units = databaseInit.QueryWithLimit(offset=0,limit=2)
        for u in units:
            print(str(u))
