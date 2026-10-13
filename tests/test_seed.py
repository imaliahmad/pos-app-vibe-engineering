from flask import Flask
from flask.testing import FlaskCliRunner
from werkzeug.security import check_password_hash

from app.db import get_db


def count_rows(table: str) -> int:
    # Table names come from the tests only, never from input.
    return get_db().execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_seed_inserts_categories_and_items(app: Flask, runner: FlaskCliRunner) -> None:
    result = runner.invoke(args=["seed"])
    assert result.exit_code == 0
    assert "Seeded" in result.output
    with app.app_context():
        assert count_rows("categories") == 3
        assert count_rows("items") == 10


def test_seed_creates_users_with_hashed_passwords(
    app: Flask, runner: FlaskCliRunner
) -> None:
    runner.invoke(args=["seed"])
    with app.app_context():
        rows = get_db().execute("SELECT username, password_hash, role FROM users")
        users = {row["username"]: row for row in rows}
    assert users["admin"]["role"] == "admin"
    assert users["cashier"]["role"] == "cashier"
    assert users["admin"]["password_hash"] != "admin123"
    assert check_password_hash(users["admin"]["password_hash"], "admin123")
    assert check_password_hash(users["cashier"]["password_hash"], "cashier123")


def test_seed_items_have_int_prices_and_valid_categories(
    app: Flask, runner: FlaskCliRunner
) -> None:
    runner.invoke(args=["seed"])
    with app.app_context():
        db = get_db()
        category_ids = {row["id"] for row in db.execute("SELECT id FROM categories")}
        items = db.execute("SELECT category_id, price FROM items").fetchall()
    for item in items:
        assert isinstance(item["price"], int)
        assert item["price"] > 0
        assert item["category_id"] in category_ids


def test_seed_twice_changes_nothing(app: Flask, runner: FlaskCliRunner) -> None:
    runner.invoke(args=["seed"])
    result = runner.invoke(args=["seed"])
    assert result.exit_code == 0
    assert "already seeded" in result.output
    with app.app_context():
        assert count_rows("categories") == 3
        assert count_rows("items") == 10
        assert count_rows("users") == 2


def test_seed_skips_when_category_exists(app: Flask, runner: FlaskCliRunner) -> None:
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO categories (name) VALUES (?)", ("Manual",))
        db.commit()
    result = runner.invoke(args=["seed"])
    assert result.exit_code == 0
    assert "already seeded" in result.output
    with app.app_context():
        assert count_rows("categories") == 1
        assert count_rows("items") == 0
        assert count_rows("users") == 0
