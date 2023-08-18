from Commons.Utils import translation, getEnumTypeFromInt
from Parser.PIIDataTypes import *

'''
Generators: use trained model to generate password guessing
'''


class PIIPatternGenerator:
    """PIIPatternGenerator
    Generate password patterns utilizing classifier
    Input a structure prefix like "N1A2", output the whole structure string
    In every classification, get several results with possibility. Change this variable to adjust the size of dictionary
    Pattern Transformation: "N1A2"(input string) => PIISection of "A2"

    Parse the result of classifier into `PIISection`
    """

    def __init__(self) -> None:
        super().__init__()

    def createSectionFromInt(self, i: int) -> PIISection:
        if i == 0:
            return PIISection(BasicTypes.PIIType.BaseTypes.BeginSymbol, 0)
