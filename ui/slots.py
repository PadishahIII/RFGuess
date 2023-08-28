import json
import sys
import threading
import time

from PyQt5.QtCore import pyqtSignal, QDate, Qt, QThread
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget

from Generators.GeneralPIIGenerators import *
from Generators.PasswordGuessGenerator import *
from ui.mainWindow import *
from queue import  Queue



class Consumer(threading.Thread):
    def __init__(self, queue: Queue, handler:typing.Callable):
        super().__init__()
        self.queue = queue
        self.handler = handler # function

    def run(self) -> None:
        while True:
            s:str = self.queue.get()
            self.handler(s)
            time.sleep(0.5)


class Slots:

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

        # pattern generator tab
        self.clsFile = ""
        self.patternSavePath = "patterns.txt"
        self.patternGenerateLimit = 0
        self.patternLimitOptions = ['100', '500', '1000', '2000', '3000', '4000', '5000']
        self.patternGenerator: GeneralPIIPatternGenerator = None
        self.patternProgressThreadExitFlag = threading.Event()

        self.print_log_queue:Queue = Queue(100)
        self.error_dialog_queue:Queue = Queue(100)
        self.info_dialog_queue:Queue = Queue(100)
        self.print_log_consumer = Consumer(self.print_log_queue,self.handle_print_log_signal)
        self.error_dialog_consumer = Consumer(self.error_dialog_queue,self.handle_error_signal)
        self.info_dialog_consumer = Consumer(self.info_dialog_queue,self.handle_info_signal)
        self.print_log_consumer.start()
        self.error_dialog_consumer.start()
        self.info_dialog_consumer.start()


        self.mainWindow.patternOutputEdit.setText(self.patternSavePath)
        self.mainWindow.loadClfBtn.clicked.connect(self.loadClfSlot)
        self.mainWindow.clfFileBrowserBtn.clicked.connect(self.openClfFileSlot)
        self.mainWindow.patternSaveBrowserBtn.clicked.connect(self.selectPatternOutputSlot)
        self.mainWindow.patternLimitComboBox.addItems(self.patternLimitOptions)
        self.mainWindow.patternGenerateBtn.clicked.connect(self.generatePatternBtnSlot)

        self.buildLimitComboBox()
        self.buildUsage()

    def handle_error_signal(self, msg):
        self.patchDialog(msg)

    def handle_print_log_signal(self, msg):
        self.printPatternLog(msg)

    def handle_info_signal(self, msg):
        self.patchDialog(msg, title="Success",
                         icon=QMessageBox.Information)

    def buildUsage(self):
        usage = \
            '''
            Welcome to RFGuess :D
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
            self.mainWindow.dateEdit.setDate(QDate.fromString(self.pii.birthday, "%Y%m%d"))
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
            self.mainWindow.progressBar.setValue(_progress)

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

    def generatePatternBtnSlot(self):
        if self.patternGenerator is None:
            self.patchDialog(f"Classifier not loaded")
            return
        if self.patternSavePath is None or len(self.patternSavePath) <= 0:
            self.patchDialog(f"Please assign a pattern save file")
            return
        self.patternGenerateLimit = int(self.mainWindow.patternLimitComboBox.currentText())
        self.startPatternProgressTracking()
        self.patternWorker = self.generatePatternWorker(self)
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
            while not self.patternProgressThreadExitFlag.is_set():
                limit = self.patternGenerator.patternGenerateLimit
                progress = self.patternGenerator.patternGenerateProgress
                proportion = min(int(progress / limit * 100), 100)
                self.mainWindow.patternProgressBar.setValue((proportion))
                time.sleep(0.5)
            limit = self.patternGenerator.patternGenerateLimit
            progress = self.patternGenerator.patternGenerateProgress
            proportion = min(int(progress / limit * 100), 100)
            self.mainWindow.patternProgressBar.setValue((proportion))

        self.patternProgressThreadExitFlag.clear()
        self.patternProgressThread = threading.Thread(target=trackProgress)
        self.patternProgressThread.start()

    def endPatternProgressTracking(self):
        self.patternProgressThreadExitFlag.set()

    def setLimitOptionSlot(self):
        limitStr = self.mainWindow.limitComboBox.currentText()
        self.guessLimit = int(limitStr)

    def openPatternFileSlot(self):
        self.patternFile = ""
        file_dialog = QFileDialog()
        self.patternFile, _ = file_dialog.getOpenFileName(self.mainWindow.mainWindow, "Select pattern file")
        self.mainWindow.patternFileEdit.setText(self.patternFile)

    def openClfFileSlot(self):
        self.clsFile = ""
        file_dialog = QFileDialog()
        self.clsFile, _ = file_dialog.getOpenFileName(self.mainWindow.mainWindow, "Select clf file (.clf)")
        self.mainWindow.clfFileEdit.setText(self.clsFile)

    def selectOutputFileSlot(self):
        self.outputFile = ""
        file_path, _ = QFileDialog.getSaveFileName(self.mainWindow.mainWindow, "Save File", "", "Text Files (*.txt)")
        self.outputFile = file_path
        self.mainWindow.outputEdit.setText(self.outputFile)

    def selectPatternOutputSlot(self):
        self.patternSavePath = ""
        self.patternSavePath, _ = QFileDialog.getSaveFileName(self.mainWindow.mainWindow, "Save Pattern File", "",
                                                              "Text Files (*.txt)")
        self.mainWindow.patternOutputEdit.setText(self.patternSavePath)

    def patternFileEditChangedSlot(self):
        newContent = self.mainWindow.patternFileEdit.text()
        self.printGuessLog(f"pattern file: {newContent}")

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

    def patchDialog(self, content: str, title: str = "Error", icon=QMessageBox.Critical):
        error_box = QMessageBox()
        error_box.setIcon(icon)
        error_box.setText(content)
        error_box.setWindowTitle(title)
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.exec_()

    def printGuessLog(self, s: str):
        cur = datetime.datetime.now()
        timeStr = datetime.datetime.strftime(cur, "%Y-%m-%d %H:%M:%S")
        self.mainWindow.textBrowser.append(f"[{timeStr}] {s}")

    def printPatternLog(self, s: str):
        cur = datetime.datetime.now()
        timeStr = datetime.datetime.strftime(cur, "%Y-%m-%d %H:%M:%S")
        self.mainWindow.patternTextBrowser.append(f"[{timeStr}] {s}")

    def excepthook(type, value, traceback):
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
        sys.__excepthook__(type, value, traceback)
