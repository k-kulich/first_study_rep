class Post:
    """
    Представляет собой пост, хранит весь текст сообщения, публикующего, дату публикации и
    ссылки на аттачи. Введен для удобства хранения информации о каждом сообщении.
    """
    MAX_LENGTH = 100

    def __init__(self, head: tuple[str, str]):
        self.__creator = head[0]
        self.__datetime = head[1]
        self.__text = []
        self.__attaches = []

    def __repr__(self):
        return f'Опубликовал: {self.__creator}\nОпубликовано: {self.__datetime}'

    def add_line(self, text_line: str):
        self.__text.append(text_line)

    def add_attach(self, attach: tuple[str, str, str]):
        self.__attaches.append(attach)

    def get_only_text(self):
        return self.__text.copy()

    def get_whole_text(self):
        """Получить полный текст сообщения в готовом для вывода виде."""
        text = repr(self) + '\n\n'
        for line in self.__text:
            new_line = ''
            for word in line.split():
                if len(new_line + word) > self.MAX_LENGTH:
                    text += new_line + '\n'
                    new_line = ''
                new_line += word + ' '
            text += new_line + '\n'
        for attach in self.__attaches:
            text += f'\nИмя файла: {attach[1]}\nРазмер файла: {attach[2]}'
        return text

    def get_attaches(self):
        return self.__attaches.copy()
