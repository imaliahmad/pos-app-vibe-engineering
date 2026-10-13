import sqlite3

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app.db import get_db, transaction
from app.repositories.sale_repository import insert_sale
from app.services.sale_service import DUPLICATE_ITEM, ITEM_NOT_FOUND, create_sale


def item_id(name: str) -> int:
    return (
        get_db().execute("SELECT id FROM items WHERE name = ?", (name,)).fetchone()[0]
    )


def user_id(username: str) -> int:
    return (
        get_db()
        .execute("SELECT id FROM users WHERE username = ?", (username,))
        .fetchone()[0]
    )


def count_sale_rows() -> int:
    return get_db().execute("SELECT COUNT(*) FROM sales").fetchone()[0]


def count_sale_item_rows() -> int:
    return get_db().execute("SELECT COUNT(*) FROM sale_items").fetchone()[0]


def test_create_sale_prices_from_database(seeded_app: Flask) -> None:
    with seeded_app.app_context():
        cashier_id = user_id("cashier")
        lines = [
            {"item_id": item_id("Cola"), "quantity": 2},
            {"item_id": item_id("Water"), "quantity": 1},
        ]
        sale, error = create_sale(cashier_id, lines)

        assert error is None
        assert sale["total"] == 2 * 150 + 100
        assert isinstance(sale["sale_id"], int)
        assert sale["created_at"]

        header = get_db().execute("SELECT user_id, total FROM sales").fetchone()
        assert tuple(header) == (cashier_id, 400)
        rows = get_db().execute(
            "SELECT item_name, unit_price, quantity, line_total FROM sale_items"
            " WHERE sale_id = ? ORDER BY id",
            (sale["sale_id"],),
        )
        assert [tuple(r) for r in rows] == [
            ("Cola", 150, 2, 300),
            ("Water", 100, 1, 100),
        ]


def test_create_sale_rejects_inactive_item(seeded_app: Flask) -> None:
    with seeded_app.app_context():
        db = get_db()
        db.execute("UPDATE items SET active = 0 WHERE name = 'Cola'")
        db.commit()
        sale, error = create_sale(
            user_id("cashier"), [{"item_id": item_id("Cola"), "quantity": 1}]
        )
        assert sale is None
        assert error == ITEM_NOT_FOUND
        assert count_sale_rows() == 0


def test_create_sale_rejects_unknown_item(seeded_app: Flask) -> None:
    with seeded_app.app_context():
        sale, error = create_sale(
            user_id("cashier"), [{"item_id": 9999, "quantity": 1}]
        )
        assert sale is None
        assert error == ITEM_NOT_FOUND
        assert count_sale_rows() == 0


def test_create_sale_rejects_duplicate_item(seeded_app: Flask) -> None:
    with seeded_app.app_context():
        cola_id = item_id("Cola")
        sale, error = create_sale(
            user_id("cashier"),
            [{"item_id": cola_id, "quantity": 1}, {"item_id": cola_id, "quantity": 2}],
        )
        assert sale is None
        assert error == DUPLICATE_ITEM
        assert count_sale_rows() == 0


def test_insert_sale_rolls_back_on_error(seeded_app: Flask) -> None:
    with seeded_app.app_context():
        good = {
            "item_id": item_id("Cola"),
            "item_name": "Cola",
            "unit_price": 150,
            "quantity": 1,
            "line_total": 150,
        }
        bad = {**good, "quantity": 0}  # breaks the quantity CHECK constraint
        with pytest.raises(sqlite3.IntegrityError):
            with transaction():
                insert_sale(user_id("cashier"), 300, [good, bad])
        assert count_sale_rows() == 0
        assert count_sale_item_rows() == 0


def count_sales(app: Flask) -> int:
    with app.app_context():
        return count_sale_rows()


def ids(app: Flask, *names: str) -> list[int]:
    with app.app_context():
        return [item_id(name) for name in names]


