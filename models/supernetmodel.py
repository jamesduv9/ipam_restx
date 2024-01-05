from datetime import datetime, timezone
from core.db import db
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime
from models import IPNetworkType

class SupernetModel(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    network: Mapped[IPNetworkType] = mapped_column(IPNetworkType, unique=True)
    name: Mapped[str] = mapped_column(String, unique=True)

    def to_dict(self):
        return {"id": self.id, "network": str(self.network), "name": self.name}