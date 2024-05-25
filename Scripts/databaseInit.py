import binascii
import hashlib
import logging
import re
from abc import ABCMeta, abstractmethod

import sqlalchemy
from sqlalchemy import Column, Integer, String, text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, validates, scoped_session

import Parser.Config as Config
from Commons import pinyinUtils
from Parser.Config import TableNames

Base = declarative_base()
emailRst = re.compile(r".+?@.+?")
lineRst = re.compile(
    r"(?P<email>.+?@.+?)-{3,10}(?P<account>.+?)-{3,10}(?P<name>.+?)-{3,10}(?P<idCard>.+?)-{3,10}(?P<password>.+?)-{3,10}(?P<phoneNum>.+?)-{3,10}.*")

logging.basicConfig()  # filename="database.log"
logger = logging.getLogger("databaseInit")
logger.setLevel(logging.INFO)

engine = sqlalchemy.create_engine(Config.DatabaseUrl)

sessionFactory = sessionmaker(bind=engine)
Session = scoped_session(sessionFactory)


def update_engine(url: str):
    """Re-define the engine and session with the new url"""
    global engine, sessionFactory, Session
    engine = sqlalchemy.create_engine(url)
    sessionFactory = sessionmaker(bind=engine)
    Session = scoped_session(sessionFactory)


class PIIUnit(Base):
    __tablename__ = TableNames.PII
    attributes = ['email', 'account', 'name', 'idCard', 'phoneNum', 'password', 'fullName']

    id = Column(Integer, primary_key=True)
    email = Column(String, default='')
    account = Column(String, default='')
    name = Column(String, default='')
    idCard = Column(String, default='')
    phoneNum = Column(String, default='')
    password = Column(String, default='')
    fullName = Column(String, default='')

    def __init__(self, email, account, name, idCard, phoneNum, password, fullName=None):
        """

        Args:
            email:
            account:
            name: Name in Chinese
            idCard:
            phoneNum:
            password:
            fullName: Name in Pinyin with format "Zhang Zhong jie"
        """
        super().__init__()
        self.email = email
        self.account = account
        self.name = name
        self.idCard = idCard
        self.phoneNum = phoneNum
        self.password = password
        self.fullName = fullName

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def update(cls, a, b):
        """
        Update PIIUnit a with b

        Args:
            a: target unit to update
            b:
        """
        a.email = b.email
        a.account = b.account
        a.name = b.name
        a.idCard = b.idCard
        a.phoneNum = b.phoneNum
        a.password = b.password
        a.fullName = b.fullName

    # @validates('email')
    # def validateEmail(self, key, email):
    #     if not email:
    #         raise ValueError(f"Email is required")
    #     if not emailRst.match(email):
    #         raise ValueError(f"Invail email: {email}")
    #     return email
    #
    # @validates('account')
    # def validateAccount(self, key, account):
    #     if not account:
    #         raise ValueError(f"Account is required")
    #     return account
    #
    # @validates('name')
    # def validateName(self, key, name):
    #     if not name:
    #         raise ValueError(f"Name is required")
    #     return name
    #
    # @validates('idCard')
    # def validateIdCard(self, key, idCard):
    #     if not idCard:
    #         raise ValueError(f"IdCard is required")
    #     return idCard
    #
    # @validates('phoneNum')
    # def validatePhoneNum(self, key, phoneNum):
    #     if not phoneNum:
    #         raise ValueError(f"PhoneNum is required")
    #     if not str(phoneNum).isdigit():
    #         raise ValueError(f"Invaild phoneNum: {phoneNum}")
    #     return phoneNum
    #
    # @validates('password')
    # def validatePassword(self, key, password):
    #     if not password:
    #         raise ValueError(f"Password is required")
    #     return password


'''
Basic database approach
'''


