import requests  # для выполнения GET-запросов
import post  # для хранения сообщений из постов
from bs4 import BeautifulSoup, element  # для парсинга кода


class Parser:
    """
    Объект, осуществляющий поиск информации на сайтах и возвращающий ее для дальнейшей обработки.
    Использует BeautifulSoup для удобного просмотра HTML-кода страниц.
    """
    URL = {'bitrix': 'https://portal.anichkov.ru/extranet/',
           'vk_russian': 'https://vk.com/club207108934'}
    AUTHORIZATION = {'bitrix': ('kseniakulis45769@gmail.com', 'An1chk0v')}

    def __init__(self):
        self.__links = {'bitrix': []}

    @staticmethod
    def __get_bitrix_soup():
        """
        Отправить запрос GET по адресу сайта portal.anichkov.ru и получить код страницы.
        :return: "суп" - HTML-код в удобном виде благодаря
        """
        url = Parser.URL['bitrix']
        authorize = Parser.AUTHORIZATION['bitrix']
        request = requests.get(url, auth=authorize)
        return BeautifulSoup(request.text, 'lxml')

    @staticmethod
    def __save_bitrix_links(tag, message):
        """
        Сохранить всю информацию о файлах - ссылку на скачивание, название, размер - в Post.
        :param tag: тег, в котором находятся все аттачи конкретного сообщения.
        :param message: post.Post, в который нужно записать данные по аттачам.
        :return: None.
        """
        for div in tag.contents[1].contents[3].children:
            # в данном случае вместо обработки исключения проще избежать его возбуждения
            if type(div) == element.NavigableString:
                continue
            a = div.contents[3].a
            # запомнить все данные по файлам
            message.add_attach((a['href'], a['data-bx-title'], a['data-bx-size']))

    def parse_bitrix(self, post_limit=8):
        """
        Вытянуть информацию с портала Аничкова, сделанного в рамках Bitrix24.
        :param post_limit: int, обозначает число последних записей, с которых нужно взять данные. По
        умолчанию просматриваются последние 8 записей.
        :return: list[tuple[str]], список, в котором каждый пост представлен кортежем из двух других
        кортежей: "шапка" (имя публикующего и дата публикации) и "тело" (текст сообщения и список
        названий файлов). Если пользователь ввел post_limit < 1, то вернуть пустой список.
        """
        if post_limit < 1:
            return []
        soup = self.__get_bitrix_soup()  # получить удобный для парсинга HTML-код страницы
        posts = []  # список постов
        for tag in soup.find_all('div', class_='feed-post-title-block', limit=post_limit):
            message = []
            # получить данные из "шапки" поста
            post_head = str(tag.contents[0].get_text()), str(tag.contents[2].contents[0].get_text())
            message = post.Post(post_head)
            if post_head[0] == 'portal.anichkov.ru':
                message.add_line('Добавлен новый внешний пользователь')
            # получить текст сообщения
            for string in tag.next_sibling.contents[0].stripped_strings:
                message.add_line(str(string).replace('\xa0', ''))
            # перейти к тегу, который должен содержать аттачи
            nxt = tag.next_sibling.next_sibling
            while str(nxt.name) != 'div':
                nxt = nxt.next_sibling
            # если аттачи у текущего сообщения вообще имеются
            if 'disk-attach-block' in str(nxt.get('id')):
                # добавить список названий аттачей к тексту поста
                self.__save_bitrix_links(nxt, message)
            posts.append(message)

        return posts


prs = Parser()
prs.parse_bitrix()
