import requests, \
    cloudscraper, \
    gzip, \
    json, \
    random, \
    re, \
    pandas, \
    validators

from typing import Literal
from datetime import datetime, date

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

    __MONRIF: list = ['ilgiorno', 'lanazione', 'ilrestodelcarlino', 'quotidiano', 'iltelegrafolivorno']

    __connection: sqlalchemy.engine.base.Engine | Spreadsheet = None

    __data_frame: pandas.DataFrame = pandas.DataFrame()

    def __init__(self, url: str,
                 local: str = None,
                 type: Literal['sitemap', 'rss-feed'] = 'xml-sitemap',
                 date_to_scrape: datetime = datetime.now(),
                 connection: str = None,
                 range: str = None
                 ) -> None:
        r"""
        Crawl a specified url of sitemap or rss-feed, take url, published date, parse url to take journal.
        you can store it in a ``pandas.DataFrame()``, in database o in a spreadsheet

        Notes:
            - If url is None must be set_url first
            - the `get_article_source()` function works only with Monrif Journal

        Parameters:
            url (str): url of sitemap or rss-feed
            local (str, optional): location of journal
            type(Literal['sitemap', 'rss-feed']): select type of document to parse
            date_to_scrape (datetime, optional): datetime to check pubdate. Defaults today
            connection (str, optional): connection type => see :func:`set_connection()`
            range (str, optional): if connection is a :class:`Spreadsheet` object, range must be specified
        """

        self.local = local
        self.url = url
        self.content_type = type

        if datetime:
            self.date_time = date_to_scrape

        if connection:
            self.set_connection(connection, range)

    ############
    #  GETTER  #
    ############
    @property
    def url(self) -> str:
        return self.__url

    @property
    def journal(self) -> str:
        r"""
        This is a **read-only** attrbute is created and set by the url setter, because it is a domain dependent attribute
        """
        return self.__journal

    @property
    def content_type(self) -> AttributeError:
        raise AttributeError(f"property content_type object has no getter, write-only attribute")

    @property
    def connection(self) -> sqlalchemy.engine.base.Engine | Spreadsheet:
        return self.__connection

    @property
    def data(self) -> pandas.DataFrame:
        return self.__data_frame


    ############
    #  SETTER  #
    ############

    @url.setter
    def url(self, url: str) -> None:
        r"""
        Setter method to validate the url attribute and also set the ``journal`` attribute.

        The ``journal`` attribute was parsed from the url, taking only the **second-level domain** and adding the
        location at the beginning, if it exists.

        Examples:
            >>> istance.url = 'https://www.example.com/sitemap.xml'
            >>> istance.local = 'Honolulu'
            >>> istance.journal
            Honolulu-example

        Parameters:
            url (str): Valid URL of sitemap or rss-feed

                es => ``https://example.com/sitemap.xml`` or ``https://example.com/feed.rss``

        See Also:
            - https://validators.readthedocs.io/en/latest/

        Raises:
            TypeError: if url not is a valid url
        """

        if validators.url(url):
            self.__url = url
            self.__journal = (self.local + '-' if self.local else '') + re.sub(
                r'^http(s)?://\w+\.(?P<journal>\w+)\.(.*)', r'\g<journal>', url)
        else:
            raise TypeError(f"{url} is not a valid url")

    @content_type.setter
    def content_type(self, type: Literal['sitemap', 'rss-feed'] = 'xml-sitemap') -> None:
        r"""
        Examples:
            **sitemap**:
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

            **rss**:
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
                self.__content_type = {
                    'group': 'url',
                    'date': 'publication_date',
                    'url': 'loc',
                }
                pass
            case 'rss-feed':
                self.__content_type = {
                    'group': 'item',
                    'date': 'pubDate',
                    'url': 'link',
                }
                pass
            case _:
                raise TypeError('Unrecognized content type')

    ############
    #  METHOD  #
    ############

    def set_connection(self, connection: str, range: str = None) -> None:
        r"""Create a connection to database and test if it works.
        Note:
            It can be connected to:

            - **RDBMS**: with a URI such as ``schmea://userName:password@host[:port]/databaseName``.
                This will be a connection to :class:`sqlalchemy`
            - **SHEET**: with **UUID** of the document and its **range**
                This will be a connection to :class:`Spreadsheet`

        Parameters:
            connection (str): Can be a RDBMS URi or UUID of sheet

                - **URI**: ``'schmea://userName:password@host[:port]/databaseName'``
                - **UUID**: 'docs.google.com/spreadsheets/d/**<<UUID>>**/edit'

            range (str, optional): Works only if the connection is a UUID Sheet.

                must be composed: ``<name>!COL[row]:COL[row]``

                Ex:

                >>> range = "sheet1!A2:Z5"

                **or**

                >>> range = "sheet!A:K"
        """

        if re.match(
                r'(.+)://[a-zA-Z0-9-_]+:[a-zA-Z0-9-_]+@((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|[a-zA-Z0-9-_]+)(:\d{4})?/[a-zA-Z0-9-_]+',
                connection):
            self.__connection = sqlalchemy.create_engine(connection)
            self.__connection.connect()
        elif range and re.match(r"[a-zA-Z0-9-_]+![A-Z]{1,3}\d*:[A-Z]{1,3}\d*", range):
            self.__connection = Spreadsheet(connection, range)
            self.__connection.check_status()
        else:
            raise Exception('Connection error: DBMS or Spreadsheet Not found')

    @staticmethod
    def requests_url(url, param: dict | None = None) -> requests.Response:
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
    def parse_datetime_UTC_rome(my_date: str | datetime) -> datetime:
        r"""
        Parameters:
            my_date: the raw string date not converted

        Returns:
            (datetime): parsed to ``YYYY-MM-DD HH:MM:SS``
        """
        if isinstance(my_date, str):
            my_date = parse(my_date)

        utc_time = my_date.astimezone(gettz('UTC+1')).strftime('%Y-%m-%d %H:%M:%S')
        return datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def drop_duplicates_from_data_frames(*data_frame: pandas.DataFrame, subset: list) -> pandas.DataFrame:
        r"""
        Clean the dataframe from the duplicate entities and return the cleanest dataframe possible.

        Parameters:
            subset (list): The values that need to be checked to find duplicates
            data_frame(pandas.DataFrame): multiple data set to clean the duplicate value

        Returns:
            (pandas.DataFrame): One dataframe with all data and cleaned of all duplicate values
        """
        data_frame_concatenated = concatenated_result = pandas.DataFrame()

        for dataFrame in data_frame:
            data_frame_concatenated = pandas.concat([data_frame_concatenated, dataFrame.drop_duplicates()])

            concatenated_result = pandas.concat(
                objs=[data_frame_concatenated, dataFrame],
                ignore_index=True,
            )
        concatenated_result.drop_duplicates(subset=subset, ignore_index=True, inplace=True, keep=False)
        return concatenated_result

    @staticmethod
    def __get_article_data(url: str) -> json:
        response = StupidSpider.requests_url(url, {'User-Agent': random.choice(StupidSpider.__USER_AGENT)})

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
        jsonData = StupidSpider.__get_article_data(url)
        type = jsonData['__typename'] if jsonData['__typename'] is not None else ''

        if str.lower(type) == 'article':
            match jsonData['source']:
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

    def undermining(self) -> pandas.DataFrame:
        r"""
        """
        result: dict = {
            'editorial': None,
            'image': None,
            'body': None
        }
        dataResult = pandas.DataFrame()
        requested: requests.Response = StupidSpider.requests_url(self.url,
                                                                 param={'User-Agent': random.choice(self.__USER_AGENT)})
        response = gzip.decompress(requested.content) if 'octet-stream' in requested.headers.get(
            'Content-Type') else requested.content
        soup = BeautifulSoup(response, 'xml')

        for item in soup.find_all(self.__content_type['group']):  ## get url from sitemap

            art_datetime = self.parse_datetime_UTC_rome(item.find(self.__content_type['date']).text)  # published date

            if art_datetime.date() == self.date_time.date():
                url = item.find(self.__content_type['url']).text

                if self.journal in self.__MONRIF:
                    result = self.get_article_info(url)

                series = {
                    'journal': self.journal,
                    'url': url,
                    'datetime': str(art_datetime),
                }
                series.update(result)
                dataResult = dataResult._append(series,ignore_index=True)

        self.__data_frame = dataResult
        return dataResult

    def upload_data(self):
        # Se la connessione è una connessione al database
        if isinstance(self.connection, sqlalchemy.engine.base.Engine) and self.connection.connect():
            print('sql')
        elif isinstance(self.connection, Spreadsheet):
            print('popp')

### TODO:
#       fai il controllo duplicati sull'id 8 caratteri finali e non sull'intera url
#       ______________ Implementa treads ______________
