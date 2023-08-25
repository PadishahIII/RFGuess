from unittest import TestCase
from Generators.GeneralPIIGenerators import *

class TestGeneralPIIPatternGenerator(TestCase):
    def test_get_basic_piipatterns(self):
        generator:GeneralPIIPatternGenerator = GeneralPIIPatternGenerator.getInstance("../save.clf")
        print(generator.getBasicPIIPatterns())
