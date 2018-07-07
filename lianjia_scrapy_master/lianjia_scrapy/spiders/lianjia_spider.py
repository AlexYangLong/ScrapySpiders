import json

import scrapy
from scrapy import Request, Selector

from lianjia_scrapy.items import MasterItem


class LianjiaSpider(scrapy.Spider):
    name = 'lianjia_master'

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
            item = MasterItem()
            item['url'] = self.base_url + response.meta.get('area_href') + 'pg' + str(i)
            yield item
