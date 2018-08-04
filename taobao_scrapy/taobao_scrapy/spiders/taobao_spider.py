from urllib.parse import quote

import scrapy
from scrapy import Request

from taobao_scrapy.items import TaobaoScrapyItem


class TaobaoSpider(scrapy.Spider):
    name = 'taobao'
    base_url = 'https://s.taobao.com/search?q='

    def start_requests(self):
        for keyword in self.settings.get('KEYWORDS'):
            for page in range(1, self.settings.get('MAX_PAGE') + 1):
                url = self.base_url + quote(keyword)
                yield Request(url=url, callback=self.parse, meta={'page': page}, dont_filter=True)

    def parse(self, response):
        items = response.xpath('//div[@id="mainsrp-itemlist"]//div[@class="items"][1]//div[contains(@class,"item")]')
        for goods in items:
            item = TaobaoScrapyItem()
            item['url'] = 'https:' + goods.xpath('.//div[@class="pic"]/a/@data-href').extract()[0].strip()
            item['image'] = 'https:' + goods.xpath('.//div[@class="pic"]/a/img/@data-src').extract()[0].strip()
            item['price'] = ''.join(goods.xpath('.//div[contains(@class,"price")]//text()').extract()).strip()
            item['deal'] = goods.xpath('.//div[contains(@class,"deal-cnt")]//text()').extract_first()
            item['title'] = ''.join(goods.xpath('.//div[contains(@class,"title")]//text()').extract()).strip()
            item['shop'] = ''.join(goods.xpath('.//div[contains(@class,"shop") ]//text()').extract()).strip()
            item['location'] = goods.xpath ('.//div[contains(@class,"location")]//text()').extract_first()
            yield item
