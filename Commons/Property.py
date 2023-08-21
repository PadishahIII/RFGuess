'''
Abstract properties
'''
from abc import ABCMeta


class AbstractProperty(metaclass=ABCMeta):

    def __init__(self) -> None:
        super().__init__()


class RepStrProperty(AbstractProperty):
    """
    A abstract class which only contains 'repStr' property, namely representation serialized string
    """

    def __init__(self, repStr: str) -> None:
        super().__init__()
        self.repStr = repStr


class StrProperty(AbstractProperty):
    """A abstract class which contains a field `str` and a method `getStr`

    """

    def __init__(self, s: str) -> None:
        super().__init__()
        self.str = s

    def getStr(self) -> str:
        return self.str
