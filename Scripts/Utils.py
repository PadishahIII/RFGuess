from Commons.DatabaseLayer import RepUnit, PwRepUniqueUnit
from Commons.Utils import Serializer
from Parser.PIIDataTypes import PIIRepresentation


class CsvHelper:
    @classmethod
    def parseline(cls, line: str) -> list:
        """
        Split a line by comma and return a list of values in order
        Args:
            line: string of line

        Returns:
            list: values in order

        """
        if line is None:
            return None
        line = line.strip()
        if len(line) <= 0:
            return None
        l = line.split(",")
        ll = [x.strip() for x in l if x is not None and len(x.strip()) > 0]
        return ll

    @classmethod
    def listToCsvLine(cls, l: list) -> str:
        """
        Join a list of string to a single line with fields separated by comma
        Args:
            l: target string list


        """
        if l is None:
            return ""
        if len(l) <= 0:
            return ""
        return ",".join(l)


def getRepStructurePriorityList(offset: int = 0, limit: int = 1e6) -> list[RepUnit]:
    """
    Get the priority list of representation structure in descending order(list[0] has the max frequency)

    Returns:
        list of representation structures in frequency-descending order
    """
    from Commons.DatabaseLayer import RepFrequencyTransformer, RepUnit

    transformer: RepFrequencyTransformer = RepFrequencyTransformer.getInstance()
    units: list[RepUnit] = transformer.readWithRepUnit(offset=offset, limit=limit)
    return units


def getGeneralRepStructurePriorityList(offset: int = 0, limit: int = 1e6) -> list[RepUnit]:
    """
    Get the priority list of representation structure in descending order(list[0] has the max frequency)

    Returns:
        list of representation structures in frequency-descending order
    """
    from Commons.DatabaseLayer import GeneralRepFrequencyTransformer, RepUnit

    transformer: GeneralRepFrequencyTransformer = GeneralRepFrequencyTransformer.getInstance()
    units: list[RepUnit] = transformer.readWithRepUnit(offset=offset, limit=limit)
    return units


def getAllRepStructureOfPw(pwStr: str) -> list[RepUnit]:
    """
    Get all representation structure of pwStr

    Args:
        pwStr: pwStr

    Returns:
        list of representation structures of pwStr
    """
    from Commons.DatabaseLayer import PwRepFrequencyTransformer

    transformer: PwRepFrequencyTransformer = PwRepFrequencyTransformer.getInstance()
    units = transformer.QueryWithPwToRepUnit(pwStr)
    return units


def getGeneralAllRepStructureOfPw(pwStr: str) -> list[RepUnit]:
    """Get all representation structure of pwStr
    """
    from Commons.DatabaseLayer import GeneralPwRepFrequencyTransformer

    transformer: GeneralPwRepFrequencyTransformer = GeneralPwRepFrequencyTransformer.getInstance()
    units = transformer.QueryWithPwToRepUnit(pwStr)
    return units


def getAllRepStructureDict(offset: int = 0, limit: int = 1e6) -> dict[str, list[RepUnit]]:
    """Get all representation of password in a dict

    """
    from Commons.DatabaseLayer import PwRepFrequencyTransformer, PwRepFrequencyUnit

    transformer: PwRepFrequencyTransformer = PwRepFrequencyTransformer.getInstance()
    units: list[PwRepFrequencyUnit] = transformer.read(offset, limit)
    d: dict[str, list[RepUnit]] = dict()
    for unit in units:
        pwStr = unit.pwStr
        if pwStr in d.keys():
            d[pwStr].append(
                RepUnit(repStructureStr=unit.repStr, repStructureHash=unit.repHash, frequency=unit.frequency))
        else:
            d[pwStr] = list()
            d[pwStr].append(
                RepUnit(repStructureStr=unit.repStr, repStructureHash=unit.repHash, frequency=unit.frequency))

    return d