class BasicManipulateMethods(metaclass=ABCMeta):
    """Basic query methods

    """

    def __init__(self, entityCls):
        """

        Args:
            entityCls: class of entity
        """
        self.entityCls = entityCls

    @abstractmethod
    def CheckExist(self, unit: Base) -> bool:
        pass

    @abstractmethod
    def Update(self, unit: Base):
        pass

    def Insert(self, obj: Base):
        with Session() as session:
            session.add(obj)
            session.commit()

    def QuerySize(self) -> int:
        """Get number of data items
        """
        with Session() as session:
            num = session.query(self.entityCls).count()
            return num

    def QueryAll(self) -> list[Base]:
        with Session() as session:
            units = session.query(self.entityCls).all()
            return units

    def QueryWithLimit(self, offset: int = 0, limit: int = 1e6) -> list[Base]:
        with Session() as session:
            units = session.query(self.entityCls).offset(offset).limit(limit).all()
            return units

    def DeleteAll(self, ):
        with Session() as session:
            session.query(self.entityCls).delete()
            # units = self.QueryAll()
            # for unit in units:
            #     session.delete(unit)
            session.commit()

    def SmartInsert(self, unit: Base, update: bool = False) -> bool:
        """
        Insert unit to table if not exists, else update units with the same `name`

        Args:
            unit:
            update: if set to True, update the unit when existing, else ignore.
        Returns:
            bool: if really updated
        """
        if self.CheckExist(unit):
            if update:
                self.Update(unit)
                return True
        else:
            self.Insert(unit)
            return True
        return False


class BaseQueryMethods(BasicManipulateMethods):
    """With default abstract methods
    """

    def CheckExist(self, unit: Base) -> bool:
        return False

    def Update(self, unit: Base):
        pass


'''
PIIUnit query methods
'''


class PIIUnitQueryMethods(BasicManipulateMethods):
    def __init__(self):
        super().__init__(PIIUnit)

    def QueryWithId(self, id: int) -> PIIUnit:
        with Session() as session:
            unit = session.query(self.entityCls).filter_by(id=id).first()
            return unit

    def QueryIdRange(self) -> (int, int):
        """Get maxid and minid

        Returns:
            (int,int) : maxId, minId
        """
        with Session() as session:
            maxId = session.query(func.max(self.entityCls.id)).scalar()
            minId = session.query(func.min(self.entityCls.id)).scalar()
            return maxId, minId

    def UpdateFullName(self, name, fullname):
        with Session() as session:
            units = session.query(PIIUnit).filter_by(name=name).all()
            for unit in units:
                unit.fullName = fullname
            session.commit()

    def Update(self, unit: PIIUnit):
        """
          Update all units with the same `name` as unit given

          Args:
              unit:
              session_:
          """
        with Session() as session:
            if self.CheckExist(unit):
                units = session.query(PIIUnit).filter_by(name=unit.name).all()
                for u in units:
                    PIIUnit.update(u, unit)

    def CheckExist(self, unit: PIIUnit) -> bool:
        with Session() as session:
            units = session.query(PIIUnit).filter_by(account=unit.account).all()
            if not units or len(units) <= 0:
                return False
            else:
                return True


'''
Main logics
'''


class ProgressTracker:
    load_pii_data_progress = 0  # for outer progress tracking
    load_pii_data_limit = 100


def BuildFullName():
    """
    Update the fullName field of all table items.
    """
    queryMethods = PIIUnitQueryMethods()
    units = queryMethods.QueryAll()
    nameList = [unit.name for unit in units if unit]
    for name in nameList:
        fullName = pinyinUtils.getFullName(name)
        if fullName and len(fullName) > 0:
            queryMethods.UpdateFullName(name, fullName)


def UnitGenerator(offset: int = 0, limit: int = 1e6):
    queryMethods = PIIUnitQueryMethods()
    units = queryMethods.QueryWithLimit(offset, limit)
    for unit in units:
        yield unit


'''
Password representation unit
'''


