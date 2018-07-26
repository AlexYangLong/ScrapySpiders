import json
import re

import scrapy
from datetime import datetime
from scrapy import FormRequest, Request

from petshow_scrapy.items import ArticleItem, BaikeItem, Q_AItem, TopicItem


class PetShowSpider(scrapy.Spider):
    name = 'petshow'

    # 用于本地数据库映射
    type_dict = {
        '趣闻': 2,
        '狗狗': 4,
        '发现': 5,
        '动图': 6,
        '轶事': 7,
        '萌讯': 8,
        '事件': 9,
        '猫咪': 10,
        '小宠': 11,
        '水族': 12,
        '花鸟': 13,
        '爬虫': 14
    }

    # PetShow网站上新鲜事的分类
    f_tag_dict = {'222': '趣闻', '227': '发现', '218': '动图', '220': '轶事', '217': '萌讯', '219': '事件'}
    # PetShow网站上涨知识的分类
    k_tag_dict = {'110': '狗狗', '24': '猫咪', '215': '小宠', '221': '水族', '233': '花鸟', '234': '爬虫'}

    # 新鲜事列表接口
    fresh_url = 'http://www.petshow.cc/v2/articlelist?page={page}&tag_id={tag}'
    # 涨知识列表接口
    knowledge_url = 'http://www.petshow.cc/v2/articlelisttwo?page={page}&tag_id={tag}'

    # 新鲜事、涨知识文章内容页
    article_url = 'http://www.petshow.cc/a/{aid}.html'

    # 百科接口
    baike_url = 'http://www.petshow.cc/v2/baikelist?page={page}&tag_id=0'

    # 萌专题列表接口
    topic_url = 'http://www.petshow.cc/v2/topiclist?page={page}'
    # 萌专题内容页
    topic_c_url = 'http://www.petshow.cc/v2/topic'

    # 问答列表接口
    q_a_url = 'http://www.petshow.cc/v2/questionlist?page={page}&tag_id=0'
    # 问答内容页
    q_a_c_url = 'http://www.petshow.cc/q/{qid}.html'

    # 涂鸦列表接口
    ty_url = ''

    def start_requests(self):
        """开始爬取"""
        for k, v in self.f_tag_dict.items():
            yield FormRequest(url=self.fresh_url.format(page='1', tag=k),
                              formdata={'pagesize': '20'},
                              meta={'t': 'f', 'tag_id': k, 'tag_v': v},
                              callback=self.parse_page)

        for k, v in self.k_tag_dict.items():
            yield FormRequest(url=self.knowledge_url.format(page='1', tag=k),
                              formdata={'pagesize': '20'},
                              meta={'t': 'k', 'tag_id': k, 'tag_v': v},
                              callback=self.parse_page)

        yield FormRequest(url=self.baike_url.format(page='1'),
                          meta={'t': 'b'},
                          callback=self.parse_page)

        yield FormRequest(url=self.topic_url.format(page='1'),
                          formdata={'pagesize': '20'},
                          meta={'t': 't'},
                          callback=self.parse_page)

        yield FormRequest(url=self.q_a_url.format(page='1'),
                          meta={'t': 'q'},
                          callback=self.parse_page)

    def parse_page(self, response):
        """解析总页数"""
        data = json.loads(response.text)
        if data.get('data').get('page_data').get('page_total'):
            page_count = int(data.get('data').get('page_data').get('page_total'))
            tag_id = response.meta.get('tag_id')
            tag_v = response.meta.get('tag_v')
            t = response.meta.get('t')
            for i in range(1, page_count + 1):
                if t == 'f':
                    yield FormRequest(url=self.fresh_url.format(page=str(i), tag=tag_id),
                                      formdata={'pagesize': '20'},
                                      meta={'tag_v': tag_v},
                                      callback=self.parse_list,
                                      dont_filter=True)
                elif t == 'k':
                    yield FormRequest(url=self.knowledge_url.format(page=str(i), tag=tag_id),
                                      formdata={'pagesize': '20'},
                                      meta={'tag_v': tag_v},
                                      callback=self.parse_list,
                                      dont_filter=True)
                elif t == 'b':
                    yield FormRequest(url=self.baike_url.format(page=i),
                                      meta={'t': 'b'},
                                      callback=self.parse_baike,
                                      dont_filter=True)
                elif t == 'q':
                    yield FormRequest(url=self.q_a_url.format(page=i),
                                      meta={'t': 'q'},
                                      callback=self.parse_q_list,
                                      dont_filter=True)
                elif t == 't':
                    yield FormRequest(url=self.topic_url.format(page=i),
                                      meta={'t': 't'},
                                      callback=self.parse_t_list,
                                      dont_filter=True)
        else:
            print('下载数据出错')

    def parse_list(self, response):
        """解析新鲜事、涨知识列表"""
        data = json.loads(response.text)
        if data.get('data').get('list'):
            list = data.get('data').get('list')
            t_id = self.type_dict[response.meta.get('tag_v')]
            for art in list:
                title = art.get('title')
                cover = art.get('picture1')
                c_t = art.get('create_time')
                id = art.get('id')
                yield Request(url=self.article_url.format(aid=id),
                              meta={'title': title, 'cover': cover, 't_id': t_id, 'c_t': c_t},
                              callback=self.parse_content)

    def parse_content(self, response):
        """解析新鲜事、涨知识的内容页"""
        html = response.text
        if html:
            item = ArticleItem()
            item['content'] = re.findall(r'.*<div class="article_nr_content">(.*?)</div>.*', html, re.S)[0].strip()
            item['title'] = response.meta.get('title')
            item['cover'] = response.meta.get('cover')
            item['t_id'] = response.meta.get('t_id')
            item['create_time'] = response.meta.get('c_t')
            # print(item['content'])
            yield item

    def parse_baike(self, response):
        """解析百科"""
        data = json.loads(response.text)
        if data.get('data').get('list'):
            list = data.get('data').get('list')
            for bk in list:
                item = BaikeItem()
                item['name'] = bk.get('name')
                item['name_en'] = bk.get('english_name')
                item['other_name'] = bk.get('alias')
                item['cover'] = bk.get('picture')
                item['shapes'] = bk.get('figure')
                item['ages'] = bk.get('life')
                item['fci_group'] = bk.get('fci_group')
                item['akc_group'] = bk.get('akc_group')
                item['history'] = bk.get('history')
                item['character'] = bk.get('character')
                item['suit_person'] = bk.get('crowd')
                item['suit_environment'] = bk.get('environment')
                item['hair_color'] = bk.get('hair_color_description')
                item['disease'] = bk.get('disease')
                item['tags'] = bk.get('baike_tags')
                item['create_time'] = bk.get('create_time')
                yield item

    def parse_q_list(self, response):
        """解析问答列表"""
        data = json.loads(response.text)
        if data.get('data').get('list'):
            list = data.get('data').get('list')
            for ques in list:
                question = ques.get('title')
                subtitle = ques.get('content')
                q_ct = ques.get('create_time')
                id = ques.get('id')
                yield Request(url=self.q_a_c_url.format(qid=id),
                              meta={'question': question, 'subtitle': subtitle, 'q_ct': q_ct},
                              callback=self.parse_answer)

    def parse_answer(self, response):
        """解析问答内容页"""
        html = response.text
        if html:
            item = Q_AItem()
            item['answer'] = re.findall(r'.*<div class="pet_question_form_content">(.*?)</div>.*', html, re.S)[0].strip()
            item['question'] = response.meta.get('question')
            item['subtitle'] = response.meta.get('subtitle')
            item['q_ct'] = response.meta.get('q_ct')
            item['a_ct'] = response.meta.get('q_ct')
            # print(item['content'])
            yield item

    def parse_t_list(self, response):
        """解析萌专题列表页"""
        data = json.loads(response.text)
        if data.get('data').get('list'):
            list = data.get('data').get('list')
            for topic in list:
                title = topic.get('name')
                content = topic.get('intro')
                views = topic.get('count')
                cover = topic.get('top_album')
                id = topic.get('id')
                yield FormRequest(url=self.topic_c_url,
                                  formdata={'tag_id': id, 'page': '1', 'pagesize': '50'},
                                  meta={'id': id, 'title': title, 'content': content, 'views': views, 'cover': cover, 'page': '1'},
                                  callback=self.parse_tcp_list,
                                  dont_filter=True)

    def parse_tcp_list(self, response):
        """解析萌专题内容页的图片列表"""
        data = json.loads(response.text)
        if data.get('data').get('page_data').get('page_total'):
            page_count = int(data.get('data').get('page_data').get('page_total'))
            next_page = int(response.meta.get('page')) + 1
            pics = response.meta.get('pics', [])
            list = data.get('data').get('list')
            for tcp in list:
                pics.append(tcp.get('picture'))
            if next_page <= page_count:
                yield FormRequest(url=self.topic_c_url,
                                  formdata={'tag_id': response.meta['id'], 'page': str(next_page), 'pagesize': '50'},
                                  meta={'page': str(next_page), 'id': response.meta['id'], 'title': response.meta['title'], 'content': response.meta['content'], 'views': response.meta['views'], 'cover': response.meta['cover'], 'pics': pics},
                                  callback=self.parse_tcp_list,
                                  dont_filter=True)
            else:
                item = TopicItem()
                item['title'] = response.meta.get('title')
                item['content'] = response.meta.get('content')
                item['views'] = response.meta.get('views')
                item['cover'] = response.meta.get('cover')
                item['t_ct'] = datetime.now()
                item['pic_list'] = pics
                yield item

            # for i in range(1, page_count + 1):
            #     yield FormRequest(url=self.topic_c_url,
            #                       formdata={'tag_id': response.meta['id'], 'page': str(i), 'pagesize': '50'},
            #                       meta={'title': response.meta['title'], 'content': response.meta['content'], 'views': response.meta['views'], 'cover': response.meta['cover']},
            #                       callback=self.parse_tcp,
            #                       dont_filter=True)

    # def parse_tcp(self, response):
    #     data = json.loads(response.text)
    #     if data.get('data').get('list'):
    #         list = data.get('data').get('list')
    #         item = TopicItem()
    #         item['title'] = response.meta.get('title')
    #         item['content'] = response.meta.get('content')
    #         item['views'] = response.meta.get('views')
    #         item['cover'] = response.meta.get('cover')
    #         item['t_ct'] = datetime.now()
    #         item['pic_list'] = []
    #         for tcp in list:
    #             item['pic_list'].append(tcp.get('picture'))
    #         yield item
