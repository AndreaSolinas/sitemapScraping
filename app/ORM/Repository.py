from abc import ABC
from sqlalchemy import func, desc

from .Entity import Article, Sitemap, Entity
from .__EntityManager import entity_manager


class __BaseRepository(ABC):
    __entity: Entity

    def __init__(self):
        self.__entity = getattr(Entity, self.__class__.__name__.replace('Repository', ''))

    def get_all(self) -> list[Entity]:
        return entity_manager.query(self.__entity).all()

    def get_by_id(self, id: int, *criterion) -> Entity:
        return entity_manager.query(self.__entity).where(
            self.__entity.id == id,
            *criterion
        ).one()

    def get_by(self, *criterion) -> list[Entity]:
        return entity_manager.query(self.__entity).where(
            *criterion
        ).all()


class SitemapRepository(__BaseRepository):
    def get_all_active(self, *criterion) -> list[Entity]:
        return self.get_by(
            Sitemap.deleted_at == None,
            Sitemap.deleted_by_id == None,
            *criterion
        )


class ArticleRepository(__BaseRepository):

    def get_duplicate_url_desc(self) -> list[Entity]:
        return entity_manager.query(Article).filter(
            Article.url.in_(
                entity_manager.query(Article.url).group_by(Article.url).having(
                    func.count(Article.url) > 1)
            )
        ).order_by(desc(Article.id)).all()

    def delete(self, article: list[Article] | Article) -> None:
        entity_manager.delete_all(Article if type(article) is list else [article])
        entity_manager.commit()
