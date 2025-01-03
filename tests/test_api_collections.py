"""Testing /api/v1/collections endpoints."""


import os
import io
import json
from unittest.mock import patch

import pytest
from zinny_api.config import COLLECTION_PATHS
from zinny_api.db.db_init import get_connection
from zinny_api.db.db_schema import (
    SCHEMA_TITLES_TABLE,
    SCHEMA_COLLECTIONS_TABLE
)
from .data_samples import (
    # TITLES_2024VFX_SAMPLE,
    COLLECTION_CLASSICS_SAMPLE,
    COLLECTION_FAVORITES_SAMPLE,
    COLLECTION_SCI_FI_SAMPLE
)

from .util_db_helpers import add_collections_test_data

# pylint: disable=redefined-outer-name,line-too-long
# pylint: disable=missing-function-docstring,unused-argument
# pylint: disable=import-outside-toplevel


@pytest.fixture(scope="function")
def setup_database(monkeypatch):
    """Set up a fresh database for each test."""
    test_db_path = "/tmp/test_database.db"
    monkeypatch.setattr("zinny_api.db.db_init.DATABASE_PATH", test_db_path)

    collections = [COLLECTION_CLASSICS_SAMPLE, COLLECTION_FAVORITES_SAMPLE, COLLECTION_SCI_FI_SAMPLE]

    conn = get_connection()
    with conn:
        conn.executescript(
            SCHEMA_TITLES_TABLE
            + SCHEMA_COLLECTIONS_TABLE
        )
        add_collections_test_data(conn, collections)
        conn.commit()
    conn.close()

    yield

    # Clean up after tests
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture
def client(setup_database):
    # pylint: disable=import-outside-toplevel
    from flask import Flask
    from zinny_api.api.collections import collections_bp

    app = Flask(__name__)
    app.register_blueprint(collections_bp, url_prefix='/api/v1/collections')

    with app.test_client() as client:
        yield client


@pytest.fixture(scope="function", autouse=True)
def patch_collection_paths(tmp_path):
    """Patch collection paths to use temporary directories."""
    with patch.dict(COLLECTION_PATHS, {
        "shared": tmp_path / "shared",
        "local": tmp_path / "local"
    }):
        os.makedirs(COLLECTION_PATHS["shared"], exist_ok=True)
        os.makedirs(COLLECTION_PATHS["local"], exist_ok=True)
        yield COLLECTION_PATHS

def test_create_collection(client):
    """Test creating a new collection."""
    data = {"name": "New Collection", "description": "A test collection."}
    response = client.post('/api/v1/collections/', json=data)
    assert response.status_code == 201
    result = response.get_json()
    assert result["message"] == "Collection created successfully."
    assert "collection_id" in result

def test_create_collection_missing_name(client):
    """Test creating a collection with missing name."""
    data = {"description": "Missing name."}
    response = client.post('/api/v1/collections/', json=data)
    assert response.status_code == 400
    result = response.get_json()
    assert result["error"] == "Collection name is required."


def test_get_collections(client, setup_database):
    """Test fetching all collections from the API."""
    response = client.get('/api/v1/collections/')
    assert response.status_code == 200
    data = response.get_json()
    assert any(collection["name"] == "Classic Movies" for collection in data)
    assert any(collection["name"] == "Favorites 2024" for collection in data)
    assert any(collection["name"] == "Sci-Fi Favorites" for collection in data)


def test_get_collection_invalid(client):
    """Test the /collections/<id> endpoint with an invalid ID."""
    response = client.get('/api/v1/collections/999')
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == "Collection not found"


