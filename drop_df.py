from datetime import datetime, timedelta

import pandas
from stupidSpider_class import PublicationSpider


class MyClass(PublicationSpider):
    def __init__(self, sitemap_url: str, connection: str, table_name: str, **kwargs) -> None:
        super().__init__(sitemap_url, connection, table_name, **kwargs)


if "__main__" == __name__:
    scraped = pandas.DataFrame({
        "A": [1,2,3,4,75]
    })
    database = pandas.DataFrame({
        "A": [1,2,3,4,8]
    })
    print("\n RESULT:")
    print(MyClass.drop_duplicates_from_data_frames(scraped, database, subset=['A']))

    # myspider = MyClass(     sitemap_url='https://www.bolognatoday.it/sitemaps/sitemap_news_0.xml.gz',
    #                         connection="mysql+pymysql://py_user:1@127.0.0.1:3306/py_prova",
    #                         table_name="prova_drop2",
    #                         date_to_scrape= datetime.now() #- timedelta(hours=3)
    #                         )
    # myspider.execute()
    # print(myspider.data.to_string())
    # myspider.flush()

