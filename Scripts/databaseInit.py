import logging
import os
import re

import sqlalchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, validates

from Commons import jinjiaUtils

Base = declarative_base()
emailRst = re.compile(r"\w+@.+?")
lineRst = re.compile(
    r"(?P<email>\w+@[^\-]+)----(?P<account>[^\-]+)----(?P<name>[^\-]+)----(?P<idCard>[^\-]+)----(?P<password>[^\-]+)----(?P<phoneNum>[^\-]+)----.*")

logging.basicConfig(filename="database.log")
logger = logging.getLogger("sqlalchemy.engine")
logger.setLevel(logging.INFO)

engine = sqlalchemy.create_engine(url="mysql://root:914075@localhost/dataset12306")


# Session = sessionmaker(bind=engine)


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
    with Session(engine) as session:
        session.add(pii)
        session.commit()


def QueryAll() -> list[PIIUnit]:
    with Session(engine) as session:
        units = session.query(PIIUnit).all()
        return units


def UpdateFullName(name, fullname):
    with Session(engine) as session:
        units = session.query(PIIUnit).filter_by(name=name).all()
        for unit in units:
            unit.fullName = fullname
        session.commit()


def DeleteAll():
    with Session(engine) as session:
        units = QueryAll()
        for unit in units:
            session.delete(unit)
        session.commit()


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
    fullname = jinjiaUtils.getFullName(name)
    d['fullName'] = fullname
    pii = PIIUnit(**d)
    return pii


class ParseLineException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


'''
Main logics
'''


def LoadDataset(file, start=0, limit=-1, clear=False):
    """
    Load dataset file into database

    Args:
        file: dataset file path
        start: line number to start
        limit: limitation of lines to load, -1 for no limit
        clear: whether clear the table before insert
    """
    if not os.path.exists(file):
        raise LoadDatasetException(f"Error: invalid dataset path: {file}")
    lines = []
    with open(file, encoding='gbk', errors="replace") as f:
        for i in range(start):
            f.readline()
        if limit > 0:
            for i in range(limit):
                line = f.readline()
                if len(line) > 5:
                    lines.append(line)
        else:
            # no limit
            line = f.readline()
            while not line:
                if len(line) > 5:
                    lines.append(line)
                line = f.readline()
    # clear table
    if clear:
        DeleteAll()
    # Insert into database
    for line in lines:
        pii = parseLineToPIIUnit(line)
        Insert(pii)


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
        fullName = jinjiaUtils.getFullName(name)
        if fullName and len(fullName) > 0:
            UpdateFullName(name, fullName)
