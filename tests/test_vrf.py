from models.vrfmodel import VRFModel
from models.supernetmodel import SupernetModel
from tests.helper import create_user, login, create_vrf, create_supernet
from core.db import db


def test_global_vrf(app):
    """
    Validate the global vrf is present from db init
    """
    with app.app_context():
        assert db.session.query(VRFModel).filter_by(name="Global").first()

def test_vrf_model(app):
    """
    test manual creation of vrf
    """
    with app.app_context():
        vrf = VRFModel(name="vrfA")
        db.session.add(vrf)
        db.session.commit()
        vrf_q = db.session.query(VRFModel).filter_by(name="vrfA").first()
        assert vrf_q.name == "vrfA"
        
def test_vrf_add(app, client, headers):
    """
    test /api/v1/vrf POST request to add new vrf
    """
    create_user(app, username="adminaccount", password="adminaccount",
                permission_level=15, user_active=True)
    admin_token = login(client, headers, "adminaccount", "adminaccount")
    create_user(app, username="test_user", password="test_user")
    request_json = {"name": "test_vrf"}
    request_headers = headers
    request_headers['X-Ipam-Apikey'] = admin_token
    path = "/api/v1/vrf"
    response = client.post(path, json=request_json, headers=request_headers)
    assert response.json.get("status") == "Success"
    with app.app_context():
        assert db.session.query(VRFModel).filter_by(name="test_vrf").first()

def test_get_all_vrfs(app, client, admin_headers):
    """
    test /api/v1/vrf GET request for all vrfs
    """
    test_vrfs = ["test_vrf1", "test_vrf2", "test_vrf3"]
    for vrf in test_vrfs:
        create_vrf(app, vrfname=vrf)

    path = "/api/v1/vrf"
    response = client.get(path, headers=admin_headers)
    assert len(response.json.get("data")) == 4
    for vrf in response.json.get("data"):
        if vrf.get('name') == "Global":
            continue
        assert vrf.get('name') in test_vrfs
        assert vrf.get('id')

def test_get_single_vrf_id(app, client, admin_headers):
    """
    test /api/v1/vrf GET request for a single vrf by ID
    """
    create_vrf(app, vrfname="testvrf")

    path = "/api/v1/vrf?id=2"
    response = client.get(path, headers=admin_headers)
    assert response.json.get("data",{}).get('name') == "testvrf"
    assert response.json.get("data",{}).get('id') == 2

def test_get_single_vrf_name(app, client, admin_headers):
    """
    test /api/v1/vrf GET request for a single vrf by name
    """
    create_vrf(app, vrfname="testvrf")

    path = "/api/v1/vrf?name=testvrf"
    response = client.get(path, headers=admin_headers)
    assert response.json.get("data",{}).get('name') == "testvrf"
    assert response.json.get("data",{}).get('id') == 2

def test_delete_vrf_id(app, client, admin_headers):
    """
    test /api/v1/vrf DELETE request for a vrf by ID
    """
    create_vrf(app, vrfname="testvrf")
    path = "/api/v1/vrf?id=2"
    response = client.delete(path, headers=admin_headers)
    assert response.status_code == 200
    with app.app_context():
        assert not db.session.query(VRFModel).filter_by(id=2).first()

def test_delete_vrf_name(app, client, admin_headers):
    """
    test /api/v1/vrf DELETE request for a vrf by name
    """
    create_vrf(app, vrfname="testvrf")
    path = "/api/v1/vrf?name=testvrf"
    response = client.delete(path, headers=admin_headers)
    assert response.status_code == 200
    with app.app_context():
        assert not db.session.query(VRFModel).filter_by(name="testvrf").first()

def test_supernet_relationship(app, client, admin_headers):
    """
    test relationship between vrf and supernet
    """
    create_vrf(app, vrfname="test_supernet_relationship")
    create_supernet(app, vrfname="test_supernet_relationship", network="192.168.1.0/24", name="test_supernet_relationship")
    path = "/api/v1/vrf"
    response = client.get(path, headers=admin_headers)
    assert response.json.get("data")[1].get("supernets")

    #Test if deletion of VRF successfully deletes supernets
    with app.app_context():
        assert db.session.query(SupernetModel).filter_by(network="192.168.1.0/24").first()
        response = client.delete(f"{path}?id=2", headers=admin_headers)
        assert not db.session.query(SupernetModel).filter_by(network="192.168.1.0/24").first()
