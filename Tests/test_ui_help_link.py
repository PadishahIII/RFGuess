import unittest

from PyQt5 import QtWidgets

from ui.mainWindow import Ui_MainWindow


class TestUiHelpLink(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_help_link_opens_in_external_browser(self):
        window = QtWidgets.QMainWindow()
        ui = Ui_MainWindow()

        ui.setupUi(window)

        self.assertTrue(ui.textBrowser_2.openExternalLinks())
