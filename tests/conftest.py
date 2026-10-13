from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner

from app import create_app
from app.db import init_db
from app.seed import seed_db


@pytest.fixture
def app(tmp_path: Path) -> Flask:
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.sqlite")})
    with app.app_context():
        init_db()
    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()


@pytest.fixture
def seeded_app(app: Flask) -> Flask:
    with app.app_context():
        seed_db()
    return app


@pytest.fixture
def auth_client(seeded_app: Flask) -> FlaskClient:
    """A client already logged in as the seeded cashier."""
    client = seeded_app.test_client()
    response = client.post(
        "/api/auth/login", json={"username": "cashier", "password": "cashier123"}
    )
    assert response.status_code == 200
    return client


@pytest.fixture
def admin_client(seeded_app: Flask) -> FlaskClient:
    """A client already logged in as the seeded admin."""
    client = seeded_app.test_client()
    response = client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    return client
