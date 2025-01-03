"""Testing enhanced /titles/search functionality."""

import os
import pytest
from flask import Flask
from zinny_api.db.db_init import get_connection
from zinny_api.api.titles import titles_bp
from zinny_api.db.db_schema import (
    SCHEMA_TITLES_TABLE,
    SCHEMA_SCREEN_TYPE_TABLE,
    SCHEMA_RATINGS_TABLE
)
from .data_samples import (
    TITLES_2024VFX_SAMPLE,
    TITLES_WONVFX_SAMPLE,
    TITLES_SHORT_SAMPLE,
    TITLES_TVMOVIE_MINISERIES_SAMPLE,
    TITLES_VIDEO_TVSHORT_SAMPLE,
    TITLES_TVSERIES_SAMPLE,
    RATINGS_VFX_SAMPLE,
    RATINGS_PICTURE_SAMPLE
)
from tests.util_db_helpers import add_titles_test_data, add_ratings_test_data

# pylint: disable=redefined-outer-name,line-too-long
# pylint: disable=missing-function-docstring,unused-argument

@pytest.fixture(scope="function")
def setup_database(monkeypatch):
    """Set up a fresh database for each test."""
    test_db_path = "/tmp/test_database.db"
    monkeypatch.setattr("zinny_api.db.db_init.DATABASE_PATH", test_db_path)

    # Consolidate all title samples
    all_titles = (
        TITLES_2024VFX_SAMPLE +
        TITLES_WONVFX_SAMPLE +
        TITLES_SHORT_SAMPLE +
        TITLES_TVMOVIE_MINISERIES_SAMPLE +
        TITLES_VIDEO_TVSHORT_SAMPLE +
        TITLES_TVSERIES_SAMPLE
    )

    conn = get_connection()
    with conn:
        conn.executescript(
            SCHEMA_TITLES_TABLE +
            SCHEMA_SCREEN_TYPE_TABLE +
            SCHEMA_RATINGS_TABLE
        )
        add_titles_test_data(conn, all_titles)
        add_ratings_test_data(conn, RATINGS_VFX_SAMPLE)
        add_ratings_test_data(conn, RATINGS_PICTURE_SAMPLE)
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
    app.register_blueprint(titles_bp, url_prefix='/api/v1/titles')
    with app.test_client() as client:
        yield client


def test_search_by_name(client):
    """Test searching titles by name."""
    response = client.get('/api/v1/titles/search?query=godzilla')
    assert response.status_code == 200
    results = response.get_json()["results"]
    assert len(results) == 1
    assert results[0]["name"] == "Godzilla Minus One"

    response = client.get('/api/v1/titles/search?query=Pierrot')
    assert response.status_code == 200
    results = response.get_json()["results"]
    assert len(results) == 1
    assert results[0]["name"] == "Poor Pierrot"


def test_filter_by_year_range(client):
    """Test filtering titles by year range."""
    response = client.get('/api/v1/titles/search?year_start=1892&year_end=1894')
    assert response.status_code == 200
    results = response.get_json()["results"]
    assert len(results) == 5  # All titles from TITLES_SHORT_SAMPLE

    response = client.get('/api/v1/titles/search?year_start=1948&year_end=1955')
    assert response.status_code == 200
    results = response.get_json()["results"]
    assert len(results) == 7  # From TITLES_TVSERIES_SAMPLE and TITLES_VIDEO_TVSHORT_SAMPLE


def test_filter_by_type(client):
    """Test filtering titles by type."""
    response = client.get('/api/v1/titles/search?type=short')
    assert response.status_code == 200
    results = response.get_json()["results"]
    assert len(results) == 5  # From TITLES_SHORT_SAMPLE

    response = client.get('/api/v1/titles/search?type=tvSeries')
    assert response.status_code == 200
    results = response.get_json()["results"]
    assert len(results) == 5  # From TITLES_TVSERIES_SAMPLE


def test_combined_filters(client):
    """Test combining query, year range, and type filters."""
    response = client.get('/api/v1/titles/search?query=Pierrot&type=short&year_start=1892')
    assert response.status_code == 200
    results = response.get_json()["results"]
    assert len(results) == 1
    assert results[0]["name"] == "Poor Pierrot"

    response = client.get('/api/v1/titles/search?type=tvSeries&year_start=1948&year_end=1950')
    assert response.status_code == 200
    results = response.get_json()["results"]
    print(results)
    assert len(results) == 5  # First 5 titles from TITLES_TVSERIES_SAMPLE


def test_pagination(client):
    """Test pagination of search results."""
    response = client.get('/api/v1/titles/search?type=short&limit=2&page=1')
    assert response.status_code == 200
    results = response.get_json()["results"]
    assert len(results) == 2

    response = client.get('/api/v1/titles/search?type=short&limit=2&page=2')
    assert response.status_code == 200
    results = response.get_json()["results"]
    assert len(results) == 2

    response = client.get('/api/v1/titles/search?type=short&limit=2&page=3')
    assert response.status_code == 200
    results = response.get_json()["results"]
    assert len(results) == 1  # Only 1 title left on page 3
