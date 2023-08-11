from unittest import TestCase

from Commons import BasicTypes
from Parser.PIIDataTypes import PIIDataSet,PIIDataUnit


class Test(TestCase):
    def test_piidata_unit(self):
        self.fail()

    def test_piidata_set(self):
        pii = BasicTypes.PII(email="274667266@qq.com",
                             account="6837605",
                             idcardNum="332522198705040011",
                             phoneNum="15068860664",
                             name="郑一峰",
                             firstName="zheng",
                             givenName="yi feng",
                             birthday="19870504")
        pwStr = "aaaa"
        dataset = PIIDataSet()
        dataset.generateKeyList(pii)
        unit = dataset.createUnit(dataset.getValueList(pii,pwStr))
        dataset.push(unit)
        for u in iter(dataset):
            print(str(u))



    def test_piidata_set_exception(self):
        self.fail()

    def test_piisection(self):
        self.fail()

    def test_piidatagram(self):
        self.fail()
