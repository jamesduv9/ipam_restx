from models.user import User
from models.vrfmodel import VRFModel
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