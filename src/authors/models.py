from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.books.models import Book


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(index=True)
    biography: Mapped[Optional[str]]
    date_birth: Mapped[DateTime] = mapped_column(DateTime)

    books: Mapped[list["Book"]] = relationship(
        back_populates="author", cascade="all, delete-orphan", passive_deletes=True
    )

    def __str__(self):
        return f"Author id:{self.id} full_name: {self.full_name} date_birthe:{self.date_birth}"
