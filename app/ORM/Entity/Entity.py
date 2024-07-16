from app.utils import *
from datetime import datetime
import sqlalchemy, validators
from sqlalchemy import event

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase

from app.ORM.Exception import *


class __Base(DeclarativeBase):
    pass


class __Readonly():
    def __init__(self):
        event.listen(self, 'before_insert', self.__raise_readonly_exc())
        event.listen(self, 'before_update', self.__raise_readonly_exc())
        event.listen(self, 'before_delete', self.__raise_readonly_exc())

    def __raise_readonly_exc(self):
        raise ReadOnlyException()


class Article(__Base):
    __tablename__ = yaml_config.orm['entity']['Article']['table_name']

    id: Mapped[int] = mapped_column(sqlalchemy.BIGINT, primary_key=True)
    journal: Mapped[str] = mapped_column(sqlalchemy.String, name="journal")
    url: Mapped[str] = mapped_column(sqlalchemy.String, name='url')
    editorial: Mapped[str | None] = mapped_column(sqlalchemy.String, nullable=True)
    img: Mapped[int | None] = mapped_column(sqlalchemy.Integer, nullable=True)
    body: Mapped[int | None] = mapped_column(sqlalchemy.Integer, nullable=True)
    datetime: Mapped[datetime] = mapped_column(sqlalchemy.DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"Article(id={self.id!r}, journal={self.journal!r}, url={self.url!r} ,editorial={self.editorial!r}, img={self.img!r}, body={self.body!r}, datetime={self.datetime!r})"


class Sitemap(__Base, __Readonly):
    __tablename__ = yaml_config.orm['entity']['Sitemap']['table_name']
    __placeholder_date = yaml_config.settings["placeholder"]

    id: Mapped[int] = mapped_column(sqlalchemy.BIGINT, primary_key=True)

    __url: Mapped[str] = mapped_column(sqlalchemy.String, name="url")
    local: Mapped[str] = mapped_column(sqlalchemy.String)
    type: Mapped[str] = mapped_column(sqlalchemy.String, default='xml-sitemap')

    created_by_id: Mapped[int] = mapped_column(sqlalchemy.BIGINT)
    updated_by_id: Mapped[int] = mapped_column(sqlalchemy.BIGINT)
    deleted_by_id: Mapped[int] = mapped_column(sqlalchemy.BIGINT)

    created_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime(timezone=True), default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime(timezone=True), default=datetime.now())
    deleted_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime(timezone=True), default=None, nullable=True)

    @property
    def url(self):
        if "current_year" in self.__placeholder_date:
            self.__url = self.__url.replace(self.__placeholder_date["current_year"], f"{datetime.today().year}")
        if "current_month" in self.__placeholder_date:
            self.__url = self.__url.replace(self.__placeholder_date["current_month"], f"{datetime.today().month:02}")
        if "current_day" in self.__placeholder_date:
            self.__url = self.__url.replace(self.__placeholder_date["current_day"], f"{datetime.today().day:02}")

        return self.__url

    @url.setter
    def url(self, value):
        if validators.url(value):
            self.__url = value

    def __repr__(self) -> str:
        return f"Sitemap(id={self.id!r}, url={self.url!r}, local={self.local!r} ,type={self.type!r}, created_by_id={self.created_by_id!r}, created_at={self.created_at!r}, updated_by_id={self.updated_by_id!r}, updated_at={self.updated_at!r}, deleted_by_id={self.deleted_by_id!r}, deleted_at={self.deleted_at!r})"
