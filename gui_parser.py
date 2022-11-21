import sys
from PyQt5 import uic
from post import Post
from data_manager import DataManager, DatatypeError, DataError
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QHeaderView


class ParserUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dm = DataManager()
        uic.loadUi('parser.ui', self)
        header = self.tableDBView.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.status = self.statusBar()
        self.showAttaches()
        self.loadToFilter()
        self.updateData()
        self.loadDataBtn.clicked.connect(self.updateData)
        self.filterBtn.clicked.connect(self.loadData)
        self.loadAttachBtn.clicked.connect(self.downloadLink)

    def updateData(self):
        self.dm.update_db(self.syncVk.isChecked(), self.syncPortal.isChecked())
        self.loadData()

    def loadData(self):
        self.messageTextView.clear()
        data = self.dm.load_from_db(self.subjectFilter.currentText())  # получить данные из БД
        # заполнить таблицу
        self.tableDBView.setRowCount(0)
        for i, row in enumerate(data):
            self.tableDBView.setRowCount(self.tableDBView.rowCount() + 1)
            for j, elem in enumerate(row[:-2]):
                self.tableDBView.setItem(i, j, QTableWidgetItem(str(elem)))
            self.tableDBView.setItem(i, j + 1, QTableWidgetItem(str(row[-1])))
        # заполнить поле PlainText
        for i, line in enumerate(data, 1):
            post = Post((line[0], line[1]))
            post.add_line(line[2])
            for attach in line[3].split(' :: '):
                try:
                    attach = self.dm.find_attach(attach)
                    post.add_attach((attach[0], attach[1], '', attach[2]))
                except DataError:
                    continue
            self.messageTextView.appendPlainText('\n\n' + '-' * 20 + f' Message {i} ' + '-' * 20
                                                 + '\n\n')
            self.messageTextView.appendPlainText(post.get_whole_text())

    def loadToFilter(self):
        self.subjectFilter.addItems(self.dm.load_subjects())

    def showAttaches(self):
        self.selectAttach.addItems(list(map(lambda x: f'{x[2]}: {x[1]} <|{x[0]}|>',
                                            self.dm.load_attaches())))

    def downloadLink(self):
        attach = self.selectAttach.currentText()[:-2]
        index = attach.index(':')
        attach_type = attach[:index]
        url = attach.split('<|')[-1]
        title = attach[index + 1:attach.index('<|')].strip()
        try:
            self.dm.ask_parser(url, title, attach_type)
        except DatatypeError:
            self.status.showMessage('Ошибка: нельзя скачать ссылку', 5000)

    def closeEvent(self, event):
        self.dm.close_connection()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mygui = ParserUI()

    sys.excepthook = except_hook
    mygui.show()
    sys.exit(app.exec())
