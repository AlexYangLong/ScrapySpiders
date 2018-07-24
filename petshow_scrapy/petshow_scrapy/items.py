# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticleItem(scrapy.Item):
    table_name = 'article'

    # id = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    cover = scrapy.Field()
    t_id = scrapy.Field()
    admin_id = scrapy.Field()
    create_time = scrapy.Field()

