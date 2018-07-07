# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime

import pymongo
import redis

from lianjia_scrapy import settings
from lianjia_scrapy.items import MasterItem


class LianjiaScrapyPipeline(object):
    def __init__(self):
        self.conn = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

    def process_item(self, item, spider):
        if isinstance(item, MasterItem):
            self.conn.lpush('lianjia:start_urls', item['url'])
        return item