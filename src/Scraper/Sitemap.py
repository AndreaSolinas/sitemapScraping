import logging
from logging import Logger
import re
import validators
from bs4 import BeautifulSoup

from abc import ABC, ABCMeta, abstractmethod


class SitemapInterface(ABC):
    @abstractmethod
    def method(self):
        pass


class Sitemap(SitemapInterface):
    __url: str | None
    __soup: BeautifulSoup
    __journal: str

    def method(self):
        print('pippo')
        pass

    def __init__(self, url: str, soup: BeautifulSoup = None, journal: str = None):
        self.set_url(url)

    def get_url(self):
        return self.__url

    def set_url(self, url: str):
        if not validators.url(url):
            logging.error(f' Invalid URL: %s', url)
            logging.info("Info")
        else:
            self.__url = url
