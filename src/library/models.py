from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.users.models import User
    from src.books.models import Book


class ReceivingBook(Base):
    __tablename__ = "receiving_books"
    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="idx_unique_user_book"),
    )
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    date_of_issue: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.utcnow(),
    )
    date_of_return: Mapped[DateTime] = mapped_column(DateTime)

    book: Mapped["Book"] = relationship(back_populates="user_details")
    user: Mapped["User"] = relationship(back_populates="book_details")

    def __repr__(self) -> str:
        return f"{self.book_id}, {self.user_id}, {self.date_of_issue}, {self.date_of_return}"
