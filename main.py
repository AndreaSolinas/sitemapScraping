from datetime import datetime

import Spider

if "__main__" == __name__:
    sitemaps = {
        "bologna": [
            {'url': 'https://www.bolognatoday.it/sitemaps/sitemap_news_0.xml.gz'},
            {'url': 'https://bologna.repubblica.it/sitemap-n.xml', 'local': 'bologna'},
            {'url': 'https://www.corriere.it/dynamic-sitemap/sitemap-last-100/Bologna.xml', 'local': 'bologna'},
            {'url': 'https://www.ilrestodelcarlino.it/feedservice/sitemap/rdc/articles/2024/day/sitemap.xml'},
            # 579
        ],
        "milano": [
            {'url': 'https://www.milanotoday.it/sitemaps/sitemap_news_0.xml.gz'},
            {'url': 'https://milano.repubblica.it/sitemap-n.xml', 'local': 'milano'},
            {'url': 'https://www.corriere.it/dynamic-sitemap/sitemap-last-100/Milano.xml', 'local': 'milano'},
            {'url': 'https://www.ilgiorno.it/feedservice/sitemap/gio/articles/2024/day/sitemap.xml'},
        ],
        "firenze": [
            {'url': 'https://www.firenzetoday.it/sitemaps/sitemap_news_0.xml.gz'},
            {'url': 'https://firenze.repubblica.it/sitemap-n.xml', 'local': 'firenze'},
            {'url': 'https://www.corriere.it/dynamic-sitemap/sitemap-last-100/Firenze.xml', 'local': 'firenze'},
            {'url': 'https://www.lanazione.it/feedservice/sitemap/lan/articles/2024/day/sitemap.xml'},
        ],
        "nazionali": [
            {'url': 'https://www.fanpage.it/feed/', 'type': 'rss-feed'},
            {'url': 'https://www.ilmessaggero.it/?sez=XML&p=MapNews'},
            {'url': 'https://www.repubblica.it/sitemap-n.xml'},
            {'url': 'https://www.tgcom24.mediaset.it/sitemap_news.xml'},
            {'url': 'https://www.lastampa.it/sitemap-n.xml'},  # stampa
            {'url': f'https://www.corriere.it/rss/sitemaps/2024/sitemap_{datetime.now().month:>02}_{datetime.now().day:>02}_items.xml'},
            {'url': 'https://www.quotidiano.net/feedservice/sitemap/qn/articles/2024/day/sitemap.xml'},
        ],
        "sport": [
            {'url': 'https://sport.quotidiano.net/feedservice/sitemap/qs/articles/2024/day/sitemap.xml'}
        ]
    }

    spi = Spider.Publication(
                        connection="mysql+pymysql://py_user:1@127.0.0.1:3306/",
                        table_name="prova_drop2",
                        )

    for location, local_sitemaps in sitemaps.items():
        spi.local = location
        for sitemap in local_sitemaps:
            spi.sitemap_url = sitemap['url']
            if 'type' in sitemap:
                spi.content_type = sitemap['type']
            spi.execute()

    print(spi.data)

