from tests.helper import create_subnet, create_supernet


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

