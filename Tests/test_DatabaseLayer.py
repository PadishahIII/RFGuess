from unittest import TestCase

from Commons.DatabaseLayer import *
from Parser.PIIParsers import PIITagRepresentationStrParser


class Test(TestCase):
    def test_database_transformer(self):
        self.fail()

    def test_pw_rep_unit(self):
        self.fail()

    def test_rep_frequency_unit(self):
        self.fail()

    def test_pw_representation_transformer(self):
        transformer = PwRepresentationTransformer.getInstance()
        units: list[PwRepUnit] = transformer.read()
        for unit in units:
            print({k: v for k, v in unit.__dict__.items() if k != "representation" and k != "repStr"})

    def test_rep_frequency_transformer(self):
        transformer = RepFrequencyTransformer.getInstance()
        repStrTransformer: RepStrPropertyTransformer = RepStrPropertyTransformer()
        repParser = PIITagRepresentationStrParser()
        units: list[RepFrequencyUnit] = transformer.read(offset=0,limit=10)
        priority = 0
        for unit in units:
            rep: PIIRepresentation = repStrTransformer.transform(unit)
            s = repParser.representationToStr(rep)
            priority += 1
            print(f"{priority}:frequency:{unit.frequency}\n{s}")


class TestRepStrPropertyTransformer(TestCase):
    def test_transform(self):
        self.fail()

    def test_de_transform(self):
        self.fail()
