from app.utils import *
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import Self, Union, Callable

from . import Entity
from .Exception import *
from .Entity.Entity import __Readonly as Readonly


class EntityManager(Session):
    def __init__(self) -> None:
        engine = create_engine(self.__find_engine(), echo=env.DEBUG)
        super().__init__(engine)

    @staticmethod
    def __find_engine():
        if hasattr(env, 'DATABASE_URL'):
            return env.DATABASE_URL
        else:
            raise ODBCException(
                "ODBC Url Not Found. Please, set the DATABASE_URL environment variable. with ODBC url.\n"
                "Ex.\n\t{driver}://{username}:{password}@{host}[:{port}]/{db_name}")

    def insert(self, *entities: Entity) -> Self:
        for entity in entities:
            if issubclass(entity, Readonly):
                raise ReadOnlyException()
            super().add(entity)
        super().flush()
        return self

    def select(self, *entities, **knowargs):
        return super().query(*entities, **knowargs)

    def __rollback(self):
        super().rollback()

    def __del__(self):
        if hasattr(self, '_flushing'):
            super().close()
        log.debug('deleted object')

    def __enter__(self):
        log.debug('start inside with statement')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        log.debug('exit from with statement')
        self.__del__()


__all__ = ['Entity', 'EntityManager']
