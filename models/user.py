from datetime import datetime, timezone
from core.db import db
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy.types import DateTime


class User(db.Model):
    """
    User Model

    Used primarily by the core.authen module, creates and manages user creds and apikeys
    """
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    password_hash: Mapped[str] = mapped_column(String)
    apikey: Mapped[str] = mapped_column(String, default="F"*16)
    apikey_expiration: Mapped[DateTime] = mapped_column(
        DateTime, default=datetime(1970, 1, 1, tzinfo=timezone.utc))
    permission_level: Mapped[Integer] = mapped_column(Integer, default=0)
    user_active: Mapped[bool] = mapped_column(Boolean, default=False)

    @validates('permission_level')
    def validate_permission_level(self, key, permission_level):
        if not (0 <= permission_level <= 15):
            raise ValueError("Permission level must be between 0 and 15")
        return permission_level
