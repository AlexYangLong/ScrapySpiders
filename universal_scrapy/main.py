# from scrapy.cmdline import execute
#
# execute(['scrapy', 'crawl', 'china'])
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from universal_scrapy.utils import get_config


def run():
    name = sys.argv[1]
    custom_config = get_config(name)
    # 获取json配置中的要爬取的爬虫名
    spider_name = custom_config.get('spider')
    project_settings = get_project_settings()
    settings = dict(project_settings.copy())
    # 合并配置
    settings.update(custom_config.get('settings'))
    process = CrawlerProcess(settings)
    # 启动爬虫
    process.crawl(spider_name, **{'name': name})
    process.start()


if __name__ == '__main__':
    run()
