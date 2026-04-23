import signal

from ui.mainWindow import *
from ui.slots import *


def install_shutdown_handlers(app, slots):
    app.aboutToQuit.connect(slots.shutdown)

    def handle_sigint(*_args):
        app.quit()

    signal.signal(signal.SIGINT, handle_sigint)
    if QtWidgets.QApplication.instance() is not None:
        signal_timer = QtCore.QTimer()
        signal_timer.timeout.connect(lambda: None)
        signal_timer.start(100)
        app._rfguess_signal_timer = signal_timer
    return handle_sigint


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.mainWindow = MainWindow

    slots = Slots(ui)
    install_shutdown_handlers(app, slots)

    MainWindow.show()
    sys.exit(app.exec_())
