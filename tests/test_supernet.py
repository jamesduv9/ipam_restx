from tests.helper import create_vrf, create_supernet
from models.supernetmodel import SupernetModel
from core.db import db

def test_create_supernet(app, client, admin_headers):
    """
    Tests /api/v1/supernet POST request
    creation of supernets under certain constraints
    """
    path = "/api/v1/supernet"
    request_json = {"network": "192.168.0.0/16",
                    "vrf": "Global", "name": "Global vrf pool"}
    #Test a successful add with correct params to global vrf
    response = client.post(path, headers=admin_headers, json=request_json)
    assert response.status_code == 200

    #Test unsuccessful add due to duplicate supernet
    response = client.post(path, headers=admin_headers, json=request_json)
    assert response.status_code != 200

    #Test unsuccessful add due to overlapping supernets
    request_json["network"] = "192.168.1.0/24"
    response = client.post(path, headers=admin_headers, json=request_json)
    assert response.status_code != 200

    #Test successful add in new test_vrf
    create_vrf(app, "test_vrf")
    request_json["name"] = "test_vrf pool1"
    request_json["vrf"] = "test_vrf"
    response = client.post(path, headers=admin_headers, json=request_json)
    assert response.status_code == 200

    #Test unsuccessful add of a overlapped supernet in test_vrf
    request_json["network"] = "192.168.0.0/16"
    request_json["vrf"] = "test_vrf"
    request_json["name"] = "test_vrf pool2"
    response = client.post(path, headers=admin_headers, json=request_json)
    assert response.status_code != 200
    
    #Test successful add of overlapped supernet in test_vrf2
    create_vrf(app, "test_vrf2")
    request_json["name"] = "test_vrf2 pool1"
    request_json["vrf"] = "test_vrf2"
    response = client.post(path, headers=admin_headers, json=request_json)
    assert response.status_code == 200
    

def test_get_supernet(app, client, admin_headers):
    """
    Tests /api/v1/supernet GET request
    Grab supernet data under certain constraints
    """
    path = "/api/v1/supernet"
    #Test successful get of a supernet in the Global VRF
    create_supernet(app, name="get_supernet_test1", vrfname="get_supernet_test1")
    response = client.get(f"{path}?id=1", headers=admin_headers)
    assert response.status_code == 200
    assert response.json.get("data").get("name") == "get_supernet_test1"

    #Test successful get of supernet based on name 
    response = client.get(f"{path}?name=get_supernet_test1", headers=admin_headers)
    assert response.status_code == 200
    assert response.json.get("data").get("name") == "get_supernet_test1"

    #Test unsucessful get of notexistant supernet
    response = client.get(f"{path}?id=9999", headers=admin_headers)
    assert not response.json.get("data").get("name")

    #Test successful get of all supernets
    create_supernet(app, name="get_supernet_test2", vrfname="get_supernet_test2")
    create_supernet(app, name="get_supernet_test3", vrfname="get_supernet_test3")
    create_supernet(app, name="get_supernet_test4", vrfname="get_supernet_test4")
    response = client.get(f"{path}", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json.get("data")) == 4


def test_delete_supernet(app, client, admin_headers):
    """
    Tests /api/v1/supernet DELETE method
    """
    #Test successful delete by id
    create_supernet(app, name="get_supernet_test2", vrfname="get_supernet_test2")
    path = "/api/v1/supernet?id=1"
    response = client.delete(path, headers=admin_headers)
    assert response.status_code == 200
    assert response.json.get("status") == "Success"
    with app.app_context():
        assert not db.session.query(SupernetModel).filter_by(id=1).first()

    #Test successful detele by name
    create_supernet(app, name="get_supernet_test2", vrfname="get_supernet_test2")
    path = "/api/v1/supernet?name=get_supernet_test2"
    response = client.delete(path, headers=admin_headers)
    assert response.status_code == 200
    assert response.json.get("status") == "Success"
    with app.app_context():
        assert not db.session.query(SupernetModel).filter_by(name="get_supernet_test2").first()