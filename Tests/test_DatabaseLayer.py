from unittest import TestCase

from Commons.DatabaseLayer import *
from Parser.GeneralPIIParsers import *


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

    def test_pw_representation_transformer_read(self):
        transformer = PwRepresentationTransformer.getInstance()
        units: list[PwRepUnit] = transformer.read(offset=0, limit=10)
        parser = PIITagRepresentationStrParser()
        for unit in units:
            rep = parser.representationToStr(unit.rep)
            repStruct = parser.representationToStr(unit.repStructure)
            print(f"pwStr:{unit.pwStr}\nrep:{rep}\nrepStructure:{repStruct}\n")

    def test_rep_frequency_transformer(self):
        transformer = RepFrequencyTransformer.getInstance()
        pwrepTransformer = PwRepresentationTransformer.getInstance()
        repStrTransformer: RepStrPropertyTransformer = RepStrPropertyTransformer()
        repParser = PIITagRepresentationStrParser()
        units: list[RepFrequencyUnit] = transformer.read(offset=0, limit=10)
        priority = 0
        for unit in units:
            repStructure: PIIRepresentation = repStrTransformer.transform(unit)
            s = repParser.representationToStr(repStructure)
            repSample: PIIRepresentation = pwrepTransformer.getStructureSample(unit.repHash)
            ss = repParser.representationToStr(repSample)
            priority += 1
            print(f"{priority}:frequency:{unit.frequency}\nStructure:{s}Sample:{ss}")


class TestRepStrPropertyTransformer(TestCase):
    def test_transform(self):
        self.fail()

    def test_de_transform(self):
        self.fail()


class TestPwRepresentationTransformer(TestCase):
    def test_get_pw_representation(self):
        """
        Two different password have identical representation, representation hash should also be identical

        """
        pii1 = BasicTypes.PII(account="account1",
                              name="yhangzhongjie",
                              firstName="yhang",
                              givenName="zhong jie",
                              birthday="19820607",
                              phoneNum="13222245678",
                              email="3501111asd11@qq.com",
                              idcardNum="1213213213")
        pw1 = "yhang888!@#account1"
        pii2 = BasicTypes.PII(account="account2",
                              name="zhangzhongjie",
                              firstName="zhang",
                              givenName="zhong jie",
                              birthday="19820607",
                              phoneNum="13222245678",
                              email="3501111asd11@qq.com",
                              idcardNum="1213213213")
        pw2 = "zhang777%^&account2"

        piiStructureParser1 = PIIStructureParser(pii1)
        piiStructureParser2 = PIIStructureParser(pii2)

        piiStructure1 = piiStructureParser1.getPwPIIStructure(pw1)
        piiStructure2 = piiStructureParser2.getPwPIIStructure(pw2)

        rep1 = piiStructure1.piiRepresentationList[0]
        rep2 = piiStructure2.piiRepresentationList[0]

        pr1: PwRepresentation = PwRepresentationTransformer.getPwRepresentation(pwStr=pw1, rep=rep1)
        pr2: PwRepresentation = PwRepresentationTransformer.getPwRepresentation(pwStr=pw2, rep=rep2)

        parser = PIITagRepresentationStrParser()

        repStr1 = parser.representationToStr(rep1)
        repStr2 = parser.representationToStr(rep2)

        print(f"rep1:{repStr1}")
        print(f"rep2:{repStr2}")

        print(f"hash1:{pr1.representationHash}")
        print(f"hash2:{pr2.representationHash}")

        assert pr1.representationHash == pr2.representationHash


class TestPwRepFrequencyTransformer(TestCase):
    def test_get_instance(self):
        transformer = PwRepFrequencyTransformer.getInstance()
        transformer2 = PwRepFrequencyTransformer.getInstance()
        print(f"1:{transformer}\n2:{transformer2}")

    def test_transform(self):
        self.fail()

    def test_transform_to_rep_unit(self):
        self.fail()

    def test_read(self):
        self.fail()

    def test_query_with_pw_to_rep_unit(self):
        self.fail()

    def test_query_with_pw(self):
        self.fail()


class TestGeneralPwRepUniqueTransformer(TestCase):
    def test_read_as_parse_unit(self):
        transformer: GeneralPwRepUniqueTransformer = GeneralPwRepUniqueTransformer.getInstance()
        l: list[GeneralPwRepAndStructureUnit] = transformer.readAsParseUnit(offset=0, limit=10)
        tagParser: GeneralPIIRepresentationStrParser = GeneralPIIRepresentationStrParser.getInstance()
        for unit in l:
            rep: GeneralPIIRepresentation = unit.rep
            parser: GeneralPIIParser = GeneralPIIParser(None, unit.pwStr, rep)
            parser.parse()
            featureList = parser.getFeatureList()
            label = parser.getLabelList()
            s = tagParser.representationToStr(rep)
            print(f"{s}\nfeature:{len(featureList)},{featureList}\nlabel:{len(label)},{label}")


class TestPIIUnitTransformer(TestCase):
    def test_get_piiintermediate_with_idrange(self):
        transformer: PIIUnitTransformer = PIIUnitTransformer.getInstance()
        maxId = transformer.getMaxId()
        minId = transformer.getMinId()
        print(f"max:{maxId},min:{minId}")
        end = maxId + 1
        start = maxId - int(0.01 * (maxId - minId))
        l: list[PIIIntermediateUnit] = transformer.getPIIIntermediateWithIdrange(start, end)
        print(f"len:{len(l)}")
        for unit in l:
            print(unit)


class TestPIIUnitTransformer(TestCase):
    def test_transform_intermediate_to_piiand_pw(self):
        transformer: PIIUnitTransformer = PIIUnitTransformer.getInstance()
        minId = transformer.getMinId()
        piiU:PIIUnit = transformer.queryMethods.QueryWithId(minId)
        piiI:PIIIntermediateUnit = transformer.transform(piiU)
        pii,pwStr = transformer.transformIntermediateToPIIAndPw(piiI)
        print(str(pii.__dict__))
        print(pwStr)


