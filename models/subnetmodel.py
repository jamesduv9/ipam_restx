from core.db import db
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from models import IPNetworkType

class SubnetModel(db.Model):
    """
    SubnetModel - Used to handle networks within a supernet

    Relationships:
    VRF to SubnetModel == one-to-many
    SubnetModel to AddressModel == one-to-many
    """
    __tablename__ = "subnet"
    __table_args__ = (
        db.UniqueConstraint('network', 'vrf_id', name='_network_vrf_uc'),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vrf_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('vrf.id'))
    supernet_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('supernet.id'))
    network: Mapped[IPNetworkType] = mapped_column(IPNetworkType)
    name: Mapped[str] = mapped_column(String, unique=True)
