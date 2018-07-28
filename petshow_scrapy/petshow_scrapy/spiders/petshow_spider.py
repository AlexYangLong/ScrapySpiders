import json
import re

import scrapy
from datetime import datetime
from scrapy import FormRequest, Request, Selector

from petshow_scrapy.items import ArticleItem, BaikeItem, Q_AItem, TopicItem, PetItem


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
    ty_url = ['http://www.petshow.cc/v2/indexhotlist', 'http://www.petshow.cc/v2/indexnewestlist', 'http://www.petshow.cc/v2/indexvoicelist']
    ty_c_url = 'http://www.petshow.cc/g/{tyid}.html'
    ty_d_list = 'http://www.petshow.cc/v2/petalbumgraffitolist?pet_album_id={did}'
    ty_comment = 'http://www.petshow.cc/v2/petalbumcommentlist?pet_album_id={cid}'

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

        for url in self.ty_url:
            if 'voice' in url:
                yield FormRequest(url=url,
                                  formdata={'page':'1', 'pagesize':'200'},
                                  meta={'t': 'ty', 'tag': '语音涂鸦'},
                                  callback=self.parse_page)
            else:
                yield FormRequest(url=url,
                                  formdata={'page': '1', 'pagesize': '200'},
                                  meta={'t': 'ty', 'tag': '图片涂鸦'},
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
                elif t == 'ty':
                    yield FormRequest(url=response.url,
                                      formdata={'page': str(i), 'pagesize': '200'},
                                      meta={'t': 'ty', 'tag': response.meta.get('tag')},
                                      callback=self.parse_ty_list)
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

    def parse_ty_list(self, response):
        """解析涂鸦的列表"""
        data = json.loads(response.text)
        if data.get('data').get('list'):
            list = data.get('data').get('list')
            tag = response.meta.get('tag')
            for ty in list:
                # print(response.url, ty.get('id'))
                pet_pic = ty.get('picture')
                like_num = ty.get('like_num')
                if ty.get('user'):
                    owner_name = ty.get('user').get('nick')
                    owner_avatar = ty.get('user').get('avatar')
                else:
                    owner_name = ''
                    owner_avatar = ''
                id = ty.get('id')
                yield Request(url=self.ty_c_url.format(tyid=id),
                              meta={'id': id, 'tag': tag, 'pet_pic': pet_pic, 'like_num': like_num, 'owner_name': owner_name, 'owner_avatar': owner_avatar},
                              callback=self.parse_ty_content)

    def parse_ty_content(self, response):
        """解析涂鸦内容页"""
        html = Selector(response)
        if html.xpath('//div[@class="pet-voice"]'):
            v_second = html.xpath('//div[@class="pet-voice"]/text()').extract()[0]
            video = html.xpath('//audio[@class="pet-music"]/@src').extract()[0]
        else:
            v_second = ''
            video = ''

        city = html.xpath('//div[@class="am_tuya_user_info_coordinate"]/text()').extract()[0].split(' ')[-1]
        meta_d = {
            'id': response.meta.get('id'),
            'tag': response.meta.get('tag'),
            'pet_pic': response.meta.get('pet_pic'),
            'like_num': response.meta.get('like_num'),
            'owner_name': response.meta.get('owner_name'),
            'owner_avatar': response.meta.get('owner_avatar'),
            'city': city,
            'v_second': v_second,
            'video': video
        }
        yield FormRequest(url=self.ty_d_list.format(did=response.meta.get('id')),
                          meta=meta_d,
                          callback=self.parse_doodle)

    def parse_doodle(self, response):
        """解析其他用户对图片的涂鸦内容"""
        data = json.loads(response.text)
        if data.get('data') and data.get('data').get('list'):
            list = data.get('data').get('list')
            if len(list) > 0:
                create_time = list[-1].get('create_time')
            else:
                create_time = datetime.now()
            pd_list = []
            for doodle in list:
                user = {}
                user['user_avatar'] = doodle.get('avatar')
                user['doodle_time'] = doodle.get('create_time')
                user['doodle_list'] = []
                for d in doodle.get('chartlet_list'):
                    d_dict = {}
                    d_dict['angle'] = d.get('angle')
                    d_dict['center_x'] = d.get('center_x')
                    d_dict['center_y'] = d.get('center_y')
                    d_dict['zoom'] = d.get('zoom')
                    d_dict['picture'] = d.get('picture')
                    d_dict['is_turn'] = d.get('is_turn')
                    d_dict['rect_upper_left_x'] = d.get('rect_upper_left_x')
                    d_dict['rect_upper_left_y'] = d.get('rect_upper_left_y')
                    d_dict['rect_width'] = d.get('rect_width')
                    d_dict['rect_height'] = d.get('rect_height')
                    d_dict['word'] = d.get('word')

                    user['doodle_list'].append(d_dict)

                pd_list.append(user)

            meta_d = {
                'id': response.meta.get('id'),
                'tag': response.meta.get('tag'),
                'pet_pic': response.meta.get('pet_pic'),
                'like_num': response.meta.get('like_num'),
                'owner_name': response.meta.get('owner_name'),
                'owner_avatar': response.meta.get('owner_avatar'),
                'city': response.meta.get('city'),
                'v_second': response.meta.get('v_second'),
                'video': response.meta.get('video'),
                'doodle_list': pd_list,
                'create_time': create_time
            }
            yield FormRequest(url=self.ty_comment.format(cid=response.meta.get('id')),
                              meta=meta_d,
                              callback=self.parse_comment)

    def parse_comment(self, response):
        """解析涂鸦评论"""
        data = json.loads(response.text)
        comment_list = []
        if data.get('data') and data.get('data').get('list'):
            list = data.get('data').get('list')
            for comment in list:
                c_d = {}
                c_d['c_username'] = comment.get('user').get('nick')
                c_d['c_avatar'] = comment.get('user').get('avatar')
                c_d['c_city'] = comment.get('user').get('city')
                c_d['c_content'] = comment.get('content')
                c_d['c_time'] = comment.get('create_time')
                comment_list.append(c_d)
        item = PetItem()
        item['owner_name'] = response.meta.get('owner_name')
        item['owner_avatar'] = response.meta.get('owner_avatar')
        item['pet_picture'] = response.meta.get('pet_pic')
        item['like_num'] = response.meta.get('like_num')
        item['tag'] = response.meta.get('tag')
        item['create_time'] = response.meta.get('create_time')
        item['city'] = response.meta.get('city')
        item['v_second'] = response.meta.get('v_second')
        item['video'] = response.meta.get('video')

        item['doodle_list'] = response.meta.get('doodle_list')
        item['comment_list'] = comment_list

        yield item
