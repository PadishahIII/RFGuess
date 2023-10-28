import concurrent
import os
from abc import ABCMeta, abstractmethod
from concurrent.futures import ThreadPoolExecutor

from Commons import pinyinUtils
from Scripts.Utils import CsvHelper
from Scripts.databaseInit import PIIUnit, lineRst, PIIUnitQueryMethods, logger, ProgressTracker


class AbstractDatasetLineParser(metaclass=ABCMeta):
    """
    Parse each line of dataset into database units
    """

    @abstractmethod
    def parseline(self, line: str, keys: list[str]):
        """
        Parse one line to a unit. The fields of line are parsed as the same order of keys
        Args:
            line: string to parse
            keys: field names

        Returns:
            A database unit

        """
        pass


class AbstractDatasetLoader(metaclass=ABCMeta):
    """
    Handle user provided dataset, load into database
    """

    @abstractmethod
    def load_dataset(self, file, start=0, limit=-1, clear=False, update=False):
        """
           Load dataset file into database

           Args:
               file: dataset file path
               start: line number to start
               limit: limitation of lines to load, -1 for no limit
               clear: whether clear the table before insert
               update: update unit if already exists
        """
        pass


class DatasetLineParserException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidKeyException(DatasetLineParserException):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DatasetLoaderException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ShortBarDatasetLineParser(AbstractDatasetLineParser):

    def parseline(self, line: str, keys: list[str] = None) -> PIIUnit:
        """
        Convert a line of the dataset file into PIIUnit object.
        Line must be in the below format:
        > email----account----name----idCard----password----phoneNum----email(ignored)

        Args:
            keys(not used): field names of pii
            line: a single line containing pii
        """
        newLine = line.strip().lstrip()
        m = lineRst.search(newLine)
        if not m:
            raise DatasetLineParserException(f"line regex match failed: {line}")
        d = dict()
        md = m.groupdict()
        for k in md.keys():
            if not md[k] or len(md[k]) <= 0:
                raise DatasetLineParserException(f"Error: Empty '{k}' in line '{line}'")
            d[k] = md[k]
        name = d['name']
        # get full name
        fullname = pinyinUtils.getFullName(name)
        d['fullName'] = fullname
        unit = PIIUnit(**d)

        return unit


class CsvDatasetLineParser(AbstractDatasetLineParser):

    def __init__(self, keys: list[str]) -> None:
        """
        Provide field names of dataset, line parser will transform them into standard field names of PIIUnit by approximate matching
        Args:
            keys: self-defined fields
        """
        if keys is None or len(keys) <= 0:
            raise DatasetLineParserException(f"Failed to instantiate line parser: Invalid keys")
        self.keys = keys
        self.dim = len(keys)
        self.pii_unit_keys = list()  # ordered according to keys
        self.empty_keys = list()  # keys set to empty
        for key in keys:
            key = key.lower()
            target_key = ""
            if key is None or len(key) <= 0:
                raise DatasetLineParserException(f"Failed to instantiate line parser: Empty key in '{keys}'")
            if key.__contains__("account"):
                target_key = "account"
            elif key.__contains__("name"):
                target_key = "name"
            elif key.__contains__("idcard"):
                target_key = "idCard"
            elif key.__contains__("phone"):
                target_key = "phoneNum"
            elif key.__contains__("email"):
                target_key = "email"
            elif key.__contains__("password"):
                target_key = "password"
            if target_key == "":
                raise InvalidKeyException(f"Unsupported key: '{key}'")
            if self.pii_unit_keys.__contains__(target_key):
                raise InvalidKeyException(f"Conflicted key: '{key}' on the scope of '{target_key}'")
            self.pii_unit_keys.append(target_key)
        for key in PIIUnit.attributes:
            if key not in self.pii_unit_keys and key != "fullName":  # fullName will be set dynamically
                self.empty_keys.append(key)

    def parseline(self, line: str, keys: list[str] = None) -> PIIUnit:
        """
        Convert a csv formatted line into PIIUnit object.

        Args:
            line:
            keys(ignored):

        """
        if keys is None:
            keys = self.pii_unit_keys
        values = CsvHelper.parseline(line)
        dim = len(values)
        if values is None or dim != self.dim:
            raise DatasetLineParserException(f"Invalid dimension at '{line}', provided:{dim}, expected:{self.dim} ")
        d = dict()
        for key in self.empty_keys:
            d[key] = ""
        for i in range(dim):
            key = keys[i]
            value = values[i]
            d[key] = value
        d['fullName'] = pinyinUtils.getFullName(d['name'])
        unit = PIIUnit(**d)
        return unit