def test_post_sale(seeded_app: Flask, auth_client: FlaskClient) -> None:
    cola_id, water_id = ids(seeded_app, "Cola", "Water")
    response = auth_client.post(
        "/api/sales",
        json={
            "lines": [
                {"item_id": cola_id, "quantity": 2},
                {"item_id": water_id, "quantity": 1},
            ]
        },
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["status"] is True
    assert body["message"] == "Sale saved"
    assert set(body["data"]) == {"sale_id", "total", "created_at"}
    assert body["data"]["total"] == 400
    with seeded_app.app_context():
        header = get_db().execute("SELECT user_id FROM sales").fetchone()
        assert header["user_id"] == user_id("cashier")


def test_post_sale_ignores_browser_price(
    seeded_app: Flask, auth_client: FlaskClient
) -> None:
    (cola_id,) = ids(seeded_app, "Cola")
    response = auth_client.post(
        "/api/sales",
        json={"lines": [{"item_id": cola_id, "quantity": 2, "price": 1}]},
    )
    assert response.status_code == 201
    assert response.get_json()["data"]["total"] == 300


@pytest.mark.parametrize(
    "body",
    [
        None,
        [],
        {},
        {"lines": []},
        {"lines": "Cola"},
        {"lines": [5]},
        {"lines": [{"item_id": 1, "quantity": 0}]},
        {"lines": [{"item_id": 1, "quantity": 1000}]},
        {"lines": [{"item_id": 1, "quantity": "2"}]},
        {"lines": [{"item_id": 1, "quantity": 1.5}]},
        {"lines": [{"item_id": 1, "quantity": True}]},
        {"lines": [{"item_id": "1", "quantity": 1}]},
        {"lines": [{"quantity": 1}]},
        {"lines": [{"item_id": 0, "quantity": 1}]},
        {"lines": [{"item_id": -1, "quantity": 1}]},
        {"lines": [{"item_id": 99999999999999999999, "quantity": 1}]},
    ],
)
def test_post_sale_bad_input(
    seeded_app: Flask, auth_client: FlaskClient, body: object
) -> None:
    response = auth_client.post("/api/sales", json=body)
    assert response.status_code == 400
    result = response.get_json()
    assert result["status"] is False
    assert result["message"] == "Invalid request"
    assert result["errors"]
    assert count_sales(seeded_app) == 0


def test_post_sale_unknown_item(seeded_app: Flask, auth_client: FlaskClient) -> None:
    response = auth_client.post(
        "/api/sales", json={"lines": [{"item_id": 9999, "quantity": 1}]}
    )
    assert response.status_code == 400
    assert response.get_json()["message"] == ITEM_NOT_FOUND
    assert count_sales(seeded_app) == 0


def test_post_sale_inactive_item(seeded_app: Flask, auth_client: FlaskClient) -> None:
    (cola_id,) = ids(seeded_app, "Cola")
    with seeded_app.app_context():
        db = get_db()
        db.execute("UPDATE items SET active = 0 WHERE id = ?", (cola_id,))
        db.commit()
    response = auth_client.post(
        "/api/sales", json={"lines": [{"item_id": cola_id, "quantity": 1}]}
    )
    assert response.status_code == 400
    assert response.get_json()["message"] == ITEM_NOT_FOUND
    assert count_sales(seeded_app) == 0


def test_post_sale_duplicate_item(seeded_app: Flask, auth_client: FlaskClient) -> None:
    (cola_id,) = ids(seeded_app, "Cola")
    response = auth_client.post(
        "/api/sales",
        json={
            "lines": [
                {"item_id": cola_id, "quantity": 1},
                {"item_id": cola_id, "quantity": 1},
            ]
        },
    )
    assert response.status_code == 400
    assert response.get_json()["message"] == DUPLICATE_ITEM
    assert count_sales(seeded_app) == 0


def test_post_sale_not_logged_in(client: FlaskClient) -> None:
    response = client.post(
        "/api/sales", json={"lines": [{"item_id": 1, "quantity": 1}]}
    )
    assert response.status_code == 401
    assert response.get_json()["status"] is False
