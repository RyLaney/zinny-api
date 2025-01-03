"""Testing /titles endpoints."""

import os
import io
import pytest
from zinny_api.db.db_init import get_connection

from zinny_api.db.db_schema import (
    SCHEMA_TITLES_TABLE,
    SCHEMA_SCREEN_TYPE_TABLE,
    SCHEMA_RATINGS_TABLE
)
from tests.util_db_helpers import add_titles_test_data
from .data_samples import TITLES_2024VFX_SAMPLE, TITLES_WONVFX_SAMPLE

# pylint: disable=redefined-outer-name,line-too-long
# pylint: disable=missing-function-docstring,unused-argument


@pytest.fixture(scope="function")
def setup_database(monkeypatch):
    """Set up a fresh database for each test."""
    test_db_path = "/tmp/test_database.db"
    # Monkeypatch the DATABASE_PATH to point to test_db_path
    monkeypatch.setattr("zinny_api.db.db_init.DATABASE_PATH", test_db_path)

    print(f"Using database path: {test_db_path}")

    # Ensure a clean slate
    conn = get_connection()  # uses the monkeypatched DATABASE_PATH
    with conn:
        conn.executescript(
            SCHEMA_TITLES_TABLE +
            SCHEMA_SCREEN_TYPE_TABLE +
            SCHEMA_RATINGS_TABLE
        )
        print("Inserting sample data...")
        add_titles_test_data(conn, TITLES_2024VFX_SAMPLE)
        add_titles_test_data(conn, TITLES_WONVFX_SAMPLE)
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
    from zinny_api.api.titles import titles_bp

    app = Flask(__name__)
    app.register_blueprint(titles_bp, url_prefix='/api/v1/titles')

    with app.test_client() as client:
        yield client


def test_get_titles(client, setup_database):
    """Test fetching all titles from the API."""
    response = client.get('/api/v1/titles/')
    assert response.status_code == 200
    data = response.get_json()
    assert any(title["name"] == "Ojai" for title in data)
    assert any(title["name"] == "Godzilla Minus One" for title in data)
    assert any(title["name"] == "Spaceman" for title in data)


def test_get_title_by_id(client):
    """Test the /titles/<id> endpoint with a valid ID."""
    response = client.get('/api/v1/titles/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == "Ojai"


def test_get_title_invalid(client):
    """Test the /titles/<id> endpoint with an invalid ID."""
    response = client.get('/api/v1/titles/999')
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == "Title not found"


def test_import_titles_with_headers(client, setup_database):
    """Test the /titles/import endpoint with headers."""
    file_data = (
        "imdb_title_id\ttype\tname\tyear\n"
        "tt999999\tmovie\tImport Movie w Headers\t2024\n"
    )
    file = (io.BytesIO(file_data.encode('utf-8')), "titles.tsv")

    response = client.post(
        '/api/v1/titles/import',
        data={"file": file},
        content_type='multipart/form-data'
    )
    assert response.status_code == 200
    result = response.get_json()
    assert result['message'] == "1 titles imported successfully."


def test_import_titles_without_headers(client, setup_database):
    """Test the /titles/import endpoint without headers."""
    file_data = (
        "tt999999\tmovie\tImport Movie wo Headers\t2024\n"
    )
    file = (io.BytesIO(file_data.encode('utf-8')), "titles.tsv")

    response = client.post(
        '/api/v1/titles/import?has_headers=false',
        data={"file": file},
        content_type='multipart/form-data'
    )
    assert response.status_code == 200
    result = response.get_json()
    assert result['message'] == "1 titles imported successfully."


def test_add_title(client):
    """Test the /titles POST endpoint to add a title."""
    new_title = {
        "imdb_title_id": "tt888888",
        "type": "movie",
        "name": "Add Title Test",
        "year": 2025
    }
    response = client.post('/api/v1/titles/', json=new_title)
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == "Title added successfully."


def test_update_title(client):
    """Test the /titles/<id> PUT endpoint to update a title."""
    updated_data = {
        "type": "movie",
        "name": "Updated Movie",
        "year": 2026
    }
    response = client.put('/api/v1/titles/1', json=updated_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == "Title updated successfully"


def test_delete_title(client):
    """Test the /titles/<id> DELETE endpoint to remove a title."""
    response = client.delete('/api/v1/titles/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == "Title deleted successfully"


def test_search_titles(client):
    """Test the /titles/search endpoint."""
    response = client.get('/api/v1/titles/search?query=ne')
    assert response.status_code == 200
    data = response.get_json()
    results = data["results"]
    assert len(results) == 3
    assert any(title["name"] == "Godzilla Minus One" for title in results)
    assert any(title["name"] == "Dune" for title in results)
    assert any(title["name"] == "Tenet" for title in results)

    response = client.get('/api/v1/titles/search?query=Oj')
    assert response.status_code == 200
    data = response.get_json()
    results = data["results"]
    assert len(results) == 1
    assert any(title["name"] == "Ojai" for title in results)

    response = client.get('/api/v1/titles/search?query=Nonexistent')
    assert response.status_code == 200
    data = response.get_json()
    results = data["results"]
    assert len(results) == 0


def test_add_title_success(client):
    """Test adding a new title with valid data."""
    new_title = {
        "name": "New Title",
        "year": 2024,
        "type": "movie"
    }
    response = client.post('/api/v1/titles/', json=new_title)
    assert response.status_code == 200
    result = response.get_json()
    assert result["message"] == "Title added successfully."

    # Verify the title was added
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM titles WHERE name = ?;", ("New Title",))
    added_title = cursor.fetchone()
    conn.close()

    assert added_title is not None
    assert added_title["name"] == "New Title"
    assert added_title["year"] == 2024
    assert added_title["type"] == "movie"


def test_add_title_duplicate(client):
    """Test adding a duplicate title."""
    duplicate_title = TITLES_WONVFX_SAMPLE[-1]
    response = client.post('/api/v1/titles/', json=duplicate_title)
    assert response.status_code == 400
    result = response.get_json()
    assert "error" in result
    assert result["error"] == "Duplicate title found."


def test_add_title_missing_fields(client):
    """Test adding a title with missing fields."""
    response = client.post('/api/v1/titles/', json={"year": 2024})
    assert response.status_code == 400
    result = response.get_json()
    assert "error" in result
    assert result["error"] == "Title is required."
