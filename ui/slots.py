import functools
import json
import os.path
import sys
import threading
import time
import traceback
from logging import LogRecord
from queue import Queue

from PyQt5.QtCore import pyqtSignal, Qt, QThread, QObject, pyqtSlot
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QLabel
from sqlalchemy import create_engine
from sqlalchemy.engine import reflection
from sqlalchemy.exc import OperationalError

from Generators.GeneralPIIGenerators import *
from Generators.PasswordGuessGenerator import *
from Parser import Config
from Parser.DatasetParser import CsvDatasetLoader
from Scripts import databaseInit, main_General_PII_Mode
from Scripts.main_General_PII_Mode import BuildDatabase, GeneralPIITrainMain
from ui.mainWindow import *


class Consumer(threading.Thread):
    def __init__(self, queue: Queue, handler: typing.Callable):
        super().__init__()
        self.queue = queue
        self.handler = handler  # function

    def run(self) -> None:
        while True:
            s: str = self.queue.get()
            self.handler(s)
            time.sleep(0.5)


class TrainModelStatus:
    def __init__(self, label: QLabel):
        self.label: QLabel = label
        self.passed = False

    def setPass(self):
        self.label.setStyleSheet("color: green")
        self.label.setText("Pass")
        self.passed = True

    def setFail(self):
        self.label.setStyleSheet("color: red")
        self.label.setText("Fail")
        self.passed = False

    def getStatus(self) -> bool:
        return self.passed


class TaskRecorder:
    def __init__(self):
        self.task = None
        self.lock = threading.Lock()

    def get_task(self):
        return self.task

    def set_task(self, task: str):
        with self.lock:
            self.task = task

    def set_empty(self):
        with self.lock:
            self.task = ""

    def is_empty(self) -> bool:
        if self.task is None or len(self.get_task()) <= 0:
            return True
        else:
            return False


def release_current_task_record_func(f):
    def wrapper(*args, **kwargs):
        result = None
        try:
            result = f(*args, **kwargs)
        finally:
            if result is not False:  # return False to avoid set empty
                Slots.currentTask.set_empty()
        return result

    return wrapper


class ProgressBarWorker(QObject):
    changed = pyqtSignal(int)

    def __init__(self, progressBarObj: QProgressBar):
        super().__init__()
        self.progressBar: QProgressBar = progressBarObj
        self.changed.connect(self.progressBar.setValue)

    def updateValue(self, value):
        self.changed.emit(value)


class PatternGenerateProgressBarWorker(QObject):
    patternGenerateProgressBarChanged = pyqtSignal(int)

    def __init__(self, progressBarObj: QProgressBar):
        super().__init__()
        self.progressBar: QProgressBar = progressBarObj
        self.patternGenerateProgressBarChanged.connect(self.progressBar.setValue)

    def updateValue(self, value):
        self.patternGenerateProgressBarChanged.emit(value)


class TextBrowserWorker(QObject):
    appendSignal = pyqtSignal(str)
    clearSignal = pyqtSignal()
    # MaxContentLen = 5000  # max character of textbrowser
    MaxLineNum = 200

    def __init__(self, textbrowser: QTextBrowser):
        super().__init__()
        self.textbrowser: QTextBrowser = textbrowser
        # self.content_length = 0
        self.lineNum = 0
        self.appendSignal.connect(self.update_text_browser)
        self.clearSignal.connect(self.clean_text_browser)

    @pyqtSlot(str)
    def update_text_browser(self, s: str):
        self.textbrowser.append(s)

    @pyqtSlot()
    def clean_text_browser(self):
        self.textbrowser.clear()

    def clear(self):
        self.clearSignal.emit()

    def append(self, text: str):
        self.appendSignal.emit(text)
        self.lineNum += 1
        if self.lineNum > TextBrowserWorker.MaxLineNum:
            self.clear()
            self.lineNum = 0


class TextBrowserHandler(logging.Handler):
    """Bind a certain logger into a certain textbrowser

    """
    MaxSingalSize = 300  # max character per append request

    def __init__(self, textbrowserWorker: TextBrowserWorker):
        super().__init__()
        self.textbrowserWorker: TextBrowserWorker = textbrowserWorker
        self.lineNum = 0

    def emit(self, record: LogRecord) -> None:
        msg = self.format(record)
        msg = msg[:TextBrowserHandler.MaxSingalSize] + "......" if len(msg) > TextBrowserHandler.MaxSingalSize else msg
        self.textbrowserWorker.append(msg)
        # self.lineNum += 1
        # if self.lineNum > TextBrowserHandler.MaxLineNum:
        #     t = self.textbrowser.toPlainText()
        #     self.textbrowser.setPlainText(t[-TextBrowserHandler.MaxTotalSize:])
        #     self.lineNum = 0


