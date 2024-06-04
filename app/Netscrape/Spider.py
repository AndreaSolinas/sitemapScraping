from app.utils import *
import json, cloudscraper
from scrapy.spiders.sitemap import SitemapSpider


# class ArticleNewsSpider(Spider):
#     name = 'newsArticleScraper'
#     data: list = []
#
#     start_urls: str | list
#     response: Iterable
#
#     def parse(self, response):
#         response = check_response(response)
#
#         title = response.css('title::text').get()
#         canonical = response.xpath('//link[@rel="canonical"]/@href').get()
#         self.data.append(
#             {
#                 'url': response.url,
#                 'title': title,
#                 'canonical': canonical,
#                 'og_tags': self.scrape_og(response),
#                 'schema': self.scrape_schema(response)
#             }
#         )
#
#         return self.data
#
#     @staticmethod
#     def scrape_og(response) -> dict:
#         og_tags = {}
#         for meta in response.xpath('//meta[starts-with(@property, "og:")]'):
#             property_name = meta.xpath('@property').get()
#             content = meta.xpath('@content').get()
#             if property_name and content:
#                 og_tags[property_name] = content
#         return og_tags
#
#     @staticmethod
#     def scrape_schema(response) -> list:
#         schema_data = []
#         for script in response.xpath('//script[@type="application/ld+json"]/text()').getall():
#             try:
#                 schema_data.append(json.loads(script))
#             except json.JSONDecodeError:
#                 log.error(f"Errore nel parsing del JSON-LD: {script}")
#         return schema_data
#

class SitemapNewsSpider(SitemapSpider):
    name = 'sitemapArticleSpider'
    data: list = []
    entries = None
    sitemap_urls: str | list

    @staticmethod
    def check_response(response):
        return response if response.status < 400 else cloudscraper.create_scraper(response.url)

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
                schema_data.append(json.loads(script))
            except json.JSONDecodeError:
                log.error(f"Errore nel parsing del JSON-LD: {script}")
        return schema_data

