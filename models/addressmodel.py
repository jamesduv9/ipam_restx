from core.db import db
from sqlalchemy import Integer, String
from sqlalchemy_utils.types import IPAddressType
from sqlalchemy.orm import Mapped, mapped_column

class AddressModel(db.Model):
    """
    AddressModel - Used to handle host within a Address

    Relationships:
    VRF to AddressModel == one-to-many
    Subnet to AddressModel == one-to-many
    """
    __tablename__ = "address"
    __table_args__ = (
        db.UniqueConstraint('address', 'vrf_id', name='_network_vrf_uc'),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vrf_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('vrf.id'))
    subnet_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('subnet.id'))
    address: Mapped[IPAddressType] = mapped_column(IPAddressType)
    mac_address: Mapped[str] = mapped_column(String, default="FFFFFFFFFFFF")
    name: Mapped[str] = mapped_column(String, unique=True)
