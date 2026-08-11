import os

import pytest

os.environ.setdefault("FLASK_SECRET_KEY", "test-secret-key")
os.environ.setdefault("MYSQL_USER", "test-user")
os.environ.setdefault("MYSQL_PASSWORD", "test-password")
os.environ.setdefault("MYSQL_DB", "findb")
os.environ.setdefault("FLASK_ENV", "testing")

from app import app as flask_app


@pytest.fixture
def app():
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()
