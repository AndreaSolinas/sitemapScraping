import requests, \
    cloudscraper, \
    gzip, \
    json, \
    random, \
    re, \
    pandas, \
    dataclasses, \
    validators

from typing import Literal
from datetime import datetime

import sqlalchemy
from bs4 import BeautifulSoup
from dateutil.parser import parse
from dateutil.tz import gettz

from google.Sheet import Spreadsheet


class StupidSpider:
    r"""
    Crawl a specified url of sitemap or rss-feed, take url, published date, parse url to take journal and
    store it in a database (sheet, database)
    Notes:
        - If url is None must be set_url first
        - the __get_article_source()__ function works only with Monrif Journal
       """

    __USER_AGENT = [
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.94 Chrome/37.0.2062.94 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9',
        'Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240',
        'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
        'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0) Gecko/20100101 Firefox/40.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/7.1.8 Safari/537.85.17',
        'Mozilla/5.0 (iPad; CPU OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H143 Safari/600.1.4',
        'Mozilla/5.0 (iPad; CPU OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F69 Safari/600.1.4',
        'Mozilla/5.0 (Windows NT 6.1; rv:40.0) Gecko/20100101 Firefox/40.0',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0',
    ]
    __MONRIF: list = ['ilgiorno', 'lanazione', 'ilrestodelcarlino', 'quotidiano']

    datetime_to_scrape: datetime = datetime.now()
    __url: str = None
    __type_of_doc: dict = None
    __journal: str = None
    __connection = None
    __data_frame: pandas.DataFrame = pandas.DataFrame()

    def __init__(self, url: str = None,
                 local: str = None,
                 type: Literal['sitemap', 'rss-feed'] = 'xml-sitemap',
                 datetime: datetime = None,
                 my_journals: list | str = None,
                 connection: str = None,
                 range: str = None
                 ) -> None:
        r"""
        Crawl a specified url of sitemap or rss-feed, take url, published date, parse url to take journal.
        you can store it in a ``pandas.DataFrame()``, in database o in a spreadsheet

        Notes:
            - If url is None must be set_url first
            - the `get_article_source()` function works only with Monrif Journal

        Examples:
            >>> my_spider = StupidSpider('https://example.com/sitemap.xml').mine()
            as equal to:
            >>> my_spider = StupidSpider()
            >>> my_spider.set_url('https://example.com/sitemap.xml')
            >>> my_spider.mine()

        Parameters:
            url (str): url of sitemap or rss-feed
            type(Literal['sitemap', 'rss-feed']): select type of document to parse
            datetime (datetime, optional): datetime to check pubdate. Defaults today
            my_journals (list,str): list to personal journals
        """

        self.local = local
        self.set_url(url)
        self.set_type_of_document(type)
        self.__data_frame: pandas.DataFrame = pandas.DataFrame()

        if datetime:
            self.datetime_to_scrape = datetime

        if my_journals:
            self.__MONRIF = my_journals if isinstance(my_journals, list) else [my_journals]

        self.set_connection_object(connection, range)

    def set_connection_object(self, connection: str, range: str = None) -> None:
        if connection:
            if re.match(
                    r'(.+):\/\/[a-zA-Z0-9-_]+:[a-zA-Z0-9-_]+@(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|[a-zA-Z0-9-_]+:\d{4}\/[a-zA-Z0-9-_]+',
                    connection):
                self.__connection = sqlalchemy.create_engine(connection)
                self.__connection.connect()
            elif range and re.match(r"[a-zA-Z0-9-_]+![A-Z]{1,3}\d*:[A-Z]{1,3}\d*", range):
                self.__connection = Spreadsheet(connection, range)
                self.__connection.check_status()
            else:
                raise Exception('no dbms or spreadsheet')

        else:
            raise Exception('pippo')

    def get_connection(self):
        return self.__connection

    def get_journal(self) -> str:
        r"""
        Returns:
            a current journal
        """
        return self.__journal

    def set_url(self, url: str) -> None:
        r"""
        Args:
            url (str): url to set and validate
        """
        if not validators.url(url):
            raise Exception(
                f'\nInvalid URL: the url {url} is not valid\n\tThe url must be composed in relation to the rfc1808 document\n\t<scheme>://<net_loc>/<path>... ')

        self.__journal = self.local or '' + re.sub(r'^http(s)?://\w+\.(?P<journal>\w+)\.(.*)',
                                                   r'\g<journal>', url)
        self.__url = url

    def set_type_of_document(self, type: Literal['sitemap', 'rss-feed']) -> None:
        r"""
        Examples:
            sitemap:
                ``<url>``
                    ``<loc>https://example.com/path-to-article</loc>``

                    ``<news:news>``
                        ``<news:publication>``
                            ``<news:name>Example</news:name>``
                            ``<news:language>LANG</news:language>``
                        ``</news:publication>``

                        ``<news:publication_date>Example of date</news:publication_date>``

                        ``...``
                    ``</news:news>``
                ``</url>``

                rss:
                    ``<item>``
                        ``<title>Example of title</title>``

                        ``<link>https://example.com/path-to-article</link>``

                        ``<pubDate>Example of date</pubDate>``

                        ``...``
                    ``</item>``
        Args:
            type (Literal['sitemap', 'rss-feed']): type of document to parse if is sitemap or rss-feed

        """
        match type:
            case 'xml-sitemap':
                self.__type_of_doc = {
                    'group': 'url',
                    'date': 'publication_date',
                    'url': 'loc',
                }
            case 'rss-feed':
                self.__type_of_doc = {
                    'group': 'item',
                    'date': 'pubDate',
                    'url': 'link',
                }

    @staticmethod
    def _requests_url(url, param: dict | None = None) -> requests.Response:
        r"""
        Check response of the first call and if it is blocked by cloudflare, try with another request
        :params:
            url: the url to get the request
            param: the parameters to pass to the request
        :return: Response of **GET** request
        """
        response = requests.get(url, param if param is not None else {
            'User-Agent': random.choice(StupidSpider.__USER_AGENT)})
        if response.status_code != 200:
            request = cloudscraper.create_scraper(delay=2, browser="chrome")
            response = request.get(url)
        return response

    @staticmethod
    def parse_datetime_UTC_rome(my_date: str) -> datetime:
        r"""
        Args:
            my_date: the raw string date not converted
        Returns:
            datetime parsed to YYYY-MM-DD HH:MM:SS
        """
        date_time = parse(my_date)
        utc_time = date_time.astimezone(gettz('UTC+1')).strftime('%Y-%m-%d %H:%M:%S')
        return datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def drop_duplicates_from_data_frames(*data_frame: pandas.DataFrame) -> pandas.DataFrame:
        """
        Clean the dataframe from the duplicate entities and return the cleanest dataframe possible.
        :param data_frame: multiple data set to clean the duplicate value
        :return: the cleaned dataframe
        """
        data_frame_concatenated = concatenated_result = pandas.DataFrame()

        for dataFrame in data_frame:
            data_frame_concatenated = pandas.concat([data_frame_concatenated, dataFrame.drop_duplicates()])

            concatenated_result = pandas.concat(
                objs=[data_frame_concatenated, dataFrame],
                ignore_index=True,
            )
        concatenated_result.drop_duplicates(subset=['url'], ignore_index=True, inplace=True, keep=False)
        return concatenated_result

    @staticmethod
    def __get_article_data(url: str) -> json:
        response = StupidSpider._requests_url(url, {'User-Agent': random.choice(StupidSpider.__USER_AGENT)})

        if response.status_code != 200:
            raise requests.HTTPError(f"The request was unsuccessful:\n {url} response with code {response.status_code}")
        soup = BeautifulSoup(response.content, 'lxml')

        return json.loads(soup.find(attrs={'id': '__NEXT_DATA__'}).text)["props"]["pageProps"]["leaf"]

    @staticmethod
    def get_article_info(url: str) -> dict | None:
        """
        this function is used **ONLY WITH MONRIF EDITORIAL**
        get the source (referrer) and return what kind of media used to create the news
        :param url: the url of the single article
        :return: the Source of the news
        """
        result: dict = {}
        try:
            jsonData = StupidSpider.__get_article_data(url)
            type = jsonData['__typename'] if jsonData['__typename'] is not None else ''

            if str.lower(type) == 'article':
                match jsonData['editorial']:
                    case 'carta':
                        result['editorial'] = 'carta'
                    case 'Synch da Polopoly':
                        result['editorial'] = 'webcarta'
                    case 'aicarta':
                        result['editorial'] = 'carta-opti'
                    case _:
                        result['editorial'] = 'web'

                result['image'] = 1 if jsonData['socialImage'] and jsonData['socialImage']['baseUrl'] else 0
                if jsonData['body']:
                    result['body'] = len(jsonData['body'].split())

                ##TODO: Implement a **knowarg to get item and SUBITEM from json

            return result
        except AttributeError as NoneType:
            print(NoneType, url)
        except Exception as E:
            print(E, url)

    def undermining(self):  # -> str:
        r"""
        """

        result: dict = {}

        requested: requests.Response = StupidSpider._requests_url(self.__url, param={
            'User-Agent': random.choice(self.__USER_AGENT)})
        response = gzip.decompress(requested.content) if 'octet-stream' in requested.headers.get(
            'Content-Type') else requested.content
        soup = BeautifulSoup(response, 'xml')

        for item in soup.find_all(self.__type_of_doc['group']):  ## get url from sitemap

            art_datetime = self.parse_datetime_UTC_rome(item.find(self.__type_of_doc['date']).text)  # published date

            if art_datetime.date() == self.datetime_to_scrape.date():
                url = item.find(self.__type_of_doc['url']).text

                if self.__journal in self.__MONRIF:
                    result = self.__get_article_data(url)
                self.__data_frame = self.__data_frame._append({
                                                                  'journal': self.__journal,
                                                                  'url': url,
                                                                  'datetime': str(art_datetime),
                                                              }.update(result),
                                                              ignore_index=True)

        return self.__data_frame.to_string()

    def upload_data(self):
        # Se la connessione è una connessione al database
        if isinstance(self.__connection, sqlalchemy.engine.base.Engine) and self.__connection.connect():
            print('sql')
        elif isinstance(self.__connection, Spreadsheet):
            print('popp')

    def get_data(self, **kwargs):
        if isinstance(self.__connection, sqlalchemy.engine.base.Engine):
            pass
        elif isinstance(self.__connection, Spreadsheet):
            data_frame = pandas.DataFrame(self.__connection.get_data()).fillna(0)
            data_frame.columns = data_frame.iloc[0]
            return data_frame[1:]
### TODO:
#       fai il controllo duplicati sull'id 8 caratteri finali e non sull'intera url
#       ______________ Implementa treads ______________
