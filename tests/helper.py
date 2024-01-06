from models.user import User
from models.vrfmodel import VRFModel
from models.supernetmodel import SupernetModel
from models.subnetmodel import SubnetModel
from core.db import db
from werkzeug.security import generate_password_hash


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

def create_supernet(app, name: str="Test Name", network: str="192.168.0.0/16", vrfname: str="Global") -> SupernetModel:
    """
    Helper function to simply create a supernet through direct db interaction
    """
    with app.app_context():
        vrf = VRFModel.query.filter_by(name=vrfname).first()
        if not vrf:
            #If the passed in vrf doesn't already exist.. lets create it
            vrf = create_vrf(app, vrfname=vrfname)

        new_supernet = SupernetModel(network=network, vrf=vrf, name=name)
        db.session.add(new_supernet)
        db.session.commit()
    
    return vrf, new_supernet

def create_subnet(app, name: str="Test Name", network: str="192.168.0.0/24", supernet_network: str="192.168.0.0/16", vrfname: str="Global"):
    """
    Helper function to simply create a subnet through direct db interaction
    """
    with app.app_context():
        #create a supernet and vrf (if not global)
        vrf, supernet = create_supernet(app, name=name, network=supernet_network, vrfname=vrfname)
        
        new_subnet = SubnetModel(name=name, network=network, vrf=vrf, supernet=supernet)
        db.session.add(new_subnet)
        db.session.commit()
    
    return vrf, new_subnet

def login(client, headers, username: str, password: str) -> str:
    """
    Helper function to login and return the apikey for a specific user
    """
    path = "/auth/login"
    login_json = {"username": username, "password": password}
    response = client.post(path, json=login_json, headers=headers)

    return response.json.get("data", {}).get("X-Ipam-Apikey")

def create_vrf(app, vrfname: str="test_vrf") -> VRFModel:
    """
    test manual creation of vrf
    """
    with app.app_context():
        vrf = VRFModel(name=vrfname)
        db.session.add(vrf)
        db.session.commit()
    
    return vrf