class CsvDatasetLoader(AbstractDatasetLoader):
    """
    Load dataset from csv file 

    """

    def __init__(self) -> None:
        self.lineparser: CsvDatasetLineParser = None
        self.valid_fields = ['account', 'name', 'phone', 'idcard', 'email', 'password']
        self.minimum_fields = ['name', 'password']
        self.keys = list()  # provided field names
        self.keys_num = 0  # number of fields

    def check_keys(self, keys: list):
        """
        Check if the given field names can be accepted. And keys should meet minimum_fields

        Args:
            keys: a list of field names


        """
        keys = [x.lower() for x in keys if x is not None]
        for key in keys:
            if key not in self.valid_fields:
                raise DatasetLoaderException(
                    f"Invalid field name: {key}, allowed fields: {self.valid_fields}")
        for key in self.minimum_fields:
            if key not in keys:
                raise DatasetLoaderException(
                    f"A required key is missing: '{key}', the minimum key set is '{self.minimum_fields}'")

    def clear_and_load_dataset(self, file, start=0, limit=-1, charset="utf-8"):
        """
        Clear the database before loading dataset, in order to accumulate the process of inserting unit
        Args:
            file: dataset file path
            start: line number to start
            limit: limitation of lines to load, -1 for no limit

        """
        self.load_dataset(file, start, limit, clear=True, update=True, charset=charset)

    def load_and_update_dataset(self, file, start=0, limit=-1, charset="utf-8"):
        """
        Load the dataset to an existing database, and update existed units.
        This method can not apply to databases of quite large scope, since seeking for existing unit is a significantly time-consuming procedure.
        Args:
            file: dataset file path
            start: line number to start
            limit: limitation of lines to load, -1 for no limit

        """
        self.load_dataset(file, start, limit, clear=False, update=True, charset=charset)

    def load_dataset(self, file, start=0, limit=-1, charset="utf-8", clear=False, update=False):
        """
            Load dataset file into database

            Args:
                charset: the character set of dataset file
                file: dataset file path
                start: line number to start
                limit: limitation of lines to load, -1 for no limit
                clear: whether clear the table before insert
                update: update unit if already exists
        """
        count = 0
        updateCount = 0
        queryMethods = PIIUnitQueryMethods()

        invalidLines = list()
        exceptionList = list()
        from Parser.PIIParsers import PIIStructureParser
        from Commons import Utils

        def insertline(line, count, directInsert: bool = False) -> bool:
            updated = False
            try:
                unit = self.lineparser.parseline(line)

                # check format
                pii, pwStr = Utils.parsePIIUnitToPIIAndPwStr(unit)
                piiParser = PIIStructureParser(pii)
                piiStructure = piiParser.getPwPIIStructure(pwStr=pwStr)
                if directInsert:
                    queryMethods.Insert(unit)
                    updated = True
                else:
                    u = queryMethods.SmartInsert(unit, update)
                    updated = u
            except Exception as e:
                logger.info(f"Exception occurred. Restart at {count} to continue the process.")
                invalidLines.append(line)
                exceptionList.append(e)
                return updated
            if count % 100 == 0:
                logger.info(f"Completed: {count}")
            return updated

        if not os.path.exists(file):
            raise DatasetLoaderException(f"Error: invalid dataset path: {file}")

        # clear table
        if clear:
            logger.info(f"Clearing original data, which has size:{queryMethods.QuerySize()}")
            queryMethods.DeleteAll()
            logger.info(f"Clear PII data finish, start write new data")
        directInsert = clear

        threadpool = ThreadPoolExecutor()
        futureList = list()

        with open(file, encoding=charset, errors="replace") as f:
            firstLine = f.readline()
            file_size = os.stat(file).st_size
            line_length = len(firstLine) if len(firstLine) > 0 else 50
            line_count = file_size // line_length
            keys = CsvHelper.parseline(firstLine)
            if keys is None or len(keys) <= 0:
                logger.error(f"Invalid dataset format: first line must present the name of fields")
                raise DatasetLoaderException(f"Invalid dataset format: first line must present the name of fields")

            self.check_keys(keys)

            self.keys_num = len(keys)
            self.keys = keys
            self.lineparser = CsvDatasetLineParser(self.keys)

            for i in range(start - 1):
                f.readline()
            if limit > 0:
                for i in range(limit):
                    line = f.readline()
                    if len(line) > 5:
                        count += 1
                        ProgressTracker.load_pii_data_progress = count
                        ProgressTracker.load_pii_data_limit = limit
                        futureList.append(threadpool.submit(insertline, line, count, directInsert))
            else:
                # no limit
                line = f.readline()
                while line:
                    if len(line) > 5:
                        count += 1
                        ProgressTracker.load_pii_data_progress = count
                        ProgressTracker.load_pii_data_limit = line_count
                        futureList.append(threadpool.submit(insertline, line, count, directInsert))
                    line = f.readline()
            task_number = len(futureList)
            i = 0
            for future in concurrent.futures.as_completed(futureList):
                future.result()
                i += 1
                ProgressTracker.load_pii_data_progress = i
                ProgressTracker.load_pii_data_limit = task_number

        threadpool.shutdown()
        logger.info(f"number of data unit: {count}")
        logger.info(f"Have insert {count} PII data, updated: {updateCount}")
        logger.info(f"Invalid Lines ({len(invalidLines)}):")

        for i in range(len(invalidLines)):
            line = invalidLines[i]
            exception = exceptionList[i]
            print(f"{exception}:{line}")
