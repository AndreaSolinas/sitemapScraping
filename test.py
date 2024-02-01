from datetime import datetime

import pandas

from stupidSpider_1 import StupidSpider
from google.Sheet import *

if __name__ == '__main__':
    #
    # myspider = StupidSpider(
    #                         url='https://www.bolognatoday.it/sitemaps/sitemap_news_0.xml.gz',
    #                         connection="mysql+pymysql://py_user:PyPsw@127.0.0.1:3306/py_prova",
    #                         table_name="Class!A:F"
    #                         )
    # # the database infromation
    # print(myspider.data)
    # db = myspider.data
    # scraped = pandas.DataFrame()._append([
    #     {
    #         'journal': 'pippo',
    #         'url': "https://www.bolognatoday.it/cronaca/incidente-stradale/budrio-moto-daniele-caradio-morto-carabiniere.html",
    #         'datetime': str(datetime.now())
    #     },
    #     {
    #         'journal': 'pippo',
    #         'url': "https://www.bolognatoday.it/cronacvsdvsdvsa/incidente-stradale/budrio-moto-daniele-caradio-morto-carabiniere.html",
    #         'datetime': str(datetime.now())
    #     },
    #     {
    #         'journal': 'pippo',
    #         'url': "https://www.bolognatoday.it/cronacvlsdvsdvsa/incidente-stradale/budrio-moto-daniele-caradio-morto-carabiniere.html",
    #         'datetime': str(datetime.now())
    #     }
    # ], ignore_index=True)
    #
    #
    # myspider.execute().flush()
    #
    # print(myspider.data)
    #print(StupidSpider.drop_duplicates_from_data_frames(scraped, db))
    # myspider.url = "https://www.ilrestodelcarlino.it/feedservice/sitemap/rdc/articles/2024/day/sitemap.xml"
    # myspider.execute()
    # myspider.commit()

    print(Spreadsheet.path)
