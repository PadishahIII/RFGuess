from unittest import TestCase

from Scripts import databaseInit
from Scripts.databaseInit import *


class TestGeneralPwRepresentation(TestCase):
    a = GeneralPwRepresentation("a", "re", "re")
    pass


class TestBasicManipulateMethods(TestCase):
    def test_query_size(self):
        queryMethods = databaseInit.PIIUnitQueryMethods()
        print(queryMethods.QuerySize())

