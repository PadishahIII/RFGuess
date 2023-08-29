import concurrent.futures
import threading
import time
from unittest import TestCase

import joblib
from sklearn import tree

from Generators.GeneralPIIGenerators import *
from Generators.PasswordGuessGenerator import *
from Parser.Factory import *
from Parser.PIIPreprocessor import *

TRAINSET_PROPORTION = 0.5  # train set proportion

logger = logging.getLogger("main_General_PII_Mode")
logger.setLevel(logging.INFO)


class GeneralPIITrainMain(TestCase):
    def test_train_generate_assess(self):
        """Train, generate pattern and assess accuracy
        """
        logger.info(f"[Train] procession start")
        time.sleep(1)
        self.test_train_general()
        logger.info(f"[Generate Pattern] procession start")
        time.sleep(1)
        self.test_generate_pattern()
        logger.info(f"[Clean Guess dir]")
        time.sleep(1)
        self.test_clean_guesses_dir()
        logger.info(f"[Assessment] procession start")
        time.sleep(1)
        self.test_accuracy_assessment()

    def train_generate_assess(self, savePath):
        """(For Api use)Train, generate pattern and assess accuracy
        """
        logger.info(f"[Train] procession start")
        time.sleep(1)
        self.train_general(savePath)
        logger.info(f"[Generate Pattern] procession start")
        time.sleep(1)
        # self.test_generate_pattern()
        # logger.info(f"[Clean Guess dir]")
        # time.sleep(1)
        # self.test_clean_guesses_dir()
        # logger.info(f"[Assessment] procession start")
        # time.sleep(1)
        # self.test_accuracy_assessment()

    def test_train_general(self):
        piiFactory = GeneralPIIFactory.getInstance(proportion=TRAINSET_PROPORTION)
        piiFactory.process()
        logger.info(
            f"Train data build Finished.\nSize of featureList:{len(piiFactory.getFeatureList())} LabelList:{len(piiFactory.getLabelList())}")
        logger.info(f"\nStart Training...")
        trainner = PIIRFTrainner(piiFactory.getFeatureList(), piiFactory.getLabelList())
        trainner.train()
        savePath = "../../save_general.clf"
        joblib.dump(trainner.getClf(), savePath)
        logger.info(f"Train finish, saved to {savePath}")

    def train_general(self, savePath):
        """(For Api use) train general model
        """
        ProgressTracker.progress = 0
        ProgressTracker.limit = 2
        logger.info(f"Build feature and label... Please Wait")
        piiFactory = GeneralPIIFactory.getInstance(proportion=TRAINSET_PROPORTION)
        piiFactory.process()
        logger.info(
            f"Train data build Finished.\nSize of featureList:{len(piiFactory.getFeatureList())} LabelList:{len(piiFactory.getLabelList())}")
        ProgressTracker.progress = 1
        logger.info(f"\nStart Training...")
        trainner = PIIRFTrainner(piiFactory.getFeatureList(), piiFactory.getLabelList())
        trainner.train()
        # savePath = "../../save_general.clf"
        joblib.dump(trainner.getClf(), savePath)
        logger.info(f"Train finish, saved to {savePath}")
        ProgressTracker.progress = 2

    def test_generate_pattern(self):
        generator: GeneralPIIPatternGenerator = GeneralPIIPatternGenerator.getInstance("../../save_general.clf")
        l = generator.getPatternStrList(limit=5000)
        logger.info(f"Generate complete: {len(l)}")

        with open("../patterns.txt", "w") as f:
            for i in range(len(l)):
                f.write(f"{l[i]}\n")

    def test_generate_guess(self):
        pii = BasicTypes.PII(account="yhang0607",
                             name="yhangzhongjie",
                             firstName="yhang",
                             givenName="zhong jie",
                             birthday="19820607",
                             phoneNum="13222245678",
                             email="3501111asd11@qq.com",
                             idcardNum="1213213213")
        pii2 = BasicTypes.PII(account="5201314",
                              name="qiaohuangyu",
                              firstName="qiao",
                              givenName="huang yu",
                              birthday="19920303",
                              phoneNum="11111111111",
                              email="2930222222@qq.com",
                              idcardNum="77777777777")
        generator: GeneralPasswordGenerator = GeneralPasswordGenerator.getInstance(
            patternFile="../patterns_general.txt",
        )
        generator.init()
        generator.generateForPII(outputFile="../passwords_general.txt",
                                 pii=pii,
                                 nameFuzz=True)
        generator.generateForPII(outputFile="../passwords_general_2.txt",
                                 pii=pii2,
                                 nameFuzz=True)

    def test_clean_guesses_dir(self):
        """
        Clear guesses dir

        """
        dirName = "../guesses"
        for filename in os.listdir(dirName):
            filePath = os.path.join(dirName, filename)
            if os.path.isfile(filePath):
                os.remove(filePath)

    def test_accuracy_assessment(self):
        self.accuracy_assessment("../patterns.txt")

    def accuracy_assessment(self, patternFile):
        """(for Api use) Assess the accuracy of generated guesses
        Get every PII and generate a guesses dictionary, if any guess match the true password, that'll be called by success

        """
        ProgressTracker.progress = 0

        filePattern = '../guesses/passwords_{0}.txt'
        transformer: PIIUnitTransformer = PIIUnitTransformer.getInstance()
        generator: GeneralPasswordGenerator = GeneralPasswordGenerator.getInstance(
            patternFile=patternFile,
        )
        generator.init()
        maxId = transformer.getMaxId()
        minId = transformer.getMinId()
        logger.info(f"max:{maxId},min:{minId}")
        end = maxId + 1
        start = end - int((1 - TRAINSET_PROPORTION) * (maxId - minId))
        # start = end - int(0.0001 * (maxId - minId))
        l: list[PIIIntermediateUnit] = transformer.getPIIIntermediateWithIdrange(start, end)
        logger.info(f"number of test pii:{len(l)}")

        total = len(l)
        index = 0
        success = 0
        saveLimit = 0  # maximum number of save files
        newlyGenerated = 0
        alreadyGenerated = 0
        successPwList = list()
        failPwList = list()
        successRepDict = dict()  # success guesses with frequency

        # PIIListLock = threading.Lock
        def searchStrInList(s: str, l: list[str]) -> bool:
            d = {i: k for k, i in enumerate(l)}
            if s in d:
                return True
            else:
                return False

        def saveGuesses(l: list[str], savePath: str):
            with open(savePath, "w") as f:
                for s in l:
                    f.write(f"{s}\n")

        for unit in l:
            h = unit.getHashBytes()
            hStr = binascii.hexlify(h).decode('utf8')
            pii, pwStr = transformer.transformIntermediateToPIIAndPw(unit)

            outputFile = filePattern.format(pwStr + "_" + unit.fullName)

            generator.generateForPII(pii=pii, outputFile=None, nameFuzz=True)
            guesses = copy(generator.guesses)

            # match guesses and pwStr
            if searchStrInList(pwStr, guesses):
                success += 1
                successPwList.append(pwStr)
            else:
                failPwList.append(pwStr)
                if saveLimit > 0:
                    saveGuesses(guesses, outputFile)
                    saveLimit -= 1

            index += 1
            if index % 100 == 0:
                logger.info(f"Test progress: {index}/{total}, {100 * (index / total):.2f}")
            ProgressTracker.progress = index
            ProgressTracker.limit = total

        logger.info(f"Guess file newly generated:{newlyGenerated},already exists:{alreadyGenerated}")
        logger.info(f"Test complete. success:{success}/{total}, accuracy:{success / total:.4f}")
        logger.info(f"successList:{successPwList[:10]}...\nfail list:{failPwList[:10]}...")

    def test_output_clf(self):
        generator: GeneralPIIPatternGenerator = GeneralPIIPatternGenerator.getInstance("../../save_general.clf")
        # export_graphviz(generator.clf.getClf().estimators_[0],out_file="./graph.dot")
        # graph = graphviz.Source(dot_data)
        text = tree.export_text(generator.clf.getClf().estimators_[0])
        with open("../Tests/tree_text.txt", "w") as f:
            f.write(text)


