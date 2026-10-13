import pytest
from flask import Flask
from flask.testing import FlaskClient

from app.db import get_db


def deactivate_user(app: Flask, username: str) -> None:
    with app.app_context():
        db = get_db()
        db.execute("UPDATE users SET active = 0 WHERE username = ?", (username,))
        db.commit()


def test_login_returns_user_and_me_matches(seeded_app: Flask) -> None:
    client = seeded_app.test_client()
    response = client.post(
        "/api/auth/login", json={"username": "cashier", "password": "cashier123"}
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] is True
    assert set(body["data"]) == {"id", "username", "role"}
    assert body["data"]["username"] == "cashier"
    assert body["data"]["role"] == "cashier"

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.get_json()["data"] == body["data"]


@pytest.mark.parametrize(
    "username, password",
    [("cashier", "wrong-password"), ("nobody", "cashier123")],
)
def test_login_bad_credentials_same_message(
    seeded_app: Flask, username: str, password: str
) -> None:
    response = seeded_app.test_client().post(
        "/api/auth/login", json={"username": username, "password": password}
    )
    assert response.status_code == 401
    body = response.get_json()
    assert body["status"] is False
    assert body["message"] == "Invalid username or password"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"json": {"username": "cashier"}},
        {"json": {"username": "", "password": "cashier123"}},
        {"data": "not json", "content_type": "text/plain"},
    ],
)
def test_login_invalid_input(seeded_app: Flask, kwargs: dict) -> None:
    response = seeded_app.test_client().post("/api/auth/login", **kwargs)
    assert response.status_code == 400
    body = response.get_json()
    assert body["status"] is False
    assert body["errors"]


def test_inactive_user_cannot_login(seeded_app: Flask) -> None:
    deactivate_user(seeded_app, "cashier")
    response = seeded_app.test_client().post(
        "/api/auth/login", json={"username": "cashier", "password": "cashier123"}
    )
    assert response.status_code == 401


def test_me_rejects_user_deactivated_after_login(
    seeded_app: Flask, auth_client: FlaskClient
) -> None:
    deactivate_user(seeded_app, "cashier")
    assert auth_client.get("/api/auth/me").status_code == 401


def test_not_logged_in_gets_401(client: FlaskClient) -> None:
    for response in (client.get("/api/auth/me"), client.post("/api/auth/logout")):
        assert response.status_code == 401
        assert response.get_json()["status"] is False


def test_logout_ends_session(auth_client: FlaskClient) -> None:
    response = auth_client.post("/api/auth/logout")
    assert response.status_code == 200
    assert response.get_json()["status"] is True
    assert auth_client.get("/api/auth/me").status_code == 401


def test_pages_when_signed_out(client: FlaskClient) -> None:
    pos = client.get("/pos")
    assert pos.status_code == 302
    assert pos.headers["Location"] == "/"
    login = client.get("/")
    assert login.status_code == 200
    assert b"<form" in login.data


def test_pages_when_signed_in(auth_client: FlaskClient) -> None:
    login = auth_client.get("/")
    assert login.status_code == 302
    assert login.headers["Location"] == "/pos"
    assert auth_client.get("/pos").status_code == 200
