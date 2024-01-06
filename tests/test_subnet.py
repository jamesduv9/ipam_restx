from tests.helper import create_supernet, create_subnet


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