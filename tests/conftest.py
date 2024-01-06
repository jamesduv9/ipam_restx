import pytest
from app import create_app
from tests.helper import create_user, login
from core.db import db, clear_db


@pytest.fixture(scope="function")
def app():
    app = create_app(environment="test")
    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def headers():
    return {"Content-Type": "application/json"}


@pytest.fixture()
def testcases():
    return [{"username": "priv5", "password": "test", "permission_level": 5},
            {"username": "priv10", "password": "test", "permission_level": 10},
            {"username": "priv15", "password": "test", "permission_level": 15},
            {"username": "deleteme", "password": "test", "permission_level": 15}]

@pytest.fixture()
def admin_headers(app, client, headers):
    """
    creates users and returns headers with admin token installed
    """
    create_user(app, username="test_admin", permission_level=15, user_active=True)
    admin_token = login(client=client, headers=headers, username="test_admin", password="test_admin")
    headers['X-Ipam-Apikey'] = admin_token

    return headers