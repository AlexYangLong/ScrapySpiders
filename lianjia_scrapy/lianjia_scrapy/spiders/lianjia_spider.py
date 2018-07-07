import json

import scrapy
from scrapy import Request, Selector

from lianjia_scrapy.items import LianjiaScrapyItem


class LianjiaSpider(scrapy.Spider):
    name = 'lianjia'

    base_url = 'https://cd.lianjia.com'
    start_linjia_url = 'https://cd.lianjia.com/ershoufang'

    def start_requests(self):
        yield Request(url=self.start_linjia_url)

    def parse(self, response):
        html = Selector(response)
        area_hrefs = html.xpath('//div[@data-role="ershoufang"]/div/a/@href').extract()
        area_names = html.xpath('//div[@data-role="ershoufang"]/div/a/text()').extract()

        for i in range(len(area_hrefs)):
            # print(area_names[i] + area_hrefs[i])
            yield Request(url=self.base_url + area_hrefs[i],
                          callback=self.parse_list,
                          meta={'area_name': area_names[i], 'area_href': area_hrefs[i]})

    def parse_list(self, response):
        html = Selector(response)
        # class="page-box house-lst-page-box"
        max_page_box = html.xpath('//div[@class="page-box house-lst-page-box"]/@page-data').extract()
        # print('123456', max_page_box)
        max_page_num = json.loads(max_page_box[0]).get('totalPage')

        for i in range(1, int(max_page_num) + 1):
            yield Request(url=self.base_url + response.meta.get('area_href') + 'pg' + str(i),
                          callback=self.parse_house,
                          meta={'area_name': response.meta.get('area_name')})


    def parse_house(self, response):
        html = Selector(response)
        lis = html.xpath('/html/body/div[4]/div[1]/ul/li[@class="clear"]')
        for li in lis:
            item = LianjiaScrapyItem()
            item['house_code'] = li.xpath('./a/@data-housecode').extract()[0]
            item['img_src'] = li.xpath('./a/img/@src').extract()[0]
            item['title'] = li.xpath('./div/div/a/text()').extract()[0]
            item['address'] = li.xpath('./div/div[2]/div/a/text()').extract()[0]
            item['info'] = self.split_str(li.xpath('./div/div[2]/div/text()').extract()[0])
            # print(li.xpath('./div[1]/div[3]/div/text()').extract()[0])
            # print(li.xpath('./div[1]/div[3]/div/a/text()').extract()[0])
            # /html/body/div[4]/div[1]/ul/li[4]/div[1]/div[3]/div/span
            item['floor'] = li.xpath('./div[1]/div[3]/div/text()').extract()[0] + li.xpath('./div[1]/div[3]/div/a/text()').extract()[0]
            item['tag'] = li.xpath('.//div[@class="tag"]/span/text()').extract()
            item['type'] = 'ershoufang'
            item['city'] = '成都'
            item['area'] = li.xpath('/html/body/div[3]/div/div[1]/dl[2]/dd/div[1]/div[1]/a[@class="selected"]/text()').extract()[0]

            #

            yield item

    def split_str(self, origin_str):
        return [s.strip() for s in origin_str.split('|')[1:]]
