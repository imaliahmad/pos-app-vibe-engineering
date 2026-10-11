from pathlib import Path

from flask import Flask
from flask.testing import FlaskCliRunner

from app import create_app
from app.db import get_db
from app.responses import failure, success

TABLES = {"users", "categories", "items", "sales", "sale_items"}


def test_create_app_uses_test_config(tmp_path: Path) -> None:
    db_path = str(tmp_path / "x.sqlite")
    app = create_app({"TESTING": True, "DATABASE": db_path})
    assert app.testing
    assert app.config["DATABASE"] == db_path


def test_init_db_creates_all_tables(app: Flask, runner: FlaskCliRunner) -> None:
    result = runner.invoke(args=["init-db"])
    assert result.exit_code == 0
    assert "Initialised" in result.output
    with app.app_context():
        rows = get_db().execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        names = {row["name"] for row in rows}
    assert TABLES <= names


def test_init_db_twice_keeps_data(app: Flask, runner: FlaskCliRunner) -> None:
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO categories (name) VALUES (?)", ("Drinks",))
        db.commit()
    result = runner.invoke(args=["init-db"])
    assert result.exit_code == 0
    with app.app_context():
        count = get_db().execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    assert count == 1


def test_get_db_reuses_connection_with_foreign_keys(app: Flask) -> None:
    with app.app_context():
        db = get_db()
        assert get_db() is db
        assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_success_response(app: Flask) -> None:
    with app.test_request_context():
        response, status_code = success({"x": 1}, "Done")
    assert status_code == 200
    assert response.get_json() == {
        "status": True,
        "message": "Done",
        "data": {"x": 1},
        "errors": [],
    }


def test_failure_response(app: Flask) -> None:
    with app.test_request_context():
        response, status_code = failure("Bad input", ["quantity required"], 422)
    assert status_code == 422
    assert response.get_json() == {
        "status": False,
        "message": "Bad input",
        "data": None,
        "errors": ["quantity required"],
    }
