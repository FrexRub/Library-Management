from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Integer, ForeignKey, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.authors.models import Author
    from src.library.models import ReceivingBook


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str] = mapped_column(String(250), default="", server_default="")
    release_date: Mapped[DateTime] = mapped_column(DateTime)
    count: Mapped[int] = mapped_column(Integer, default=0)
    id_author: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="CASCADE"))
    genres_ids: Mapped[list] = mapped_column(ARRAY(Integer), default=[], nullable=False)

    author: Mapped["Author"] = relationship(back_populates="books")

    users: Mapped[list["ReceivingBook"]] = relationship(back_populates="book")

    def __str__(self):
        return f"Book id:{self.id} title: {self.title} release date:{self.release_date}"