class PwRepresentation(Base):
    __tablename__ = TableNames.pwrepresentation

    id = Column(Integer, primary_key=True)
    pwStr = Column(String)
    representation = Column(String)
    representationStructure = Column(String)
    representationHash = Column(String)
    representationStructureHash = Column(String)
    hash = Column(String)

    def __init__(self, pwStr: str, repStr: str, repStruc: str):
        super().__init__()
        self.pwStr = pwStr
        self.representation = repStr
        self.representationStructure = repStruc
        self.representationHash = PwRepresentation.getHash(self.representation)
        self.representationStructureHash = PwRepresentation.getHash(self.representationStructure)
        self.hash = PwRepresentation.getHash(self.pwStr + self.representation)

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def getHash(cls, s: str) -> str:
        """
        Get hash of representation

        Args:
            s:

        Returns:

        """
        hashB = hashlib.md5(s.encode("utf8")).digest()
        hashS = binascii.hexlify(hashB).decode("utf8")
        return hashS

    @classmethod
    def update(cls, a, b):
        """
        Update a with b

        Args:
            a:
            b:

        Returns:

        """
        a.pwStr = b.pwStr
        a.representation = b.representation
        a.representationStructure = b.representationStructure
        a.representationStructureHash = b.representationStructureHash
        a.representationHash = b.representationHash
        a.hash = b.hash

    @validates('pwStr')
    def validatePwStr(self, key, pwStr):
        if len(pwStr) <= 0:
            raise ValueError(f"Invalid pwStr: cannot be empty")
        return pwStr

    @validates('representation')
    def validateRep(self, key, repStr):
        if len(repStr) <= 0:
            raise ValueError(f"Invalid representation string: cannot be empty")
        return repStr

    @validates('representationHash')
    def validateRep(self, key, hashStr):
        if len(hashStr) <= 0:
            raise ValueError(f"Invalid representation hash: cannot be empty")
        return hashStr

    @validates('representationStructureHash')
    def validateRep(self, key, hashStr):
        if len(hashStr) <= 0:
            raise ValueError(f"Invalid representation hash: cannot be empty")
        return hashStr

    @validates('representationStructure')
    def validateRep(self, key, repStruc):
        if len(repStruc) <= 0:
            raise ValueError(f"Invalid representation hash: cannot be empty")
        return repStruc

    @validates('hash')
    def validateRep(self, key, hashStr):
        if len(hashStr) <= 0:
            raise ValueError(f"Invalid whole hash: cannot be empty")
        return hashStr


class RepresentationMethods(BasicManipulateMethods):

    def __init__(self):
        super().__init__(PwRepresentation)

    def QueryWithPwStr(self, pwStr: str) -> list[PwRepresentation]:
        with Session() as session:
            units = session.query(self.entityCls).filter_by(pwStr=pwStr).all()
            return units

    def QueryAllPw(self, offset: int = 0, limit: int = 1e6) -> list[str]:
        with Session() as session:
            resultTuple: list[Column] = session.query(PwRepresentation.pwStr).distinct().offset(offset).limit(
                limit).all()  # list[tuple]
            result = list(map(lambda x: x[0], resultTuple))
            return result

    def QueryWithRepresentationHash(self, repHash: str) -> list[PwRepresentation]:
        """
        Query with representation's hash
        Args:
            repHash:

        Returns:

        """
        with Session() as session:
            units = session.query(self.entityCls).filter_by(representationHash=repHash).all()
            return units

    def QueryWithRepresentationStructureHash(self, repStructureHash: str, offset: int = 0, limit: int = 1e6) -> list[
        PwRepresentation]:
        """
        Query with representation structure
        Args:
            repStructure:

        Returns:

        """
        with Session() as session:
            units = session.query(self.entityCls).filter_by(representationStructureHash=repStructureHash).offset(
                offset).limit(limit).all()
            return units

    def QueryWithWholeHash(self, hashStr: str) -> list[PwRepresentation]:
        """
        Query with the hash of pwStr+representation

        Args:
            hashStr:

        Returns:

        """
        with Session() as session:
            units = session.query(self.entityCls).filter_by(hash=hashStr).all()
            return units

    def QueryWithPwRepStructureHash(self, pwStr: str, repStructureHash: str) -> PwRepresentation:
        with Session() as session:
            unit = session.query(self.entityCls).filter_by(representationStructureHash=repStructureHash,
                                                           pwStr=pwStr).first()
            return unit

    def Update(self, unit: PwRepresentation):
        """
        Update all units with the same `pwStr` as unit given

        Args:
            unit:

        Returns:

        """
        with Session() as session:
            if self.CheckExist(unit):
                units = session.query(PwRepresentation).filter_by(pwStr=unit.pwStr).all()
                for u in units:
                    PwRepresentation.update(u, unit)

    def CheckExist(self, unit: PwRepresentation) -> bool:
        """
        Check unit if exists in terms of hash of pwStr+representation namely `hash` field.

        Args:
            unit:

        Returns:

        """
        with Session() as session:
            units = session.query(PwRepresentation).filter_by(hash=unit.hash).all()
            if not units or len(units) <= 0:
                return False
            else:
                return True


