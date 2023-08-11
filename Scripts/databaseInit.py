import logging
import os
import re

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


def Insert(pii: PIIUnit):
    with Session() as session:
        session.add(pii)
        session.commit()


def QueryAll() -> list[PIIUnit]:
    with Session() as session:
        units = session.query(PIIUnit).all()
        return units


def QueryWithLimit(offset: int = 0, limit: int = 1e6) -> list[PIIUnit]:
    with Session() as session:
        units = session.query(PIIUnit).offset(offset).limit(limit).all()
        return units


def UpdateFullName(name, fullname):
    with Session() as session:
        units = session.query(PIIUnit).filter_by(name=name).all()
        for unit in units:
            unit.fullName = fullname
        session.commit()


def Update(unit: PIIUnit):
    """
    Update all units with the same `name` as unit given

    Args:
        unit:
        session_:
    """
    with Session() as session:
        if CheckExist(unit):
            units = session.query(PIIUnit).filter_by(name=unit.name).all()
            for u in units:
                PIIUnit.update(u, unit)


def DeleteAll():
    with Session() as session:
        units = QueryAll()
        for unit in units:
            session.delete(unit)
        session.commit()


def CheckExist(unit: PIIUnit) -> bool:
    with Session() as session:
        units = session.query(PIIUnit).filter_by(name=unit.name).all()
        if not units or len(units) <= 0:
            return False
        else:
            return True


def SmartInsert(unit: PIIUnit, update: bool = False):
    """
    Insert unit to table if not exists, else update units with the same `name`

    Args:
        unit:
        update: if set to True, update the unit when existing, else ignore.
    """
    if CheckExist(unit):
        if update:
            Update(unit)
    else:
        Insert(unit)


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

    def insertline(line, count):
        try:
            pii = parseLineToPIIUnit(line)
            SmartInsert(pii, update)
        except:
            logger.critical(f"Exception occured. Restart at {count} to continue the process.")
        if count % 100 == 0:
            logger.critical(f"Completed: {count}")

    if not os.path.exists(file):
        raise LoadDatasetException(f"Error: invalid dataset path: {file}")

    # clear table
    if clear:
        DeleteAll()

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
    units = QueryAll()
    nameList = [unit.name for unit in units if unit]
    for name in nameList:
        fullName = pinyinUtils.getFullName(name)
        if fullName and len(fullName) > 0:
            UpdateFullName(name, fullName)


def UnitGenerator(offset: int = 0, limit: int = 1e6):
    units = QueryWithLimit(offset, limit)
    for unit in units:
        yield unit