def getGeneralAllRepStructureDict(offset: int = 0, limit: int = 1e6) -> dict[str, list[RepUnit]]:
    """Get all representation of password in a dict

    """
    from Commons.DatabaseLayer import GeneralPwRepFrequencyTransformer, PwRepFrequencyUnit

    transformer: GeneralPwRepFrequencyTransformer = GeneralPwRepFrequencyTransformer.getInstance()
    units: list[PwRepFrequencyUnit] = transformer.read(offset, limit)
    d: dict[str, list[RepUnit]] = dict()
    for unit in units:
        pwStr = unit.pwStr
        if pwStr in d.keys():
            d[pwStr].append(
                RepUnit(repStructureStr=unit.repStr, repStructureHash=unit.repHash, frequency=unit.frequency))
        else:
            d[pwStr] = list()
            d[pwStr].append(
                RepUnit(repStructureStr=unit.repStr, repStructureHash=unit.repHash, frequency=unit.frequency))

    return d


def getAllPw(offset: int = 0, limit: int = 1e6) -> list[str]:
    from Commons.DatabaseLayer import PwRepresentationTransformer

    transformer: PwRepresentationTransformer = PwRepresentationTransformer.getInstance()
    return transformer.getAllPw(offset, limit)


def getGeneralAllPw(offset: int = 0, limit: int = 1e6) -> list[str]:
    from Commons.DatabaseLayer import GeneralPwRepresentationTransformer

    transformer: GeneralPwRepresentationTransformer = GeneralPwRepresentationTransformer.getInstance()
    return transformer.getAllPw(offset, limit)


def getRepLen(repUnit: RepUnit) -> int:
    repStr = repUnit.repStr
    rep: PIIRepresentation = Serializer.deserialize(repStr)
    return rep.len


def getIntermediateFromRepUnit(pwStr: str, repUnit: RepUnit) -> PwRepUniqueUnit:
    """
    Transform `RepUnit` => `PwRepUniqueUnit`

    """
    from Commons.DatabaseLayer import PwRepresentationTransformer, PwRepresentation

    pwrepTransformer: PwRepresentationTransformer = PwRepresentationTransformer.getInstance()
    unit: PwRepresentation = pwrepTransformer.getDatabaseUnitWithRepStructureHash(pwStr=pwStr,
                                                                                  repStructureHash=repUnit.repHash)
    if unit is None:
        raise Exception(
            f"Database Utils Error: cannot find databaseunit with pwStr:{pwStr}, repStructureHash:{repUnit.repHash}")

    resUnit: PwRepUniqueUnit = PwRepUniqueUnit.create(pwStr=pwStr, repStr=unit.representation,
                                                      repStructureStr=repUnit.repStr, repHash=unit.representationHash,
                                                      repStructureHash=repUnit.repHash)
    return resUnit


def getGeneralIntermediateFromRepUnit(pwStr: str, repUnit: RepUnit) -> PwRepUniqueUnit:
    """
    Transform `RepUnit` => `PwRepUniqueUnit`

    """
    from Commons.DatabaseLayer import GeneralPwRepresentationTransformer
    from Scripts.databaseInit import GeneralPwRepresentation

    pwrepTransformer: GeneralPwRepresentationTransformer = GeneralPwRepresentationTransformer.getInstance()
    unit: GeneralPwRepresentation = pwrepTransformer.getDatabaseUnitWithRepStructureHash(pwStr=pwStr,
                                                                                         repStructureHash=repUnit.repHash)
    if unit is None:
        raise Exception(
            f"Database Utils Error: cannot find databaseunit with pwStr:{pwStr}, repStructureHash:{repUnit.repHash}")

    resUnit: PwRepUniqueUnit = PwRepUniqueUnit.create(pwStr=pwStr, repStr=unit.representation,
                                                      repStructureStr=repUnit.repStr, repHash=unit.representationHash,
                                                      repStructureHash=repUnit.repHash)
    return resUnit
