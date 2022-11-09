import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow


class ParserUI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('parser.ui', self)

    def parse(self):
        pass

    def addLinks(self):
        pass

    def downloadFile(self):
        pass

    def createFile(self):
        pass


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mygui = ParserUI()

    sys.excepthook = except_hook
    mygui.show()
    sys.exit(app.exec())
