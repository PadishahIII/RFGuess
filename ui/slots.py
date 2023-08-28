import json
import sys

from PyQt5.QtCore import pyqtSignal, QDate, Qt
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from Generators.PasswordGuessGenerator import *
from ui.mainWindow import *


class Slots:

    def __init__(self, mainWindow: Ui_MainWindow) -> None:
        self.patterns: list[str] = list()
        self.limitOptions = ['500', '1000', '2000', '3000', '5000']
        self.limit: int = 0
        self.guesses: list[str] = list()
        self.outputFile = "guess_test.txt"
        self.patternFile = "patterns_general.txt"
        self.pii: PII = None
        self.generator: GeneralPasswordGenerator = None
        self.progressSignal = pyqtSignal(int)

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
        self.buildUsage()

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
        self.mainWindow.limitComboBox.addItems(self.limitOptions)

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
        if self.limit <= 0:
            self.patchDialog(f"Invalid limit value: {self.limit}")
            return
        if len(self.patterns) <= 0:
            self.patchDialog(f"There is no pattern loaded")
            return
        self.printLog(f"PII Data:{self.pii.__dict__}")
        self.printLog(f"Start generating guesses")
        self.generateGuess()

    def generateGuess(self):
        self.generator.patternFile = self.patternFile
        self.generator.init()
        self.printLog(f"Preparing PII tag container...")
        self.generator.pii = self.pii
        self.generator.outputFile = self.outputFile
        self.generator.piiTagContainer = PIITagContainer(pii=self.generator.pii, nameFuzz=True)
        self.generator.piiTagContainer.parse()
        self.generator.tagDict = self.generator.piiTagContainer.getTagDict()  # specified pii type to string

        self.generator.eliminatePatternDatagrams()
        self.printLog(
            f"Number of patterns after eliminating: {len(self.patterns)}, remove: {len(self.generator.initPatterns) - len(self.patterns)}")

        self.printLog(f"Start generating guesses...")

        _len = len(self.generator.patterns)
        _max = min(_len, self.limit)
        _i = 0
        _progress = 0
        for dg in self.generator.patterns:
            guesses: list[str] = self.generator.generateGuessFromPatternDatagram(dg)
            self.generator.guesses += guesses
            if len(self.generator.guesses) >= self.limit:
                break
            _progress = min(int(len(self.generator.guesses) / _max * 100), 100)
            self.mainWindow.progressBar.setValue(_progress)

        primaryLen = len(self.generator.guesses)
        self.guesses = self.generator.eliminateDuplicateGuess()
        newLen = len(self.generator.guesses)
        self.printLog(f"Generating complete, number of guesses: {primaryLen}")
        self.printLog(f"Eliminate guesses: remove {primaryLen - newLen} duplicates, final guess number: {newLen}")
        if self.generator.outputFile != None and len(self.generator.outputFile) > 0:
            self.generator.save()
        self.printLog(f"Complete!\nCount:{newLen}\nSaved to {self.outputFile}\n")
        self.patchDialog(f"Complete!\nCount:{newLen}\nSaved to {self.outputFile}\n", title="Generate Guesses Complete",
                         icon=QMessageBox.Information)

    def setLimitOptionSlot(self):
        limitStr = self.mainWindow.limitComboBox.currentText()
        self.limit = int(limitStr)

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

    def patternFileEditChangedSlot(self):
        newContent = self.mainWindow.patternFileEdit.text()
        self.printLog(f"pattern file: {newContent}")

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
            self.printLog(f"Load patterns: {len(self.patterns)}")
            self.generator: GeneralPasswordGenerator = GeneralPasswordGenerator.getInstance(self.patternFile)

    def patchDialog(self, content: str, title: str = "Error", icon=QMessageBox.Critical):
        error_box = QMessageBox()
        error_box.setIcon(icon)
        error_box.setText(content)
        error_box.setWindowTitle(title)
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.exec_()

    def printLog(self, s: str):
        cur = datetime.datetime.now()
        timeStr = datetime.datetime.strftime(cur, "%Y-%m-%d %H:%M:%S")
        self.mainWindow.textBrowser.append(f"[{timeStr}] {s}")

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
