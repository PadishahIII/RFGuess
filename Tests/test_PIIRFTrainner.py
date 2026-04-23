import os
import unittest
from unittest import TestCase
from Classifiers.PIIRFTrainner import *

@unittest.skipUnless(os.environ.get("RFGUESS_RUN_EXTERNAL_TESTS") == "1",
                     "classifier artifact tests require RFGUESS_RUN_EXTERNAL_TESTS=1")
class TestPIIRFTrainner(TestCase):
    def test_classify_piidatagram_proba(self):
        trainner:PIIRFTrainner = PIIRFTrainner.loadFromFile("../save.clf")