'''
Representation Frequency Unit and QueryMethod
'''


class RepresentationFrequency(Base):
    __tablename__ = TableNames.representation_frequency

    frequency = Column(Integer)
    representationStructureHash = Column(String, primary_key=True)
    representationStructure = Column(String)

    def __init__(self, frequency: int, repHash: str, repStr: str):
        """

        Args:
            frequency:
            repHash:
            repStr: serialized representation
        """
        super().__init__()
        self.frequency = frequency
        self.representationHash = repHash
        self.representation = repStr

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def update(cls, a, b):
        """
        Update a with b

        """
        a.frequency = b.frequency
        a.representationHash = b.representationHash
        a.representation = b.representation

    @validates('frequency')
    def validateFrequency(self, key, fre: int):
        if fre <= 0:
            raise ValueError(f"Invalid frequency: must larger than 0")
        return fre

    @validates("representationHash")
    def validateRepHash(self, key, h: str):
        if len(h) <= 0:
            raise ValueError(f"Invalid representation hash: cannot be empty")
        return h

    @validates("representation")
    def validateRepStr(self, key, h: str):
        if len(h) <= 0:
            raise ValueError(f"Invalid representation serialized data: cannot be empty")
        return h


class RepresentationFrequencyMethods(BasicManipulateMethods):
    def __init__(self):
        super().__init__(RepresentationFrequency)

    def QueryWithRepStructureHash(self, hashStr: str) -> list[RepresentationFrequency]:
        with Session() as session:
            units = session.query(self.entityCls).filter_by(representationStructureHash=hashStr).all()
            return units

    def QueryAllWithFrequencyDesc(self, offset: int = 0, limit: int = 1e7) -> list[RepresentationFrequency]:
        """
        Get all units with frequency in desc order

        """
        with Session() as session:
            units = session.query(self.entityCls).distinct().order_by(
                RepresentationFrequency.frequency.desc()).offset(offset).limit(limit)
            return units

    def Update(self, unit):
        pass

    def CheckExist(self, unit: RepresentationFrequency) -> bool:
        """
        Check unit if exists in terms of `representationHash`

        Args:
            unit:

        Returns:

        """
        with Session() as session:
            units = session.query(self.entityCls).filter_by(representationHash=unit.representationHash).all()
            if not units or len(units) <= 0:
                return False
            else:
                return True


class PwRepresentationFrequency(Base):
    __tablename__ = TableNames.pwrepresentation_frequency

    id = Column(Integer, primary_key=True)
    pwStr = Column(String)
    frequency = Column(Integer)
    representationStructureHash = Column(String)
    representationStructure = Column(String)

    def __init__(self, pwStr: str, frequency: int, repHash: str, repStr: str):
        """

        Args:
            frequency:
            repHash:
            repStr: serialized representation
        """
        super().__init__()
        self.pwStr = pwStr
        self.frequency = frequency
        self.representationHash = repHash
        self.representation = repStr

    def __str__(self):
        return str(self.__dict__)


class PwRepresentationFrequencyMethods(BasicManipulateMethods):
    def __init__(self):
        super().__init__(PwRepresentationFrequency)

    def QueryWithPw(self, pwStr: str) -> list[PwRepresentationFrequency]:
        with Session() as session:
            units = session.query(self.entityCls).filter_by(pwStr=pwStr).all()
            return units

    def Update(self, unit):
        pass

    def CheckExist(self, unit: PwRepresentationFrequency) -> bool:
        """
        Check unit if exists in terms of `representationHash`

        Args:
            unit:

        Returns:

        """
        with Session() as session:
            units = session.query(self.entityCls).filter_by(pwStr=unit.pwStr).all()
            if not units or len(units) <= 0:
                return False
            else:
                return True


