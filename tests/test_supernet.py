from tests.helper import create_vrf, create_supernet

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
    response = client.post(path, headers=admin_headers, json=request_json)
    assert response.status_code == 200

    #Test successful add of a duplicate supernet in different vrf
    request_json["network"] = "192.168.0.0/16"
    request_json["vrf"] = "test_vrf"
    request_json["name"] = "test_vrf pool2"
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

    #Test unsucessful get of notexistant supernet
    response = client.get(f"{path}?id=9999", headers=admin_headers)
    assert response.status_code != 200
    assert not response.json.get("data").get("name")

    #Test successful get of all supernets
    create_supernet(app, name="get_supernet_test2", vrfname="get_supernet_test2")
    create_supernet(app, name="get_supernet_test3", vrfname="get_supernet_test3")
    create_supernet(app, name="get_supernet_test4", vrfname="get_supernet_test4")
    response = client.get(f"{path}", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json.get("data")) == 4

