import logging
import random

import scrapy
from scrapy.crawler import CrawlerProcess, Settings

from app.utils import *

from .Spider import SitemapNewsSpider


def spider_take_of(*Spiders: type):

    process = CrawlerProcess(Settings({
        "USER_AGENT": random.choice(yaml_config.net["USER_AGENT"]) or 'Mozilla/5.0',
        "LOG_ENABLED": env.DEBUG,
        "RETRY_ENABLED": True,
        "HTTPERROR_ALLOWED_CODES": [404,403],
        "PROXY": random.choice(yaml_config.net["PROXIES"]) or '',
    }))

    for Spider in Spiders:
        if type(Spider) == type:
            log.debug('Passed "%s" it has a "%s" type' % (Spider, type(Spider)))
            process.crawl(Spider)
            process.start()
        else:
            log.error('The Spider "%s" is not a Class type. %s passed' % (Spider, type(Spider)))


__all__ = ['SitemapNewsSpider', 'spider_take_of']