class PwRepUnique(Base):
    __tablename__ = TableNames.pwrepresentation_unique

    id = Column(Integer, primary_key=True)
    pwStr = Column(String)
    representation = Column(String)
    representationStructure = Column(String)
    representationHash = Column(String)
    representationStructureHash = Column(String)
    hash = Column(String)

    def __init__(self, pwStr: str, repStr: str, repStruc: str):
        super().__init__()
        self.pwStr = pwStr
        self.representation = repStr
        self.representationStructure = repStruc
        self.representationHash = PwRepresentation.getHash(self.representation)
        self.representationStructureHash = PwRepresentation.getHash(self.representationStructure)
        self.hash = PwRepresentation.getHash(self.pwStr + self.representation)

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def getHash(cls, s: str) -> str:
        """
        Get hash of representation

        Args:
            s:

        Returns:

        """
        hashB = hashlib.md5(s.encode("utf8")).digest()
        hashS = binascii.hexlify(hashB).decode("utf8")
        return hashS

    @classmethod
    def update(cls, a, b):
        """
        Update a with b

        Args:
            a:
            b:

        Returns:

        """
        a.pwStr = b.pwStr
        a.representation = b.representation
        a.representationStructure = b.representationStructure
        a.representationStructureHash = b.representationStructureHash
        a.representationHash = b.representationHash
        a.hash = b.hash

    @validates('pwStr')
    def validatePwStr(self, key, pwStr):
        if len(pwStr) <= 0:
            raise ValueError(f"Invalid pwStr: cannot be empty")
        return pwStr

    @validates('representation')
    def validateRep(self, key, repStr):
        if len(repStr) <= 0:
            raise ValueError(f"Invalid representation string: cannot be empty")
        return repStr

    @validates('representationHash')
    def validateRep(self, key, hashStr):
        if len(hashStr) <= 0:
            raise ValueError(f"Invalid representation hash: cannot be empty")
        return hashStr

    @validates('representationStructureHash')
    def validateRep(self, key, hashStr):
        if len(hashStr) <= 0:
            raise ValueError(f"Invalid representation hash: cannot be empty")
        return hashStr

    @validates('representationStructure')
    def validateRep(self, key, repStruc):
        if len(repStruc) <= 0:
            raise ValueError(f"Invalid representation hash: cannot be empty")
        return repStruc

    @validates('hash')
    def validateRep(self, key, hashStr):
        if len(hashStr) <= 0:
            raise ValueError(f"Invalid whole hash: cannot be empty")
        return hashStr


class PwRepUniqueMethods(BasicManipulateMethods):
    def __init__(self):
        super().__init__(PwRepUnique)

    def QueryWithPw(self, pwStr: str) -> list[PwRepUnique]:
        with Session() as session:
            units = session.query(self.entityCls).filter_by(pwStr=pwStr).all()
            return units

    def QueryWithId(self, id: int) -> list[PwRepUnique]:
        with Session() as session:
            units = session.query(self.entityCls).filter_by(id=id).all()
            return units

    def QueryAllPw(self, offset: int = 0, limit: int = 1e6) -> list[str]:
        with Session() as session:
            resultTuple: list[Column] = session.query(PwRepUnique.pwStr).distinct().offset(offset).limit(
                limit).all()  # list[tuple]
            result = list(map(lambda x: x[0], resultTuple))
            return result

    def QueryWithRepresentationHash(self, repHash: str) -> list[PwRepUnique]:
        """
        Query with representation's hash

        """
        with Session() as session:
            units = session.query(self.entityCls).filter_by(representationHash=repHash).all()
            return units

    def QueryWithRepresentationStructureHash(self, repStructureHash: str, offset: int = 0, limit: int = 1e6) -> list[
        PwRepUnique]:
        """
        Query with representation structure

        """
        with Session() as session:
            units = session.query(self.entityCls).filter_by(representationStructureHash=repStructureHash).offset(
                offset).limit(limit).all()
            return units

    def QueryWithWholeHash(self, hashStr: str) -> list[PwRepUnique]:
        """
        Query with the hash of pwStr+representation

        """
        with Session() as session:
            units = session.query(self.entityCls).filter_by(hash=hashStr).all()
            return units

    def Update(self, unit):
        pass

    def CheckExist(self, unit: PwRepUnique) -> bool:
        """
        Check unit if exists in terms of `representationHash`

        Args:
            unit:

        Returns:

        """
        with Session() as session:
            units = session.query(self.entityCls).filter_by(hash=unit.hash).all()
            if not units or len(units) <= 0:
                return False
            else:
                return True


