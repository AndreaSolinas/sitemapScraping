#!venv/bin/python

import sys, os, getpass, re, subprocess
from pathlib import Path
from typing import Generator

from scrapy import Spider

sys.path.append(str(Path(__file__).parent.parent))  ## IMPORT THE RELATIVE MODULE

from argparse import ArgumentParser

import sqlalchemy
from sqlalchemy import create_engine

import app.utils
from app.ORM import Entity, ArticleRepository, entity_manager, SitemapRepository
from app.ORM.Entity import Article, Sitemap
from app.NetSpider import spider_take_of, NewsArticleSpider, SitemapNewsSpider


class Console:
    __parser = ArgumentParser(
        description='Welcome to the console scraping application console',
        usage='console.py [-h | --help] {command} [args]',
        epilog='Example: ./console.py hello'
    )
    __commands = __parser.add_subparsers(title="Database command", dest="command")
    __article_repository = ArticleRepository()
    __sitemap_repository = SitemapRepository()

    def __init__(self):

        self.__commands.add_parser(name='hello')

        self.__commands.add_parser(name='database:connection', help='Displays the ODBC database connection')
        self.__commands.add_parser(name='database:connection:test', help='Test the ODBC connection')

        show_parameter = self.__commands.add_parser(name='database:show:sitemap',
                                                    help='Display sitemap parameters from the database',
                                                    description="Display sitemap parameters from the database that have not been deleted (use -h or --help if you want to display other parameters)")
        show_parameter.add_argument('-a', '--all', action='store_true', help="show all sitemap entries of db")

        show_article = self.__commands.add_parser(name='database:show:article', help='List of article table records')
        show_article.add_argument('-u', '--url', action='store_true', help="show all article URL of db")
        show_article.add_argument('-a', '--all', action='store_true', help="show all article of db")

        article_drop = self.__commands.add_parser(name='database:drop:article', help='Delete article record')
        article_drop.add_argument('id', nargs='?', type=int, help="ID of article to delete")
        article_drop.add_argument('--url', type=str, help="the url of article to delete")
        article_drop.add_argument('--all-entry', action='store_true', help="CAUTION!!  DELETE all article of db")

        self.__commands.add_parser(name='database:clean', help='clean the Article table from duplicate')
        self.__commands.add_parser(name='database:backfill', help='clean the Article table from duplicate')

        env_var = self.__commands.add_parser(name='env', help='Set env variables')
        env_var.add_argument('name', nargs='?', type=str, help="Name of env variable")
        env_var.add_argument('value', nargs='?', type=str, help="Value of env variable")
        env_var.add_argument('--show', '-s', action='store_true', help="Show env variables")

        req_file = self.__commands.add_parser(name='requirements', help='Create a requirements file')
        req_file.add_argument('option', choices=['install', 'generate'], type=str, help="chose")

        self.__select_command(self.__parser)

        #TODO: Create a command to manage cronjob, install and delete it, and manage the time. (it can not be relative path)
        #       *       *          *          *         *         {executor} {path to execute}
        #   {minute} {hour} {day of month} {month} {day of week}

    @staticmethod
    def __select_command(parser: ArgumentParser):
        args = parser.parse_args()
        match args.command:
            case 'hello':
                print(f"""
Hi! this is Hello Word of script console scraper.

Some information for you:
\t- You are {getpass.getuser()}
\t   and we are Venom :)
\t- You run this project from: {os.getcwd()}
\t- The project directory are: {app.utils.__BASE_DIR__}
\t- {'You are in DEVELOPMENT mode\n\t   if you want switch to production set DEBUG environment variable to False' if app.utils.env.DEBUG else 'You are in PRODUCTION mode'}
\t- The core of project are: app/
\t- All runs are logging in: log/
\t- {'main.py not exist, create it' if not Path('main.py').exists() else 'All is Set Ud'}
\t- This is a CLI command module in: {str(Path(__file__)).replace(app.utils.__BASE_DIR__ + '/', '')}
\t- -h or -help to find a command that you can use for this project
    """)
            case 'run':
                # Run a Main script
                pass
            case 'database:connection':
                print(app.utils.env.DATABASE_URL)

            case 'database:connection:test':

                try:
                    create_engine(app.utils.env.DATABASE_URL).connect()
                    print("Database connection test passed")
                except sqlalchemy.exc.SQLAlchemyError as eConn:
                    print("Database connection error: ")
                    print(eConn.orig)

            case 'database:show:sitemap':
                if not args.all:
                    for url in Console.__get_all_article_entities(Sitemap, Sitemap.deleted_at.is_(None),
                                                                  Sitemap.deleted_by_id.is_(None)):
                        print(f"{url}")
                    pass
                else:
                    for url in Console.__get_all_article_entities(Sitemap):
                        print(f"{url}")

            case 'database:show:article':
                if not args.all:
                    for article in Console.__get_all_article_entities(Article, limit=1000):
                        print(f"{article.url if args.url else article}")
                    pass
                else:
                    for article in Console.__get_all_article_entities(Article):
                        print(f"{article.url if args.url else article}")

            case 'database:drop:article':
                doomed = None
                if args.all_entry:
                    choice = input(
                        "You are sure to delete ALL rows in the Item table?\nRecords can no longer be retrieved ( Y|N )")
                    if choice.lower() == 'y':
                        doomed = Console.__get_all_article_entities(Article)
                elif args.id:

                    doomed = Console.__get_all_article_entities(Article, Article.id == args.id)
                else:
                    print(
                        "usage: console.py [-h | --help] {command} [args] database:article:drop [-h] [--all-entry] id\nconsole.py [-h | --help] {command} [args] database:article:drop: error: the following arguments are required: id")
                    exit()

                entity_manager.delete_all(doomed)
                entity_manager.commit()

            case 'env':
                if args.name:
                    args.name = args.name.upper()
                    if not args.value:
                        print('THe value must be setted Ex. ./console.py env name value')
                    else:
                        with open(app.utils.__BASE_DIR__ + "/.env", 'r+') as env_file:

                            file = env_file.read()

                            if re.search(rf"[^#]{args.name}=(.+)", file):
                                file = re.sub(rf"{args.name}=(.+)", f"{args.name}={args.value}", file)
                                env_file.seek(0)
                                env_file.write(file)
                                env_file.truncate()
                            else:
                                env_file.seek(0, 2)
                                env_file.write(f'\n{args.name}={args.value}')
                if args.show:
                    for name, value in app.utils.env.all():
                        print("%s = %s" % (name, value))

            case 'requirements':
                requirements_file = f'{app.utils.__BASE_DIR__}/requirements.txt'""
                try:
                    if args.option == 'generate':
                        with open(requirements_file, 'w') as f:
                            subprocess.check_call(['pip', 'freeze'], stdout=f)
                        print(f"Requirements generated succesfully")
                    if args.option == 'install':
                        subprocess.check_call(['pip', 'install', '-r', requirements_file])
                except subprocess.CalledProcessError as e:
                    print(f"Error in requirements generation: {e}")
                pass

            case 'database:clean':
                Console.__cleaning_duplicate_article()

            case 'database:backfill':
                Console.__back_fill()

            case _:
                parser.print_help()

    @staticmethod
    def __get_all_article_entities(entity: Entity, *criterion, limit: int = None) -> list[Entity]:
        query = entity_manager.query(entity).where(
            *criterion
        )

        if limit is type(int):
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def __back_fill():

        db_article = Console.__article_repository.get_all()

        all_article = (article.url for article in db_article)

        NewsArticleSpider.start_urls = all_article

        spider_take_of(NewsArticleSpider)

        for art in db_article:
            NewsArticleSpider.start_urls = art.url
            spider_take_of(NewsArticleSpider)
            article = NewsArticleSpider.data[0]
            if art.url == article['url']:
                for schema in article['schema']:
                    if schema['@type'] == 'NewsArticle':
                        art.body = len(
                            Console.find_recursive_key(schema, "articleBody").split()) if Console.find_recursive_key(
                            schema,
                            "articleBody") else (
                            Console.find_recursive_key(schema, "wordCont") if Console.find_recursive_key(schema,
                                                                                                         "wordCont") else None)

                        art.img = (
                            1 if Console.find_recursive_key(schema, "image") else 0)

                for allowed in app.utils.yaml_config.host['allowed']:
                        if allowed in art.url:
                            art.editorial = Console.map_source(article['editorial'])

        entity_manager.commit()

        pass

    @staticmethod
    def update_entities(spider: Spider, articles: list[Entity]) -> Generator:

        for article in spider.data:
            for db_article in articles:
                if db_article.url == article['url']:
                    art = db_article

            for schema in article['schema']:
                if schema['@type'] == 'NewsArticle':
                    art.body = len(
                        Console.find_recursive_key(schema, "articleBody").split()) if Console.find_recursive_key(schema,
                                                                                                                 "articleBody") else (
                        Console.find_recursive_key(schema, "wordCont") if Console.find_recursive_key(schema,
                                                                                                     "wordCont") else None)

                    art.img = (
                        1 if Console.find_recursive_key(schema, "image") else 0)

            if art.datetime is not None:
                yield art

    @staticmethod
    def __cleaning_duplicate_article() -> None:
        duplicate = Console.__article_repository.get_duplicate_url_desc()
        if len(duplicate) > 0:
            url_to_delete: list = []
            for article in duplicate:
                if article.url not in url_to_delete:
                    url_to_delete.append(article.url)
                else:
                    Console.__article_repository.delete(article)
                    pass
            print(
                f"Database cleaned: {len(duplicate) - 1} article{'s have' if len(duplicate) - 1 > 1 else 'has'} been delete")
        else:
            print(f"Nothing to clean in database")

    @staticmethod
    def find_recursive_key(dictionary, key):
        if key in dictionary:
            return dictionary[key]
        if isinstance(dictionary, dict):
            for k, value in dictionary.items():
                if isinstance(value, dict):
                    result = Console.find_recursive_key(value, key)
                    if result is not None:
                        return result
        return None

    @staticmethod
    def map_source(json_editorial: dict) -> str:
        raw_source = Console.find_recursive_key(json_editorial, 'source')
        if raw_source is not None and raw_source.lower() in list(app.utils.yaml_config.host['source_mapping'].keys()):
            return app.utils.yaml_config.host['source_mapping'][raw_source.lower()]
        else:
            return app.utils.yaml_config.host['source_mapping']['_default_']


if __name__ == '__main__':
    Console()
