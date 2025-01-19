from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

from src.core.database import Base

if TYPE_CHECKING:
    from src.library.models import ReceivingBook
    from src.books.models import Book


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    email: Mapped[str] = mapped_column(unique=True)
    registered_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.utcnow(),
    )
    hashed_password: Mapped[str]
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    book_details: Mapped[list["ReceivingBook"]] = relationship(back_populates="user")

    books: AssociationProxy[list["Book"]] = association_proxy("book_details", "book")
