import logging
import os

from flask import Flask

from app import db, seed
from app.endpoints import auth_endpoints, catalog_endpoints, page_endpoints

# Configured once at import, not on every create_app() call.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        DATABASE=os.path.join(app.instance_path, "pos.sqlite"),
    )
    if test_config is None:
        # Optional local overrides, e.g. a real SECRET_KEY.
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    seed.init_app(app)
    app.register_blueprint(auth_endpoints.bp)
    app.register_blueprint(catalog_endpoints.bp)
    app.register_blueprint(page_endpoints.bp)
    return app
