from core.db import db
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from models import IPNetworkType
from models.subnetmodel import SubnetModel


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
    vrf_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('vrf.id'))
    network: Mapped[IPNetworkType] = mapped_column(IPNetworkType)
    name: Mapped[str] = mapped_column(String, unique=True)
    subnets = db.relationship("SubnetModel", backref="supernet", cascade="all, delete-orphan")