class ProgressTracker:
    progress = 0
    limit = 100

    @classmethod
    def updateProgress(cls, current, total, proportion: float, base: float):
        cls.progress = current / total * proportion * cls.limit + base * cls.limit


class BuildDatabase(TestCase):
    def test_rebuild(self):
        """Rebuild all datatables
        """
        ProgressTracker.progress = 0
        ProgressTracker.limit = 100

        logger.info(f"Start addressing dataset...")
        self.test_build()
        logger.info(f"Finish addressing dataset")
        logger.info(f"Start generating datatables...")
        time.sleep(1)
        self.test_generate_frequency_tables()
        logger.info(f"Finish generating datatables")
        logger.info(f"Start resolving representations and build unique datatable...")
        time.sleep(1)
        self.test_build_general_unique()
        logger.info(f"\nRebuild complete!")

    def buildGeneralPwRepresentationTable(self):
        """
        Build `pwrepresentation_general` table based on `pii` dataset.
        Parse all representations of password and store in `pwrepresentation_general` datatable.
        """
        ProgressTracker.progress = 0

        processor = PIIPreprocessor(initDataset=PIIDataTypes.PIIDataSet(), start=0, limit=-1)
        processor.preprocess()
        dataset = processor.getDataSet()
        # for unit in iter(dataset):
        #     logger.info(str(unit))
        logger.info(f"Total: {dataset.row}")
        logger.info(f"keyList:{dataset.keyList}")

        transformer: GeneralPwRepresentationTransformer = GeneralPwRepresentationTransformer.getInstance()
        transformer.queryMethods.DeleteAll()
        datasetIter: typing.Iterable[PIIDataUnit] = iter(dataset)
        i = 0
        repCount = 0
        updateCount = 0
        exceptionCount = 0
        timeUseList: list[float] = list()

        threadpool = ThreadPoolExecutor(max_workers=10)
        countLock = threading.Lock()
        futureList = list()

        def parsePII(unit: PIIDataUnit) -> (int, int):
            pii = unit.pii
            repCount = 0
            exceptionCount = 0
            try:
                piiParser = GeneralPIIStructureParser(pii)
                piiStructure = piiParser.getGeneralPIIStructure(pwStr=unit.password)
                for rep in piiStructure.repList:
                    pr = transformer.transformParseunitToBaseunit(pwStr=unit.password, rep=rep)
                    try:
                        transformer.Insert(pr)
                        repCount += 1
                    except Exception as e:
                        logger.info(f"Exception occur: {str(e)}, pr: {str(pr)}")
                        exceptionCount += 1
                    finally:
                        return repCount, exceptionCount
            except Exception as e:
                logger.info(f"Exception occur: {str(e)}")
                exceptionCount += 1
            finally:
                return repCount, exceptionCount

        t1 = time.time()
        for unit in datasetIter:
            futureList.append(threadpool.submit(parsePII, unit))
            i += 1
            if i % 500 == 0:
                logger.info(f"Submit progress:{i}/{dataset.row}({(i / dataset.row) * 100:.2f})")

        oldTime = time.time()
        logger.info(f"Submit tasks take:{int(oldTime - t1)}s")
        i = 0
        for future in concurrent.futures.as_completed(futureList):
            repCountAdd, exceptionCountAdd = future.result()
            repCount += repCountAdd
            exceptionCount += exceptionCountAdd
            i += 1
            if i % 500 == 0:
                timeUse = (time.time() - oldTime)
                timeUseList.append(timeUse)
                remainSec = (dataset.row - i) / 500 * (sum(timeUseList) / len(timeUseList))
                logger.info(
                    f"Progress:{i}/{dataset.row} ({(i / dataset.row * 100):.2f}%), remain time:{int(remainSec) // 60}m{int(remainSec) % 60}s")
                oldTime = time.time()
            ProgressTracker.updateProgress(i, dataset.row, 0.3, 0)

        logger.info(
            f"Completed! Total password:{i}, total item:{repCount}, update item:{updateCount}, total exception:{exceptionCount}")
        threadpool.shutdown()

    def test_build(self):
        self.buildGeneralPwRepresentationTable()

    def test_generate_frequency_tables(self):
        """Generate three datatable: `representation_frequency_base_general`, `pwrepresentation_frequency_general`, `representation_frequency_general`
        """
        transformers = list()
        transformers.append(GeneralRepFrequencyBaseTransformer.getInstance())
        ProgressTracker.updateProgress(1, 3, 0.3, 0.3)
        transformers.append(GeneralRepFrequencyTransformer.getInstance())
        ProgressTracker.progress += 1
        transformers.append(GeneralPwRepFrequencyTransformer.getInstance())
        ProgressTracker.progress += 1
        for t in transformers:
            t.rebuild()
        logger.info(f"Re-generate Complete")

    def test_build_general_unique(self):
        """Build unique datatable
        """
        resolver: GeneralPIIRepresentationResolver = GeneralPIIRepresentationResolver.getInstance()
        transformer: GeneralPwRepUniqueTransformer = GeneralPwRepUniqueTransformer.getInstance()

        transformer.queryMethods.DeleteAll()

        exceptionCount = 0
        i = 0

        pwRepDict: dict[str, RepUnit] = resolver.resolve()
        _len = len(pwRepDict)
        logger.info(f"Resolved:{_len}")

        executor = ThreadPoolExecutor()
        futureList = list()

        def insertUnit(pwStr: str, repUnit: RepUnit) -> int:
            exceptionCount = 0
            try:
                unit: PwRepUniqueUnit = DatabaseUtils.getGeneralIntermediateFromRepUnit(pwStr, repUnit)
                transformer.Insert(unit)
            except Exception as e:
                logger.info(f"Exception occur: {str(e)}, pwStr: {pwStr}, RepUnit:{str(repUnit)}")
                exceptionCount += 1
            finally:
                return exceptionCount

        i = 0
        for pwStr, repUnit in pwRepDict.items():
            futureList.append(executor.submit(insertUnit, pwStr, repUnit))
            i += 1
            if i % 100 == 0:
                logger.info(f"Submit progress:{i}/{_len}({(i / _len) * 100:.2f})")

        i = 0
        for future in concurrent.futures.as_completed(futureList):
            exceptionCountAdd = future.result()
            exceptionCount += exceptionCountAdd
            i += 1
            if i % 100 == 0:
                logger.info(f"Progress:{i}/{_len} ({(i / _len * 100):.2f}%)")
            ProgressTracker.updateProgress(i, _len, 0.3, 0.6)

        logger.info(f"Completed! Total:{i}, total exception:{exceptionCount}")
        executor.shutdown()


