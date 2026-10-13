import pytest
from flask import Flask
from flask.testing import FlaskClient

from app.db import get_db


def count_sales(app: Flask) -> int:
    with app.app_context():
        return get_db().execute("SELECT COUNT(*) FROM sales").fetchone()[0]


def cola_id(app: Flask) -> int:
    with app.app_context():
        return (
            get_db().execute("SELECT id FROM items WHERE name = 'Cola'").fetchone()[0]
        )


def test_admin_cannot_save_sale(seeded_app: Flask, admin_client: FlaskClient) -> None:
    response = admin_client.post(
        "/api/sales", json={"lines": [{"item_id": cola_id(seeded_app), "quantity": 1}]}
    )
    assert response.status_code == 403
    assert response.get_json()["status"] is False
    assert count_sales(seeded_app) == 0


def test_cashier_can_save_sale(seeded_app: Flask, auth_client: FlaskClient) -> None:
    response = auth_client.post(
        "/api/sales", json={"lines": [{"item_id": cola_id(seeded_app), "quantity": 1}]}
    )
    assert response.status_code == 201
    assert count_sales(seeded_app) == 1


@pytest.mark.parametrize(
    "path, location",
    [("/", "/admin"), ("/pos", "/admin")],
)
def test_admin_pages_redirect_to_admin(
    admin_client: FlaskClient, path: str, location: str
) -> None:
    response = admin_client.get(path)
    assert response.status_code == 302
    assert response.headers["Location"] == location


def test_admin_sees_admin_page(admin_client: FlaskClient) -> None:
    response = admin_client.get("/admin")
    assert response.status_code == 200
    assert b'href="/css/style.css"' in response.data
    assert b'src="/js/admin.js"' in response.data


def test_cashier_admin_page_redirects_to_pos(auth_client: FlaskClient) -> None:
    response = auth_client.get("/admin")
    assert response.status_code == 302
    assert response.headers["Location"] == "/pos"


def test_signed_out_admin_page_redirects_to_login(client: FlaskClient) -> None:
    response = client.get("/admin")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_unknown_role_does_not_loop(seeded_app: Flask) -> None:
    client = seeded_app.test_client()
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "manager"
    assert client.get("/").status_code == 200
    for path in ("/pos", "/admin"):
        response = client.get(path)
        assert response.status_code == 302
        assert response.headers["Location"] == "/"


def test_admin_page_has_report_tables(admin_client: FlaskClient) -> None:
    response = admin_client.get("/admin")
    for element_id in ("category-report", "item-report", "message"):
        assert f'id="{element_id}"'.encode() in response.data


def test_admin_page_has_orders_and_dialog(admin_client: FlaskClient) -> None:
    response = admin_client.get("/admin")
    assert b"<dialog" in response.data
    for period in ("today", "7d", "30d"):
        assert f'data-period="{period}"'.encode() in response.data
    for element_id in ("order-list", "order-dialog", "order-dialog-total"):
        assert f'id="{element_id}"'.encode() in response.data
