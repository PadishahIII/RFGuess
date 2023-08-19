from unittest import TestCase
from Classifiers.PIIRFTrainner import *

class TestPIIRFTrainner(TestCase):
    def test_classify_piidatagram_proba(self):
        trainner:PIIRFTrainner = PIIRFTrainner.loadFromFile("../save.clf")

