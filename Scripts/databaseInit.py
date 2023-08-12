import binascii
import hashlib
import logging
import os
import re
from abc import ABCMeta, abstractmethod

import sqlalchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, validates, scoped_session

from Commons import pinyinUtils

Base = declarative_base()
emailRst = re.compile(r".+?@.+?")
lineRst = re.compile(
    r"(?P<email>.+?@[^\-]+)----(?P<account>[^\-]+)----(?P<name>[^\-]+)----(?P<idCard>[^\-]+)----(?P<password>[^\-]+)----(?P<phoneNum>[^\-]+)----.*")

logging.basicConfig(filename="database.log")
logger = logging.getLogger("sqlalchemy.engine")
logger.setLevel(logging.CRITICAL)

engine = sqlalchemy.create_engine(url="mysql://root:914075@localhost/dataset12306")

sessionFactory = sessionmaker(bind=engine)
Session = scoped_session(sessionFactory)


class PIIUnit(Base):
    __tablename__ = 'PII'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    account = Column(String)
    name = Column(String)
    idCard = Column(String)
    phoneNum = Column(String)
    password = Column(String)
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

    @validates('email')
    def validateEmail(self, key, email):
        if not email:
            raise ValueError(f"Email is required")
        if not emailRst.match(email):
            raise ValueError(f"Invail email: {email}")
        return email

    @validates('account')
    def validateAccount(self, key, account):
        if not account:
            raise ValueError(f"Account is required")
        return account

    @validates('name')
    def validateName(self, key, name):
        if not name:
            raise ValueError(f"Name is required")
        return name

    @validates('idCard')
    def validateIdCard(self, key, idCard):
        if not idCard:
            raise ValueError(f"IdCard is required")
        return idCard

    @validates('phoneNum')
    def validatePhoneNum(self, key, phoneNum):
        if not phoneNum:
            raise ValueError(f"PhoneNum is required")
        if not str(phoneNum).isdigit():
            raise ValueError(f"Invaild phoneNum: {phoneNum}")
        return phoneNum

    @validates('password')
    def validatePassword(self, key, password):
        if not password:
            raise ValueError(f"Password is required")
        return password


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
            units = self.QueryAll()
            for unit in units:
                session.delete(unit)
            session.commit()

    def SmartInsert(self, unit: Base, update: bool = False):
        """
        Insert unit to table if not exists, else update units with the same `name`

        Args:
            unit:
            update: if set to True, update the unit when existing, else ignore.
        """
        if self.CheckExist(unit):
            if update:
                self.Update(unit)
        else:
            self.Insert(unit)


'''
PIIUnit query methods
'''


class PIIUnitQueryMethods(BasicManipulateMethods):
    def __init__(self):
        super().__init__(PIIUnit)

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
            units = session.query(PIIUnit).filter_by(name=unit.name).all()
            if not units or len(units) <= 0:
                return False
            else:
                return True


'''
Top level apis
'''


def parseLineToPIIUnit(line: str) -> PIIUnit:
    """
    Convert a line of the dataset file into PIIUnit object.
    Line must be in the below format:
    > email----account----name----idCard----password----phoneNum----email(ignored)

    Args:
        line: a single line containing pii
    """
    newLine = line.strip().lstrip()
    m = lineRst.search(newLine)
    if not m:
        raise ParseLineException(f"regex match failed: {line}")
    d = dict()
    md = m.groupdict()
    for k in md.keys():
        if not md[k] or len(md[k]) <= 0:
            raise ParseLineException(f"Error: Empty '{k}' in line '{line}'")
        d[k] = md[k]
    name = d['name']
    # get full name
    fullname = pinyinUtils.getFullName(name)
    d['fullName'] = fullname
    pii = PIIUnit(**d)
    return pii


class ParseLineException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


'''
Main logics
'''


def LoadDataset(file, start=0, limit=-1, clear=False, update=False):
    """
    Load dataset file into database

    Args:
        file: dataset file path
        start: line number to start
        limit: limitation of lines to load, -1 for no limit
        clear: whether clear the table before insert
        update: update unit when already existing
    """
    count = 0
    queryMethods = BasicManipulateMethods()

    def insertline(line, count):
        try:
            pii = parseLineToPIIUnit(line)
            queryMethods.SmartInsert(pii, update)
        except:
            logger.critical(f"Exception occured. Restart at {count} to continue the process.")
        if count % 100 == 0:
            logger.critical(f"Completed: {count}")

    if not os.path.exists(file):
        raise LoadDatasetException(f"Error: invalid dataset path: {file}")

    # clear table
    if clear:
        queryMethods.DeleteAll()

    with open(file, encoding='gbk', errors="replace") as f:
        for i in range(start):
            f.readline()
        if limit > 0:
            for i in range(limit):
                line = f.readline()
                if len(line) > 5:
                    count += 1
                    insertline(line, count)
        else:
            # no limit
            line = f.readline()
            while line:
                if len(line) > 5:
                    count += 1
                    insertline(line, count)
                line = f.readline()
    logger.critical(f"number of data unit: {count}")
    logger.critical(f"Have insert {count} PII data")


class LoadDatasetException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


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
    __tablename__ = "PwRepresentation"

    id = Column(Integer, primary_key=True)
    pwStr = Column(String)
    representation = Column(String)
    representationHash = Column(String)
    hash = Column(String)

    def __init__(self, pwStr: str, repStr: str):
        super().__init__()
        self.pwStr = pwStr
        self.representation = repStr
        self.representationHash = PwRepresentation.getHash(self.representation)
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
            units = session.query(PwRepresentation).filter_by(pwStr=pwStr).all()
            return units

    def QueryWithRepresentationHash(self, repHash: str) -> list[PwRepresentation]:
        """
        Query with representation's hash
        Args:
            repHash:

        Returns:

        """
        with Session() as session:
            units = session.query(PwRepresentation).filter_by(representationHash=repHash).all()
            return units

    def QueryWithWholeHash(self, hashStr: str) -> list[PwRepresentation]:
        """
        Query with the hash of pwStr+representation

        Args:
            hashStr:

        Returns:

        """
        with Session() as session:
            units = session.query(PwRepresentation).filter_by(hash=hashStr).all()
            return units

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
    __tablename__ = "representation_frequency_view"

    frequency = Column(Integer,primary_key=True)
    representationHash = Column(String)

    def __init__(self, frequency: int, repHash: str):
        super().__init__()
        self.frequency = frequency
        self.representationHash = repHash

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def update(cls, a, b):
        """
        Update a with b

        """
        a.frequency = b.frequency
        a.representationHash = b.representationHash

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


class RepresentationFrequencyMethods(BasicManipulateMethods):
    def __init__(self):
        super().__init__(RepresentationFrequency)

    def QueryWithRepHash(self, hashStr: str) -> list[RepresentationFrequency]:
        with Session() as session:
            units = session.query(self.entityCls).filter_by(representationHash=hashStr).all()
            return units

    def QueryAllWithFrequencyDesc(self) -> list[RepresentationFrequency]:
        """
        Get all units with frequency in desc order

        """
        with Session() as session:
            units = session.query(self.entityCls).order_by(RepresentationFrequency.frequency.desc())
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
