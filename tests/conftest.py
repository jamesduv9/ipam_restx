import pytest
from app import create_app
from core.db import db, clear_db


@pytest.fixture(scope="session")
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
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def headers():
    return {"X-Ipam-Apikey": "test_key",
            "Content-Type": "application/json"}


@pytest.fixture()
def testcases():
    return [{"username": "priv5", "password": "test", "permission_level": 5},
            {"username": "priv10", "password": "test", "permission_level": 10},
            {"username": "priv15", "password": "test", "permission_level": 15},
            {"username": "deleteme", "password": "test", "permission_level": 15}]
