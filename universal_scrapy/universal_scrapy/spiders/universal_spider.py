from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from universal_scrapy.items import NewsItem

from universal_scrapy.itemloader import ChinaLoader

from universal_scrapy.utils import get_config

from universal_scrapy.rules import rules
from universal_scrapy import urls


class UniversalSpider(CrawlSpider):
    name = 'universal'

    def __init__(self, name, *args, ** kwargs):
        """初始化，从json中获取配置信息"""
        config = get_config(name)
        self.config = config
        self.rules = rules.get(config.get('rules'))
        # self.start_urls = config.get('start_urls')
        start_urls = config.get('start_urls')
        if start_urls:
            if start_urls.get('type') == 'static':
                self.start_urls = start_urls.get('value')
            elif start_urls.get('type') == 'dynamic':
                self.start_urls = list(eval('urls.' + start_urls.get('method'))(start_urls.get('base_url'), *start_urls.get('args', [])))
        self.allowed_domains = config.get('allowed_domains')
        super(UniversalSpider, self).__init__(*args, ** kwargs)

    def parse_item(self, response):
        items = self.config.get('item')
        if items:
            # 从json中获取Item类
            cls = eval(items.get('class'))()
            # 根据Item类和json中配置的Loader类生成Loader
            loader = eval(items.get('item_loader'))(cls, response=response)
            # 动态获取属性配置
            for key, value in items.get('attrs').items():
                for extractor in value:
                    if extractor.get('method') == 'xpath':
                        loader.add_xpath(key, *extractor.get('args'), **{'re': extractor.get('re')})
                    if extractor.get('method') == 'css':
                        loader.add_css(key, *extractor.get('args'), **{'re': extractor.get('re')})
                    if extractor.get('method') == 'value':
                        loader.add_value(key, *extractor.get('args'), **{'re': extractor.get('re')})
                    if extractor.get('method') == 'attr':
                        loader.add_value(key, getattr(response, *extractor.get('args')))
            yield loader.load_item()

    # 初始写法
    # name = 'china'
    # allowed_domains = ['tech.china.com']
    # start_urls = ['https://tech.china.com/articles/']
    #
    # rules = [
    #     Rule(LinkExtractor('article\/.*\.html', restrict_xpaths='//div[@id="left_side"]//div[@class="con_item"]'), callback='parse_item', follow=True),
    #     Rule(LinkExtractor(restrict_xpaths='//div[@id="pageStyle"]//a[contains(.,"下一页")]'))
    # ]
    #

    # def parse_item(self, response):
    #     loader = ChinaLoader(item=NewsItem(), response=response)
    #     loader.add_xpath('title', '//h1[@id="chan_newsTitle"]/text()')
    #     loader.add_value('url', response.url)
    #     loader.add_xpath('text', '//div[@id="chan_newsDetail"]')
    #     loader.add_xpath('datetime', '//div[@id="chan_newsInfo"]/text()', re='(\d+-\d+-\d+\s\d+:\d+:\d+)')
    #     loader.add_xpath('source', '//div[@id="chan_newsInfo"]/text()', re='来源：(.*)')
    #     loader.add_value('website', '中华网')
    #     yield loader.load_item()

        # item = UniversalScrapyItem()
        # item['title'] = response.xpath('//h1[@id="chan_newsTitle"]/text()').extract_first()
        # item['url'] = response.url
        # item['text'] = response.xpath('//div[@id="chan_newsDetail"]').extract()[0]
        # item['datetime'] = response.xpath('//div[@id="chan_newsInfo"]/text()').re_first('(\d+-\d+-\d+\s\d+:\d+:\d+)')
        # item['source'] = response.xpath('//div[@id="chan_newsInfo"]/text()').re_first('来源：(.*)').strip()
        # item['website'] = '中华网'
        # yield item
