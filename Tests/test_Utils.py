from unittest import TestCase

from Commons.DatabaseLayer import *
from Parser.PIIParsers import *
from Scripts import Utils


class Test(TestCase):
    def test_get_rep_structure_priority_list(self):
        units: list[RepFrequencyUnit] = Utils.getRepStructurePriorityList(offset=0, limit=10)
        for u in units:
            print(u)

    def test_get_all_rep_structure_of_pw(self):
        self.fail()
