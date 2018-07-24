# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from petshow_scrapy.items import ArticleItem

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
        return item
