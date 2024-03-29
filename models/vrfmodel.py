from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from core.db import db
from models.supernetmodel import SupernetModel
from models.subnetmodel import SubnetModel
from models.addressmodel import AddressModel

class VRFModel(db.Model):
    """
    VRFModel - Used to handle VRF creation and relationships

    Relationships:
    VRF to SupernetModel == one-to-many
    VRF to SubnetModel == one-to-many
    VRF to AddressModel == one-to-many
    """
    __tablename__ = "vrf"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)

    supernets = db.relationship("SupernetModel", backref="vrf", cascade="all, delete-orphan")
    addresses = db.relationship("SubnetModel", backref="vrf")
    subnets = db.relationship("AddressModel", backref="vrf")
