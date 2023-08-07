from abc import  ABCMeta, abstractmethod
from Parser import  BasicDataTypes
from Parser import BasicParsers

'''
Factory: given a dataset, Output feature list and label list, toppest layer
Require:
    1. a Preprocessor to read file and preprocess dataset 
    2. a Parser to tackle every single data unit of the dataset  
'''
class BasicFactory(metaclass=ABCMeta):

    def __init__(self) -> None:
        super().__init__()

