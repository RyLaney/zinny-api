"""Testing /api/v1/screen-types endpoints."""

import os
import pytest
from flask import Flask
from zinny_api.db.db_init import get_connection
from zinny_api.api.screen_types import screen_types_bp
from zinny_api.db.db_schema import SCHEMA_SCREEN_TYPE_TABLE
from tests.util_db_helpers import add_screen_types_test_data
from .data_samples import SCREEN_TYPES_SAMPLE

# pylint: disable=redefined-outer-name,line-too-long
# pylint: disable=missing-function-docstring,unused-argument


@pytest.fixture(scope="function")
def setup_database(monkeypatch):
    """Set up a fresh database for each test."""
    test_db_path = "/tmp/test_database.db"
    monkeypatch.setattr("zinny_api.db.db_init.DATABASE_PATH", test_db_path)

    conn = get_connection()
    with conn:
        conn.executescript(SCHEMA_SCREEN_TYPE_TABLE)
        # add_screen_types_test_data(conn, SCREEN_TYPES_SAMPLE)  # data is loaded in SCHEMA, needs to migrate
        conn.commit()
    conn.close()

    yield

    # Clean up after tests
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture
def client(setup_database):
    """Create a Flask test client with database setup."""
    app = Flask(__name__)
    app.register_blueprint(screen_types_bp, url_prefix='/api/v1/screen-types')
    with app.test_client() as client:
        yield client


def test_get_screen_types(client):
    """Test fetching all screen types."""
    response = client.get('/api/v1/screen-types/')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == len(SCREEN_TYPES_SAMPLE)
    assert any(screen_type["type"] == "medium" for screen_type in data)


def test_get_screen_type_by_type(client):
    """Test fetching a specific screen type by its type."""
    response = client.get('/api/v1/screen-types/medium')
    assert response.status_code == 200
    data = response.get_json()
    assert data["type"] == "medium"
    assert data["display_name"] == "Medium screen"


def test_get_screen_type_invalid(client):
    """Test fetching a non-existent screen type."""
    response = client.get('/api/v1/screen-types/nonexistent')
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "screen_types not found"


def test_add_screen_type(client):
    """Test adding a new screen type."""
    new_screen_type = {"type": "newtype", "display_name": "A New Type", "description": "A new type of screen"}
    response = client.post('/api/v1/screen-types/', json=new_screen_type)
    assert response.status_code == 200
    result = response.get_json()
    assert result["message"] == "screen_type_item added successfully."
    assert result["screen_type_item"]["type"] == "newtype"

    # Verify in database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM screen_types WHERE type = 'newtype';")
    data = cursor.fetchone()
    conn.close()

    assert data is not None
    assert data["display_name"] == "A New Type"


# def test_load_screen_types(client):
#     """Test loading screen types from the predefined directory."""
#     response = client.post('/api/v1/screen-types/load')
#     assert response.status_code == 200
#     data = response.get_json()
#     assert data["message"] == "screen_types loaded successfully."
