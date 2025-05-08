from app.backend.db import Base
import enum
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.mixins.model_mixins.id_mixins import IDMixin
from app.mixins.model_mixins.timestamps_mixins import TimestampsMixin


class UserRoles(enum.Enum):
    admin = "admin"
    user = "user"

class User(IDMixin, TimestampsMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    fullname: Mapped[str | None] = mapped_column(String(200), default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool]  = mapped_column(Boolean, default=False)
    role: Mapped[UserRoles] = mapped_column(default=UserRoles.user)