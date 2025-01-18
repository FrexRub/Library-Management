from typing import Optional

from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(index=True)
    biography: Mapped[Optional[str]]
    date_birth: Mapped[DateTime] = mapped_column(DateTime)
