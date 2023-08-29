# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ui\test.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1434, 675)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 1271, 641))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridWidget = QtWidgets.QWidget(self.tab)
        self.gridWidget.setGeometry(QtCore.QRect(0, 0, 1151, 471))
        self.gridWidget.setObjectName("gridWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollArea = QtWidgets.QScrollArea(self.gridWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1131, 177))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.guessTabTextBrowser = QtWidgets.QTextBrowser(self.scrollAreaWidgetContents)
        self.guessTabTextBrowser.setGeometry(QtCore.QRect(-5, 1, 1141, 201))
        self.guessTabTextBrowser.setObjectName("guessTabTextBrowser")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 3, 0, 1, 1)
        self.progressBar = QtWidgets.QProgressBar(self.gridWidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 4, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.gridWidget)
        self.label_2.setIndent(4)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.outputEdit = QtWidgets.QLineEdit(self.gridWidget)
        self.outputEdit.setClearButtonEnabled(True)
        self.outputEdit.setObjectName("outputEdit")
        self.horizontalLayout_2.addWidget(self.outputEdit)
        self.outputBrowser = QtWidgets.QToolButton(self.gridWidget)
        self.outputBrowser.setObjectName("outputBrowser")
        self.horizontalLayout_2.addWidget(self.outputBrowser)
        self.label_15 = QtWidgets.QLabel(self.gridWidget)
        self.label_15.setObjectName("label_15")
        self.horizontalLayout_2.addWidget(self.label_15)
        self.limitComboBox = QtWidgets.QComboBox(self.gridWidget)
        self.limitComboBox.setObjectName("limitComboBox")
        self.horizontalLayout_2.addWidget(self.limitComboBox)
        self.generateBtn = QtWidgets.QPushButton(self.gridWidget)
        self.generateBtn.setObjectName("generateBtn")
        self.horizontalLayout_2.addWidget(self.generateBtn)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.horizontalLayout.addLayout(self.horizontalLayout_15)
        self.label = QtWidgets.QLabel(self.gridWidget)
        self.label.setIndent(4)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.patternFileEdit = QtWidgets.QLineEdit(self.gridWidget)
        self.patternFileEdit.setObjectName("patternFileEdit")
        self.horizontalLayout.addWidget(self.patternFileEdit)
        self.fileBrowserBtn = QtWidgets.QToolButton(self.gridWidget)
        self.fileBrowserBtn.setObjectName("fileBrowserBtn")
        self.horizontalLayout.addWidget(self.fileBrowserBtn)
        self.loadBtn = QtWidgets.QPushButton(self.gridWidget)
        self.loadBtn.setObjectName("loadBtn")
        self.horizontalLayout.addWidget(self.loadBtn)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_8 = QtWidgets.QLabel(self.gridWidget)
        self.label_8.setIndent(4)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_8.addWidget(self.label_8)
        self.idCardEdit = QtWidgets.QLineEdit(self.gridWidget)
        self.idCardEdit.setAutoFillBackground(False)
        self.idCardEdit.setInputMask("")
        self.idCardEdit.setObjectName("idCardEdit")
        self.horizontalLayout_8.addWidget(self.idCardEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_7 = QtWidgets.QLabel(self.gridWidget)
        self.label_7.setIndent(4)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_7.addWidget(self.label_7)
        self.emailEdit = QtWidgets.QLineEdit(self.gridWidget)
        self.emailEdit.setObjectName("emailEdit")
        self.horizontalLayout_7.addWidget(self.emailEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_6 = QtWidgets.QLabel(self.gridWidget)
        self.label_6.setIndent(4)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_6.addWidget(self.label_6)
        self.accountEdit = QtWidgets.QLineEdit(self.gridWidget)
        self.accountEdit.setDragEnabled(False)
        self.accountEdit.setReadOnly(False)
        self.accountEdit.setObjectName("accountEdit")
        self.horizontalLayout_6.addWidget(self.accountEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_5 = QtWidgets.QLabel(self.gridWidget)
        self.label_5.setIndent(4)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_5.addWidget(self.label_5)
        self.fullNameEdit = QtWidgets.QLineEdit(self.gridWidget)
        self.fullNameEdit.setObjectName("fullNameEdit")
        self.horizontalLayout_5.addWidget(self.fullNameEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.gridWidget)
        self.label_3.setIndent(4)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.phoneEdit = QtWidgets.QLineEdit(self.gridWidget)
        self.phoneEdit.setObjectName("phoneEdit")
        self.horizontalLayout_3.addWidget(self.phoneEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.birthdayLabel = QtWidgets.QLabel(self.gridWidget)
        self.birthdayLabel.setIndent(4)
        self.birthdayLabel.setObjectName("birthdayLabel")
        self.horizontalLayout_4.addWidget(self.birthdayLabel)
        self.dateEdit = QtWidgets.QDateEdit(self.gridWidget)
        self.dateEdit.setObjectName("dateEdit")
        self.horizontalLayout_4.addWidget(self.dateEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_16.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.verticalLayout_2.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.verticalLayout_2.addLayout(self.horizontalLayout_10)
        self.scrollArea_2 = QtWidgets.QScrollArea(self.gridWidget)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 558, 97))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.usageTextBrowser = QtWidgets.QTextBrowser(self.scrollAreaWidgetContents_2)
        self.usageTextBrowser.setGeometry(QtCore.QRect(0, 0, 561, 101))
        self.usageTextBrowser.setObjectName("usageTextBrowser")
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.verticalLayout_2.addWidget(self.scrollArea_2)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.verticalLayout_2.addLayout(self.horizontalLayout_11)
        self.loadPIIBtn = QtWidgets.QPushButton(self.gridWidget)
        self.loadPIIBtn.setObjectName("loadPIIBtn")
        self.verticalLayout_2.addWidget(self.loadPIIBtn)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.verticalLayout_2.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.verticalLayout_2.addLayout(self.horizontalLayout_13)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.verticalLayout_2.addLayout(self.horizontalLayout_14)
        self.horizontalLayout_16.addLayout(self.verticalLayout_2)
        self.gridLayout.addLayout(self.horizontalLayout_16, 2, 0, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.tab_2)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(9, 9, 1241, 51))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout(self.verticalLayoutWidget)
        self.horizontalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.label_4 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_17.addWidget(self.label_4)
        self.clfFileEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.clfFileEdit.setObjectName("clfFileEdit")
        self.horizontalLayout_17.addWidget(self.clfFileEdit)
        self.clfFileBrowserBtn = QtWidgets.QToolButton(self.verticalLayoutWidget)
        self.clfFileBrowserBtn.setObjectName("clfFileBrowserBtn")
        self.horizontalLayout_17.addWidget(self.clfFileBrowserBtn)
        self.loadClfBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.loadClfBtn.setObjectName("loadClfBtn")
        self.horizontalLayout_17.addWidget(self.loadClfBtn)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.tab_2)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(9, 120, 1241, 321))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.scrollArea_3 = QtWidgets.QScrollArea(self.verticalLayoutWidget_2)
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollArea_3.setObjectName("scrollArea_3")
        self.scrollAreaWidgetContents_3 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 98, 28))
        self.scrollAreaWidgetContents_3.setObjectName("scrollAreaWidgetContents_3")
        self.patternTextBrowser = QtWidgets.QTextBrowser(self.scrollAreaWidgetContents_3)
        self.patternTextBrowser.setGeometry(QtCore.QRect(0, 0, 1241, 311))
        self.patternTextBrowser.setObjectName("patternTextBrowser")
        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_3)
        self.verticalLayout_3.addWidget(self.scrollArea_3)
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.tab_2)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(10, 70, 1241, 41))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        self.horizontalLayout_18 = QtWidgets.QHBoxLayout(self.verticalLayoutWidget_3)
        self.horizontalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.label_9 = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_18.addWidget(self.label_9)
        self.patternOutputEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget_3)
        self.patternOutputEdit.setObjectName("patternOutputEdit")
        self.horizontalLayout_18.addWidget(self.patternOutputEdit)
        self.patternSaveBrowserBtn = QtWidgets.QToolButton(self.verticalLayoutWidget_3)
        self.patternSaveBrowserBtn.setObjectName("patternSaveBrowserBtn")
        self.horizontalLayout_18.addWidget(self.patternSaveBrowserBtn)
        self.label_10 = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_18.addWidget(self.label_10)
        self.patternLimitComboBox = QtWidgets.QComboBox(self.verticalLayoutWidget_3)
        self.patternLimitComboBox.setObjectName("patternLimitComboBox")
        self.horizontalLayout_18.addWidget(self.patternLimitComboBox)
        self.patternGenerateBtn = QtWidgets.QPushButton(self.verticalLayoutWidget_3)
        self.patternGenerateBtn.setObjectName("patternGenerateBtn")
        self.horizontalLayout_18.addWidget(self.patternGenerateBtn)
        self.patternProgressBar = QtWidgets.QProgressBar(self.tab_2)
        self.patternProgressBar.setGeometry(QtCore.QRect(10, 450, 1241, 23))
        self.patternProgressBar.setProperty("value", 0)
        self.patternProgressBar.setObjectName("patternProgressBar")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.tab_3)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 1261, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout_19 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_19.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_19.setObjectName("horizontalLayout_19")
        self.label_11 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label_11.setIndent(4)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout_19.addWidget(self.label_11)
        self.databaseUrlEdit = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.databaseUrlEdit.setObjectName("databaseUrlEdit")
        self.horizontalLayout_19.addWidget(self.databaseUrlEdit)
        self.checkDbConnBtn = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.checkDbConnBtn.setObjectName("checkDbConnBtn")
        self.horizontalLayout_19.addWidget(self.checkDbConnBtn)
        self.connectDatabaseLabel = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.connectDatabaseLabel.setObjectName("connectDatabaseLabel")
        self.horizontalLayout_19.addWidget(self.connectDatabaseLabel)
        self.verticalLayoutWidget_4 = QtWidgets.QWidget(self.tab_3)
        self.verticalLayoutWidget_4.setGeometry(QtCore.QRect(0, 250, 1241, 321))
        self.verticalLayoutWidget_4.setObjectName("verticalLayoutWidget_4")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_4)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.scrollArea_4 = QtWidgets.QScrollArea(self.verticalLayoutWidget_4)
        self.scrollArea_4.setWidgetResizable(True)
        self.scrollArea_4.setObjectName("scrollArea_4")
        self.scrollAreaWidgetContents_4 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_4.setGeometry(QtCore.QRect(0, 0, 1237, 317))
        self.scrollAreaWidgetContents_4.setObjectName("scrollAreaWidgetContents_4")
        self.trainTabTextBrowser = QtWidgets.QTextBrowser(self.scrollAreaWidgetContents_4)
        self.trainTabTextBrowser.setGeometry(QtCore.QRect(0, 0, 1241, 251))
        self.trainTabTextBrowser.setObjectName("trainTabTextBrowser")
        self.trainTabProgressBar = QtWidgets.QProgressBar(self.scrollAreaWidgetContents_4)
        self.trainTabProgressBar.setGeometry(QtCore.QRect(0, 260, 1239, 20))
        self.trainTabProgressBar.setProperty("value", 0)
        self.trainTabProgressBar.setObjectName("trainTabProgressBar")
        self.scrollArea_4.setWidget(self.scrollAreaWidgetContents_4)
        self.verticalLayout_4.addWidget(self.scrollArea_4)
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.tab_3)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(0, 80, 1261, 61))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_20 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_20.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_20.setObjectName("horizontalLayout_20")
        self.label_12 = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label_12.setIndent(4)
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_20.addWidget(self.label_12)
        self.piiFileEdit = QtWidgets.QLineEdit(self.horizontalLayoutWidget_2)
        self.piiFileEdit.setObjectName("piiFileEdit")
        self.horizontalLayout_20.addWidget(self.piiFileEdit)
        self.piiFileBrowser = QtWidgets.QToolButton(self.horizontalLayoutWidget_2)
        self.piiFileBrowser.setObjectName("piiFileBrowser")
        self.horizontalLayout_20.addWidget(self.piiFileBrowser)
        self.label_14 = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label_14.setObjectName("label_14")
        self.horizontalLayout_20.addWidget(self.label_14)
        self.clfSaveEdit = QtWidgets.QLineEdit(self.horizontalLayoutWidget_2)
        self.clfSaveEdit.setObjectName("clfSaveEdit")
        self.horizontalLayout_20.addWidget(self.clfSaveEdit)
        self.clfSaveBtn = QtWidgets.QToolButton(self.horizontalLayoutWidget_2)
        self.clfSaveBtn.setObjectName("clfSaveBtn")
        self.horizontalLayout_20.addWidget(self.clfSaveBtn)
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(self.tab_3)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(0, 40, 1261, 41))
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        self.horizontalLayout_21 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.horizontalLayout_21.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_21.setObjectName("horizontalLayout_21")
        self.label_13 = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
        self.label_13.setIndent(4)
        self.label_13.setObjectName("label_13")
        self.horizontalLayout_21.addWidget(self.label_13)
        self.sqlFileEdit = QtWidgets.QLineEdit(self.horizontalLayoutWidget_3)
        self.sqlFileEdit.setObjectName("sqlFileEdit")
        self.horizontalLayout_21.addWidget(self.sqlFileEdit)
        self.sqlFileBrowser = QtWidgets.QToolButton(self.horizontalLayoutWidget_3)
        self.sqlFileBrowser.setObjectName("sqlFileBrowser")
        self.horizontalLayout_21.addWidget(self.sqlFileBrowser)
        self.checkStatusBtn = QtWidgets.QPushButton(self.tab_3)
        self.checkStatusBtn.setGeometry(QtCore.QRect(1080, 180, 171, 71))
        self.checkStatusBtn.setObjectName("checkStatusBtn")
        self.gridLayoutWidget = QtWidgets.QWidget(self.tab_3)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 180, 1061, 70))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.analyzePIIStatusLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.analyzePIIStatusLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.analyzePIIStatusLabel.setObjectName("analyzePIIStatusLabel")
        self.gridLayout_2.addWidget(self.analyzePIIStatusLabel, 1, 2, 1, 1)
        self.trainModelStatusLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.trainModelStatusLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.trainModelStatusLabel.setObjectName("trainModelStatusLabel")
        self.gridLayout_2.addWidget(self.trainModelStatusLabel, 1, 3, 1, 1)
        self.assessBtn = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.assessBtn.setObjectName("assessBtn")
        self.gridLayout_2.addWidget(self.assessBtn, 0, 4, 1, 1)
        self.initDatabaseBtn = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.initDatabaseBtn.setObjectName("initDatabaseBtn")
        self.gridLayout_2.addWidget(self.initDatabaseBtn, 0, 0, 1, 1)
        self.loadPIIDataBtn = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.loadPIIDataBtn.setObjectName("loadPIIDataBtn")
        self.gridLayout_2.addWidget(self.loadPIIDataBtn, 0, 1, 1, 1)
        self.assessStatusLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.assessStatusLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.assessStatusLabel.setObjectName("assessStatusLabel")
        self.gridLayout_2.addWidget(self.assessStatusLabel, 1, 4, 1, 1)
        self.analyzePIIBtn = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.analyzePIIBtn.setObjectName("analyzePIIBtn")
        self.gridLayout_2.addWidget(self.analyzePIIBtn, 0, 2, 1, 1)
        self.loadPIIDataStatusLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.loadPIIDataStatusLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.loadPIIDataStatusLabel.setObjectName("loadPIIDataStatusLabel")
        self.gridLayout_2.addWidget(self.loadPIIDataStatusLabel, 1, 1, 1, 1)
        self.initDatabaseStatusLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.initDatabaseStatusLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.initDatabaseStatusLabel.setObjectName("initDatabaseStatusLabel")
        self.gridLayout_2.addWidget(self.initDatabaseStatusLabel, 1, 0, 1, 1)
        self.trainModelBtn = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.trainModelBtn.setObjectName("trainModelBtn")
        self.gridLayout_2.addWidget(self.trainModelBtn, 0, 3, 1, 1)
        self.horizontalLayoutWidget_4 = QtWidgets.QWidget(self.tab_3)
        self.horizontalLayoutWidget_4.setGeometry(QtCore.QRect(0, 140, 1261, 41))
        self.horizontalLayoutWidget_4.setObjectName("horizontalLayoutWidget_4")
        self.horizontalLayout_23 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_4)
        self.horizontalLayout_23.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_23.setObjectName("horizontalLayout_23")
        self.label_16 = QtWidgets.QLabel(self.horizontalLayoutWidget_4)
        self.label_16.setIndent(4)
        self.label_16.setObjectName("label_16")
        self.horizontalLayout_23.addWidget(self.label_16)
        self.assessPatternFileEdit = QtWidgets.QLineEdit(self.horizontalLayoutWidget_4)
        self.assessPatternFileEdit.setObjectName("assessPatternFileEdit")
        self.horizontalLayout_23.addWidget(self.assessPatternFileEdit)
        self.assessPatternFileBrowserBtn = QtWidgets.QToolButton(self.horizontalLayoutWidget_4)
        self.assessPatternFileBrowserBtn.setObjectName("assessPatternFileBrowserBtn")
        self.horizontalLayout_23.addWidget(self.assessPatternFileBrowserBtn)
        self.tabWidget.addTab(self.tab_3, "")
        self.textBrowser_2 = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser_2.setGeometry(QtCore.QRect(1270, 20, 151, 461))
        self.textBrowser_2.setObjectName("textBrowser_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1434, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "RFGuess"))
        self.label_2.setText(_translate("MainWindow", "Output path:"))
        self.outputBrowser.setText(_translate("MainWindow", "..."))
        self.label_15.setText(_translate("MainWindow", "Limit:"))
        self.generateBtn.setText(_translate("MainWindow", "Generate"))
        self.label.setText(_translate("MainWindow", "Pattern file:"))
        self.fileBrowserBtn.setText(_translate("MainWindow", "..."))
        self.loadBtn.setText(_translate("MainWindow", "Load"))
        self.label_8.setText(_translate("MainWindow", "Id Card:"))
        self.idCardEdit.setPlaceholderText(_translate("MainWindow", "id card number"))
        self.label_7.setText(_translate("MainWindow", "Email:"))
        self.emailEdit.setPlaceholderText(_translate("MainWindow", "abc123456@example.com"))
        self.label_6.setText(_translate("MainWindow", "Account:"))
        self.accountEdit.setPlaceholderText(_translate("MainWindow", "ever used account name"))
        self.label_5.setText(_translate("MainWindow", "Full Name:"))
        self.fullNameEdit.setPlaceholderText(_translate("MainWindow", "Chinese or English name, e.g. Jason Harris"))
        self.label_3.setText(_translate("MainWindow", "Phone Number:"))
        self.phoneEdit.setPlaceholderText(_translate("MainWindow", "phone number"))
        self.birthdayLabel.setText(_translate("MainWindow", "Birthday: "))
        self.usageTextBrowser.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Welcome to RFGuess</p></body></html>"))
        self.loadPIIBtn.setText(_translate("MainWindow", "Load PII from Json"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Guess Generator"))
        self.label_4.setText(_translate("MainWindow", "Classifier file(.clf):"))
        self.clfFileBrowserBtn.setText(_translate("MainWindow", "..."))
        self.loadClfBtn.setText(_translate("MainWindow", "Load"))
        self.label_9.setText(_translate("MainWindow", "Pattern output path(.txt):"))
        self.patternSaveBrowserBtn.setText(_translate("MainWindow", "..."))
        self.label_10.setText(_translate("MainWindow", "Limit:"))
        self.patternGenerateBtn.setText(_translate("MainWindow", "Generate"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Pattern Generator"))
        self.label_11.setText(_translate("MainWindow", "Database Url:"))
        self.databaseUrlEdit.setPlaceholderText(_translate("MainWindow", "mysql://<username>:<password>@<host>/<database name>"))
        self.checkDbConnBtn.setText(_translate("MainWindow", "Connect"))
        self.connectDatabaseLabel.setText(_translate("MainWindow", "Pass"))
        self.label_12.setText(_translate("MainWindow", "Dataset File(.txt):"))
        self.piiFileEdit.setPlaceholderText(_translate("MainWindow", "personal infomation data used to train the model"))
        self.piiFileBrowser.setText(_translate("MainWindow", "..."))
        self.label_14.setText(_translate("MainWindow", "   Save model to:"))
        self.clfSaveBtn.setText(_translate("MainWindow", "..."))
        self.label_13.setText(_translate("MainWindow", "Database Structure(.sql):"))
        self.sqlFileEdit.setPlaceholderText(_translate("MainWindow", "(.sql) import database structure"))
        self.sqlFileBrowser.setText(_translate("MainWindow", "..."))
        self.checkStatusBtn.setText(_translate("MainWindow", "Update Status"))
        self.analyzePIIStatusLabel.setText(_translate("MainWindow", "Fail"))
        self.trainModelStatusLabel.setText(_translate("MainWindow", "Pass"))
        self.assessBtn.setText(_translate("MainWindow", "Assess Accuracy"))
        self.initDatabaseBtn.setText(_translate("MainWindow", "Init Database"))
        self.loadPIIDataBtn.setText(_translate("MainWindow", "Load PII Data"))
        self.assessStatusLabel.setText(_translate("MainWindow", "Fail"))
        self.analyzePIIBtn.setText(_translate("MainWindow", "Analyze PII Data"))
        self.loadPIIDataStatusLabel.setText(_translate("MainWindow", "Fail"))
        self.initDatabaseStatusLabel.setText(_translate("MainWindow", "Fail"))
        self.trainModelBtn.setText(_translate("MainWindow", "Train Model"))
        self.label_16.setText(_translate("MainWindow", "Pattern File(for assess, .txt)"))
        self.assessPatternFileEdit.setPlaceholderText(_translate("MainWindow", "pattern file to be assessed, please use Pattern Generator to generate"))
        self.assessPatternFileBrowserBtn.setText(_translate("MainWindow", "..."))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Train Model"))
        self.textBrowser_2.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">For help:</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://www.baidu.com\"><span style=\" text-decoration: underline; color:#0000ff;\">train your own model</span></a></p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())