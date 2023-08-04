from Commons import BasicTypes
from Context.Context import BasicContext

CONTEXT = None


class PIIVector:
    def __init__(self, s: str, piitype: BasicTypes.PIIType, piivalue: int):
        self.str: str = s
        self.piitype: BasicTypes.PIIType = piitype
        self.piivalue: int = piivalue
        self.row = 0
        self.col = 0


class Datagram(BasicContext):
    pass

class Password(BasicContext):
    pass

def parseStrToPIIVector(s: str, ) -> PIIVector:
    pass

