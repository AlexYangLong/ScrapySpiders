# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from petshow_scrapy.items import ArticleItem, BaikeItem, Q_AItem

from petshow_scrapy import settings


class PetshowScrapyPipeline(object):
    def __init__(self):
        self.conn = pymysql.connect(host=settings.MYSQL_HOST,
                                    user=settings.MYSQL_USER,
                                    password=settings.MYSQL_PWD,
                                    database=settings.MYSQL_DB,
                                    port=settings.MYSQL_PORT,
                                    charset='utf8',
                                    autocommit=False,
                                    cursorclass=pymysql.cursors.DictCursor  # cursorclass设置cursor游标的类型，这里设置的是dict类型
                                    )

    def process_item(self, item, spider):
        if isinstance(item, ArticleItem):
            item['admin_id'] = 1
            sql = 'insert into article (title, cover, content, create_time, update_time, t_id, admin_id) values (%(title)s, %(cover)s, %(content)s, %(create_time)s, %(update_time)s, %(t_id)s, %(admin_id)s)'
            with self.conn.cursor() as cursor:
                cursor.execute(sql, {
                    'title': item['title'],
                    'cover': item['cover'],
                    'content': item['content'],
                    't_id': item['t_id'],
                    'admin_id': item['admin_id'],
                    'create_time': item['create_time'],
                    'update_time': item['create_time']
                })
                self.conn.commit()
        elif isinstance(item, BaikeItem):
            item['admin_id'] = 1
            sql = 'insert into baike (`name`, name_en, other_name, cover, shapes, ages, fci_group, akc_group, history, `character`, suit_person, suit_environment, hair_color, disease, tags, create_time, update_time, admin_id) values (%(name)s, %(name_en)s, %(other_name)s, %(cover)s, %(shapes)s, %(ages)s, %(fci_group)s, %(akc_group)s, %(history)s, %(character)s, %(suit_person)s, %(suit_environment)s, %(hair_color)s, %(disease)s, %(tags)s, %(create_time)s, %(update_time)s, %(admin_id)s)'
            with self.conn.cursor() as cursor:
                cursor.execute(sql, {
                    'name': item['name'],
                    'name_en': item['name_en'] if item['name_en'] else item['name'],
                    'other_name': item['other_name'] if item['other_name'] else item['name'],
                    'cover': item['cover'],
                    'shapes': item['shapes'] if item['shapes'] else item['name'],
                    'ages': item['ages'] if item['ages'] else item['name'],
                    'fci_group': item['fci_group'] if item['fci_group'] else item['name'],
                    'akc_group': item['akc_group'] if item['akc_group'] else item['name'],
                    'history': item['history'] if item['history'] else item['name'],
                    'character': item['character'] if item['character'] else item['name'],
                    'suit_person': item['suit_person'] if item['suit_person'] else item['name'],
                    'suit_environment': item['suit_environment'] if item['suit_environment'] else item['name'],
                    'hair_color': item['hair_color'] if item['hair_color'] else item['name'],
                    'disease': item['disease'] if item['disease'] else item['name'],
                    'tags': item['tags'] if item['tags'] else item['name'],
                    'create_time': item['create_time'],
                    'admin_id': item['admin_id'],
                    'update_time': item['create_time']
                })
                self.conn.commit()
        elif isinstance(item, Q_AItem):
            item['q_uid'] = 4
            sql_q = 'insert into question (question, subtitle, create_time, update_time, user_id) values (%(question)s, %(subtitle)s, %(create_time)s, %(update_time)s, %(user_id)s)'
            sql_a = 'insert into answer (content, create_time, update_time, question_id, user_id) values (%(content)s, %(create_time)s, %(update_time)s, %(question_id)s, %(user_id)s)'
            with self.conn.cursor() as cursor:
                cursor.execute(sql_q, {
                    'question': item['question'],
                    'subtitle': item['subtitle'],
                    'create_time': item['q_ct'],
                    'update_time': item['q_ct'],
                    'user_id': item['q_uid'],
                })
                cursor.execute('select last_insert_id()')
                d = cursor.fetchall()
                item['q_id'] = d[0].get('last_insert_id()')
                item['a_uid'] = 4
                cursor.execute(sql_a, {
                    'content': item['answer'],
                    'create_time': item['a_ct'],
                    'update_time': item['a_ct'],
                    'question_id': item['q_id'],
                    'user_id': item['a_uid'],
                })
                self.conn.commit()
        return item
