"""Testing /ratings endpoints with database integration."""
import os
import json
from unittest.mock import patch
import sqlite3
import pytest

from flask import Flask

from zinny_api.db.db_init import get_connection
from zinny_api.api.ratings import ratings_bp
from zinny_api.db.db_schema import (
    SCHEMA_TITLES_TABLE,
    SCHEMA_SCREEN_TYPE_TABLE,
    SCHEMA_RATINGS_TABLE,
    SCHEMA_SURVEYS_TABLE
)
# from zinny_api.api.collections import collections_bp

from tests.util_db_helpers import (
    add_titles_test_data,
    add_surveys_test_data,
    add_ratings_test_data
)
from .data_samples import (
    TITLES_2024VFX_SAMPLE,
    SURVEY_VFX_SAMPLE,
    SURVEY_PICTURE_SAMPLE,
    RATINGS_VFX_SAMPLE,
    RATINGS_PICTURE_SAMPLE
)

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
            SCHEMA_TITLES_TABLE
            + SCHEMA_SURVEYS_TABLE
            + SCHEMA_SCREEN_TYPE_TABLE
            + SCHEMA_RATINGS_TABLE            
        )
        add_titles_test_data(conn, TITLES_2024VFX_SAMPLE)
        add_surveys_test_data(conn, [SURVEY_VFX_SAMPLE, SURVEY_PICTURE_SAMPLE])
        # add_ratings_test_data(conn, [RATINGS_VFX_SAMPLE, RATINGS_PICTURE_SAMPLE])
        add_ratings_test_data(conn, RATINGS_VFX_SAMPLE)
        add_ratings_test_data(conn, RATINGS_PICTURE_SAMPLE)

    conn.close()

    yield

    # Clean up after tests
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture
def client(setup_database):
    """Create a Flask test client with database setup."""
    app = Flask(__name__)
    app.register_blueprint(ratings_bp, url_prefix='/api/v1/ratings')
    with app.test_client() as client:
        yield client

def test_save_rating(client):
    """Test saving a rating."""
    title_id = 2
    rating_data = {
        "title_id": title_id,
        "survey_id": "vfx_minimal",
        "ratings": '{"artistry": 8, "technical_achievement": 7}',
        "comments": "Great effects!"
    }
    response = client.post('/api/v1/ratings/', json=rating_data)
    assert response.status_code == 201
    result = response.get_json()
    assert result["message"] == "Rating saved successfully."

    # # Verify the rating was updated
    rating_id = result["rating_id"]
    response = client.get(f'/api/v1/ratings/{rating_id}')
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["comments"] == "Great effects!"
    ratings = json.loads(response_json["ratings"])
    assert ratings["artistry"] == 8
    assert ratings["technical_achievement"] == 7


def test_save_rating_missing_fields(client):
    """Test saving a rating with missing required fields."""
    rating_data = {
        "survey_id": "vfx_basic",
        "ratings": '{"artistry": 8}'
    }
    response = client.post('/api/v1/ratings/', json=rating_data)
    assert response.status_code == 400
    result = response.get_json()
    assert "error" in result
    assert "title_id" in result["error"]


def test_get_all_ratings(client):
    """Test retrieving all ratings."""
    response = client.get('/api/v1/ratings/')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 4  # 2 from each sample set


def test_get_rating_by_id(client):
    """Test retrieving a specific rating by ID."""
    response = client.get('/api/v1/ratings/1')
    assert response.status_code == 200
    rating = response.get_json()
    assert rating["id"] == 1
    assert rating["survey_id"] == "vfx_basic"


def test_get_rating_by_title_and_survey(client):
    """Test fetching a rating by title_id and survey_id."""
    title_id = 1
    survey_id = "vfx_basic"

    response = client.get(f'/api/v1/ratings/?title_id={title_id}&survey_id={survey_id}')
    assert response.status_code == 200
    rating = response.get_json()
    assert rating["title_id"] == title_id
    assert rating["survey_id"] == survey_id
    assert "ratings" in rating


def test_get_rating_by_title_and_survey_not_found(client):
    """Test fetching a rating by title_id and survey_id when no match is found."""
    title_id = 999
    survey_id = "nonexistent_survey"

    response = client.get(f'/api/v1/ratings/?title_id={title_id}&survey_id={survey_id}')
    assert response.status_code == 200
    assert response.get_json() == {}


def test_get_rating_invalid(client):
    """Test retrieving a non-existent rating by ID."""
    response = client.get('/api/v1/ratings/999')
    assert response.status_code == 404
    error = response.get_json()
    assert error["error"] == "Rating not found"


@patch("zinny_api.api.ratings.get_connection", side_effect=sqlite3.OperationalError("Database error"))
def test_get_ratings_db_error(mocked_get_connection, client):
    """Test error handling when database operation fails in get_ratings."""
    response = client.get('/api/v1/ratings/')
    assert response.status_code == 500
    result = response.get_json()
    assert "error" in result
    assert "Database error" in result["error"]


def test_save_rating_with_screen_type(client):
    """Test saving a rating with a valid screen_type."""
    rating_data = {
        "title_id": 1,
        "survey_id": "vfx_basic",
        "ratings": '{"artistry": 9}',
        "comments": "Excellent effects!",
        "screen_type": "big"
    }
    response = client.post('/api/v1/ratings/', json=rating_data)
    assert response.status_code == 201
    result = response.get_json()
    assert result["message"] == "Rating saved successfully."

    # Fetch and verify
    rating_id = result["rating_id"]
    response = client.get(f'/api/v1/ratings/{rating_id}')
    rating = response.get_json()
    assert rating["screen_type_id"] == 1  # Assuming "big" maps to ID 1