class GeneralPwRepresentation(Base):
    __tablename__ = TableNames.pwrepresentation_general

    id = Column(Integer, primary_key=True)
    pwStr = Column(String)
    representation = Column(String)
    representationStructure = Column(String)
    representationHash = Column(String)
    representationStructureHash = Column(String)
    hash = Column(String)

    def __init__(self, pwStr: str, repStr: str, repStruc: str):
        super().__init__()
        self.pwStr = pwStr
        self.representation = repStr
        self.representationStructure = repStruc
        self.representationHash = PwRepresentation.getHash(self.representation)
        self.representationStructureHash = PwRepresentation.getHash(self.representationStructure)
        self.hash = PwRepresentation.getHash(self.pwStr + self.representation)

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def getHash(cls, s: str) -> str:
        """
        Get hash of representation

        Args:
            s:

        Returns:

        """
        hashB = hashlib.md5(s.encode("utf8")).digest()
        hashS = binascii.hexlify(hashB).decode("utf8")
        return hashS

    @classmethod
    def update(cls, a, b):
        """
        Update a with b

        Args:
            a:
            b:

        Returns:

        """
        a.pwStr = b.pwStr
        a.representation = b.representation
        a.representationStructure = b.representationStructure
        a.representationStructureHash = b.representationStructureHash
        a.representationHash = b.representationHash
        a.hash = b.hash

    @validates('pwStr')
    def validatePwStr(self, key, pwStr):
        if len(pwStr) <= 0:
            raise ValueError(f"Invalid pwStr: cannot be empty")
        return pwStr

    @validates('representation')
    def validateRep(self, key, repStr):
        if len(repStr) <= 0:
            raise ValueError(f"Invalid representation string: cannot be empty")
        return repStr

    @validates('representationHash')
    def validateRep(self, key, hashStr):
        if len(hashStr) <= 0:
            raise ValueError(f"Invalid representation hash: cannot be empty")
        return hashStr

    @validates('representationStructureHash')
    def validateRep(self, key, hashStr):
        if len(hashStr) <= 0:
            raise ValueError(f"Invalid representation hash: cannot be empty")
        return hashStr

    @validates('representationStructure')
    def validateRep(self, key, repStruc):
        if len(repStruc) <= 0:
            raise ValueError(f"Invalid representation hash: cannot be empty")
        return repStruc

    @validates('hash')
    def validateRep(self, key, hashStr):
        if len(hashStr) <= 0:
            raise ValueError(f"Invalid whole hash: cannot be empty")
        return hashStr


class GeneralPwRepresentationMethods(RepresentationMethods):
    def __init__(self):
        super().__init__()
        self.entityCls = GeneralPwRepresentation

    def QueryAllPw(self, offset: int = 0, limit: int = 1e6) -> list[str]:
        with Session() as session:
            resultTuple: list[Column] = session.query(GeneralPwRepresentation.pwStr).distinct().offset(offset).limit(
                limit).all()  # list[tuple]
            result = list(map(lambda x: x[0], resultTuple))
            return result


class GeneralRepresentationFrequency(Base):
    __tablename__ = TableNames.representation_frequency_general

    frequency = Column(Integer)
    representationStructureHash = Column(String, primary_key=True)
    representationStructure = Column(String)

    def __init__(self, frequency: int, repHash: str, repStr: str):
        """

        Args:
            frequency:
            repHash:
            repStr: serialized representation
        """
        super().__init__()
        self.frequency = frequency
        self.representationHash = repHash
        self.representation = repStr

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def update(cls, a, b):
        """
        Update a with b

        """
        a.frequency = b.frequency
        a.representationHash = b.representationHash
        a.representation = b.representation

    @validates('frequency')
    def validateFrequency(self, key, fre: int):
        if fre <= 0:
            raise ValueError(f"Invalid frequency: must larger than 0")
        return fre

    @validates("representationHash")
    def validateRepHash(self, key, h: str):
        if len(h) <= 0:
            raise ValueError(f"Invalid representation hash: cannot be empty")
        return h

    @validates("representation")
    def validateRepStr(self, key, h: str):
        if len(h) <= 0:
            raise ValueError(f"Invalid representation serialized data: cannot be empty")
        return h


