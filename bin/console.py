#!/usr/venv/V3.12/bin/python
import importlib
import re
import subprocess
import sys, os, getpass
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from argparse import ArgumentParser

from app.utils import *
from app.ORM import EntityManager, Entity
from app.ORM.Entity import Article, Sitemap


class Console():
    __parser = ArgumentParser(
        description='Welcome to the console scraping application console',
        usage='console.py [-h | --help] {command} [args]',
        epilog='Example: ./console.py hello'
    )
    __commands = __parser.add_subparsers(title="Database command", dest="command")
    __entity_manager = EntityManager()

    def __init__(self):
        self.__commands.add_parser(name='run', help='execute the main script', description='Executes the main script avoiding the timing of the cronjob, which is executed anyway')

        self.__commands.add_parser(name='hello')

        self.__commands.add_parser(name='database:connection', help='Displays the ODBC database connection')

        show_parameter = self.__commands.add_parser(name='database:show:parameter', help='Display sitemap parameters from the database',
                                   description="Display sitemap parameters from the database that have not been deleted (use -h or --help if you want to display other parameters)")
        show_parameter.add_argument('-a', '--all', action='store_true', help="show all sitemap entries of db")

        show_article = self.__commands.add_parser(name='database:show:article', help='List of article table records')
        show_article.add_argument('-u', '--url', action='store_true', help="show all article URL of db")
        show_article.add_argument('-a', '--all', action='store_true', help="show all article of db")

        article_drop = self.__commands.add_parser(name='database:drop:article', help='Delete article record')
        article_drop.add_argument('id', nargs='?', type=int, help="ID of article to delete")
        article_drop.add_argument('--url', type=str, help="the url of article to delete")
        article_drop.add_argument('--all-entry', action='store_true', help="CAUTION!!  DELETE all article of db")

        self.__commands.add_parser(name='database:backfill', help='backfill')

        env_var = self.__commands.add_parser(name='env', help='Set env variables')
        env_var.add_argument('name', nargs='?', type=str, help="Name of env variable")
        env_var.add_argument('value', nargs='?', type=str, help="Value of env variable")
        env_var.add_argument('--show', '-s',action='store_true', help="Show env variables")

        req_file = self.__commands.add_parser(name='requirements', help='Create a requirements file')
        req_file.add_argument('option', choices=['install', 'generate'], type=str, help="chose")

        self.__select_command(self.__parser)

        # NewsArticleSpider.start_urls = ["https://www.bolognatoday.it/politica/ballottaggi-Pd-Bologna-Pianoro-Casalecchio-Castel-maggiore.html"]
        # self.__spider_take_of(NewsArticleSpider)

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
\t- The project directory are: {__BASE_DIR__}
\t- {'You are in DEVELOPMENT mode\n\t   if you want switch to production set DEBUG environment variable to False' if env.DEBUG else 'You are in PRODUCTION mode' }
\t- The core of project are: app/
\t- All runs are logging in: log/
\t- This is a CLI command module in: {str(Path(__file__)).replace(__BASE_DIR__ + '/', '')}
\t- -h or -help to find a command that you can use for this project
    """)
            case 'run':
                # Run a Main script
                pass
            case 'database:connection':
                print(env.DATABASE_URL)

            case 'database:show:parameter':
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

                Console.__entity_manager.delete_all(doomed)
                Console.__entity_manager.commit()
            case 'env':
                if args.name:
                    args.name = args.name.upper()
                    if not args.value:
                        print('THe value must be setted Ex. ./console.py env name value')
                    else:
                        with open(__BASE_DIR__ + "/.env", 'r+') as env_file:

                            file = env_file.read()

                            if re.search(rf"[^#]{args.name}=(.+)",file):
                                file = re.sub(rf"{args.name}=(.+)", f"{args.name}={args.value}", file)
                                env_file.seek(0)
                                env_file.write(file)
                                env_file.truncate()
                            else:
                                env_file.seek(0,2)
                                env_file.write(f'\n{args.name}={args.value}')
                if args.show:
                    for name, value in env.all():
                        print("%s = %s" % (name, value))

            case 'requirements':
                requirements_file = f'{__BASE_DIR__}/requirements.txt'""
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
            case _:
                parser.print_help()

    @staticmethod
    def __get_all_article_entities(entity: Entity, *criterion, limit: int = None) -> list[Entity]:
        query = Console.__entity_manager.query(entity).where(
            *criterion
        )

        if limit is type(int):
            query = query.limit(limit)

        return query.all()

    def __fill_back(self):
        #TODO: Prendi elementi on giusti del db e rifillali facendo un nuova richiesta di articolo
        #   NB: gestisci monrif con yaml
        pass

    def __craning_duplicate(self):
        pass

if __name__ == '__main__':
    Console()