from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, String, Integer, ForeignKey, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

from src.core.database import Base

if TYPE_CHECKING:
    from src.authors.models import Author
    from src.library.models import ReceivingBook
    from src.users.models import User


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

    user_details: Mapped[list["ReceivingBook"]] = relationship(back_populates="book")

    users: AssociationProxy[list["User"]] = association_proxy("user_details", "user")
