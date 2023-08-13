from Commons.Utils import Serializer
from Parser.PIIParsers import *


class DatabaseTransformer(metaclass=ABCMeta):
    """Used for intermediate databases

    Facade api to read from database or manipulate database.
    Transform database unit into types directly employed in algorithms.

    Notes:
        - DatabaseTransformers are exclusive for intermediate databases.
        - If you want to work with primitive database, consider `Preprocessor`s in `Parser` package.
    Attributes:
        queryMethods (BasicManipulateMethods): api for specified datatable or dataUnit

    """

    def __init__(self, queryMethods: BasicManipulateMethods) -> None:
        super().__init__()
        self.queryMethods = queryMethods

    def read(self, offset: int = 0, limit: int = 1e7) -> list:
        """
        Read from database and transform unit by calling `transform` method.

        Args:
            offset: offset in datatable
            limit: limit

        Returns:
            list of units after transformation
        """
        units: list[Base] = self.queryMethods.QueryWithLimit(offset=offset, limit=limit)
        l = list()
        for unit in units:
            l.append(self.transform(unit))
        return l

    @abstractmethod
    def transform(self, baseUnit: Base) -> object:
        pass


'''
Transformer for `pwrepresentation` datatable and `representation_frequency_view` dataview.
'''


class PwRepUnit:
    """Unit transformed corresponding to `pwrepresentation` dataunit

    Attributes:
        pwStr (str): password string
        rep (PIIRepresentation): deserialized object
        repStr (str): serialized data
        repHash (str): hash of `repStr`
    """

    def __init__(self, pwStr: str, rep: PIIRepresentation, repStr: str, repHash: str) -> None:
        self.pwStr = pwStr
        self.rep = rep
        self.repStr = repStr
        self.repHash = repHash


class RepFrequencyUnit:
    """Unit transformed corresponding to `representation_frequency_view` dataview

    Attributes:
        repStr (str): serialized data
        repHash (str): hash of `repStr`
        frequency (int): frequency of representation
    """

    def __init__(self, repStr: str, repHash: str, frequency: int) -> None:
        self.repStr = repStr
        self.repHash = repHash
        self.frequency = frequency


class PwRepresentationTransformer(DatabaseTransformer):
    """Transformer for `pwrepresentation` datatable
    Transform representation serialization data into PIIRepresentation object.

    Examples:
        transformer = PwRepresentationTransformer.getInstance()
        units: list[PwRepUnit] = transformer.read()

        pr = PwRepresentationTransformer.getPwRepresentation(pwStr=unit.pwStr, rep=rep)
        transformer.insert(pr)

    """

    def __init__(self, queryMethods: BasicManipulateMethods) -> None:
        super().__init__(queryMethods)

    @classmethod
    def getInstance(cls):
        return PwRepresentationTransformer(RepresentationMethods())

    def transform(self, baseUnit: PwRepresentation) -> PwRepUnit:
        repSe: str = baseUnit.representation
        rep: PIIRepresentation = Serializer.deserialize(repSe)
        unit = PwRepUnit(pwStr=baseUnit.pwStr, rep=rep, repStr=baseUnit.representation,
                         repHash=baseUnit.representationHash)
        return unit

    @classmethod
    def getPwRepresentation(cls, pwStr: str, rep: PIIRepresentation) -> PwRepresentation:
        """
        Parse representation object into `PwRepresentation` object

        Args:
            pwStr: password string
            rep: `PIIRepresentation` object

        Returns:
            PwRepresentation
        """
        repStr = Serializer.serialize(rep)
        pr = PwRepresentation(pwStr=pwStr, repStr=repStr)
        return pr

    @classmethod
    def getRepresentation(cls, pwRep: PwRepresentation) -> PIIRepresentation:
        """
        Convert `PwRepresentation` object into `PIIRepresentation`
        Args:
            pwRep: `PwRepresentation` object

        Returns:
            PIIRepresentation
        """
        repStr = pwRep.representation
        rep: PIIRepresentation = Serializer.deserialize(repStr)
        return rep

    def read(self, offset: int = 0, limit: int = 1e7) -> list[PwRepUnit]:
        return super().read(offset, limit)

    def Insert(self, pr: PwRepresentation):
        self.queryMethods.Insert(pr)

    def SmartInsert(self,pr:PwRepresentation):
        self.queryMethods.SmartInsert(pr)


class RepFrequencyTransformer(DatabaseTransformer):
    """Transformer for `representation_frequency_view` dataview
    No transformation currently.

    Examples:
        transformer = RepFrequencyTransformer.getInstance()
        units: list[RepFrequencyUnit] = transformer.read()
    """

    def __init__(self, queryMethods: BasicManipulateMethods) -> None:
        super().__init__(queryMethods)

    @classmethod
    def getInstance(cls):
        return RepFrequencyTransformer(RepresentationFrequencyMethods())

    def transform(self, baseUnit: RepresentationFrequency) -> RepFrequencyUnit:
        unit = RepFrequencyUnit(repStr=baseUnit.representation, repHash=baseUnit.representationHash,
                                frequency=baseUnit.frequency)
        return unit

    def read(self, offset: int = 0, limit: int = 1e7) -> list[RepFrequencyUnit]:
        return super().read(offset, limit)
