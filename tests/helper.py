from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from models.user import User
from models.vrfmodel import VRFModel
from models.supernetmodel import SupernetModel
from models.subnetmodel import SubnetModel
from models.addressmodel import AddressModel
from core.db import db



def create_user(app, username: str = "test_admin", password: str = "test_admin", permission_level: int = 0, user_active: bool = False) -> User:
    """
    Helper function to simply create a user through direct db interaction
    """
    with app.app_context():
        new_user = User(username=username, password_hash=generate_password_hash(password),
                        permission_level=permission_level, user_active=user_active)
        db.session.add(new_user)
        db.session.commit()

    return new_user

def create_vrf(app, vrfname: str = "test_vrf") -> VRFModel:
    """
    test manual creation of vrf
    """
    with app.app_context():
        vrf = db.session.query(VRFModel).filter_by(name=vrfname).first()
        if not vrf:
            vrf = VRFModel(name=vrfname)
            db.session.add(vrf)
            db.session.commit()

    return vrf

def create_supernet(app, name: str = "Test Name", network: str = "192.168.0.0/16", vrfname: str = "Global") -> SupernetModel:
    """
    Helper function to simply create a supernet through direct db interaction
    """
    with app.app_context():
        supernet = db.session.query(SupernetModel).filter_by(name=name).first()
        vrf = db.session.query(VRFModel).filter_by(name=vrfname).first()
        if not supernet:
            if not vrf:
                # If the passed in vrf doesn't already exist.. lets create it
                vrf = create_vrf(app, vrfname=vrfname)

            supernet = SupernetModel(network=network, vrf=vrf, name=name)
            db.session.add(supernet)
            db.session.commit()

    return vrf, supernet


def create_subnet(app, name: str = "Test Name", network: str = "192.168.0.0/24", supernet_network: str = "192.168.0.0/16", vrfname: str = "Global", supernet_name: str = "test_supernet"):
    """
    Helper function to simply create a subnet through direct db interaction
    """
    with app.app_context():
        # create a supernet and vrf (if not global)
        vrf, supernet = create_supernet(
            app, name=supernet_name, network=supernet_network, vrfname=vrfname)
        subnet = db.session.query(SubnetModel).filter_by(name=name).first()
        if not subnet:
            if not vrf:
                # If the passed in vrf doesn't already exist.. lets create it
                vrf = create_vrf(app, vrfname=vrfname)
            subnet = SubnetModel(
                name=name, network=network, vrf=vrf, supernet=supernet)

            db.session.add(subnet)
            db.session.commit()

    return vrf, subnet


def create_address(app, name: str = "Test Address", address: str = "192.168.1.1", subnet_network: str = "192.168.0.0/24", supernet_network: str = "192.168.0.0/16", vrfname: str = "Global", subnet_name: str = "test_subnet"):
    """
    Helper function to simply create an address through direct db interaction
    """
    with app.app_context():
        # create a subnet, supernet and vrf (if not global)
        vrf, subnet = create_subnet(
            app, name=subnet_name, network=subnet_network, supernet_network=supernet_network, vrfname=vrfname)
        if not vrf:
            vrf = create_vrf(app, vrfname=vrfname)
        address_ = db.session.query(AddressModel).filter_by(name=name).first()
        if not address_:
            address_ = AddressModel(
                name=name, address=address, vrf=vrf, subnet=subnet)

            db.session.add(address_)
            db.session.commit()

    return vrf, address_


def login(client, headers, username: str, password: str) -> str:
    """
    Helper function to login and return the apikey for a specific user
    """
    path = "/auth/login"
    login_json = {"username": username, "password": password}
    response = client.post(path, json=login_json, headers=headers)

    return response.json.get("data", {}).get("X-Ipam-Apikey")



