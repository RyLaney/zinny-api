"""Testing /api/v1/title-types endpoints."""

import os
import pytest
from flask import Flask
from zinny_api.db.db_init import get_connection
from zinny_api.api.title_types import title_types_bp
from zinny_api.db.db_schema import SCHEMA_TITLE_TYPE_TABLE
from tests.util_db_helpers import add_title_types_test_data
from .data_samples import TITLE_TYPES_SAMPLE


# pylint: disable=redefined-outer-name,line-too-long
# pylint: disable=missing-function-docstring,unused-argument

@pytest.fixture(scope="function")
def setup_database(monkeypatch):
    """Set up a fresh database for each test."""
    test_db_path = "/tmp/test_database.db"
    monkeypatch.setattr("zinny_api.db.db_init.DATABASE_PATH", test_db_path)

    conn = get_connection()
    with conn:
        conn.executescript(SCHEMA_TITLE_TYPE_TABLE)
        add_title_types_test_data(conn, TITLE_TYPES_SAMPLE)
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
    app.register_blueprint(title_types_bp, url_prefix='/api/v1/title-types')
    with app.test_client() as client:
        yield client


def test_get_title_types(client):
    """Test fetching all title types."""
    response = client.get('/api/v1/title-types/')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == len(TITLE_TYPES_SAMPLE)
    assert any(title_type["type"] == "tvSeries" for title_type in data)


def test_get_title_type_by_type(client):
    """Test fetching a specific title type by its type."""
    response = client.get('/api/v1/title-types/tvSeries')
    assert response.status_code == 200
    data = response.get_json()
    assert data["type"] == "tvSeries"
    assert data["display_name"] == "TV Series"


def test_get_title_type_invalid(client):
    """Test fetching a non-existent title type."""
    response = client.get('/api/v1/title-types/nonexistent')
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "title_types not found"


def test_add_title_type(client):
    """Test adding a new title type."""
    new_title_type = {"type": "tvSpecial", "display_name": "TV Special"}
    response = client.post('/api/v1/title-types/', json=new_title_type)
    assert response.status_code == 200
    result = response.get_json()
    assert result["message"] == "title_type_item added successfully."
    assert result["title_type_item"]["type"] == "tvSpecial"

    # Verify in database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM title_types WHERE type = 'tvSpecial';")
    data = cursor.fetchone()
    conn.close()

    assert data is not None
    assert data["display_name"] == "TV Special"


def test_load_title_types(client):
    """Test loading title types from the predefined directory."""
    response = client.post('/api/v1/title-types/load')
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "title_types loaded successfully."
