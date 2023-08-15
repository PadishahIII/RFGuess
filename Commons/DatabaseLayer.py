from Commons.Modes import Singleton
from Commons.Utils import Serializer
from Parser.PIIParsers import *

'''
Abstract properties
'''


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


'''
Property Transformers
'''


class BasicPropertyTransformer(Singleton, metaclass=ABCMeta):
    """
    Transform an abstract property into certain type, vice verse.
    Singleton.
    """

    @abstractmethod
    def transform(self, property: AbstractProperty) -> object:
        pass

    @abstractmethod
    def deTransform(self, obj: object) -> AbstractProperty:
        pass


class RepStrPropertyTransformer(BasicPropertyTransformer):

    def transform(self, property: RepStrProperty) -> PIIRepresentation:
        repStr = property.repStr
        rep: PIIRepresentation = Serializer.deserialize(repStr)
        return rep

    def deTransform(self, rep: PIIRepresentation) -> RepStrProperty:
        repStr = Serializer.serialize(rep)
        property = RepStrProperty(repStr)
        return property


'''
Database transformers
'''


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


class PwRepUnit(RepStrProperty):
    """Unit transformed corresponding to `pwrepresentation` dataunit

    Attributes:
        pwStr (str): password string
        rep (PIIRepresentation): deserialized object
        repStructure (PIIRepresentation): deserialized object without exact vector string
        repStr (str): serialized data
        repHash (str): hash of `repStr`
        repStructureHash (str): hash of `repStructure`
    """

    def __init__(self, pwStr: str, rep: PIIRepresentation, repStructure: PIIRepresentation, repStr: str, repHash: str,
                 repStructureHash: str) -> None:
        super().__init__(repStr)
        self.pwStr = pwStr
        self.rep: PIIRepresentation = rep
        self.repStructure: PIIRepresentation = repStructure
        self.repHash = repHash
        self.repStructureHash = repStructureHash


class RepFrequencyUnit(RepStrProperty):
    """Unit transformed corresponding to `representation_frequency_view` dataview

    Attributes:
        repStr (str): serialized data of representation structure
        repHash (str): hash of `repStr`
        frequency (int): frequency of representation
    """

    def __init__(self, repStr: str, repHash: str, frequency: int) -> None:
        super().__init__(repStr)
        self.repHash = repHash
        self.frequency = frequency


class PwRepresentationTransformer(DatabaseTransformer):
    """Transformer for `pwrepresentation` datatable
    Transform representation serialization data into PIIRepresentation object.

    Examples:
        # get deserialized unit with PIIRepresentation object
        transformer = PwRepresentationTransformer.getInstance()
        units: list[PwRepUnit] = transformer.read()

        # build database, transform PIIRepresentation into database unit
        pr = PwRepresentationTransformer.getPwRepresentation(pwStr=unit.pwStr, rep=rep)
        transformer.insert(pr)

    """

    def __init__(self, queryMethods: BasicManipulateMethods) -> None:
        super().__init__(queryMethods)
        self.queryMethods: RepresentationMethods = queryMethods

    @classmethod
    def getInstance(cls):
        return PwRepresentationTransformer(RepresentationMethods())

    def transform(self, baseUnit: PwRepresentation) -> PwRepUnit:
        repSe: str = baseUnit.representation
        repStrucSe: str = baseUnit.representationStructure
        rep: PIIRepresentation = Serializer.deserialize(repSe)
        repStruc: PIIRepresentation = Serializer.deserialize(repStrucSe)
        unit = PwRepUnit(pwStr=baseUnit.pwStr, rep=rep, repStr=baseUnit.representation,
                         repHash=baseUnit.representationHash, repStructure=repStruc,
                         repStructureHash=baseUnit.representationStructureHash)
        return unit

    @classmethod
    def getPwRepresentation(cls, pwStr: str, rep: PIIRepresentation) -> PwRepresentation:
        """Build database phase
        Parse representation object into `PwRepresentation` object

        Args:
            pwStr: password string
            rep: `PIIRepresentation` object

        Returns:
            PwRepresentation
        """
        repStr = Serializer.serialize(rep)
        newRep: PIIRepresentation = copy(rep)
        # vector str(part of pwStr) will be excluded in hash calculation
        for vector in newRep.piiVectorList:
            vector.str = ""
        repStructure = Serializer.serialize(newRep)
        pr = PwRepresentation(pwStr=pwStr, repStr=repStr, repStruc=repStructure)
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
        """
        Read from database and transform unit into `PwRepUnit`

        Args:
            offset:
            limit:

        Returns:

        """
        return super().read(offset, limit)

    def Insert(self, pr: PwRepresentation):
        self.queryMethods.Insert(pr)

    def SmartInsert(self, pr: PwRepresentation):
        self.queryMethods.SmartInsert(pr)

    def getStructureSample(self, hashStr: str) -> PIIRepresentation:
        """
        Input the hash of representation structure, return a sample representation(with pwStr section not empty)

        Args:
            hashStr: the hash of representation structure

        Returns:
            a sample of the representation structure

        """
        units: list[PwRepresentation] = self.queryMethods.QueryWithRepresentationStructureHash(repStructureHash=hashStr,
                                                                                               offset=0, limit=1)
        if len(units) <= 0:
            return None
        else:
            unit = units[0]
            return self.getRepresentation(unit)


class RepFrequencyTransformer(DatabaseTransformer):
    """Transformer for `representation_frequency_view` dataview
    No transformation currently.

    Examples:
        transformer = RepFrequencyTransformer.getInstance()
        units: list[RepFrequencyUnit] = transformer.read()
    """

    def __init__(self, queryMethods: BasicManipulateMethods) -> None:
        super().__init__(queryMethods)
        self.queryMethods: RepresentationFrequencyMethods = queryMethods

    @classmethod
    def getInstance(cls):
        return RepFrequencyTransformer(RepresentationFrequencyMethods())

    def transform(self, baseUnit: RepresentationFrequency) -> RepFrequencyUnit:
        unit = RepFrequencyUnit(repStr=baseUnit.representationStructure, repHash=baseUnit.representationStructureHash,
                                frequency=baseUnit.frequency)
        return unit

    def read(self, offset: int = 0, limit: int = 1e7) -> list[RepFrequencyUnit]:
        """
        Get frequency priority queue

        """
        units: list[RepresentationFrequency] = self.queryMethods.QueryAllWithFrequencyDesc(offset=offset, limit=limit)
        l = list()
        for unit in units:
            l.append(self.transform(unit))
        return l