class Slots:
    currentTask = TaskRecorder()  # record current running task name
    Task = release_current_task_record_func  # release current task

    def __init__(self, mainWindow: Ui_MainWindow) -> None:
        self.patterns: list[str] = list()
        self.guessLimitOptions = ['500', '1000', '2000', '3000', '5000']
        self.guessLimit: int = 0  # guess limit
        self.guesses: list[str] = list()
        self.outputFile = "guess_test.txt"
        self.patternFile = "patterns_general.txt"
        self.pii: PII = None
        self.guessGenerator: GeneralPasswordGenerator = None
        self.progressSignal = pyqtSignal(int)

        # guess generator tab
        self.mainWindow: Ui_MainWindow = mainWindow
        self.mainWindow.fileBrowserBtn.clicked.connect(self.openPatternFileSlot)
        self.mainWindow.patternFileEdit.textChanged.connect(self.patternFileEditChangedSlot)
        self.mainWindow.loadBtn.clicked.connect(self.loadPatternSlot)
        self.mainWindow.limitComboBox.currentTextChanged.connect(self.setLimitOptionSlot)
        self.mainWindow.outputBrowser.clicked.connect(self.selectOutputFileSlot)
        self.mainWindow.generateBtn.clicked.connect(self.generateBtnSlot)
        self.mainWindow.loadPIIBtn.clicked.connect(self.loadPIIJsonSlot)
        self.mainWindow.outputEdit.setText(self.outputFile)
        self.mainWindow.patternFileEdit.setText(self.patternFile)

        self.buildLimitComboBox()
        # self.buildUsage()

        # pattern generator tab
        self.clsFile = ""
        self.patternSavePath = "patterns.txt"
        self.patternGenerateLimit = 0
        self.patternLimitOptions = ['100', '500', '1000', '2000']
        self.patternGenerator: GeneralPIIPatternGenerator = None
        self.patternProgressThreadExitFlag = threading.Event()

        self.print_log_queue: Queue = Queue(100)
        self.error_dialog_queue: Queue = Queue(100)
        self.info_dialog_queue: Queue = Queue(100)
        self.print_log_consumer = Consumer(self.print_log_queue, self.handle_print_log_signal)
        self.error_dialog_consumer = Consumer(self.error_dialog_queue, self.handle_error_signal)
        self.info_dialog_consumer = Consumer(self.info_dialog_queue, self.handle_info_signal)
        self.print_log_consumer.start()
        self.error_dialog_consumer.start()
        self.info_dialog_consumer.start()

        self.mainWindow.patternOutputEdit.setText(self.patternSavePath)
        self.mainWindow.loadClfBtn.clicked.connect(self.loadClfSlot)
        self.mainWindow.clfFileBrowserBtn.clicked.connect(self.openClfFileSlot)
        self.mainWindow.patternSaveBrowserBtn.clicked.connect(self.selectPatternOutputSlot)
        self.mainWindow.patternLimitComboBox.addItems(self.patternLimitOptions)
        self.mainWindow.patternGenerateBtn.clicked.connect(self.generatePatternBtnSlot)

        # train model tab

        self.databaseUrl = ""
        self.sqlFile = ""
        self.piiFile = ""
        self.clfSavePath = "save_test.clf"
        self.assessPatternFile = "patterns.txt"
        self.connectDatabaseStatus = TrainModelStatus(self.mainWindow.connectDatabaseLabel)
        self.initDatabaseStatus = TrainModelStatus(self.mainWindow.initDatabaseStatusLabel)
        self.loadPIIDataStatus = TrainModelStatus(self.mainWindow.loadPIIDataStatusLabel)
        self.analyzePIIDataStatus = TrainModelStatus(self.mainWindow.analyzePIIStatusLabel)
        self.trainModelStatus = TrainModelStatus(self.mainWindow.trainModelStatusLabel)
        self.assessStatus = TrainModelStatus(self.mainWindow.assessStatusLabel)
        self.trainStatusList = [self.connectDatabaseStatus, self.initDatabaseStatus, self.loadPIIDataStatus,
                                self.analyzePIIDataStatus
            , self.trainModelStatus, self.assessStatus]
        self.engine = None  # database engine
        self.logFormater = logging.Formatter('%(asctime)s - %(message)s', '%Y-%m-%d %H:%M:%S')
        self.loadPIIDataProgressExitFlag = threading.Event()
        self.analyzePIIDataProgressExitFlag = threading.Event()
        self.trainModelProgressExitFlag = threading.Event()
        self.assessProgressExitFlag = threading.Event()

        @Slots.Task
        def on_task_finished():
            if not self.currentTask.is_empty():
                task_name = self.currentTask.get_task()
                self.currentTask.set_empty()
                self.patchInfoDialog(f"[{task_name}] finished!")

        self.on_task_finished = on_task_finished

        self.mainWindow.checkDbConnBtn.clicked.connect(self.checkDbConnBtnSlot)
        self.mainWindow.sqlFileBrowser.clicked.connect(self.sqlFileBrowserBtnSlot)
        self.mainWindow.piiFileBrowser.clicked.connect(self.piiFileBrowserBtnSlot)
        self.mainWindow.clfSaveBtn.clicked.connect(self.clfSaveBrowserBtnSlot)
        self.mainWindow.clfSaveEdit.setText(self.clfSavePath)
        self.mainWindow.assessPatternFileEdit.setText(self.assessPatternFile)
        self.mainWindow.assessPatternFileBrowserBtn.clicked.connect(self.assessPatternFileBrowserBtnSlot)
        self.mainWindow.initDatabaseBtn.clicked.connect(self.initDatabaseBtnSlot)
        self.mainWindow.initDatabaseBtn.adjustSize()
        self.mainWindow.loadPIIDataBtn.clicked.connect(self.loadPIIDataBtnSlot)
        self.mainWindow.loadPIIDataBtn.adjustSize()
        self.mainWindow.analyzePIIBtn.clicked.connect(self.analyzePIIDataBtnSlot)
        self.mainWindow.analyzePIIBtn.adjustSize()
        self.mainWindow.trainModelBtn.clicked.connect(self.trainModelBtnSlot)
        self.mainWindow.trainModelBtn.adjustSize()
        self.mainWindow.assessBtn.clicked.connect(self.assessAccuracyStatusBtnSlot)
        self.mainWindow.assessBtn.adjustSize()
        self.mainWindow.checkStatusBtn.clicked.connect(self.checkDbStatusBtnSlot)
        self.mainWindow.checkStatusBtn.adjustSize()

        self.mainWindow.trainTabTextBrowser.textChanged.connect(
            functools.partial(self.auto_scroll_textbrowser, self.mainWindow.trainTabTextBrowser))
        # self.mainWindow.trainTabTextBrowser.setMaximumBlockCount(5000)

        self.mainWindow.trainTabTextBrowser.ensureCursorVisible()

        self.trainTabTextbrowserWorker = TextBrowserWorker(self.mainWindow.trainTabTextBrowser)
        self.patternTabTextbrowserWorker = TextBrowserWorker(self.mainWindow.patternTextBrowser)
        self.guessTabTextbrowserWorker = TextBrowserWorker(self.mainWindow.guessTabTextBrowser)

        self.trainTabProgressBarWorker = ProgressBarWorker(self.mainWindow.trainTabProgressBar)
        self.patternGenerateProgressBarWorker = ProgressBarWorker(self.mainWindow.patternProgressBar)
        self.guessGenerateProgressBarWorker = ProgressBarWorker(self.mainWindow.progressBar)

        self.initAllStatus()
        self.redirect_logger()

        self.registerErrorHandler()

    def registerErrorHandler(self):
        import sys
        sys._excepthook = sys.excepthook

        def exception_hook(exc_type, exc_value, exc_traceback):
            self.patchDialog(f"Unhandled Exception occurred:\n{exc_type}: {exc_value}\n{exc_traceback}")
            if exc_type is KeyboardInterrupt:
                sys.__excepthook__(exc_type, exc_value, exc_traceback)

        sys.excepthook = exception_hook

    def exist_current_task(self) -> bool:
        """Check if there is current task running, patch dialog
        """
        if self.currentTask.is_empty():
            return False
        else:
            self.patchInfoDialog(f"Task [{self.currentTask.get_task()}] is running, please wait")
            return True

    def auto_scroll_textbrowser(self, textbrowser: QTextBrowser):
        textbrowser.verticalScrollBar().setValue(textbrowser.verticalScrollBar().maximum())

    def redirect_logger(self):
        """Redirect and format loggers into textbrowser
        """
        handler = TextBrowserHandler(self.trainTabTextbrowserWorker)
        self.trainTabLogHandler = handler
        handler.setFormatter(self.logFormater)
        databaseInit.logger.addHandler(handler)
        main_General_PII_Mode.logger.addHandler(handler)

    def handle_error_signal(self, msg):
        self.patchDialog(msg)

    def handle_print_log_signal(self, msg):
        self.printPatternLog(msg)

    def handle_info_signal(self, msg):
        self.patchDialog(msg, title="Success",
                         icon=QMessageBox.Information)

    '''
    Guess generation tab
    '''

    def buildUsage(self):
        usage = \
            '''
            Welcome to RFGuess!
            Usage:
            1. Select a pattern file and load
            2. Assign an output file to store password guesses and limitation of guess number
            3. Fill PII data
            4. Click 'Generate'!
            '''
        self.mainWindow.usageTextBrowser.setText(usage)

    def loadPIIJsonSlot(self) -> bool:
        self.piijsonFile = ""
        file_dialog = QFileDialog()
        file_dialog.selectFile("pii.json")  # init filename
        file_dialog.setNameFilters(["JSON files (*.json)"])
        self.piijsonFile, _ = file_dialog.getOpenFileName(self.mainWindow.mainWindow, "Select pii json")
        try:
            with open(self.piijsonFile, "r", encoding='utf8', errors='ignore') as f:
                self.piijson = json.load(f)

            self.pii = PII.create(idCard=self.piijson['idCard'],
                                  email=self.piijson['email'],
                                  phoneNum=self.piijson['phoneNum'],
                                  account=self.piijson['account'],
                                  fullname=self.piijson['name'])

            self.mainWindow.idCardEdit.setText(self.pii.idcardNum)
            self.mainWindow.emailEdit.setText(self.pii.email)
            self.mainWindow.accountEdit.setText(self.pii.account)
            self.mainWindow.fullNameEdit.setText(self.pii.name)
            self.mainWindow.phoneEdit.setText(self.pii.phoneNum)
            self.mainWindow.dateEdit.setText(self.pii.birthday)
            # self.mainWindow.dateEdit.setDate(QDate.fromString(self.pii.birthday, "%Y%m%d"))
            self.patchDialog(f"load pii successful", title="Success", icon=QMessageBox.Information)
            return True

        except Exception as e:
            self.patchDialog(f"Exception when load pii json:{e}")
            return False

    def buildLimitComboBox(self):
        self.mainWindow.limitComboBox.addItems(self.guessLimitOptions)

    def getPII(self) -> bool:
        idCard = self.mainWindow.idCardEdit.text()
        if idCard is None or len(idCard) <= 0:
            pass
            # self.patchDialog("IdCard cannot be empty")
            # return False
        email = self.mainWindow.emailEdit.text()
        if email is None or len(email) <= 0:
            pass
            # self.patchDialog("Email cannot be empty")
            # return False
        account = self.mainWindow.accountEdit.text()
        if account is None or len(account) <= 0:
            pass
            # self.patchDialog("Account cannot be empty")
            # return False
        name = self.mainWindow.fullNameEdit.text()
        if name is None or len(name) <= 0:
            pass
            # self.patchDialog("fullname cannot be empty")
            # return False
        phoneNum = self.mainWindow.phoneEdit.text()
        if phoneNum is None or len(phoneNum) <= 0:
            pass
            # self.patchDialog("phoneNum cannot be empty")
            # return False
        birthday = self.mainWindow.dateEdit.text()
        if birthday is None or len(birthday) <= 0:
            pass
            # self.patchDialog("birthday cannot be empty")
            # return False

        fullname = pinyinUtils.getFullName(name)
        self.pii = PII.create(idCard=idCard,
                              email=email,
                              phoneNum=phoneNum,
                              account=account,
                              fullname=fullname)
        self.pii.birthday = birthday.replace("/", "")
        return True

    def updateGuessGenerateProgressBar(self, value):
        self.guessGenerateProgressBarWorker.updateValue(value)

    def generateBtnSlot(self):
        if not self.getPII():
            return
        if self.patternFile == None or len(self.patternFile) <= 0:
            self.patchDialog("Please assign a pattern file")
            return
        if self.outputFile == None or len(self.outputFile) <= 0:
            self.patchDialog("Please assign an output file path")
            return
        if self.guessLimit <= 0:
            self.patchDialog(f"Invalid limit value: {self.guessLimit}")
            return
        if len(self.patterns) <= 0:
            self.patchDialog(f"There is no pattern loaded")
            return
        self.printGuessLog(f"PII Data:{self.pii.__dict__}")
        self.printGuessLog(f"Start generating guesses")
        self.generateGuess()

    def generateGuess(self):
        self.guessGenerator.patternFile = self.patternFile
        self.guessGenerator.init()
        self.printGuessLog(f"Preparing PII tag container...")
        self.guessGenerator.pii = self.pii
        self.guessGenerator.outputFile = self.outputFile
        self.guessGenerator.piiTagContainer = PIITagContainer(pii=self.guessGenerator.pii, nameFuzz=True)
        self.guessGenerator.piiTagContainer.parse()
        self.guessGenerator.tagDict = self.guessGenerator.piiTagContainer.getTagDict()  # specified pii type to string

        self.guessGenerator.eliminatePatternDatagrams()
        self.printGuessLog(
            f"Number of patterns after eliminating: {len(self.patterns)}, remove: {len(self.guessGenerator.initPatterns) - len(self.patterns)}")

        self.printGuessLog(f"Start generating guesses...")

        _len = len(self.guessGenerator.patterns)
        _max = min(_len, self.guessLimit)
        _i = 0
        _progress = 0
        for dg in self.guessGenerator.patterns:
            guesses: list[str] = self.guessGenerator.generateGuessFromPatternDatagram(dg)
            self.guessGenerator.guesses += guesses
            if len(self.guessGenerator.guesses) >= self.guessLimit:
                break
            _progress = min(int(len(self.guessGenerator.guesses) / _max * 100), 100)
            # self.mainWindow.progressBar.setValue(_progress)
            self.updateGuessGenerateProgressBar(_progress)

        primaryLen = len(self.guessGenerator.guesses)
        self.guesses = self.guessGenerator.eliminateDuplicateGuess()
        newLen = len(self.guessGenerator.guesses)
        self.printGuessLog(f"Generating complete, number of guesses: {primaryLen}")
        self.printGuessLog(f"Eliminate guesses: remove {primaryLen - newLen} duplicates, final guess number: {newLen}")
        if self.guessGenerator.outputFile != None and len(self.guessGenerator.outputFile) > 0:
            self.guessGenerator.save()
        self.printGuessLog(f"Complete!\nCount:{newLen}\nSaved to {self.outputFile}\n")
        self.patchDialog(f"Complete!\nCount:{newLen}\nSaved to {self.outputFile}\n", title="Generate Guesses Complete",
                         icon=QMessageBox.Information)

    def setLimitOptionSlot(self):
        limitStr = self.mainWindow.limitComboBox.currentText()
        self.guessLimit = int(limitStr)

    def openPatternFileSlot(self):
        self.patternFile = ""
        file_dialog = QFileDialog()
        self.patternFile, _ = file_dialog.getOpenFileName(self.mainWindow.mainWindow, "Select pattern file")
        self.mainWindow.patternFileEdit.setText(self.patternFile)

    def selectOutputFileSlot(self):
        self.outputFile = ""
        file_path, _ = QFileDialog.getSaveFileName(self.mainWindow.mainWindow, "Save File", "", "Text Files (*.txt)")
        self.outputFile = file_path
        self.mainWindow.outputEdit.setText(self.outputFile)

    def patchDialog(self, content: str, title: str = "Error", icon=QMessageBox.Critical):
        """Patch an error dialog
        """
        error_box = QMessageBox()
        error_box.setIcon(icon)
        error_box.setText(content)
        error_box.setWindowTitle(title)
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.exec_()

    def questionDialog(self, content: str, title: str = "Confirmation") -> bool:
        """Patch a question dialog and get Y/N
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setText(content)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        result = msg_box.exec_()
        if result == QMessageBox.Yes:
            return True
        else:
            return False

    def patchInfoDialog(self, content: str):
        self.patchDialog(content, title="Success", icon=QMessageBox.Information)

    def printGuessLog(self, s: str):
        """Log output for Guess generation tab
        """
        cur = datetime.datetime.now()
        timeStr = datetime.datetime.strftime(cur, "%Y-%m-%d %H:%M:%S")
        # self.mainWindow.textBrowser.append(f"[{timeStr}] {s}")
        self.guessTabTextbrowserWorker.append(f"[{timeStr}] {s}")

    def excepthook(t, value, traceback):
        """Self-defined global exception handler
        """
        # Create a QMessageBox to display the exception details
        error_msg_box = QMessageBox()
        error_msg_box.setIcon(QMessageBox.Warning)
        error_msg_box.setWindowTitle("Exception")
        error_msg_box.setText("An exception occurred:")
        error_msg_box.setInformativeText(str(value))
        error_msg_box.setDetailedText(traceback)
        error_msg_box.setStandardButtons(QMessageBox.Ok)
        error_msg_box.setDefaultButton(QMessageBox.Ok)
        error_msg_box.setWindowFlag(Qt.WindowStaysOnTopHint)
        error_msg_box.exec_()

        # Call the default exception handler
        sys.__excepthook__(t, value, traceback)

    '''
    Pattern generation tab
    '''

    def updatePatternProgressBar(self, value):
        # self.mainWindow.patternProgressBar.valueChanged.emit(value)
        self.patternGenerateProgressBarWorker.updateValue(value)

    def printPatternLog(self, s: str):
        """Log output for Pattern generation tab
        """
        cur = datetime.datetime.now()
        timeStr = datetime.datetime.strftime(cur, "%Y-%m-%d %H:%M:%S")
        # self.mainWindow.patternTextBrowser.append(f"[{timeStr}] {s}")
        self.patternTabTextbrowserWorker.append(f"[{timeStr}] {s}")

    class generatePatternWorker(QThread):
        def __init__(self, obj):
            super().__init__()
            self.obj = obj

        def run(self) -> None:
            try:
                self.obj.generatePattern()
            except Exception as e:
                return
                # self.obj.error_dialog_queue.put(f"Exception occur: {e}")
            finally:
                self.obj.endPatternProgressTracking()
                # self.finished.emit()

    def generatePatternBtnSlot(self):
        if self.exist_current_task():
            return False
        if self.patternGenerator is None:
            self.patchDialog(f"Classifier not loaded")
            return
        if self.patternSavePath is None or len(self.patternSavePath) <= 0:
            self.patchDialog(f"Please assign a pattern save file")
            return
        self.patternGenerateLimit = int(self.mainWindow.patternLimitComboBox.currentText())
        self.startPatternProgressTracking()
        self.patternWorker = self.generatePatternWorker(self)

        # @Slots.Task
        # def on_task_finished():
        #     self.patchInfoDialog(f"Generate Pattern finish!")

        self.printPatternLog(f"Start generating patterns to {self.patternSavePath}... Please wait")
        self.currentTask.set_task("Generate Pattern")
        self.patternWorker.finished.connect(self.on_task_finished)
        self.patternWorker.start()

    def generatePattern(self):
        l = list()
        l = self.patternGenerator.getPatternStrList(limit=self.patternGenerateLimit)
        with open(self.patternSavePath, "w", encoding="utf8", errors='ignore') as f:
            for i in range(len(l)):
                f.write(f"{l[i]}\n")
        self.print_log_queue.put(f"Pattern generation complete: {len(l)}, saved to {self.patternSavePath}")
        # self.info_dialog_queue.put(f"Pattern generation complete: {len(l)}, saved to {self.patternSavePath}")

    def startPatternProgressTracking(self):
        """Track pattern generating progress
        """

        def trackProgress():
            self.patternProgressThreadExitFlag.clear()
            while not self.patternProgressThreadExitFlag.is_set():
                limit = self.patternGenerator.patternGenerateLimit
                progress = self.patternGenerator.patternGenerateProgress
                proportion = min(int(progress / limit * 100), 100)
                self.updatePatternProgressBar(proportion)
                time.sleep(0.5)
            limit = self.patternGenerator.patternGenerateLimit
            progress = self.patternGenerator.patternGenerateProgress
            proportion = min(int(progress / limit * 100), 100)
            self.updatePatternProgressBar(proportion)

        self.patternProgressThread = threading.Thread(target=trackProgress)
        self.patternProgressThread.start()

    def endPatternProgressTracking(self):
        self.patternProgressThreadExitFlag.set()

    def openClfFileSlot(self):
        self.clsFile = ""
        file_dialog = QFileDialog()
        self.clsFile, _ = file_dialog.getOpenFileName(self.mainWindow.mainWindow, "Select clf file (.clf)")
        self.mainWindow.clfFileEdit.setText(self.clsFile)

    def selectPatternOutputSlot(self):
        self.patternSavePath = ""
        self.patternSavePath, _ = QFileDialog.getSaveFileName(self.mainWindow.mainWindow, "Save Pattern File", "",
                                                              "Text Files (*.txt)")
        self.mainWindow.patternOutputEdit.setText(self.patternSavePath)

    def patternFileEditChangedSlot(self):
        newContent = self.mainWindow.patternFileEdit.text()

    def loadPatternSlot(self):
        patternFile = self.mainWindow.patternFileEdit.text()
        if not os.path.exists(patternFile):
            self.patchDialog(f"Pattern file: {patternFile} not exists")
        with open(patternFile, "r") as f:
            for line in f.readlines():
                line = line.strip()
                if len(line) > 0:
                    self.patterns.append(line)
        if len(self.patterns) <= 0:
            self.patchDialog(f"Empty pattern file: {patternFile}")
        else:
            self.patchDialog(f"Load patterns: {len(self.patterns)}", title="Success", icon=QMessageBox.Information)
            self.printGuessLog(f"Load patterns: {len(self.patterns)}")
            self.guessGenerator: GeneralPasswordGenerator = GeneralPasswordGenerator.getInstance(self.patternFile)

    def loadClfSlot(self):
        self.clsFile = self.mainWindow.clfFileEdit.text()
        if not os.path.exists(self.clsFile):
            self.patchDialog(f"Classifier file: {self.clsFile} not exists")
        try:
            self.patternGenerator = GeneralPIIPatternGenerator.getInstance(self.clsFile)
            self.printPatternLog(f"Load classifier object success")
            self.patchDialog(f"Load classifier object success", title="Success", icon=QMessageBox.Information)
        except Exception as e:
            self.patchDialog(f"Load classifier object failed: {e}")
            self.patternGenerator = None

    '''
    Train model tab
    '''

    def printTrainLog(self, s: str):
        """Log output for Train model tab
        """
        cur = datetime.datetime.now()
        timeStr = datetime.datetime.strftime(cur, "%Y-%m-%d %H:%M:%S")
        # self.mainWindow.trainTabTextBrowser.append(f"[{timeStr}] {s}")
        self.trainTabTextbrowserWorker.append(f"[{timeStr}] {s}")

    def setPhasePassed(self, status: TrainModelStatus):
        """Set status and phases before to Passed
        """
        i = self.trainStatusList.index(status)
        if i < 0:
            self.printTrainLog(f"Error when setPhasePassed: {status} not in list")
            return
        for _i in range(i + 1):
            self.trainStatusList[_i].setPass()

    def checkPhasePassed(self, status: TrainModelStatus) -> bool:
        """Check whether phase of status and before phases all Passed
        """
        i = self.trainStatusList.index(status)
        if i < 0:
            self.printTrainLog(f"Error when setPhasePassed: {status} not in list")
            return
        for _i in range(i + 1):
            if not self.trainStatusList[_i].getStatus():
                return False
        return True

    def checkDbConnBtnSlot(self):
        """Check database connection
        """
        self.databaseUrl = self.mainWindow.databaseUrlEdit.text()
        if len(self.databaseUrl) <= 0:
            self.patchDialog(f"Please input a valid database URL")
            return
        try:
            engine = create_engine(self.databaseUrl)
            self.engine = engine
            conn = engine.connect()
            conn.close()
            self.patchDialog(f"Connect to database successfully", title="Success", icon=QMessageBox.Information)
            Config.DatabaseUrl = self.databaseUrl
            databaseInit.update_engine(Config.DatabaseUrl)
            # databaseInit.engine = sqlalchemy.create_engine(url=Config.DatabaseUrl)
            self.setPhasePassed(self.connectDatabaseStatus)
            return
        except OperationalError as e:
            self.patchDialog(f"Fail to connect to database: {str(e)}")
            return

    def sqlFileBrowserBtnSlot(self):
        """Assign sql file
        """
        self.sqlFile = ""
        file_dialog = QFileDialog()
        self.sqlFile, _ = file_dialog.getOpenFileName(self.mainWindow.mainWindow, "Select sql file(.sql)")
        self.mainWindow.sqlFileEdit.setText(self.sqlFile)

    def piiFileBrowserBtnSlot(self):
        """Assign pii data file
        """
        self.piiFile = ""
        file_dialog = QFileDialog()
        self.piiFile, _ = file_dialog.getOpenFileName(self.mainWindow.mainWindow, "Select pii dataset(.txt)")
        self.mainWindow.piiFileEdit.setText(self.piiFile)

    def clfSaveBrowserBtnSlot(self):
        """Clf file save path
        """
        self.clfSavePath = ""
        file_dialog = QFileDialog()
        self.clfSavePath, _ = file_dialog.getSaveFileName(self.mainWindow.mainWindow, "Save clf model(.clf)", "",
                                                          "Clf Files (*.clf)")
        self.mainWindow.clfSaveEdit.setText(self.clfSavePath)

    def assessPatternFileBrowserBtnSlot(self):
        """Browser pattern file to assess
        """
        self.assessPatternFile = ""
        file_dialog = QFileDialog()
        self.assessPatternFile, _ = file_dialog.getOpenFileName(self.mainWindow.mainWindow, "Select pattern file(.txt)",
                                                                "", "Text Files (*.txt)")
        self.mainWindow.assessPatternFileEdit.setText(self.assessPatternFile)

    def initAllStatus(self):
        """init all status
        """
        for s in self.trainStatusList:
            s.setFail()

    def updateTrainTabProgressBar(self, value):
        # self.mainWindow.trainTabProgressBar.valueChanged.emit(value)
        self.trainTabProgressBarWorker.updateValue(value)

    def initDatabaseBtnSlot(self):
        """Import sql structure
        """
        if self.exist_current_task():
            return False
        self.currentTask.set_task("Init Database")
        try:
            if not self.checkPhasePassed(self.connectDatabaseStatus):
                if self.questionDialog(f"There is at least one phase before not passed, are you sure to proceed?"):
                    pass
                else:
                    return
            if self.sqlFile is None or len(self.sqlFile) <= 0:
                self.patchDialog(f"Please assign a sql structure file (.sql)")
                return
            self.sqlFile = self.mainWindow.sqlFileEdit.text()
            if not os.path.exists(self.sqlFile):
                self.patchDialog(f"Sql file not exists: {self.sqlFile}")
                return
            if self.engine is None:
                self.patchDialog(f"Please connect to database first!")
                return
            with open(self.sqlFile, "r", encoding="utf8", errors="ignore") as f:
                sql_statements = f.read()
            try:
                with self.engine.connect() as conn:
                    conn.execute(text(sql_statements))
            except Exception as e:
                self.patchDialog(f"Exception occur when import sql file to {self.databaseUrl}, {e}")
                self.printTrainLog(f"Exception occur when import sql file to {self.databaseUrl}, {e}")
                return
            self.patchDialog(f"Database initialized", title="Success", icon=QMessageBox.Information)
            self.printTrainLog(f"Database initialized from {self.sqlFile}")
            self.setPhasePassed(self.initDatabaseStatus)
        finally:
            self.currentTask.set_empty()

    def loadPIIDataBtnSlot(self):
        """Load pii txt file into database
        """
        if self.exist_current_task():
            return False
        if not self.checkPhasePassed(self.initDatabaseStatus):
            if self.questionDialog(f"There is at least one phase before not passed, are you sure to proceed?"):
                pass
            else:
                return
        self.charset = self.mainWindow.charsetEdit.text()
        if self.charset is None or len(self.charset) <= 0:
            self.printTrainLog(f"Invalid charset:'{self.charset}', using UTF-8 by default")
            self.charset = "utf-8"
        self.piiFile = self.mainWindow.piiFileEdit.text()
        if self.piiFile is None or len(self.piiFile) <= 0:
            self.patchDialog(f"Please assign pii file(.txt) first")
            return
        if not os.path.exists(self.piiFile):
            self.patchDialog(f"Pii file not exists: {self.piiFile}")
            return

        def startLoadPIIDataProgressTracking():
            self.loadPIIDataProgressExitFlag.clear()
            while not self.loadPIIDataProgressExitFlag.is_set():
                progress = databaseInit.ProgressTracker.load_pii_data_progress
                limit = databaseInit.ProgressTracker.load_pii_data_limit
                proportion = int(progress / limit * 100)
                self.updateTrainTabProgressBar(proportion)
                time.sleep(0.5)
            self.updateTrainTabProgressBar(100)

        progress_thread = threading.Thread(target=startLoadPIIDataProgressTracking)
        progress_thread.start()

        thread = QThread()

        def run():
            try:
                self.currentTask.set_task("Load PII Data")
                # databaseInit.LoadDataset(self.piiFile, start=0, limit=-1, clear=True, update=False)
                loader = CsvDatasetLoader()
                loader.clear_and_load_dataset(self.piiFile, charset=self.charset)
                self.setPhasePassed(self.loadPIIDataStatus)
                self.printTrainLog(f"Load pii data finished !")
                # self.patchInfoDialog(f"Load pii data success from {self.piiFile}")
            except Exception as e:
                self.printTrainLog(
                    f"Exception occurs when load pii data into database({self.databaseUrl}), Original Exception: {e}")
                # self.patchDialog(f"Load pii data failed, check exception log for more details")
                return
            finally:
                self.loadPIIDataProgressExitFlag.set()
                thread.finished.emit()  # must set

        # @Slots.Task
        # def on_task_finished():
        #     self.patchInfoDialog(f"Load PII Data finished!")

        thread.finished.connect(self.on_task_finished)
        thread.run = run
        thread.start()

        # thread = threading.Thread(target=run)
        # thread.start()
        self.printTrainLog(f"Reading PII Data... Please Wait")

    def analyzePIIDataBtnSlot(self):
        """Build all datatables
        """
        if self.exist_current_task():
            return False
        if not self.checkPhasePassed(self.loadPIIDataStatus):
            if self.questionDialog("There is at least one phase before not passed, are you sure to proceed?"):
                pass
            else:
                return

        def startAnalyzePIIDataProgressTrack():
            self.analyzePIIDataProgressExitFlag.clear()
            while not self.analyzePIIDataProgressExitFlag.is_set():
                progress = main_General_PII_Mode.ProgressTracker.progress
                limit = main_General_PII_Mode.ProgressTracker.limit
                proportion = int(progress / limit * 100)
                # self.mainWindow.trainTabProgressBar.setValue(proportion)
                # self.mainWindow.trainTabProgressBar.valueChanged.emit(proportion)
                self.updateTrainTabProgressBar(proportion)
                time.sleep(0.5)
            self.updateTrainTabProgressBar(100)

        progress_thread = threading.Thread(target=startAnalyzePIIDataProgressTrack)
        progress_thread.start()

        thread = QThread()

        def run():
            try:
                # for i in range(10000):
                #     main_General_PII_Mode.logger.info("A" * 1000)
                #     main_General_PII_Mode.logger.info(
                #         str(len(self.mainWindow.trainTabTextBrowser.toPlainText())) + ":" + str(
                #             self.logHandler.lineNum))
                #     time.sleep(0.05)
                #
                # return
                self.currentTask.set_task("Analyze PII Data")
                buildDbObj = BuildDatabase()
                buildDbObj.test_rebuild()
                self.setPhasePassed(self.analyzePIIDataStatus)
                self.printTrainLog(f"Analyze PII Data and build datatables finished !")
                # self.patchInfoDialog(f"Analyze PII Data and build datatables finished")
            except Exception as e:
                self.printTrainLog(
                    f"Exception occur when Analyzing PII Data and Building datatables, Original Exception is {e}\nTraceback:{''.join(traceback.format_exception(type(e), e, e.__traceback__))}\n")
                # self.patchDialog(f"Analyze pii data and build datatable failed, check exception log for more details")
            finally:
                self.analyzePIIDataProgressExitFlag.set()
                thread.finished.emit()

        thread.run = run
        thread.finished.connect(self.on_task_finished)
        thread.start()

        # thread = threading.Thread(target=run)
        # thread.start()
        self.printTrainLog(f"Analyzing PII Data... Please Wait")

    def trainModelBtnSlot(self):
        """Train model
        """
        if self.exist_current_task():
            return False
        if not self.checkPhasePassed(self.trainModelStatus):
            if self.questionDialog("There is at least one phase before not passed, are you sure to proceed?"):
                pass
            else:
                return
        if self.clfSavePath is None or len(self.clfSavePath) <= 0:
            self.patchDialog(f"Please assign model save path(.clf) first")
            return

        def startTrainModelProgressTrack():
            self.trainModelProgressExitFlag.clear()
            while not self.trainModelProgressExitFlag.is_set():
                progress = main_General_PII_Mode.ProgressTracker.progress
                limit = main_General_PII_Mode.ProgressTracker.limit
                proportion = int(progress / limit * 100)
                self.updateTrainTabProgressBar(proportion)
                time.sleep(0.5)
            self.updateTrainTabProgressBar(100)

        progress_thread = threading.Thread(target=startTrainModelProgressTrack)
        progress_thread.start()

        thread = QThread()

        def run():
            try:
                self.currentTask.set_task("Train Model")
                api = GeneralPIITrainMain()
                api.train_general(self.clfSavePath)
                self.setPhasePassed(self.trainModelStatus)
                self.printTrainLog(f"Train Model finished !")
                # self.patchInfoDialog(f"Train Model finished")
            except Exception as e:
                self.printTrainLog(
                    f"Exception occur when Training Model, Original Exception is {e}\nTraceback:{''.join(traceback.format_exception(type(e), e, e.__traceback__))}\n")
                # self.patchDialog(f"Train Model failed, check exception log for more details")
                return
            finally:
                self.trainModelProgressExitFlag.set()
                thread.finished.emit()

        # @Slots.Task
        # def on_task_finished():
        #     self.patchInfoDialog(f"Train Model finished!")

        thread.run = run
        thread.finished.connect(self.on_task_finished)
        thread.start()

        # thread = threading.Thread(target=run)
        # thread.start()

    def assessAccuracyStatusBtnSlot(self):
        """Assess accuracy for assigned pattern file
        Do not need previous status to be completed
        """
        if self.exist_current_task():
            return False
        if not self.checkPhasePassed(self.assessStatus):
            if self.questionDialog("There is at least one phase before not passed, are you sure to proceed?"):
                pass
            else:
                return
        if self.assessPatternFile is None or len(self.assessPatternFile) <= 0:
            self.patchDialog(f"Please assign a pattern file to assess !")
            return
        if not os.path.exists(self.assessPatternFile):
            self.patchDialog(f"Error: {self.assessPatternFile} not exists")
            return

        def startAssessProgressTrack():
            self.assessProgressExitFlag.clear()
            while not self.trainModelProgressExitFlag.is_set():
                progress = main_General_PII_Mode.ProgressTracker.progress
                limit = main_General_PII_Mode.ProgressTracker.limit
                proportion = int(progress / limit * 100)
                self.updateTrainTabProgressBar(proportion)
                time.sleep(0.5)
            self.updateTrainTabProgressBar(100)

        progress_thread = threading.Thread(target=startAssessProgressTrack)
        progress_thread.start()

        thread = QThread()

        def run():
            try:
                self.currentTask.set_task("Assess Accuracy")
                api = GeneralPIITrainMain()
                api.accuracy_assessment(self.assessPatternFile)
                self.setPhasePassed(self.assessStatus)
                self.printTrainLog(f"Accuracy Assessment finished !")
            except Exception as e:
                self.printTrainLog(
                    f"Exception occur when Assessing accuracy, Original Exception is {e}\nTraceback:{''.join(traceback.format_exception(type(e), e, e.__traceback__))}\n")
                return
            finally:
                self.assessProgressExitFlag.set()
                thread.finished.emit()

        # @Slots.Task
        # def on_task_finished():
        #     self.patchInfoDialog(f"Accuracy Assessment finished!")

        thread.run = run
        thread.finished.connect(self.on_task_finished)
        thread.start()

        # thread = threading.Thread(target=run)
        # thread.start()

    def checkDbStatusBtnSlot(self):
        """Check database structure, datatable capability
        """
        if self.exist_current_task():
            return False
        self.currentTask.set_task("Update Status")
        try:
            if not self.connectDatabaseStatus.getStatus() or self.engine is None:
                self.patchDialog(f"Please check database connection again")
                return
            logList = ["\nUpdate Status Result:\n", ]

            # check database structure
            not_exist_tables = self.checkInitDatabaseStatus()
            if len(not_exist_tables) >= 1:
                logList.append(f"Init Database: Failed\nMissing datatables: {not_exist_tables}\n")
                self.printTrainLog(''.join(logList))
                self.initDatabaseStatus.setFail()
                return
            logList.append(f"Init Database: Passed\n")
            self.setPhasePassed(self.initDatabaseStatus)

            # check PII datatable
            pii_table_size = self.checkLoadPIIDataStatus()
            if pii_table_size <= 0:
                logList.append(f"Load PII Data: Failed.\n Empty PII datatable in database {self.databaseUrl}\n")
                self.printTrainLog(''.join(logList))
                self.loadPIIDataStatus.setFail()
                return
            logList.append(f"Load PII Data: Passed.\nPII table size: {pii_table_size}\n")
            self.setPhasePassed(self.loadPIIDataStatus)

            # check analyze PII data status
            rep_unique_table_size = self.checkAnalyzePIIDataStatus()
            if rep_unique_table_size <= 0:
                logList.append(
                    f"Analyze PII Data: Failed.\nEmpty pwrepresentation_general datatable in database {self.databaseUrl}")
                self.printTrainLog(''.join(logList))
                self.analyzePIIDataStatus.setFail()
                return
            logList.append(f"Analyze PII Data: Passed.\npwrepresentation_general table size: {rep_unique_table_size}\n")
            self.setPhasePassed(self.analyzePIIDataStatus)

            self.printTrainLog(''.join(logList))
            self.patchInfoDialog(f"Update status finished!")
        finally:
            self.currentTask.set_empty()

    def checkInitDatabaseStatus(self) -> list[str]:
        """Check for missing datatables

        Returns:
            list: list of missing table names
        """
        self.tablenames = Config.TableNames.generalTables
        self.inspector = reflection.Inspector.from_engine(self.engine)

        not_exist_tables = list()
        for tb in self.tablenames:
            if not self.inspector.has_table(tb):
                not_exist_tables.append(tb)
        return not_exist_tables

    def checkLoadPIIDataStatus(self) -> int:
        """Inspect PII datatable
        Returns:
            int: pii datatable size
        """
        queryMethods = databaseInit.PIIUnitQueryMethods()
        return queryMethods.QuerySize()

    def checkAnalyzePIIDataStatus(self) -> int:
        """Inspect pwrepresentation_unique_general datatable

        Returns:
            int: pwrepresentation_unique_general datatable size
        """
        queryMethods = databaseInit.GeneralPwRepUniqueMethods()
        return queryMethods.QuerySize()
