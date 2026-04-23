import os
import unittest
from unittest import TestCase

from Scripts import databaseInit
from Scripts.databaseInit import *


class TestGeneralPwRepresentation(TestCase):
    a = GeneralPwRepresentation("a", "re", "re")
    pass


@unittest.skipUnless(os.environ.get("RFGUESS_RUN_DB_TESTS") == "1",
                     "database integration tests require RFGUESS_RUN_DB_TESTS=1")
class TestBasicManipulateMethods(TestCase):
    def test_query_size(self):
        queryMethods = databaseInit.PIIUnitQueryMethods()
        print(queryMethods.QuerySize())

    def test_general_pw_rep_unique(self):
        queryMethod = databaseInit.GeneralPwRepUniqueMethods()
        print(queryMethod.QueryWithLimit(0,10))
