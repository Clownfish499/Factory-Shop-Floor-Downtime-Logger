import pytest
import sqlite3
import os
import tempfile
from app import create_app
from config import TestConfig
from database.init_db import init_db

@pytest.fixture
def app():
    # Create a temporary file database for tests so transactions and restarts behave reliably
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    # Initialize the temp DB with 40 machines & work orders
    init_db(db_path, populate_sample_data=True)

    class CustomTestConfig(TestConfig):
        DATABASE_PATH = db_path
        TESTING = True

    app = create_app(CustomTestConfig)
    yield app

    # Cleanup temp database file
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_conn(app):
    with app.app_context():
        from database.connection import get_db
        conn = get_db()
        yield conn
