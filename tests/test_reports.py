import pytest
from flask import Flask
from flask.testing import FlaskClient

from app.db import get_db

ADMIN_PATHS = [
    "/api/admin/reports/categories",
    "/api/admin/reports/items",
    "/api/admin/orders?period=today",
    "/api/admin/orders/1",
]


def item_ids(app: Flask, *names: str) -> list[int]:
    with app.app_context():
        db = get_db()
        return [
            db.execute("SELECT id FROM items WHERE name = ?", (name,)).fetchone()[0]
            for name in names
        ]


def save_sale(client: FlaskClient, lines: list[dict]) -> dict:
    response = client.post("/api/sales", json={"lines": lines})
    assert response.status_code == 201
    return response.get_json()["data"]


@pytest.fixture
def sold_app(seeded_app: Flask, auth_client: FlaskClient) -> Flask:
    """Two sales by the cashier: Cola x2 + Water x1, then Cola x1."""
    cola_id, water_id = item_ids(seeded_app, "Cola", "Water")
    save_sale(
        auth_client,
        [{"item_id": cola_id, "quantity": 2}, {"item_id": water_id, "quantity": 1}],
    )
    save_sale(auth_client, [{"item_id": cola_id, "quantity": 1}])
    return seeded_app


def test_category_report(sold_app: Flask, admin_client: FlaskClient) -> None:
    response = admin_client.get("/api/admin/reports/categories")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] is True
    rows = {row["name"]: row for row in body["data"]}
    assert set(rows) == {"Drinks", "Snacks", "Bakery"}
    assert set(rows["Drinks"]) == {"id", "name", "quantity", "revenue"}
    assert (rows["Drinks"]["quantity"], rows["Drinks"]["revenue"]) == (4, 550)
    assert (rows["Snacks"]["quantity"], rows["Snacks"]["revenue"]) == (0, 0)
    # Highest revenue first.
    assert body["data"][0]["name"] == "Drinks"


def test_item_report(sold_app: Flask, admin_client: FlaskClient) -> None:
    response = admin_client.get("/api/admin/reports/items")
    assert response.status_code == 200
    data = response.get_json()["data"]
    rows = {row["name"]: row for row in data}
    assert len(rows) == 10
    assert set(rows["Cola"]) == {"id", "name", "category", "quantity", "revenue"}
    assert rows["Cola"]["category"] == "Drinks"
    assert (rows["Cola"]["quantity"], rows["Cola"]["revenue"]) == (3, 450)
    assert (rows["Water"]["quantity"], rows["Water"]["revenue"]) == (1, 100)
    assert (rows["Muffin"]["quantity"], rows["Muffin"]["revenue"]) == (0, 0)
    assert [row["name"] for row in data[:2]] == ["Cola", "Water"]


def test_item_report_uses_price_at_time_of_sale(
    sold_app: Flask, admin_client: FlaskClient
) -> None:
    with sold_app.app_context():
        db = get_db()
        db.execute("UPDATE items SET price = 999 WHERE name = 'Cola'")
        db.commit()
    data = admin_client.get("/api/admin/reports/items").get_json()["data"]
    cola = next(row for row in data if row["name"] == "Cola")
    assert cola["revenue"] == 450


@pytest.mark.parametrize("path", ADMIN_PATHS)
def test_admin_endpoints_reject_cashier(auth_client: FlaskClient, path: str) -> None:
    response = auth_client.get(path)
    assert response.status_code == 403
    assert response.get_json()["status"] is False


@pytest.mark.parametrize("path", ADMIN_PATHS)
def test_admin_endpoints_need_login(client: FlaskClient, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 401
    assert response.get_json()["status"] is False


def set_days_ago(app: Flask, sale_id: int, days: int) -> None:
    with app.app_context():
        db = get_db()
        db.execute(
            "UPDATE sales SET created_at = datetime('now', ?) WHERE id = ?",
            (f"-{days} days", sale_id),
        )
        db.commit()


def order_ids(client: FlaskClient, period: str) -> list[int]:
    response = client.get(f"/api/admin/orders?period={period}")
    assert response.status_code == 200
    return [order["id"] for order in response.get_json()["data"]]


def test_orders_by_period(
    seeded_app: Flask, auth_client: FlaskClient, admin_client: FlaskClient
) -> None:
    (cola_id,) = item_ids(seeded_app, "Cola")
    line = [{"item_id": cola_id, "quantity": 1}]
    old = save_sale(auth_client, line)["sale_id"]
    edge = save_sale(auth_client, line)["sale_id"]
    week_old = save_sale(auth_client, line)["sale_id"]
    new = save_sale(auth_client, line)["sale_id"]
    set_days_ago(seeded_app, old, 10)
    set_days_ago(seeded_app, edge, 6)
    set_days_ago(seeded_app, week_old, 7)

    assert order_ids(admin_client, "today") == [new]
    assert order_ids(admin_client, "7d") == [new, edge]
    assert order_ids(admin_client, "30d") == [new, edge, week_old, old]


def test_orders_row_fields(sold_app: Flask, admin_client: FlaskClient) -> None:
    data = admin_client.get("/api/admin/orders?period=today").get_json()["data"]
    assert len(data) == 2
    assert set(data[0]) == {"id", "created_at", "cashier", "total"}
    assert data[0]["cashier"] == "cashier"
    # Newest first: the second sale (Cola x1) is on top.
    assert [order["total"] for order in data] == [150, 400]


@pytest.mark.parametrize("query", ["?period=year", "?period=", ""])
def test_orders_invalid_period(admin_client: FlaskClient, query: str) -> None:
    response = admin_client.get(f"/api/admin/orders{query}")
    assert response.status_code == 400
    body = response.get_json()
    assert body["status"] is False
    assert body["errors"]


def test_order_detail(sold_app: Flask, admin_client: FlaskClient) -> None:
    first_id = order_ids(admin_client, "today")[-1]
    response = admin_client.get(f"/api/admin/orders/{first_id}")
    assert response.status_code == 200
    order = response.get_json()["data"]
    assert order["id"] == first_id
    assert order["cashier"] == "cashier"
    assert order["total"] == 400
    assert order["created_at"]
    assert order["lines"] == [
        {"item_name": "Cola", "quantity": 2, "unit_price": 150, "line_total": 300},
        {"item_name": "Water", "quantity": 1, "unit_price": 100, "line_total": 100},
    ]


@pytest.mark.parametrize("order_id", ["9999", "99999999999999999999"])
def test_order_detail_unknown(admin_client: FlaskClient, order_id: str) -> None:
    response = admin_client.get(f"/api/admin/orders/{order_id}")
    assert response.status_code == 404
    assert response.get_json()["status"] is False
