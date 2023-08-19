import joblib

from Commons.Utils import translation, getEnumTypeFromInt
from Parser.PIIDataTypes import *
from Parser.PIIParsers import *
import  os
from Classifiers.PIIRFTrainner import PIIRFTrainner

'''
Generators: use trained model to generate password guessing
'''


class PIIPatternGenerator:
    """PIIPatternGenerator
    Generate password patterns utilizing classifier
    Input a structure prefix like "N1A2", output the whole structure string
    In every classification, get several results with possibility. Change this variable to adjust the size of dictionary
    Pattern Transformation: "N1A2"(input string) => PIIDatagram

    Parse the result of classifier into `PIISection`
    """

    def __init__(self, model:PIIRFTrainner) -> None:
        super().__init__()
        self.factory:PIISectionFactory = PIISectionFactory.getInstance()
        self.clf:PIIRFTrainner = model

    def getInstance(self,clfPath):
        if not os.path.exists(clfPath):
            raise PIIPatternGeneratorException(f"Error: invalid classifier path: {clfPath}")
        clf = joblib.load(clfPath)
        t = PIIRFTrainner.getInstance()
        t.setClf(clf)
        return PIIPatternGenerator(model=t)




class PIIPatternGeneratorException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)