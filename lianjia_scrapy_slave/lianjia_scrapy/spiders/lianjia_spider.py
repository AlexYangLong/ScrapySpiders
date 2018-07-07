import json

import scrapy
from scrapy import Request, Selector
from scrapy_redis.spiders import RedisSpider

from lianjia_scrapy.items import LianjiaScrapyItem


class LianjiaSpider(RedisSpider):
    name = 'lianjia_slave'

    redis_key = 'lianjia:start_urls'

    def parse(self, response):
        html = Selector(response)
        lis = html.xpath('/html/body/div[4]/div[1]/ul/li[@class="clear"]')
        for li in lis:
            item = LianjiaScrapyItem()
            item['house_code'] = li.xpath('./a/@data-housecode').extract()[0]
            item['img_src'] = li.xpath('./a/img/@src').extract()[0]
            item['title'] = li.xpath('./div/div/a/text()').extract()[0]
            item['address'] = li.xpath('./div/div[2]/div/a/text()').extract()[0]
            item['info'] = self.split_str(li.xpath('./div/div[2]/div/text()').extract()[0])
            item['floor'] = li.xpath('./div[1]/div[3]/div/text()').extract()[0] + li.xpath('./div[1]/div[3]/div/a/text()').extract()[0]
            item['tag'] = li.xpath('.//div[@class="tag"]/span/text()').extract()
            item['type'] = 'ershoufang'
            item['city'] = '成都'
            item['area'] = li.xpath('/html/body/div[3]/div/div[1]/dl[2]/dd/div[1]/div[1]/a[@class="selected"]/text()').extract()[0]

            yield item

    def split_str(self, origin_str):
        return [s.strip() for s in origin_str.split('|')[1:]]
