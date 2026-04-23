import tempfile
import unittest
from pathlib import Path

from Generators.DatasetGenerator import DatasetGenerator
from Generators.DictionaryGenerator import DictionaryGenerator


class TestGeneratorRegressions(unittest.TestCase):
    def test_dictionary_generator_does_not_share_default_seed_list(self):
        a = DictionaryGenerator()
        b = DictionaryGenerator()
        a._seeds.append("x")
        self.assertEqual([], b._seeds)

    def test_dataset_generator_limit_is_exact(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "pw.txt"
            file.write_text("a\nb\nc\n", encoding="utf-8")
            gen = DatasetGenerator(str(file), limit=2)
            seen = []
            gen.readFromFile = lambda _: ["a", "b", "c"]
            gen.resolvePassword = seen.append
            gen.save = lambda _: None
            gen._build()
            self.assertEqual(["a", "b"], seen)
