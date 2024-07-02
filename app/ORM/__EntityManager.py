from app.ORM.Exception import *
from .Entity import Entity
from .Entity.Entity import __Readonly as Readonly
from app.utils import *
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import Self, Iterable


class _EntityManager(Session):
    __count: int = 0

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

    def add(self, instance: Entity, _warn: bool = True) -> Self:
        if isinstance(instance, Readonly):
            raise ReadOnlyException("Cannot add Readonly Entity.")
        self.__count += 1
        super().add(instance, _warn=_warn)
        super().flush()
        return self

    def add_all(self, instances: Iterable[Entity]) -> Self:
        for instance in instances:
            self.add(instance)
        return self

    def select(self, *entities, **knowargs):
        return super().query(*entities, **knowargs)

    def delete_all(self, instances: Iterable[Entity]) -> None:
        for instance in instances:
            self.delete(instance)

    def __rollback(self):
        super().rollback()

    def commit(self) -> None:
        log.info(str(self.__count) + " committed article")
        super().commit()

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


entity_manager = _EntityManager()

EntityManager = type(_EntityManager)

__all__ = ['entity_manager', 'EntityManager']
