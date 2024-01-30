import json
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from stupidSpider_1 import StupidSpider


if __name__ == '__main__':

    myspider = StupidSpider(
                            url='https://www.ilrestodelcarlino.it/feedservice/sitemap/rdc/articles/2024/day/sitemap.xml',
                            )
    myspider.undermining()
    print(myspider.data)
