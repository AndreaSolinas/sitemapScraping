import random
from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from app.utils import *
import json, cloudscraper
from scrapy.spiders import SitemapSpider, XMLFeedSpider, Spider


def __timing(method):
    def wrapper(self):
        timing = datetime.now()
        log.debug("Start")
        method(self)
        log.debug("Finish")
        log.info(f'"{method.__name__}" ha impiegato {(datetime.now() - timing)}')

    return wrapper

class RssFeedSpider(XMLFeedSpider):
    #TODO: Creare uno scraper per analizzare i feed rss.
    pass


class SitemapNewsSpider(SitemapSpider):
    name = 'sitemapArticleSpider'
    data: list = []

    sitemap_urls: str | list = []

    @staticmethod
    def check_response(response):
        if response.status != 403:
            return response
        else:
            cloudflare = cloudscraper.create_scraper(response.url)
            if cloudflare.status_code == 200:
                return cloudflare
            else:
                log.error("The request failed with status code: " + str(cloudflare.status_code))

    def parse(self, response):
        response = self.check_response(response)

        title = response.css('title::text').get()
        canonical = response.xpath('//link[@rel="canonical"]/@href').get()
        self.data.append(
            {
                'url': response.url,
                'title': title,
                'canonical': canonical,
                'og_tags': self.scrape_og(response),
                'schema': self.scrape_schema(response)
            }
        )

        return self.data

    @staticmethod
    def get_url():
        for data in SitemapNewsSpider.data:
            yield data['url']

    @staticmethod
    def scrape_og(response) -> dict:
        og_tags = {}
        for meta in response.xpath('//meta[starts-with(@property, "og:")]'):
            property_name = meta.xpath('@property').get()
            content = meta.xpath('@content').get()
            if property_name and content:
                og_tags[property_name] = content
        return og_tags

    @staticmethod
    def scrape_schema(response) -> list:
        schema_data = []
        for script in response.xpath('//script[@type="application/ld+json"]/text()').getall():
            try:
                schema_json = json.loads(script)
                if isinstance(schema_json, list):
                    log.debug("this schema is a list")
                    log.debug(schema_json)
                    for thing in schema_json:
                        schema_data.append(thing)
                elif isinstance(schema_json, dict):
                    schema_data.append(schema_json)
            except json.JSONDecodeError:
                log.error(f"Error to parse JSON-LD: {script}")
        return schema_data

class NewsArticleSpider(Spider):
    name = 'ArticleSpider'
    data: list = []

    start_urls: str | list = []

    @staticmethod
    def check_response(response):
        if response.status != 403:
            return response
        else:
            cloudflare = cloudscraper.create_scraper(response.url)
            if cloudflare.status_code == 200:
                return cloudflare
            else:
                log.error("The request failed with status code: " + str(cloudflare.status_code))

    def parse(self, response):
        response = self.check_response(response)

        title = response.css('title::text').get()
        canonical = response.xpath('//link[@rel="canonical"]/@href').get()
        self.data.append(
            {
                'url': response.url,
                'title': title,
                'canonical': canonical,
                'og_tags': self.scrape_og(response),
                'schema': self.scrape_schema(response)
            }
        )

        return self.data

    @staticmethod
    def get_url():
        for data in SitemapNewsSpider.data:
            yield data['url']

    @staticmethod
    def scrape_og(response) -> dict:
        og_tags = {}
        for meta in response.xpath('//meta[starts-with(@property, "og:")]'):
            property_name = meta.xpath('@property').get()
            content = meta.xpath('@content').get()
            if property_name and content:
                og_tags[property_name] = content
        return og_tags

    @staticmethod
    def scrape_schema(response) -> list:
        schema_data = []
        for script in response.xpath('//script[@type="application/ld+json"]/text()').getall():
            try:
                schema_json = json.loads(script)
                if isinstance(schema_json, list):
                    log.debug("this schema is a list")
                    log.debug(schema_json)
                    for thing in schema_json:
                        schema_data.append(thing)
                elif isinstance(schema_json, dict):
                    schema_data.append(schema_json)
            except json.JSONDecodeError:
                log.error(f"Error to parse JSON-LD: {script}")
        return schema_data


@__timing
def spider_take_of(*spiders: type[Spider]) -> None:

    process = CrawlerProcess(Settings({
        "USER_AGENT": random.choice(yaml_config.net["USER_AGENT"]) or 'Mozilla/5.0',
        "LOG_ENABLED": env.DEBUG,
        "RETRY_ENABLED": True,
        "HTTPERROR_ALLOWED_CODES": [404, 403]
    }))

    for spider in spiders:
        if type(spider) == type:
            log.debug('Passed "%s" it has a "%s" type' % (spider, type(spider)))
            process.crawl(spider)
            process.start()
        else:
            log.error('The Spider "%s" is not a Class type. %s passed' % (spider, type(spider)))