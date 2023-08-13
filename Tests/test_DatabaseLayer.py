from unittest import TestCase

from Commons.DatabaseLayer import *


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
        units: list[RepFrequencyUnit] = transformer.read()
        for unit in units:
            print(unit.__dict__)
