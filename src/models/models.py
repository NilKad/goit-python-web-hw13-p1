import enum
from datetime import date

from sqlalchemy import (
    Boolean,
    String,
    Integer,
    String,
    DateTime,
    ForeignKey,
    func,
    Enum,
)
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship

# from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), index=True)
    last_name: Mapped[str] = mapped_column(String(50), index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(50))
    birthday: Mapped[str] = mapped_column(String(10), nullable=True, default=None)
    addition: Mapped[str] = mapped_column(String(250), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship("User", backref="contacts", lazy="joined")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(250))
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime, onupdate=func.now(), nullable=True, default=None
    )
    role: Mapped[Enum] = mapped_column(
        "role", Enum(Role), default=Role.user, nullable=True
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
