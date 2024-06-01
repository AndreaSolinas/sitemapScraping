from app.utils import *
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import Self

from . import Entity
from .Exception import *
from .Entity import __Readonly as Readonly


class EntityManager(Session):
    def __init__(self) -> None:
        engine = create_engine(env.DATABASE_URL, echo=bool(env.DEBUG.lower() in ("true", "1")))
        super().__init__(engine)

    def insert(self, *entities: Entity) -> Self:
        for entity in entities:
            if issubclass(entity, Readonly):
                raise ReadOnlyException()
            super().add(entity)
        super().flush()
        return self

    def select(self,*entities,**knowargs):
        return super().query(*entities,**knowargs)

    def commit(self):
        try:
            super().commit()
        except Exception as e:
            self.__rollback()
            log.error(e)

    def __rollback(self):
        super().rollback()

    def __del__(self):
        super().flush()
        super().close()
        log.debug('deleted object')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        log.debug('exit from with')
        self.__del__()


__all__ = ['Entity', 'EntityManager']
