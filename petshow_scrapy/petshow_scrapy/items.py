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


class BaikeItem(scrapy.Item):
    table_name = 'baike'

    name = scrapy.Field()
    name_en = scrapy.Field()
    other_name = scrapy.Field()
    cover = scrapy.Field()
    shapes = scrapy.Field()
    ages = scrapy.Field()
    fci_group = scrapy.Field()
    akc_group = scrapy.Field()
    history = scrapy.Field()
    character = scrapy.Field()
    suit_person = scrapy.Field()
    suit_environment = scrapy.Field()
    hair_color = scrapy.Field()
    disease = scrapy.Field()
    tags = scrapy.Field()
    create_time = scrapy.Field()
    # update_time = scrapy.Field()
    admin_id = scrapy.Field()


class Q_AItem(scrapy.Item):
    table_name = 'q_a'

    question = scrapy.Field()
    subtitle = scrapy.Field()
    q_ct = scrapy.Field()
    # q_ut = scrapy.Field()
    q_uid = scrapy.Field()

    answer = scrapy.Field()
    a_ct = scrapy.Field()
    # a_ut = scrapy.Field()
    q_id = scrapy.Field()
    a_uid = scrapy.Field()


class TopicItem(scrapy.Item):
    table_name = 'topic'

    title = scrapy.Field()
    content = scrapy.Field()
    t_ct = scrapy.Field()
    user_id = scrapy.Field()
    views = scrapy.Field()
    cover = scrapy.Field()

    pic_list = scrapy.Field()
    topic_id = scrapy.Field()


class PetItem(scrapy.Item):
    table_name = 'pet'

    # pet info
    owner_name = scrapy.Field()
    owner_avatar = scrapy.Field()
    pet_picture = scrapy.Field()
    like_num = scrapy.Field()
    tag = scrapy.Field()
    create_time = scrapy.Field()
    city = scrapy.Field()
    v_second = scrapy.Field()
    video = scrapy.Field()

    # pet-doodle info
    # user_avatar = scrapy.Field()
    # doodle_time = scrapy.Field()
    # pet_id = scrapy.Field()

    doodle_list = scrapy.Field()

    comment_list = scrapy.Field()

    # doodles info
    # angle = scrapy.Field()
    # center_x = scrapy.Field()
    # center_y = scrapy.Field()
    # zoom = scrapy.Field()
    # doodle_picture = scrapy.Field()
