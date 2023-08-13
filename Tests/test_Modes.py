from unittest import TestCase
from Commons.Modes import Singleton

class SingletonTest(Singleton):
    pass

class TestSingleton(TestCase):
    def test_get_instance(self):
        s1 = SingletonTest.getInstance()
        s2 = SingletonTest.getInstance()
        print(s1)
        print(s2)