class TestGeneralPIIStructureParser(TestCase):
    def test_parse_all_general_vector_recursive(self):
        pii = BasicTypes.PII(account="yhang0607",
                             name="yhangzhongjie",
                             firstName="yhang",
                             givenName="zhong jie",
                             birthday="19820607",
                             phoneNum="13222245678",
                             email="3501111asd11@qq.com",
                             idcardNum="1213213213")
        pw1 = "qwe123ryhang0607yuiyzj123wqer!@#"
        parser = GeneralPIIStructureParser(pii)
        piiParser = PIIStructureParser(pii)

        s: GeneralPIIStructure = parser.getGeneralPIIStructure(pw1)
        # logger.info(f"{json.dumps(s._tojson(),indent=2)}")

        strParser: GeneralPIIRepresentationStrParser = GeneralPIIRepresentationStrParser.getInstance()
        for rep in s.repList:
            logger.info(f"{strParser.representationToStr(rep)}\n")

        logger.info(f"\nPIIParser:\n")
        piiS: PIIStructure = piiParser.getPwPIIStructure(pw1)

        piiStrParser: PIITagRepresentationStrParser = PIITagRepresentationStrParser.getInstance()
        for rep in piiS.piiRepresentationList:
            logger.info(f"{piiStrParser.representationToStr(rep)}\n")

    def test_pii_structure_parser(self):
        piiUnit: PIIUnit = PIIUnit(email="o0oo0o5353@vip.qq.com",
                                   account="o0oo0o5353",
                                   name="刘璋",
                                   idCard="412301198604044512",
                                   phoneNum="15503708389",
                                   password="o0oo0o0000",
                                   fullName="liu zhang")
        pii, pwStr = Utils.parsePIIUnitToPIIAndPwStr(piiUnit)
        logger.info(pii.__dict__)
        # pw = "qq763699438"
        # pw = "ty333763699438"
        # pw = "haijing0325"
        pw = pwStr

        parser: GeneralPIIStructureParser = GeneralPIIStructureParser(pii=pii)
        struct: GeneralPIIStructure = parser.getGeneralPIIStructure(pw)
        repParser: GeneralPIIRepresentationStrParser = GeneralPIIRepresentationStrParser.getInstance()

        tagParser: PIIFullTagParser = PIIFullTagParser(pii, nameFuzz=True)
        tagParser.parseTag()
        tagList: list[Tag] = tagParser.getTagContainer().getTagList()
        for tag in tagList:
            logger.info(f"{tag.__dict__}")

        logger.info(f"Rep:{len(struct.repList)}")

        for rep in struct.repList[:10]:
            s = repParser.representationToStr(rep)
            logger.info(f"{s}")

    def test_pii_tag_container(self):
        pii = BasicTypes.PII(account="",
                             name="",
                             firstName="yhang",
                             givenName="zhong jie",
                             birthday="",
                             phoneNum="13222245678",
                             email="",
                             idcardNum="")
        parser: PIIFullTagParser = PIIFullTagParser(pii, nameFuzz=True)
        parser.parseTag()
        d: dict = parser.getTagContainer().getTagDict()
        logger.info(len(d))
        for k, v in d.items():
            logger.info(f"{k}:{v}")
