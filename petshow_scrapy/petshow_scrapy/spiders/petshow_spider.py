import json
import re

import scrapy
from scrapy import FormRequest, Request, Selector

from petshow_scrapy.items import ArticleItem


class PetShowSpider(scrapy.Spider):
    name = 'petshow'

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

    f_tag_dict = {'222': '趣闻', '227': '发现', '218': '动图', '220': '轶事', '217': '萌讯', '219': '事件'}
    k_tag_dict = {'110': '狗狗', '24': '猫咪', '215': '小宠', '221': '水族', '233': '花鸟', '234': '爬虫'}

    fresh_url = 'http://www.petshow.cc/v2/articlelist?page={page}&tag_id={tag}'
    knowledge_url = 'http://www.petshow.cc/v2/articlelisttwo?page={page}&tag_id={tag}'

    article_url = 'http://www.petshow.cc/a/{aid}.html'

    # baike_url = 'http://www.petshow.cc/wiki.html'
    # qa_url = 'http://www.petshow.cc/q.html'
    # topic_url = 'http://www.petshow.cc/t.html'

    def start_requests(self):
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

    def parse_page(self, response):
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
                                      callback=self.parse_list)
                elif t == 'k':
                    yield FormRequest(url=self.knowledge_url.format(page=str(i), tag=tag_id),
                                      formdata={'pagesize': '20'},
                                      meta={'tag_v': tag_v},
                                      callback=self.parse_list)
        else:
            print('下载数据出错')

    def parse_list(self, response):
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

