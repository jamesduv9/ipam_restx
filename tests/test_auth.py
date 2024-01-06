import pytest
from tests.helper import create_user, login


def test_default_admin(app, client, headers):
    """
    Tests for the existance of the default admin account
    """
    path = "/auth/login"
    response_json = {"username": "admin", "password": app.config["MASTER_APIKEY"]}
    response = client.post(path, json=response_json, headers=headers)
    assert response.status_code == 200

def test_user_authorization(app, client, headers: dict) -> None:
    """
    Tests the ability to approve users with a privileged user account
    """
    create_user(app, username="adminaccount", password="adminaccount",
                permission_level=15, user_active=True)
    admin_token = login(client, headers, "adminaccount", "adminaccount")
    create_user(app, username="test_user", password="test_user")
    authorization_json = {"username": "test_user", "permission_level": 10}
    authorization_headers = headers
    authorization_headers['X-Ipam-Apikey'] = admin_token
    authorization_path = "/auth/authorize"
    authorization_response = client.post(
        authorization_path, json=authorization_json, headers=authorization_headers)
    assert authorization_response.json.get("status") == "Success"
    assert authorization_response.status_code == 200

    user_status_path = "/auth/user_status/test_user"
    user_status_response = client.get(
        user_status_path, headers=authorization_headers)
    assert user_status_response.json.get(
        "data", {}).get("permission_level") == 10
    assert user_status_response.json.get("data", {}).get("user_active")


def test_register(client, headers, testcases) -> None:
    """
    Tests the ability to register a new account, and validates that new accounts 
    are not active by default
    """
    register_path = "/auth/register"
    login_path = "/auth/login"
    for user in testcases:
        response = client.post(register_path, json=user, headers=headers)
        assert response.status_code == 200
        assert response.json.get("status") == "Success"
        user.pop("permission_level", None)

        response = client.post(login_path, json=user, headers=headers)
        assert response.status_code == 403
        assert response.json.get("status") == "Failed"
        assert not response.json.get("data", {}).get("X-Ipam-Apikey")

def test_user_deletion(app, client, headers) -> None:
    """
    Creates a user and tests the /auth/delete route
    """
    create_user(app, username="adminaccount", password="adminaccount",
                permission_level=15, user_active=True)
    admin_token = login(client, headers, "adminaccount", "adminaccount")
    create_user(app, username="test_user", password="test_user")
    deletion_json = {"username": "test_user"}
    deletion_headers = headers
    deletion_headers['X-Ipam-Apikey'] = admin_token
    deletion_path = "/auth/delete"
    deletion_response = client.post(
        deletion_path, json=deletion_json, headers=deletion_headers)
    assert deletion_response.json.get("status") == "Success"
    assert deletion_response.status_code == 200

    user_status_path = "/auth/user_status/test_user"
    user_status_response = client.get(
        user_status_path, headers=deletion_headers)
    assert user_status_response.status_code != 200
