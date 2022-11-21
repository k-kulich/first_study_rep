import sqlite3
import os
from my_parser import Parser


class DataManager:
    """Осуществляет все взаимодействие с БД: от обновления до получения данных. Парсером также
    управляет этот класс."""
    def __init__(self):
        self.__connection = sqlite3.connect('homework_db.sqlite3')
        self.__parser = Parser()
        self.__loaded_attaches = set()

    def __add_to_db(self, cursor, post):
        """Добавляет всю информацию поста в БД."""
        sub_id = cursor.execute("""SELECT id FROM subjects
                    WHERE title = ?""", (post.get_subject(),)).fetchall()[0][0]
        cursor.execute("""INSERT INTO posts(sub_id, datetime, message, attaches_title) 
                    VALUES (?, ?, ?, ?)""", (sub_id, post.get_datetime(), post.get_only_text(),
                                             post.get_attaches_title()))
        self.__connection.commit()
        post_id = cursor.execute("""SELECT id FROM posts 
                    WHERE message = ?""", (post.get_only_text(),)).fetchone()[0]
        for attach in post.get_attaches():
            cursor.execute("""INSERT INTO attachments(link, title, type, post_id)
                        VALUES(?, ?, ?, ?)""", (attach[0], attach[1], attach[3], post_id))
        self.__connection.commit()

    def __first_big_update(self):
        """Создана для первой загрузки данных в таблицу, чтобы поместить туда все, что может
        пригодиться в ближайшее время."""
        data = self.__parser.parse_vk(post_count=15) + self.__parser.parse_bitrix(post_limit=30)
        cursor = self.__connection.cursor()
        for post in data:
            self.__add_to_db(cursor, post)

    def update_db(self, sync_vk=True, sync_bitrix=True, need_first_load=False):
        """
        Обновить данные - подгрузить то, что нужно, ели оно нужно.
        :param sync_vk: нужно ли парсить вк.
        :param sync_bitrix: нужно ли парсить битрикс.
        :param need_first_load: необходимо ли сначала заполнить таблицу данными за последние пару
        месяцев.
        :return: None.
        """
        if need_first_load:
            self.__first_big_update()
        data = []
        if sync_vk:
            data += self.__parser.parse_vk()
        if sync_bitrix:
            data += self.__parser.parse_bitrix()
        cursor = self.__connection.cursor()
        pushed_data = set(map(lambda x: x[0],
                              cursor.execute("""SELECT message FROM posts""").fetchall()))
        to_push = set(map(lambda x: x.get_only_text(), data))
        to_push = to_push - (to_push & pushed_data)
        for post in data:
            if post.get_only_text() in to_push:
                self.__add_to_db(cursor, post)

    def load_from_db(self, subject_filter='все'):
        """
        Получить данные из БД и вернуть их.
        :param subject_filter: фильтр по предмету.
        :return: список совпадений из базы, согласно фильтру.
        """
        if subject_filter != 'все':
            data = self.__connection.cursor().execute("""SELECT
                subjects.title as tit,
                posts.datetime as dt,
                posts.message as mess,
                posts.attaches_title
            FROM posts
            INNER JOIN subjects
            ON 
                posts.sub_id IN (SELECT id FROM subjects WHERE title = tit) 
                AND tit = ?""", (subject_filter,)).fetchall()
        else:
            data = self.__connection.cursor().execute("""SELECT
            subjects.title as tit,
            posts.datetime as dt,
            posts.message as mess,
            posts.attaches_title
            FROM posts
            INNER JOIN subjects
            ON posts.sub_id IN (SELECT id FROM subjects WHERE title = tit)""").fetchall()
        return data

    def load_attaches(self):
        """
        Получить все ссылки из БД.
        :return: список аттачей (ссылка, название, тип).
        """
        data = self.__connection.cursor().execute("""SELECT link, title, type 
        FROM attachments""").fetchall()
        self.__loaded_attaches |= set(data)
        return data

    def load_subjects(self):
        """
        Получить названия всех предметов, которые есть в ДБ.
        :return: список названий предметов.
        """
        return list(map(lambda x: x[0],
                        self.__connection.cursor().execute("""SELECT title 
                        FROM subjects""").fetchall()))

    def ask_parser(self, url, title, link_type):
        if link_type == 'photo':
            index = url.index('?')
            title = url[url[:index].rindex('/') + 1:index]
        elif link_type != 'doc':
            raise DatatypeError
        way = os.getcwd() + f'\\parsed_attaches\\{title}'
        self.__parser.get_attach_by_url(url, way)

    def find_attach(self, title):
        for attach in self.__loaded_attaches:
            if attach[1] == title:
                return attach
        raise DataError

    def close_connection(self):
        """Разрыв соединения с базой."""
        self.__connection.close()


class DatatypeError(Exception):
    """Ошибка типа данных."""


class DataError(Exception):
    """Ошибка данных."""
