from sqlalchemy.orm import DeclarativeBase
from .EntityManager import EntityManager

class Base(DeclarativeBase):
    pass

__all__ = ['EntityManager', 'Base']