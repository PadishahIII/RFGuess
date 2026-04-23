import os
import unittest
from unittest import TestCase
from Generators.GeneralPIIGenerators import *

@unittest.skipUnless(os.environ.get("RFGUESS_RUN_EXTERNAL_TESTS") == "1",
                     "classifier artifact tests require RFGUESS_RUN_EXTERNAL_TESTS=1")
class TestGeneralPIIPatternGenerator(TestCase):
    def test_get_basic_piipatterns(self):
        generator:GeneralPIIPatternGenerator = GeneralPIIPatternGenerator.getInstance("../save.clf")
        print(generator.getBasicPIIPatterns())
