import ast
import inspect
import textwrap
from unittest import TestCase

from Scripts import main_General_PII_Mode


class TestBuildDatabase(TestCase):
    def test_build_general_representation_table_does_not_return_inside_rep_loop(self):
        source = inspect.getsource(main_General_PII_Mode.BuildDatabase.buildGeneralPwRepresentationTable)
        tree = ast.parse(textwrap.dedent(source))

        function_def = tree.body[0]
        returns_inside_rep_loop = [
            node
            for node in ast.walk(function_def)
            if isinstance(node, ast.For)
            and isinstance(node.target, ast.Name)
            and node.target.id == "rep"
            and any(isinstance(child, ast.Return) for child in ast.walk(node))
        ]

        self.assertEqual([], returns_inside_rep_loop)
