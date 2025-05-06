from datetime import datetime
from uuid import UUID

from sqlalchemy import String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.db import Base
from app.mixins.model_mixins.id_mixins import IDMixin
from app.mixins.model_mixins.timestamps_mixins import TimestampsMixin


class Folder(IDMixin, TimestampsMixin, Base):
    __tablename__ = 'folders'

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_private: Mapped[bool] = mapped_column(Boolean, default=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(column='users.id', ondelete='CASCADE')
    )
    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey('folders.id'), nullable=True
    )