class GeneralRepresentationFrequencyMethods(RepresentationFrequencyMethods):
    def __init__(self):
        super().__init__()
        self.entityCls = GeneralRepresentationFrequency

    def Rebuild(self):
        q = f"INSERT INTO {self.entityCls.__tablename__}" \
            f" select distinct `fre`.`frequency` AS `frequency`,`fre`.`representationStructureHash` AS `representationStructureHash`,`pw`.`representationStructure` AS `representationStructure` " \
            f"from (`{TableNames.representation_frequency_base_general}` `fre` " \
            f"join `{TableNames.pwrepresentation_general}` `pw`) " \
            f"where (`fre`.`representationStructureHash` = `pw`.`representationStructureHash`) " \
            f"order by `fre`.`frequency` desc"
        with Session() as session:
            session.query(self.entityCls).delete()
            session.execute(text(q))
            session.commit()

    def QueryWithRepStructureHash(self, hashStr: str) -> list[GeneralRepresentationFrequency]:
        with Session() as session:
            units = session.query(self.entityCls).filter_by(representationStructureHash=hashStr).all()
            return units

    def QueryAllWithFrequencyDesc(self, offset: int = 0, limit: int = 1e7) -> list[GeneralRepresentationFrequency]:
        """
        Get all units with frequency in desc order

        """
        with Session() as session:
            units = session.query(self.entityCls).distinct().order_by(
                self.entityCls.frequency.desc()).offset(offset).limit(limit)
            return units

    def Update(self, unit):
        pass

    def CheckExist(self, unit: GeneralRepresentationFrequency) -> bool:
        """
        Check unit if exists in terms of `representationHash`

        Args:
            unit:

        Returns:

        """
        with Session() as session:
            units = session.query(self.entityCls).filter_by(representationHash=unit.representationHash).all()
            if not units or len(units) <= 0:
                return False
            else:
                return True


class GeneralRepresentationFrequencyBase(Base):
    __tablename__ = TableNames.representation_frequency_base_general

    frequency = Column(Integer)
    representationStructureHash = Column(String, primary_key=True)

    def __init__(self, frequency: int, repStructHash: str):
        super().__init__()
        self.frequency = frequency
        self.representationStructureHash = repStructHash


class GeneralRepresentationFrequencyBaseQueryMethods(BaseQueryMethods):

    def __init__(self):
        super().__init__(GeneralRepresentationFrequencyBase)

    def Rebuild(self):
        """Truncate the table and re-generate from pwrepresentation_general
        """
        with Session() as session:
            session.query(self.entityCls).delete()
            q = f"INSERT INTO {self.entityCls.__tablename__}" \
                f" SELECT COUNT(0) AS frequency, {TableNames.pwrepresentation_general}.representationStructureHash AS representationStructureHash " \
                f"FROM {TableNames.pwrepresentation_general} " \
                f"GROUP BY {TableNames.pwrepresentation_general}.representationStructureHash"
            session.execute(text(q))
            session.commit()


class GeneralPwRepresentationFrequency(Base):
    __tablename__ = TableNames.pwrepresentation_frequency_general

    id = Column(Integer, primary_key=True)
    pwStr = Column(String)
    frequency = Column(Integer)
    representationStructureHash = Column(String)
    representationStructure = Column(String)

    def __init__(self, pwStr: str, frequency: int, repHash: str, repStr: str):
        """

        Args:
            frequency:
            repHash:
            repStr: serialized representation
        """
        super().__init__()
        self.pwStr = pwStr
        self.frequency = frequency
        self.representationHash = repHash
        self.representation = repStr

    def __str__(self):
        return str(self.__dict__)


