from tests.helper import create_supernet, create_subnet
from core.db import db
from models.subnetmodel import SubnetModel

def test_subnet_creation(app, client, admin_headers):
    """
    tests POST method of /api/v1/subnet
    """
    create_supernet(app, name="test_subnet_creation", network="192.168.0.0/16")
    path = "/api/v1/subnet"
    request_json = {"name": "test_subnet_creation1",
                    "vrf": "Global", "network": "192.168.0.0/24"}
    response = client.post(path, json=request_json, headers=admin_headers)
    assert response.status_code == 200
    assert response.json.get("status") == "Success"


def test_subnet_overlap(app, client, admin_headers):
    """
    tests POST method of /api/v1/subnet 
    tests the failure conditions for adding a new subnet
    """
    create_subnet(app, name="test_subnet_overlap1", supernet_network="10.1.0.0/16",
                  network="10.1.100.0/24", vrfname="test_subnet_overlap")
    
    path = "/api/v1/subnet"
    #Test if overlapped subnets are Failed
    request_json = {"name": "test_subnet_creation1",
                    "vrf": "test_subnet_overlap", "network": "10.1.100.128/25"}
    response = client.post(path, json=request_json, headers=admin_headers)
    assert response.status_code != 200
    assert response.json.get("status") == "Failed"

    #Test if nonexistant supernets are Failed
    request_json = {"name": "test_subnet_creation1",
                    "vrf": "test_subnet_overlap", "network": "10.2.100.128/25"}
    response = client.post(path, json=request_json, headers=admin_headers)
    assert response.status_code != 200
    assert response.json.get("status") == "Failed"

def test_get_single_subnet_id(app, client, admin_headers):
    """
    tests GET method of /api/v1/subnet
    when getting a subnet by id
    """
    create_subnet(app, name="test_get_single_subnet_id", supernet_network="10.1.0.0/16",
                  network="10.1.100.0/24", vrfname="test_get_single_subnet_id")
    path = "/api/v1/subnet?id=1"
    response = client.get(path, headers=admin_headers)
    assert response.status_code == 200
    assert response.json.get("data").get("id") == 1

def test_get_single_subnet_name(app, client, admin_headers):
    """
    tests GET method of /api/v1/subnet
    when getting a subnet by name
    """
    create_subnet(app, name="test_get_single_subnet_name", supernet_network="10.1.0.0/16",
                  network="10.1.100.0/24", vrfname="test_get_single_subnet_name")
    path = "/api/v1/subnet?name=test_get_single_subnet_name"
    response = client.get(path, headers=admin_headers)
    assert response.status_code == 200
    assert response.json.get("data").get("name") == "test_get_single_subnet_name"


def test_get_all_subnet(app, client, admin_headers):
    """
    tests GET method of /api/v1/subnet
    when getting all subnets
    """
    create_subnet(app, name="test_get_all_subnet1", supernet_network="10.1.0.0/16",
                  network="10.1.101.0/24", vrfname="test_get_all_subnet1")
    create_subnet(app, name="test_get_all_subnet2", supernet_network="10.1.0.0/16",
                  network="10.1.102.0/24", vrfname="test_get_all_subnet2")
    create_subnet(app, name="test_get_all_subnet3", supernet_network="10.1.0.0/16",
                  network="10.1.103.0/24", vrfname="test_get_all_subnet3")
    path = "/api/v1/subnet"
    response = client.get(path, headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json.get("data")) == 3

def test_delete_subnet_id(app, client, admin_headers):
    """
    tests DELETE method of /api/v1/subnet
    when deleting by id
    """
    create_subnet(app, name="test_delete_subnet_id", supernet_network="10.1.0.0/16",
                  network="10.1.101.0/24", vrfname="test_delete_subnet_id")
    
    path = "/api/v1/subnet?id=1"
    response = client.delete(path, headers=admin_headers)
    assert response.status_code == 200
    assert response.json.get("status") == "Success"
    with app.app_context():
        assert not db.session.query(SubnetModel).filter_by(id=1).first()

def test_delete_subnet_name(app, client, admin_headers):
    """
    tests DELETE method of /api/v1/subnet
    when deleting by name
    """
    create_subnet(app, name="test_delete_subnet_name", supernet_network="10.1.0.0/16",
                  network="10.1.101.0/24", vrfname="test_delete_subnet_name")
    
    path = "/api/v1/subnet?name=test_delete_subnet_name"
    response = client.delete(path, headers=admin_headers)
    assert response.status_code == 200
    assert response.json.get("status") == "Success"
    with app.app_context():
        assert not db.session.query(SubnetModel).filter_by(name="test_delete_subnet_name").first()
