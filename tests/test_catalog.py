from flask import Flask
from flask.testing import FlaskClient

from app.db import get_db


def run_sql(app: Flask, sql: str, params: tuple = ()) -> None:
    with app.app_context():
        db = get_db()
        db.execute(sql, params)
        db.commit()


def category_id(client: FlaskClient, name: str) -> int:
    categories = client.get("/api/categories").get_json()["data"]
    return next(c["id"] for c in categories if c["name"] == name)


def test_list_categories(auth_client: FlaskClient) -> None:
    response = auth_client.get("/api/categories")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] is True
    assert [c["name"] for c in body["data"]] == ["Bakery", "Drinks", "Snacks"]
    assert all(set(c) == {"id", "name"} for c in body["data"])


def test_list_category_items(auth_client: FlaskClient) -> None:
    drinks_id = category_id(auth_client, "Drinks")
    response = auth_client.get(f"/api/categories/{drinks_id}/items")
    assert response.status_code == 200
    items = response.get_json()["data"]
    assert [i["name"] for i in items] == ["Coffee", "Cola", "Orange Juice", "Water"]
    assert all(set(i) == {"id", "name", "price"} for i in items)
    cola = next(i for i in items if i["name"] == "Cola")
    assert cola["price"] == 150
    assert isinstance(cola["price"], int)


def test_inactive_category_is_hidden_and_404(
    seeded_app: Flask, auth_client: FlaskClient
) -> None:
    drinks_id = category_id(auth_client, "Drinks")
    run_sql(seeded_app, "UPDATE categories SET active = 0 WHERE id = ?", (drinks_id,))

    names = [c["name"] for c in auth_client.get("/api/categories").get_json()["data"]]
    assert "Drinks" not in names
    response = auth_client.get(f"/api/categories/{drinks_id}/items")
    assert response.status_code == 404
    assert response.get_json()["status"] is False


def test_inactive_item_is_hidden(seeded_app: Flask, auth_client: FlaskClient) -> None:
    run_sql(seeded_app, "UPDATE items SET active = 0 WHERE name = ?", ("Cola",))
    drinks_id = category_id(auth_client, "Drinks")
    items = auth_client.get(f"/api/categories/{drinks_id}/items").get_json()["data"]
    assert "Cola" not in [i["name"] for i in items]
    assert len(items) == 3


def test_category_with_no_active_items_returns_empty_list(
    seeded_app: Flask, auth_client: FlaskClient
) -> None:
    run_sql(seeded_app, "INSERT INTO categories (name) VALUES (?)", ("Empty",))
    response = auth_client.get(
        f"/api/categories/{category_id(auth_client, 'Empty')}/items"
    )
    assert response.status_code == 200
    assert response.get_json()["data"] == []


def test_unknown_category_returns_404(auth_client: FlaskClient) -> None:
    response = auth_client.get("/api/categories/9999/items")
    assert response.status_code == 404
    body = response.get_json()
    assert body["status"] is False
    assert body["message"] == "Category not found"


def test_not_logged_in_gets_401(client: FlaskClient) -> None:
    for url in ("/api/categories", "/api/categories/1/items"):
        response = client.get(url)
        assert response.status_code == 401
        assert response.get_json()["status"] is False