def test_get_collection_by_id(client, setup_database):
    """Test the /collections/<id> endpoint with a valid ID."""
    response = client.get('/api/v1/collections/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == "Classic Movies"

def test_delete_collection(client):
    """Test deleting an existing collection."""
    response = client.delete('/api/v1/collections/1')
    assert response.status_code == 200
    result = response.get_json()
    assert result["message"] == "Collection deleted successfully."

def test_delete_nonexistent_collection(client):
    """Test deleting a non-existent collection."""
    response = client.delete('/api/v1/collections/999')
    assert response.status_code == 200  # SQLite DELETE returns success even for non-existent records
    result = response.get_json()
    assert result["message"] == "Collection deleted successfully."


def test_add_titles_to_collection(client):
    """Test adding titles to a collection."""
    data = {"title_ids": [1, 2]}
    response = client.post('/api/v1/collections/1/titles', json=data)
    assert response.status_code == 200
    result = response.get_json()
    assert result["message"] == "Titles added to collection successfully."

def test_add_invalid_titles_to_collection(client):
    """Test adding invalid title IDs to a collection."""
    data = {"title_ids": [999]}
    response = client.post('/api/v1/collections/1/titles', json=data)
    assert response.status_code == 200  # SQLite INSERT OR IGNORE doesn't error
    result = response.get_json()
    assert result["message"] == "Titles added to collection successfully."


def test_get_titles_in_collection(client, setup_database):
    """Test retrieving titles in a collection."""
    response = client.get('/api/v1/collections/1/titles')
    assert response.status_code == 200
    titles = response.get_json()
    assert len(titles) > 0
    assert titles[0]["name"] == "Casablanca"  # Update to match test data

def test_get_titles_in_empty_collection(client):
    """Test retrieving titles in an empty collection."""
    response = client.get('/api/v1/collections/999/titles')
    assert response.status_code == 200
    titles = response.get_json()
    assert len(titles) == 0

def test_remove_titles_from_collection(client):
    """Test removing titles from a collection."""
    data = {"title_ids": [1]}
    response = client.delete('/api/v1/collections/1/titles', json=data)
    assert response.status_code == 200
    result = response.get_json()
    assert result["message"] == "Titles removed from collection successfully."

def test_import_collection(client, patch_collection_paths):
    """Test the /collections/import endpoint with a valid collection file."""
    collection_data = {"id": 1, "name": "User Collection", "description": "A user-imported collection."}
    collection_file = (io.BytesIO(json.dumps(collection_data).encode('utf-8')), "user_collection.json")

    response = client.post('/api/v1/collections/import', data={"file": collection_file}, content_type='multipart/form-data')
    assert response.status_code == 200
    result = response.get_json()
    assert result["message"] == "Collection imported successfully"
    assert result["collection"]["id"] == 1
    assert result["collection"]["name"] == "User Collection"
    assert result["collection"]["description"] == "A user-imported collection."

def test_import_collection_missing_fields(client):
    """Test importing a collection with missing required fields."""
    collection_data = {"id": 1, "description": "Missing name and items."}
    collection_file = (io.BytesIO(json.dumps(collection_data).encode('utf-8')), "invalid_collection.json")
    response = client.post('/api/v1/collections/import', data={"file": collection_file}, content_type='multipart/form-data')
    assert response.status_code == 400
    result = response.get_json()
    assert "error" in result
    assert result["error"] == "Invalid collection data. Missing required fields."

def test_import_collection_invalid(client):
    """Test the /collections/import endpoint with an invalid collection file."""
    invalid_file = (io.BytesIO(b"not valid json"), "invalid_collection.json")

    response = client.post('/api/v1/collections/import', data={"file": invalid_file}, content_type='multipart/form-data')
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid JSON format."


def test_export_collections(client, setup_database):
    """Test exporting collections as JSON."""
    response = client.get('/api/v1/collections/export')
    assert response.status_code == 200
    data = response.get_json()

    assert len(data) == 3
    assert data[0]["name"] == "Classic Movies"
    assert data[1]["name"] == "Favorites 2024"
    assert data[2]["name"] == "Sci-Fi Favorites"


def test_export_collection(client, setup_database):
    """Test exporting collections as JSON."""
    response = client.get('/api/v1/collections/export/3')
    assert response.status_code == 200
    data = response.get_json()

    assert data["name"] == "Sci-Fi Favorites"

@pytest.fixture
def empty_client():
    """Create a Flask test client with an empty database."""
    from flask import Flask
    from zinny_api.api.collections import collections_bp

    test_db_path_empty = "/tmp/empty_test_database.db"

    # Patch the DATABASE_PATH dynamically for this test
    with patch("zinny_api.db.db_init.DATABASE_PATH", test_db_path_empty):
        # Set up the empty database schema
        conn = get_connection()
        with conn:
            conn.executescript(SCHEMA_TITLES_TABLE + SCHEMA_COLLECTIONS_TABLE)
        conn.close()

        # Create the test client
        app = Flask(__name__)
        app.register_blueprint(collections_bp, url_prefix='/api/v1/collections')

        with app.test_client() as client:
            yield client

        # Clean up the test database after the test
        if os.path.exists(test_db_path_empty):
            os.remove(test_db_path_empty)

def test_export_empty_collections(empty_client):
    """Test exporting collections when no collections exist."""
    response = empty_client.get('/api/v1/collections/export')

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 0
