from Commons.Utils import Serializer
from Scripts.databaseInit import *

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

from Commons.Modes import Singleton


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


from Parser.PIIDataTypes import *


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
Transformer for `pwrepresentation` datatable and `representation_frequency` dataview.
'''


class PwRepUniqueUnit(RepStrProperty):
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
    """Unit transformed corresponding to `representation_frequency` dataview

    Attributes:
        repStr (str): serialized data of representation structure
        repHash (str): hash of `repStr`
        frequency (int): frequency of representation
    """

    def __init__(self, repStr: str, repHash: str, frequency: int) -> None:
        super().__init__(repStr)
        self.repHash = repHash
        self.frequency = frequency

    def __str__(self) -> str:
        return str(self.__dict__)


class PwRepFrequencyUnit(RepStrProperty):
    """Unit transformed corresponding to `representation_frequency` dataview

    Attributes:
        pwStr (str): password string
        repStr (str): serialized data of representation structure
        repHash (str): hash of `repStr`
        frequency (int): frequency of representation
    """

    def __init__(self, pwStr: str, repStructureStr: str, repStructureHash: str, frequency: int) -> None:
        super().__init__(repStructureStr)
        self.pwStr = pwStr
        self.repHash = repStructureHash
        self.frequency = frequency


class PwRepresentationTransformer(DatabaseTransformer, Singleton):
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
        return super().getInstance(RepresentationMethods())

    def transform(self, baseUnit: PwRepresentation) -> PwRepUniqueUnit:
        repSe: str = baseUnit.representation
        repStrucSe: str = baseUnit.representationStructure
        rep: PIIRepresentation = Serializer.deserialize(repSe)
        repStruc: PIIRepresentation = Serializer.deserialize(repStrucSe)
        unit = PwRepUniqueUnit(pwStr=baseUnit.pwStr, rep=rep, repStr=baseUnit.representation,
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

    def read(self, offset: int = 0, limit: int = 1e7) -> list[PwRepUniqueUnit]:
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

    def getAllPw(self, offset: int = 0, limit: int = 1e6) -> list[str]:
        """
        Get All password string
        Returns:

        """
        return self.queryMethods.QueryAllPw(offset, limit)

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


class RepFrequencyTransformer(DatabaseTransformer, Singleton):
    """Transformer for `representation_frequency` dataview
    Transformation: RepresentationFrequency(base unit) => RepFrequencyUnit => RepUnit(parse unit)

    Examples:
        transformer = RepFrequencyTransformer.getInstance()
        units: list[RepFrequencyUnit] = transformer.read()
    """

    def __init__(self, queryMethods: BasicManipulateMethods) -> None:
        super().__init__(queryMethods)
        self.queryMethods: RepresentationFrequencyMethods = queryMethods

    @classmethod
    def getInstance(cls):
        return super().getInstance(RepresentationFrequencyMethods())

    def transform(self, baseUnit: RepresentationFrequency) -> RepFrequencyUnit:
        unit = RepFrequencyUnit(repStr=baseUnit.representationStructure, repHash=baseUnit.representationStructureHash,
                                frequency=baseUnit.frequency)
        return unit

    def transformToRepUnit(self, baseUnit: RepresentationFrequency) -> RepUnit:
        unit = RepUnit(repStructureStr=baseUnit.representationStructure,
                       repStructureHash=baseUnit.representationStructureHash, frequency=baseUnit.frequency)
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

    def readWithRepUnit(self, offset: int = 0, limit: int = 1e7) -> list[RepUnit]:
        """
        Get frequency priority queue in descending order

        """
        units: list[RepresentationFrequency] = self.queryMethods.QueryAllWithFrequencyDesc(offset=offset, limit=limit)
        l = list()
        for unit in units:
            l.append(self.transformToRepUnit(unit))
        return l


class PwRepFrequencyTransformer(DatabaseTransformer, Singleton):
    """Transformer for `pwrepresentation_frequency` dataview
    Transformation: PwRepresentationFrequency(base unit) => RepFrequencyUnit => RepUnit(parse unit)

    Examples:
        transformer = PwRepFrequencyTransformer.getInstance()
        units: list[PwRepFrequencyUnit] = transformer.read()
    """

    def __init__(self, queryMethods: BasicManipulateMethods) -> None:
        super().__init__(queryMethods)
        self.queryMethods: PwRepresentationFrequencyMethods = queryMethods

    @classmethod
    def getInstance(cls):
        return super().getInstance(PwRepresentationFrequencyMethods())

    def transform(self, baseUnit: PwRepresentationFrequency) -> PwRepFrequencyUnit:
        unit = PwRepFrequencyUnit(repStructureStr=baseUnit.representationStructure,
                                  repStructureHash=baseUnit.representationStructureHash,
                                  frequency=baseUnit.frequency, pwStr=baseUnit.pwStr)
        return unit

    def transformToRepUnit(self, baseUnit: PwRepresentationFrequency) -> RepUnit:
        unit = RepUnit(repStructureStr=baseUnit.representationStructure,
                       repStructureHash=baseUnit.representationStructureHash,
                       frequency=baseUnit.frequency)
        return unit

    def getRepresentation(self, unit: RepUnit) -> PIIRepresentation:
        """
        Convert `RepUnit` into `PIIRepresentation`

        """
        repStr = unit.repStr
        rep: PIIRepresentation = Serializer.deserialize(repStr)
        return rep

    def read(self, offset: int = 0, limit: int = 1e7) -> list[PwRepFrequencyUnit]:
        """
        Get frequency priority queue

        """
        units: list[RepresentationFrequency] = self.queryMethods.QueryWithLimit(offset=offset, limit=limit)
        l = list()
        for unit in units:
            l.append(self.transform(unit))
        return l

    def QueryWithPwToRepUnit(self, pwStr: str) -> list[RepUnit]:
        units: list[PwRepresentationFrequency] = self.queryMethods.QueryWithPw(pwStr=pwStr)
        l = list(map(lambda x: self.transformToRepUnit(x), units))
        return l

    def QueryWithPw(self, pwStr: str) -> list[PwRepFrequencyUnit]:
        units: list[PwRepresentationFrequency] = self.queryMethods.QueryWithPw(pwStr=pwStr)
        l = list(map(lambda x: self.transform(x), units))
        return l


class PwRepUniqueTransformer(DatabaseTransformer, Singleton):
    """Transformer for `pwrepresentation_unique` datatable
    Transformation: PwRepUnique(database unit) => PwRepUniqueUnit => PwRepAndStructureUnit(parse unit)

    Examples:
        # get deserialized unit with PIIRepresentation object
        transformer = PwRepUniqueTransformer.getInstance()
        units: list[PwRepUnit] = transformer.read()

        # build database, transform PIIRepresentation into database unit
        pr = PwRepUniqueTransformer.getPwRepresentation(pwStr=unit.pwStr, rep=rep)
        transformer.insert(pr)

    """

    def __init__(self, queryMethods: BasicManipulateMethods) -> None:
        super().__init__(queryMethods)
        self.queryMethods: PwRepUniqueMethods = queryMethods

    @classmethod
    def getInstance(cls):
        return super().getInstance(PwRepUniqueMethods())

    def transform(self, baseUnit: PwRepUnique) -> PwRepUniqueUnit:
        repSe: str = baseUnit.representation
        repStrucSe: str = baseUnit.representationStructure
        rep: PIIRepresentation = Serializer.deserialize(repSe)
        repStruc: PIIRepresentation = Serializer.deserialize(repStrucSe)
        unit = PwRepUniqueUnit(pwStr=baseUnit.pwStr, rep=rep, repStr=baseUnit.representation,
                               repHash=baseUnit.representationHash, repStructure=repStruc,
                               repStructureHash=baseUnit.representationStructureHash)
        return unit

    def deTransform(self, unit: PwRepAndStructureUnit) -> PwRepUnique:
        """
        Transformer used when writing to database.
        PwRepAndStructureUnit(parse unit) => PwRepUnique(database unit)

        """
        rep = unit.rep
        repStruct = unit.repStructure

        repStr = Serializer.serialize(rep)
        repStruct = Serializer.serialize(repStruct)

        baseUnit: PwRepUnique = PwRepUnique(pwStr=unit.pwStr, repStr=repStr, repStruc=repStruct)
        return baseUnit

    def InsertPwRepAndStructureUnit(self, unit: PwRepAndStructureUnit):
        """
        Insert `PwRepAndStructureUnit`(parse unit) into database

        """
        baseUnit = self.deTransform(unit)
        self.Insert(baseUnit)

    @classmethod
    def getRepresentation(cls, pwRep: PwRepUnique) -> PIIRepresentation:
        """
        Convert `PwRepUnique` object into `PIIRepresentation`
        Args:
            pwRep: `PwRepUnique` object

        Returns:
            PIIRepresentation
        """
        repStr = pwRep.representation
        rep: PIIRepresentation = Serializer.deserialize(repStr)
        return rep

    def read(self, offset: int = 0, limit: int = 1e7) -> list[PwRepUniqueUnit]:
        """
        Read from database and transform unit into `PwRepUnit`

        Args:
            offset:
            limit:

        Returns:

        """
        return super().read(offset, limit)

    def Insert(self, pr: PwRepUnique):
        self.queryMethods.Insert(pr)

    def SmartInsert(self, pr: PwRepUnique):
        self.queryMethods.SmartInsert(pr)

    def getAllPw(self, offset: int = 0, limit: int = 1e6) -> list[str]:
        """
        Get All password string

        """
        return self.queryMethods.QueryAllPw(offset, limit)
