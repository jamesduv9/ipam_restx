from core.db import db
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from models import IPNetworkType


class SupernetModel(db.Model):
    """
    SupernetModel - Used to handle large networks that are branched into subnets

    Relationships:
    VRF to SupernetModel == one-to-many
    SupernetModel to SubnetModel == one-to-many
    """

    __tablename__ = "supernet"
    __table_args__ = (
        db.UniqueConstraint('network', 'vrf_id', name='_network_vrf_uc'),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    network: Mapped[IPNetworkType] = mapped_column(IPNetworkType)  # Removed unique=True
    name: Mapped[str] = mapped_column(String, unique=True)
    vrf_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('vrf.id'))


    def to_dict(self):
        return {"id": self.id, "network": str(self.network), "name": self.name}
