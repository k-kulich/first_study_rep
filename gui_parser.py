import sys
from PyQt5 import uic
from post import Post  # пост для удобного форматирования вывода в PlainTextEdit
from my_parser import NoTokenError  # ошибки парсера
from data_manager import DataManager, DatatypeError, DataError  # DM и его ошибки
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QHeaderView


class ParserUI(QMainWindow):
    """Весь GUI и основной исполняемый файл."""
    def __init__(self):
        super().__init__()
        try:
            self.dm = DataManager()
        except NoTokenError:
            print('Ошибка доступа: у вас отсутствует токен доступа в виртуальном окружении.')
            self.close()
        uic.loadUi('parser.ui', self)
        # настроить нужный вид заголовков таблицы
        header = self.tableDBView.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.status = self.statusBar()  # инициализировать statusbar
        self.showAttaches()  # загрузить данные об аттачах
        self.loadToFilter()  # загрузить названия предметов для фильтра записей
        self.loadData()  # загрузить текущие данные из таблицы
        # привязка кнопок
        self.loadDataBtn.clicked.connect(self.updateData)
        self.filterBtn.clicked.connect(self.loadData)
        self.loadAttachBtn.clicked.connect(self.downloadLink)

    def updateData(self):
        """
        Синхронизировать данные с выбранными ресурсами (пнуть свой DataManager, чтобы сделал это
        с текущими значениями isChecked() у комбобоксов).
        """
        self.dm.update_db(self.syncVk.isChecked(), self.syncPortal.isChecked())
        self.loadData()

    def loadData(self):
        """
        Загрузить данные из БД в таблицу и PlainTextEdit для удобного просмотра.
        """
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
        """Загрузить данные о предметах для фильтрации."""
        self.subjectFilter.addItems(self.dm.load_subjects())

    def showAttaches(self):
        """Загрузить данные о всех аттачах."""
        self.selectAttach.addItems(list(map(lambda x: f'{x[2]}: {x[1]} <|{x[0]}|>',
                                            self.dm.load_attaches())))

    def downloadLink(self):
        """
        Скачать файл по ссылке. Так как в аттачах находятся не только файлы, но и ссылки на сторонние
        ресурсы, типа зумовских конференций и заданий в гугл форме, которые скачать нельзя,
        предусмотреть неверный ввод и не дать программе вылететь с ошибкой.
        """
        attach = self.selectAttach.currentText()[:-2]
        index = attach.index(':')
        attach_type = attach[:index]
        url = attach.split('<|')[-1]
        title = attach[index + 1:attach.index('<|')].strip()
        try:
            self.dm.ask_parser(url, title, attach_type)
        except DatatypeError:
            self.status.showMessage('Ошибка: нельзя скачать ссылку', 5000)
        except ValueError:
            self.status.showMessage('Ошибка: некорректный запрос', 3000)

    def closeEvent(self, event):
        """При закрытии окна нам нужно сказать DM, чтобы разорвал соединение с БД."""
        self.dm.close_connection()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ParserUI()
    gui.show()
    sys.exit(app.exec())
