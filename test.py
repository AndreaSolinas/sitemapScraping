import json
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from stupidSpider_1 import StupidSpider


if __name__ == '__main__':
    img:int = 0
    word_count_body: int = 0
    myspider = StupidSpider('https://www.ilgiorno.it/feedservice/sitemap/gio/articles/2024/day/sitemap.xml',
                            connection="1cpswx3UAJ4YC-zABh5VXoXx1xhGq17svI_InYxFQxlA",
                            range='Class!A:F'
                            )
    frame = myspider.get_data()

    for url in frame.url:
        data =StupidSpider.get_article_info(url)
        print(data)

    print(frame)

    #TODO: converti in dataframe, aggoiungi una colonna image e una colonna body
    #   l'immagine è un 0/1
    #   il body è un count world (split \s)
    #   |   journal     |   url     |   datetile    |       editorial   |   IMG: None | int     |       BODY: None | int    |

    # ultime dieci estrazione, oriario di pubblicazione e se sono andati bene.