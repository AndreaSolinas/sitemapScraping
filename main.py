from datetime import datetime, timedelta

from sqlalchemy import create_engine, engine

import Spider, pandas, re


def get_sitemap(engine: engine, table_name: str ):
    parameter = pandas.read_sql(
        sql=f"SELECT url, local, type "
            f"FROM {table_name} "
            f"WHERE deleted_at IS NULL AND deleted_by_id IS NULL",
        con=engine
    )

    for index, row in parameter.iterrows():
        parameter.loc[index, 'url'] = re.sub(r'{_YEAR_}', f"{datetime.now().year}", row["url"])
        parameter.loc[index, 'url'] = re.sub(r'{_MONTH_}', f"{datetime.now().month:>02}", row["url"])
        parameter.loc[index, 'url'] = re.sub(r'{_DAY_}', f"{datetime.now().day:>02}", row["url"])

    return parameter


if __name__ == "__main__":

    spi = Spider.Publication(
        connection="mysql+pymysql://py_admin:Poligrafici1@127.0.0.1:3306/py_scrape",
        table_name="publication",
    )

    sitemaps = get_sitemap(spi.connection_obj, 'publication__param')
    print(f"\nstart at: {datetime.now()}")
    for index, row in sitemaps.iterrows():
        spi.local = row['local']
        spi.sitemap_url = row['url']

        spi.content_type = row['type'] if row['type'] is not None else "xml-sitemap"
        spi.execute()
    print(f"Flush {len(spi.data)} data in '{spi.table_name}'")
    spi.flush()
