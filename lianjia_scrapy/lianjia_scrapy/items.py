# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LianjiaScrapyItem(scrapy.Item):
    collection = 'ershoufang'

    house_code = scrapy.Field()
    img_src = scrapy.Field()
    title = scrapy.Field()
    address = scrapy.Field()
    info = scrapy.Field()
    floor = scrapy.Field()
    tag = scrapy.Field()
    type = scrapy.Field()
    city = scrapy.Field()
    area = scrapy.Field()
    create_time = scrapy.Field()
