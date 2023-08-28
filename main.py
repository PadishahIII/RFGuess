from ui.mainWindow import *
from ui.slots import *

if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.mainWindow = MainWindow

    slots = Slots(ui)

    MainWindow.show()
    sys.exit(app.exec_())
