from Commons.Utils import translation, getEnumTypeFromInt
from Parser.PIIDataTypes import *

'''
Generators: use trained model to generate password guessing
'''


class PIIPatternGenerator:
    """PIIPatternGenerator
    Generate password patterns utilizing classifier

    Parse the result of classifier into `PIISection`
    """

    def __init__(self) -> None:
        super().__init__()

    def createSectionFromInt(self, i: int) -> PIISection:
        if i == 0:
            return PIISection(BasicTypes.PIIType.BaseTypes.BeginSymbol, 0)
