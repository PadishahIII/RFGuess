from unittest import TestCase
from Parser.PIIParsers import *
from Commons.BasicTypes import *
from Parser.PIIDataTypes import *

class TestTag(TestCase):
    def test_create(self):
        tag1 = Tag.create(PIIType.BaseTypes.L,"asd")
        tag2 = Tag.create(PIIType.NameType.FullName,"jason")
        print(tag1.__dict__)
        print(tag2.__dict__)