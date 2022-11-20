import requests  # для выполнения GET-запросов
import post  # для хранения сообщений из постов
import time  # для пауз между запросами и форматирования времени из UNIXTIME
from vk_api import VkApi  # готовая библиотека для работы с VK API
from bs4 import BeautifulSoup, element  # для парсинга кода


class Parser:
    """
    Объект, осуществляющий поиск информации на сайтах и возвращающий ее для дальнейшей обработки.
    Использует BeautifulSoup для удобного просмотра HTML-кода страниц.
    """
    URL = {'bitrix': 'https://portal.anichkov.ru/extranet/'}
    AUTHORIZATION = {'bitrix': ('kseniakulis45769@gmail.com', 'An1chk0v')}
    VK_GROUPS = {'al20202022': 'обществознание', 'anichcov10b': 'организационный',
                 '-186147026': 'история', '-207108934': 'русский язык', '-199474162': 'физика'}
    CREATORS = {'Анна Булатова': 'право', 'Николай Быков': 'физика',
                'Елизавета Гайдукова': 'литература', 'Ирина Боярская': 'химия',
                'Дарья Ганзенко': 'история', 'Анна Рогожко': 'география'}

    # TODO: delete hardcoded access_token
    __access_token = 'vk1.a.sPvuT1Nad2hp93ARPEI5X-ZwyWVUAO--4c4ThEi-VvfCQJkyWaD3TBoTudSHZIaKH0ZXAlauKFQYzXCZKORsg9eNJJ9QUORX_50l1ry8YLXNk-wVfh4KjFX3AxXTonmk0Bt9_q42bZ3hZbm-cu5zuoy1aeH3k9idQl3nL_8qhP8Bw-l3lDGfQQxwkHUyaw4-Z4rltGQ3KNkapjpthIkqGg'
    __vkapi_v = '5.131'

    def __init__(self):
        self.vk_session = VkApi(token=self.__access_token)
        self.vk = self.vk_session.get_api()

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
    def __save_bitrix_links(tag, message: post.Post):
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

    @staticmethod
    def __save_vk_attaches(attachments: list, message: post.Post):
        """
        Получить только нужную инфу о закрепах и сохоранить ее в посте.
        :param attachments: список аттачей записи, возвращаемых из vk через json (vk_api конвертит).
        :param message: пост, в котором будет сохранена ссылка на аттач.
        :return: None.
        """
        for attach in attachments:  # перебираем все прикрепленные вещи
            tp = attach['type']  # тип файла
            if tp not in ('photo', 'doc', 'link'):  # нам нужны только 3 типа аттачей
                continue
            size, url = 'unknown', ''
            if tp == 'doc':
                size = f'{round(attach[tp]["size"] / 1024)} KB'
            if tp in {'doc', 'link'}:
                title = attach[tp]['title']
                url = attach[tp]['url']
            else:
                title = 'photo'
                for sz in attach[tp]['sizes']:
                    if sz['type'] == 'y':
                        url = sz['url']
                        break
            message.add_attach((url, title, size))  # добавить к сообщению

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
            # получить данные из "шапки" поста
            post_head = str(tag.contents[0].get_text()), str(tag.contents[2].contents[0].get_text())
            message = post.Post((self.CREATORS.get(post_head[0], 'нераспознанный'), post_head[1]))
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

    def parse_vk(self, post_count=3):
        posts = []
        for group in self.VK_GROUPS:  # перебрать сообщества
            print(group)
            if group[0] == '-':
                response = self.vk.wall.get(owner_id=group, count=post_count)
            else:
                response = self.vk.wall.get(domain=group, count=post_count)
            # перебрать посты в сообществе
            for item in response['items']:
                subj = self.VK_GROUPS[group]
                tm = time.strftime("%d %b %Y %H:%M", time.localtime(item['date']))
                message = post.Post((subj, tm))
                message.add_line(item['text'])
                if item.get('attachments', False):
                    self.__save_vk_attaches(item['attachments'], message)
                posts.append(message)
            time.sleep(0.5)
        return posts