class GeneralPwRepresentationFrequencyMethods(PwRepresentationFrequencyMethods):
    def __init__(self):
        super().__init__()
        self.entityCls = GeneralPwRepresentationFrequency

    def Rebuild(self):
        q = f"INSERT INTO {self.entityCls.__tablename__}" \
            f" select `pw`.`id` AS `id`,`pw`.`pwStr` AS `pwStr`,`pw`.`representationStructure` AS `representationStructure`,`pw`.`representationStructureHash` AS `representationStructureHash`,`fre_view`.`frequency` AS `frequency` " \
            f"from (`{TableNames.pwrepresentation_general}` `pw` " \
            f"join `{TableNames.representation_frequency_base_general}` `fre_view`) " \
            f"where (`pw`.`representationStructureHash` = `fre_view`.`representationStructureHash`)"
        with Session() as session:
            session.query(self.entityCls).delete()
            session.execute(text(q))
            session.commit()

    def QueryWithPw(self, pwStr: str) -> list[GeneralPwRepresentationFrequency]:
        with Session() as session:
            units = session.query(self.entityCls).filter_by(pwStr=pwStr).all()
            return units

    def Update(self, unit):
        pass

    def CheckExist(self, unit: GeneralPwRepresentationFrequency) -> bool:
        """
        Check unit if exists in terms of `representationHash`

        Args:
            unit:

        Returns:

        """
        with Session() as session:
            units = session.query(self.entityCls).filter_by(pwStr=unit.pwStr).all()
            if not units or len(units) <= 0:
                return False
            else:
                return True


class GeneralPwRepUnique(Base):
    __tablename__ = TableNames.pwrepresentation_unique_general

    id = Column(Integer, primary_key=True)
    pwStr = Column(String)
    representation = Column(String)
    representationStructure = Column(String)
    representationHash = Column(String)
    representationStructureHash = Column(String)
    hash = Column(String)

    def __init__(self, pwStr: str, repStr: str, repStruc: str):
        super().__init__()
        self.pwStr = pwStr
        self.representation = repStr
        self.representationStructure = repStruc
        self.representationHash = PwRepresentation.getHash(self.representation)
        self.representationStructureHash = PwRepresentation.getHash(self.representationStructure)
        self.hash = PwRepresentation.getHash(self.pwStr + self.representation)

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def getHash(cls, s: str) -> str:
        """
        Get hash of representation

        Args:
            s:

        Returns:

        """
        hashB = hashlib.md5(s.encode("utf8")).digest()
        hashS = binascii.hexlify(hashB).decode("utf8")
        return hashS

    @classmethod
    def update(cls, a, b):
        """
        Update a with b

        Args:
            a:
            b:

        Returns:

        """
        a.pwStr = b.pwStr
        a.representation = b.representation
        a.representationStructure = b.representationStructure
        a.representationStructureHash = b.representationStructureHash
        a.representationHash = b.representationHash
        a.hash = b.hash

    @validates('pwStr')
    def validatePwStr(self, key, pwStr):
        if len(pwStr) <= 0:
            raise ValueError(f"Invalid pwStr: cannot be empty")
        return pwStr

    @validates('representation')
    def validateRep(self, key, repStr):
        if len(repStr) <= 0:
            raise ValueError(f"Invalid representation string: cannot be empty")
        return repStr

    @validates('representationHash')
    def validateRep(self, key, hashStr):
        if len(hashStr) <= 0:
            raise ValueError(f"Invalid representation hash: cannot be empty")
        return hashStr

    @validates('representationStructureHash')
    def validateRep(self, key, hashStr):
        if len(hashStr) <= 0:
            raise ValueError(f"Invalid representation hash: cannot be empty")
        return hashStr

    @validates('representationStructure')
    def validateRep(self, key, repStruc):
        if len(repStruc) <= 0:
            raise ValueError(f"Invalid representation hash: cannot be empty")
        return repStruc

    @validates('hash')
    def validateRep(self, key, hashStr):
        if len(hashStr) <= 0:
            raise ValueError(f"Invalid whole hash: cannot be empty")
        return hashStr


class GeneralPwRepUniqueMethods(PwRepUniqueMethods):
    def __init__(self):
        super().__init__()
        self.entityCls = GeneralPwRepUnique

    def QueryAllPw(self, offset: int = 0, limit: int = 1e6) -> list[str]:
        with Session() as session:
            resultTuple: list[Column] = session.query(GeneralPwRepUnique.pwStr).distinct().offset(offset).limit(
                limit).all()  # list[tuple]
            result = list(map(lambda x: x[0], resultTuple))
            return result

    def QueryIdRange(self) -> (int, int):
        """Get maxId and minId
        """
        with Session() as session:
            minId = session.query(func.min(self.entityCls.id)).scalar()
            maxId = session.query(func.max(self.entityCls.id)).scalar()
            return maxId, minId
