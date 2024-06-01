from datetime import datetime
import sqlalchemy
from sqlalchemy import event

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase

from .Exception import *


class __Base(DeclarativeBase):
    pass


class __Readonly(DeclarativeBase):
    def __init__(self):
        super(DeclarativeBase,self).__init__()

        event.listen(self, 'before_insert', self.__raise_readonly_exc())
        event.listen(self, 'before_update', self.__raise_readonly_exc())
        event.listen(self, 'before_delete', self.__raise_readonly_exc())

    def __raise_readonly_exc(self):
        raise ReadOnlyException()


class Url(__Base):
    __tablename__ = "publication"
    id: Mapped[int] = mapped_column(sqlalchemy.BIGINT, primary_key=True)
    journal: Mapped[str] = mapped_column(sqlalchemy.String)
    url: Mapped[str] = mapped_column(sqlalchemy.String)
    editorial: Mapped[str] = mapped_column(sqlalchemy.String, nullable=True)
    img: Mapped[int | None] = mapped_column(sqlalchemy.Integer, nullable=True)
    body: Mapped[int | None] = mapped_column(sqlalchemy.Integer, nullable=True)
    datetime: Mapped[datetime] = mapped_column(sqlalchemy.DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"Url(id={self.id!r}, journal={self.journal!r}, url={self.url!r} ,editorial={self.editorial!r}, img={self.img!r}, body={self.body!r}, datetime={self.datetime!r})"


class Sitemap(__Readonly):
    __tablename__ = "publication__param"
    id: Mapped[int] = mapped_column(sqlalchemy.BIGINT, primary_key=True)
    url: Mapped[str] = mapped_column(sqlalchemy.String)
    local: Mapped[str] = mapped_column(sqlalchemy.String)
    type: Mapped[str] = mapped_column(sqlalchemy.String, default='xml-sitemap')
    created_by_id: Mapped[int] = mapped_column(sqlalchemy.BIGINT)
    updated_by_id: Mapped[int] = mapped_column(sqlalchemy.BIGINT)
    deleted_by_id: Mapped[int] = mapped_column(sqlalchemy.BIGINT)
    created_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime(timezone=True), default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime(timezone=True), default=datetime.now())
    deleted_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime(timezone=True), default=None, nullable=True)

    def __repr__(self) -> str:
        return f"Url(id={self.id!r}, url={self.url!r}, local={self.local!r} ,type={self.type!r}, created_by_id={self.created_by_id!r}, created_at={self.created_at!r}, updated_by_id={self.updated_by_id!r}, updated_at={self.updated_at!r}, deleted_by_id={self.deleted_by_id!r}, deleted_at={self.deleted_at!r})"
