# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from petshow_scrapy.items import ArticleItem, BaikeItem, Q_AItem, TopicItem, PetItem

from petshow_scrapy import settings


class PetshowScrapyPipeline(object):
    def __init__(self, host, port, username, password, db_name):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.db_name = db_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=settings.MYSQL_HOST,
            username=settings.MYSQL_USER,
            password=settings.MYSQL_PWD,
            db_name=settings.MYSQL_DB,
            port=settings.MYSQL_PORT,
        )

    def open_spider(self, spider):
        self.conn = pymysql.connect(host=self.host,
                                    user=self.username,
                                    password=self.password,
                                    database=self.db_name,
                                    port=self.port,
                                    charset='utf8',
                                    autocommit=False,
                                    cursorclass=pymysql.cursors.DictCursor  # cursorclass设置cursor游标的类型，这里设置的是dict类型
                                    )

    def close_spider(self, spider):
        self.conn.close()

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
        elif isinstance(item, TopicItem):
            item['user_id'] = 4
            sql_t = 'insert into topic (title, content, create_time, update_time, user_id, views, cover) values (%(title)s, %(content)s, %(create_time)s, %(update_time)s, %(user_id)s, %(views)s, %(cover)s)'
            sql_p = 'insert into topic_pic (pic, create_time, update_time, topic_id) values (%(pic)s, %(create_time)s, %(update_time)s, %(topic_id)s)'
            with self.conn.cursor() as cursor:
                cursor.execute(sql_t, {
                    'title': item['title'],
                    'content': item['content'],
                    'create_time': item['t_ct'],
                    'update_time': item['t_ct'],
                    'user_id': item['user_id'],
                    'views': item['views'],
                    'cover': item['cover'],
                })
                cursor.execute('select last_insert_id()')
                d = cursor.fetchall()
                item['topic_id'] = d[0].get('last_insert_id()')
                for pic in item['pic_list']:
                    cursor.execute(sql_p, {
                        'pic': pic,
                        'create_time': item['t_ct'],
                        'update_time': item['t_ct'],
                        'topic_id': item['topic_id']
                    })
                self.conn.commit()
        elif isinstance(item, PetItem):
            sql_t = 'insert into pet (username, avatar, picture, like_num, t, create_time, update_time, city, v_second, video) values (%(username)s, %(avatar)s, %(picture)s, %(like_num)s, %(t)s, %(create_time)s, %(update_time)s, %(city)s, %(v_second)s, %(video)s)'
            sql_pd = 'insert into pet_doodle (avatar, create_time, update_time, pet_id) values (%(avatar)s, %(create_time)s, %(update_time)s, %(pet_id)s)'
            sql_d = 'insert into doodles (angle, center_x, center_y, zoom, picture, is_turn, rect_upper_left_x, rect_upper_left_y, rect_width, rect_height, word, pd_id) values (%(angle)s, %(center_x)s, %(center_y)s, %(zoom)s, %(picture)s, %(is_turn)s, %(rect_upper_left_x)s, %(rect_upper_left_y)s, %(rect_width)s, %(rect_height)s, %(word)s, %(pd_id)s)'
            sql_c = 'insert into pet_comment (username, avatar, content, city, create_time, update_time, pet_id) values (%(username)s, %(avatar)s, %(content)s, %(city)s, %(create_time)s, %(update_time)s, %(pet_id)s)'
            with self.conn.cursor() as cursor:
                cursor.execute(sql_t, {
                    'username': item['owner_name'],
                    'avatar': item['owner_avatar'],
                    'picture': item['pet_picture'],
                    'like_num': item['like_num'],
                    't': item['tag'],
                    'create_time': item['create_time'],
                    'update_time': item['create_time'],
                    'city': item['city'],
                    'v_second': item['v_second'],
                    'video': item['video']
                })
                cursor.execute('select last_insert_id()')
                pet = cursor.fetchall()
                pet_id = pet[0].get('last_insert_id()')
                for pd in item['doodle_list']:
                    cursor.execute(sql_pd, {
                        'avatar': pd.get('user_avatar'),
                        'create_time': pd.get('doodle_time'),
                        'update_time': pd.get('doodle_time'),
                        'pet_id': pet_id
                    })
                    cursor.execute('select last_insert_id()')
                    p_d = cursor.fetchall()
                    pd_id = p_d[0].get('last_insert_id()')
                    for d in pd.get('doodle_list'):
                        cursor.execute(sql_d, {
                            'angle': d.get('angle'),
                            'center_x': d.get('center_x'),
                            'center_y': d.get('center_y'),
                            'zoom': d.get('zoom'),
                            'picture': d.get('picture'),
                            'is_turn': d.get('is_turn'),
                            'rect_upper_left_x': d.get('rect_upper_left_x'),
                            'rect_upper_left_y': d.get('rect_upper_left_y'),
                            'rect_width': d.get('rect_width'),
                            'rect_height': d.get('rect_height'),
                            'word': d.get('word'),
                            'pd_id': pd_id
                        })

                for comment in item['comment_list']:
                    cursor.execute(sql_c, {
                        'username': comment.get('c_username'),
                        'avatar': comment.get('c_avatar'),
                        'content': comment.get('c_content'),
                        'city': comment.get('c_city'),
                        'create_time': comment.get('c_time'),
                        'update_time': comment.get('c_time'),
                        'pet_id': pet_id
                    })
                self.conn.commit()
        return item