def test_save_rating_invalid_screen_type(client):
    """Test saving a rating with an invalid screen type."""
    rating_data = {
        "title_id": 1,
        "survey_id": "vfx_basic",
        "ratings": '{"artistry": 8}',
        "screen_type": "invalid_type"
    }
    response = client.post('/api/v1/ratings/', json=rating_data)
    assert response.status_code == 400
    result = response.get_json()
    assert "error" in result
    assert "Invalid 'screen_type'" in result["error"]


def test_update_rating(client, setup_database):
    """Test that duplicate ratings are updated."""
    title_id = 4
    rating_data = {
        "title_id": title_id,
        "survey_id": "vfx_basic",
        "ratings": {"artistry": 8, "technical_achievement": 9},
        "comments": ""
    }
    response = client.post('/api/v1/ratings/', json=rating_data)
    assert response.status_code == 201
    result = response.get_json()
    rating_id = result["rating_id"]
    print(f"result: {result} {rating_id}")

    # Attempt to insert a duplicate with changes
    rating_data = {
        "title_id": title_id,
        "survey_id": "vfx_basic",
        "ratings": {"artistry": 10, "technical_achievement": 10},
        "comments": "Great effects!"
    }
    # Attempt to insert a duplicate
    response = client.post('/api/v1/ratings/', json=rating_data)
    assert response.status_code == 201
    result = response.get_json()
    rating_id = result["rating_id"]
    print(f"result: {result} {rating_id}")

    # get the rating by id and confirm the updates
    response = client.get(f'/api/v1/ratings/{rating_id}')
    print(f"response: {response}")
    result = response.get_json()
    print(f"result: {result}")
    assert response.status_code == 200
    assert result["ratings"] == {"artistry": 10, "technical_achievement": 10}
    assert result["comments"] == "Great effects!"


def test_update_rating_invalid_id(client):
    """Test updating a non-existent rating."""
    update_data = {
        "ratings": '{"artistry": 10}',
        "comments": "Updated feedback"
    }
    response = client.put('/api/v1/ratings/999', json=update_data)
    assert response.status_code == 404
    result = response.get_json()
    assert result["error"] == "Rating not found"


def test_delete_rating(client):
    """Test deleting an existing rating."""
    response = client.delete('/api/v1/ratings/1')
    assert response.status_code == 200
    result = response.get_json()
    assert result["message"] == "Rating deleted successfully"

    # Verify the rating was deleted
    response = client.get('/api/v1/ratings/1')
    assert response.status_code == 404


def test_delete_non_existent_rating(client):
    """Test deleting a non-existent rating."""
    response = client.delete('/api/v1/ratings/999')
    assert response.status_code == 404
    result = response.get_json()
    assert result["error"] == "Rating not found"

@patch("zinny_api.api.ratings.get_connection", side_effect=sqlite3.OperationalError("Database error"))
def test_delete_rating_db_error(mocked_get_connection, client):
    """Test error handling during a DELETE operation when the database fails."""
    response = client.delete('/api/v1/ratings/1')
    assert response.status_code == 500
    result = response.get_json()
    assert "error" in result
    assert "Database error" in result["error"]


def test_export_ratings(client, setup_database):
    """Test exporting ratings as JSON."""
    response = client.get('/api/v1/ratings/export')
    assert response.status_code == 200
    data = response.get_json()

    assert len(data) == 4
    assert data[0]["title_name"] == "Ojai"
    assert data[0]["ratings"]["artistry"] == 8
    assert data[3]["title_name"] == "Madame Web"
    assert data[3]["ratings"]["storytelling"] == 7

@pytest.fixture
def empty_client():
    """Create a Flask test client with an empty database."""
    test_db_path_empty = "/tmp/empty_test_database.db"

    # Patch the DATABASE_PATH dynamically for this test
    with patch("zinny_api.db.db_init.DATABASE_PATH", test_db_path_empty):
        # Set up the empty database schema
        conn = get_connection()
        with conn:
            conn.executescript(
                SCHEMA_TITLES_TABLE
                + SCHEMA_SURVEYS_TABLE
                + SCHEMA_SCREEN_TYPE_TABLE
                + SCHEMA_RATINGS_TABLE            
            )
        conn.close()

        # Create the test client
        app = Flask(__name__)
        app.register_blueprint(ratings_bp, url_prefix='/api/v1/ratings')

        with app.test_client() as client:
            yield client

        # Clean up the test database after the test
        if os.path.exists(test_db_path_empty):
            os.remove(test_db_path_empty)


def test_export_ratings_empty_database(empty_client):
    """Test exporting ratings when no ratings exist."""
    response = empty_client.get('/api/v1/ratings/export')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 0



@patch("zinny_api.api.ratings.get_connection", side_effect=sqlite3.OperationalError("Database error"))
def test_export_ratings_db_error(mocked_get_connection, client):
    """Test error handling during ratings export when the database fails."""
    response = client.get('/api/v1/ratings/export')
    assert response.status_code == 500
    # print(f"response: {response}")  # <WrapperTestResponse streamed [500 INTERNAL SERVER ERROR]>
    result = response.get_json()
    # print(f"result: {result}")
    assert "error" in result
    assert "Database error" in result["error"]
