from abc import ABC
from sqlalchemy import func, desc

from .Entity import Article, Sitemap, Entity
from .__EntityManager import entity_manager, EntityManager

class __BaseRepository(ABC):
    _entity_manager: EntityManager
    __entity: Entity

    def __init__(self):
        self.__entity = getattr(Entity, self.__class__.__name__.replace('Repository', ''))
        self._entity_manager: EntityManager = entity_manager

    def get_all(self, *criterion) -> list[Entity]:
        return self._entity_manager.query(self.__entity).where(
            *criterion
        ).all()

    def get_by_id(self, id: int, *criterion) -> Entity:
        return self._entity_manager.query(self.__entity).where(
            self.__entity.id == id
        ).one()


class SitemapRepository(__BaseRepository):
    def get_all_active(self, *criterion) -> list[Entity]:
        return self.get_all(
            Sitemap.deleted_at == None,
            Sitemap.deleted_by_id == None,
            *criterion
        )


class ArticleRepository(__BaseRepository):
    def get_duplicate_url_desc(self) -> list[Entity]:
        return self._entity_manager.query(Article).filter(
            Article.url.in_(
                self._entity_manager.query(Article.url).group_by(Article.url).having(
                    func.count(Article.url) > 1)
            )
        ).order_by(desc(Article.id)).all()

    def delete(self, article: list[Article] | Article)-> None:
        self._entity_manager.delete_all(Article if type(article) is list else [article])
        self._entity_manager.commit()

