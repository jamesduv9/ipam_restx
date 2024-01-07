from tests.helper import create_address, create_subnet, create_supernet, create_vrf
from core.db import db
from models.addressmodel import AddressModel

def test_usable_address(app, client, admin_headers):
    """
    tests the GET method of /api/v1/rpc/getUsableAddresses
    """
    create_address(app, address="192.168.0.1", name="test_usable_address1")
    with app.app_context():
        assert db.session.query(AddressModel).filter_by(name="test_usable_address1").first()
    create_address(app, address="192.168.0.2", name="test_usable_address2")
    create_address(app, address="192.168.0.3", name="test_usable_address3")
    create_address(app, address="192.168.0.4", name="test_usable_address4")
    for path in ["/api/v1/rpc/getUsableAddresses?network=192.168.0.0/24&vrf=Global",
                 "/api/v1/rpc/getUsableAddresses?name=test_subnet",
                 "/api/v1/rpc/getUsableAddresses?id=1"]:
        response = client.get(path, headers=admin_headers)

        assert response.status_code == 200
        assert response.json.get("data").get("first_usable") == "192.168.0.5"
        assert len(response.json.get("data").get("all_usable")) == 250

def test_usable_address_depleted(app, client, admin_headers):
    """
    tests the GET method of /api/v1/rpc/getUsableAddresses
    In the case that a subnet fills up
    """
    create_address(app, address="192.168.0.1", name="test_usable_address1", subnet_network="192.168.0.0/30")
    with app.app_context():
        assert db.session.query(AddressModel).filter_by(name="test_usable_address1").first()
    create_address(app, address="192.168.0.2", name="test_usable_address2")
    for path in ["/api/v1/rpc/getUsableAddresses?network=192.168.0.0/30&vrf=Global",
                 "/api/v1/rpc/getUsableAddresses?name=test_subnet",
                 "/api/v1/rpc/getUsableAddresses?id=1"]:
        response = client.get(path, headers=admin_headers)

        assert response.status_code == 200
        assert response.json.get("data").get("percent_utilized") == 100
    