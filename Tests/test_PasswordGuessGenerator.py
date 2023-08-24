from unittest import TestCase
from Generators.PasswordGuessGenerator import *

class TestGeneralPasswordGenerator(TestCase):
    def test_generate_all_guesses(self):
        self.fail()

    def test_generate_guess_from_pattern(self):
        pii = BasicTypes.PII(account="yhang0607",
                             name="yhangzhongjie",
                             firstName="yhang",
                             givenName="zhong jie",
                             birthday="19820607",
                             phoneNum="13222245678",
                             email="3501111asd11@qq.com",
                             idcardNum="1213213213")
        pw1 = "qwe123ryhang0607yuiyzj123wqer!@#"
        generator:GeneralPasswordGenerator = GeneralPasswordGenerator.getInstance("","passwords.txt",pii, nameFuzz=True)
        patternlist = ['Uwww<N6>a<E2><P1>aa']

        tagDict = generator.tagDict
        for k,v in tagDict.items():
            print(f"{k}({k.value}):{v}")
        print(f"tagdict len:{len(tagDict.keys())}")


        l = generator.generateGuessFromPatternStr(patternlist[0])

        for s in l:
            print(s)
        print(f"len:{len(l)}")

    def test_permutation(self):
        def generate_permutations(mixed_list):
            if len(mixed_list) == 0:
                return [[]]

            first_element = mixed_list[0]
            remaining_elements = mixed_list[1:]

            permutations = []

            for permutation in generate_permutations(remaining_elements):
                if isinstance(first_element, str):
                    permutations.append([first_element] + permutation)
                elif isinstance(first_element, list):
                    for element in first_element:
                        permutations.append([element] + permutation)

            return permutations

        mixed_list = ['a', ['1', '2'], 'b', ['c', 'd'], 'e']
        permutations = generate_permutations(mixed_list)

        print(permutations)
        for permutation in permutations:
            print(''.join(permutation))

