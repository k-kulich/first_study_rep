import sqlite3
from my_parser import Parser


class DataManager:
    def __init__(self):
        self.__connection = sqlite3.connect('homework_db.sqlite3')
        self.__parser = Parser()

    def __first_big_update(self):
        data = self.__parser.parse_vk(post_count=15) + self.__parser.parse_bitrix(post_limit=30)
        cursor = self.__connection.cursor()
        for post in data:
            sub_id = cursor.execute("""SELECT id FROM subjects
            WHERE title = {}""".format(post.get_subject())).fetchall()
            cursor.execute("""INSERT INTO posts(sub_id, datetime, message, attaches_title) 
            VALUES({}, {}, {}, {})""".format(sub_id, post.get_datetime(), post.get_only_text(),
                                             post.get_attaches_title())).fetchall()
            self.__connection.commit()
            post_id = cursor.execute("""SELECT id FROM posts 
            WHERE message = {}""".format(post.get_only_text())).fetchone()
            for attach in post.get_attaches():
                cursor.execute("""INSERT INTO attachments(link, title, type, post_id)
                VALUES({}, {}, {}, {})""".format(attach[0], attach[1],
                                                 attach[3], post_id)).fetchall()
            self.__connection.commit()

    def update_db(self, sync_vk=True, sync_bitrix=True, need_first_load=False):
        if need_first_load:
            self.__first_big_update()


dm = DataManager()
dm.update_db(need_first_load=True)
