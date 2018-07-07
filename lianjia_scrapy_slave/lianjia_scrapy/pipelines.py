# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime

import pymongo

from lianjia_scrapy import settings
from lianjia_scrapy.items import LianjiaScrapyItem


class LianjiaCreateTimePipeline(object):
    def process_item(self, item, spider):
        item['create_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return item


class LianjiaScrapyPipeline(object):
    def __init__(self):
        conn = pymongo.MongoClient(host=settings.MONGODB_HOST, port=settings.MONGODB_PORT)
        db = conn[settings.MONGODB_DB]
        self.collection = db[LianjiaScrapyItem.collection]

    def process_item(self, item, spider):
        if isinstance(item, LianjiaScrapyItem):
            self.collection.update({'house_code': item['house_code']}, {'$set': item}, True)
        return item