class Post:
    """
    Представляет собой пост, хранит весь текст сообщения, публикующего, дату публикации и
    ссылки на аттачи. Введен для удобства хранения информации о каждом сообщении.
    """
    MAX_LENGTH = 100

    def __init__(self, head: tuple[str, str]):
        self.__subject = head[0]
        self.__datetime = head[1]
        self.__text = []
        self.__attaches = []

    def __repr__(self):
        return f'Предмет: {self.__subject}\nОпубликовано: {self.__datetime}'

    def add_line(self, text_line: str):
        self.__text.append(text_line)

    def add_attach(self, attach: tuple):
        self.__attaches.append(attach)

    def get_only_text(self):
        return '\n'.join(self.__text)

    def get_whole_text(self):
        """Получить полный текст сообщения в готовом для вывода виде."""
        text = repr(self) + '\n\n' + '\n'.join(self.__text)
        for attach in self.__attaches:
            if attach[3] == 'link':
                text += f'\n\nНазвание ссылки: {attach[1]}\nСсылка: {attach[0]}'
            else:
                text += f'\n\nИмя файла: {attach[1]}'
        return text

    def get_attaches(self):
        return self.__attaches.copy()

    def get_subject(self):
        return self.__subject

    def get_datetime(self):
        return self.__datetime

    def get_attaches_title(self):
        return ' :: '.join(list(map(lambda x: x[1], self.__attaches)))

