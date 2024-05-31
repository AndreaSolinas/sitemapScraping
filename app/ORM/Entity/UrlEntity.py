from app.utils import *
from datetime import datetime
import sqlalchemy

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from app.ORM import Base


class UrlEntity(Base):
    __tablename__ = "publication"
    id: Mapped[int] = mapped_column(sqlalchemy.BIGINT, primary_key=True)
    journal:  Mapped[str] = mapped_column(sqlalchemy.String)
    url: Mapped[str] = mapped_column(sqlalchemy.String)
    editorial: Mapped[str] = mapped_column(sqlalchemy.String, nullable=True)
    img: Mapped[int] = mapped_column(sqlalchemy.Integer, nullable=True)
    body: Mapped[int] = mapped_column(sqlalchemy.Integer, nullable=True)
    datetime: Mapped[datetime] = mapped_column(sqlalchemy.DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"Url(id={self.id!r}, journal={self.journal!r}, url={self.url!r} ,editorial={self.editorial!r}, img={self.img!r}, body={self.body!r}, datetime={self.datetime!r})"
