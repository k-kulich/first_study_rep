class Post:
    """
    Представляет собой пост, хранит весь текст сообщения, публикующего, дату публикации и
    ссылки на аттачи. Введен для удобства хранения информации о каждом сообщении.
    """
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

    def get_whole_post(self):
        return [repr(self)] + self.__text.copy() + self.__attaches.copy()

    def get_attaches(self):
        return self.__attaches.copy()
