import logging

import click
from flask import Flask
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

from app.db import get_db
from app.repositories.category_repository import count_categories, insert_category
from app.repositories.item_repository import insert_item
from app.repositories.user_repository import insert_user

logger = logging.getLogger(__name__)

# Prices in the smallest unit: 150 = 1.50.
CATEGORIES: dict[str, list[tuple[str, int]]] = {
    "Drinks": [("Cola", 150), ("Water", 100), ("Orange Juice", 250), ("Coffee", 200)],
    "Snacks": [("Chips", 120), ("Chocolate Bar", 180), ("Cookies", 220)],
    "Bakery": [("Croissant", 250), ("Bagel", 200), ("Muffin", 275)],
}

# Local dev only: these passwords are public.
USERS: list[tuple[str, str, str]] = [
    ("admin", "admin123", "admin"),
    ("cashier", "cashier123", "cashier"),
]


def seed_db() -> bool:
    """Insert sample data. Skips everything if any category already exists."""
    if count_categories() > 0:
        logger.info("Database already seeded, nothing changed")
        return False

    db = get_db()
    try:
        for category_name, items in CATEGORIES.items():
            category_id = insert_category(category_name)
            for item_name, price in items:
                insert_item(category_id, item_name, price)
        for username, password, role in USERS:
            insert_user(username, generate_password_hash(password), role)
        db.commit()
    except Exception:
        db.rollback()
        raise
    logger.info("Seeded the database")
    return True


@click.command("seed")
@with_appcontext
def seed_command() -> None:
    if seed_db():
        click.echo("Seeded the database.")
    else:
        click.echo("Database already seeded, nothing changed.")


def init_app(app: Flask) -> None:
    app.cli.add_command(seed_command)
