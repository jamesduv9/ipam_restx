from tests.helper import create_subnet, create_address
from models.addressmodel import AddressModel
from core.db import db


def test_create_address(app, client, admin_headers):
    """
    tests POST method of /api/v1/address
    """
    create_subnet(app, name="test_subnet", network="192.168.1.0/24", supernet_network="192.168.0.0/16", vrfname="Global")
    path = "/api/v1/address"
    request_json = {"address": "192.168.1.100",
                    "name": "Test address", "vrf": "Global"}
    response = client.post(path, headers=admin_headers, json=request_json)

    assert response.status_code == 200
    assert response.json.get("status") == "Success"

def test_create_address_failure(app, client, admin_headers):
    """
    tests POST method of /api/v1/address
    """
    create_subnet(app, name="test_subnet", network="192.168.1.0/24", supernet_network="192.168.0.0/16", vrfname="Global")
    path = "/api/v1/address"
    request_json = {"address": "192.168.1.100",
                    "name": "Test address", "vrf": "Global"}
    client.post(path, headers=admin_headers, json=request_json)
    response = client.post(path, headers=admin_headers, json=request_json)

    assert response.status_code != 200
    assert response.json.get("status") == "Failed"

def test_get_address_id(app, client, admin_headers):
    """
    tests GET method of /api/v1/address by ID
    """
    create_address(app)
    path = "/api/v1/address?id=1"
    response = client.get(path, headers=admin_headers)
    assert response.status_code == 200
    assert response.json.get("data").get("id") == 1

def test_get_address_name(app, client, admin_headers):
    """
    tests GET method of /api/v1/address by name
    """
    create_address(app, name="test_get_address_name")
    path = "/api/v1/address?name=test_get_address_name"
    response = client.get(path, headers=admin_headers)
    assert response.status_code == 200
    assert response.json.get("data").get("name") == "test_get_address_name"

def test_get_all_address(app, client, admin_headers):
    """
    tests GET method of /api/v1/address ALL addresses
    """
    create_address(app, name="test_get_all_address1")
    create_address(app, name="test_get_all_address2", address="192.168.1.2")
    create_address(app, name="test_get_all_address3", address="192.168.1.3")
    create_address(app, name="test_get_all_address4", address="192.168.1.4")
    path = "/api/v1/address"
    response = client.get(path, headers=admin_headers)
    assert response.status_code == 200
    assert response.json.get("data")

def test_get_all_address_by_vrf(app, client, admin_headers):
    """
    tests GET method of /api/v1/address ALL addresses by vrf
    """
    create_address(app, name="test_get_all_address_by_vrf")
    create_address(app, name="test_get_all_address_by_vrf2", address="192.168.1.2")
    create_address(app, name="test_get_all_address_by_vrf3", address="192.168.1.3")
    create_address(app, name="test_get_all_address_by_vrf4", address="192.168.1.4")
    create_address(app, name="test_get_all_address_by_vrf5", address="192.168.1.4", vrfname="test")
    path = "/api/v1/address?vrf=Global"
    response = client.get(path, headers=admin_headers)
    assert response.status_code == 200
    for address in response.json.get("data"):
        assert address.get("vrf").get("name") == "Global"


def test_delete_address_id(app, client, admin_headers):
    """
    tests DELETE method of /api/v1/address by id
    """
    create_address(app)
    #Ensure the address initially exists
    with app.app_context():
        assert db.session.query(AddressModel).filter_by(id=1).first()
    path = "/api/v1/address?id=1"
    response = client.delete(path, headers=admin_headers)
    assert response.status_code == 200
    #Check for deletion
    with app.app_context():
        assert not db.session.query(AddressModel).filter_by(id=1).first()


def test_delete_address_name(app, client, admin_headers):
    """
    tests DELETE method of /api/v1/address by name
    """
    create_address(app, "test_delete_address_name")
    #Ensure the address initially exists
    with app.app_context():
        assert db.session.query(AddressModel).filter_by(name="test_delete_address_name").first()
    path = "/api/v1/address?name=test_delete_address_name"
    response = client.delete(path, headers=admin_headers)
    assert response.status_code == 200
    #Check for deletion
    with app.app_context():
        assert not db.session.query(AddressModel).filter_by(name="test_delete_address_name").first()


def test_patch_address(app, client, admin_headers):
    """
    tests PATCH method of /api/v1/address by name
    Should allow changing of mac_address and name
    """
    create_address(app, "test_patch_address")
    #Ensure the address initially exists
    with app.app_context():
        assert db.session.query(AddressModel).filter_by(name="test_patch_address").first()
    path = "/api/v1/address?name=test_patch_address"
    request_json = {"name": "new_name", "mac_address": "d34db33fd34d"}
    response = client.patch(path, headers=admin_headers, json=request_json)
    assert response.status_code == 200
    with app.app_context():
        changed_address = db.session.query(AddressModel).filter_by(name="new_name").first()
        assert changed_address
        assert changed_address.mac_address == "d34db33fd34d"
