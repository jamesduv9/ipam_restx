from datetime import datetime, timezone
from core.db import db
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime

class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    password_hash: Mapped[str] = mapped_column(String)
    apikey: Mapped[str] = mapped_column(String, default="F"*16)
    apikey_expiration: Mapped[DateTime] = mapped_column(DateTime, default=datetime(1970, 1, 1, tzinfo=timezone.utc))
    permission_level: Mapped[Integer] = mapped_column(Integer, default=0)