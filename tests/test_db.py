"testing db.py"

import os
import pytest
# import sqlite3
from zinny_api.db.db_init import init_db, get_connection

# pylint: disable=redefined-outer-name,line-too-long

@pytest.fixture
def imdb_style_test_data():
    """Provide a sample IMDb-style TSV data."""
    return [
        {"tconst": "tt10146532", "primaryTitle": "Ojai", "startYear": "2024", "titleType": "movie"},
        {"tconst": "tt11057302", "primaryTitle": "Madame Web", "startYear": "2024", "titleType": "movie"},
        {"tconst": "tt12037194", "primaryTitle": "Furiosa: A Mad Max Saga", "startYear": "2024", "titleType": "movie"}
    ]

@pytest.fixture
def sparse_test_data():
    """Provide sample sparse data with minimal fields."""
    return [
        {"name": "Ojai"},
        {"name": "Madame Web", "year": 2024},
        {"name": "Spaceman", "type": "movie"},
    ]


@pytest.fixture(scope="function")
def setup_database(monkeypatch):
    """Set up a fresh database for testing using /tmp."""
    test_db_path = "/tmp/test_database.db"

    # Mock the DATABASE_PATH to point to /tmp
    monkeypatch.setattr("zinny_api.db.db_init.DATABASE_PATH", test_db_path)

    # Ensure a clean slate
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    # Provide a mock path to avoid flask out of app context errors when using current_app
    not_a_data_path = "intentionally-not-a-data-path"
    # Initialize the database schema
    init_db(data_path=not_a_data_path)

    yield test_db_path  # Pass the path if needed for tests

    # Clean up after tests
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

@pytest.fixture
def connection(setup_database):  # pylint: disable=unused-argument
    """Provide a database connection for tests."""
    conn = get_connection()
    yield conn
    conn.close()

def test_init_db(setup_database):  # pylint: disable=unused-argument
    """Test that the database initializes correctly."""
    # monkeypatch.setattr("zinny_api.db.db_init.DATABASE_PATH", setup_database)

    conn = get_connection()
    cursor = conn.cursor()

    # Check that tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='titles';")
    assert cursor.fetchone() is not None

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ratings';")
    assert cursor.fetchone() is not None

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='surveys';")
    assert cursor.fetchone() is not None

    conn.close()

def test_insert_title(connection):
    """Test inserting a title into the titles table."""
    cursor = connection.cursor()
    title_data = {
        "imdb_title_id": "tt999999",
        "title_type": "movie",
        "title_name": "Inserted Title",
        "title_year": 2024
    }

    cursor.execute(
        """
        INSERT INTO titles (imdb_title_id, type, name, year)
        VALUES (:imdb_title_id, :title_type, :title_name, :title_year);
        """,
        title_data
    )
    connection.commit()

    cursor.execute("SELECT * FROM titles WHERE imdb_title_id = ?;", ("tt999999",))
    result = cursor.fetchone()
    assert result is not None
    assert result["name"] == "Inserted Title"


def test_import_imdb_style_data(connection, imdb_style_test_data):
    """Test importing IMDb-style data."""
    cursor = connection.cursor()

    for entry in imdb_style_test_data:
        cursor.execute(
            """
            INSERT INTO titles (imdb_title_id, name, type, year)
            VALUES (:tconst, :primaryTitle, :titleType, :startYear);
            """,
            entry
        )
    connection.commit()

    # Validate entries
    cursor.execute("SELECT * FROM titles WHERE imdb_title_id = ?;", ("tt10146532",))
    result = cursor.fetchone()
    assert result is not None
    assert result["name"] == "Ojai"
    assert result["type"] == "movie"
    assert result["year"] == 2024

def test_import_sparse_data(connection, sparse_test_data):
    """Test importing sparse data with minimal fields."""
    cursor = connection.cursor()

    for entry in sparse_test_data:
        cursor.execute(
            """
            INSERT INTO titles (imdb_title_id, name, type, year)
            VALUES (:imdb_title_id, :title_name, :title_type, :title_year);
            """,
            {
                "imdb_title_id": None,  # Explicitly test sparse cases
                "title_name": entry["name"],
                "title_type": entry.get("type"),
                "title_year": entry.get("year")
            }
        )
    connection.commit()

    # Validate sparse entries
    cursor.execute("SELECT * FROM titles WHERE name = ?;", ("Ojai",))
    result = cursor.fetchone()
    assert result is not None
    assert result["name"] == "Ojai"
    assert result["imdb_title_id"] is None
    assert result["type"] is None
    assert result["year"] is None


def test_handle_duplicates(connection):
    """Test duplicate handling for IMDb-style and sparse data."""
    cursor = connection.cursor()

    # # Verify schema by checking indexes
    # cursor.execute("PRAGMA index_list('titles');")
    # indexes = [dict(row) for row in cursor.fetchall()]
    # print("Indexes on 'titles':", indexes)

    # # Verify details of the specific index
    # cursor.execute("PRAGMA index_info('unique_name_year');")
    # index_info = [dict(row) for row in cursor.fetchall()]
    # print("Index details for 'unique_name_year':", index_info)

    # Insert and entry to test against
    cursor.execute(
        """
        INSERT INTO titles (imdb_title_id, name, type, year)
        VALUES (?, ?, ?, ?);
        """,
        ("tt10146532", "Ojai", "movie", 2024)
    )
    connection.commit()

    # Try to insert duplicate by imdb_title_id
    cursor.execute(
        """
        INSERT OR IGNORE INTO titles (imdb_title_id, name, type, year)
        VALUES (?, ?, ?, ?);
        """,
        ("tt10146532", "Ojai", "movie", 2024)
    )
    connection.commit()

    # Try to insert duplicate by title/year
    cursor.execute(
        """
        INSERT OR IGNORE INTO titles (imdb_title_id, name, type, year)
        VALUES (?, ?, ?, ?);
        """,
        (None, "Ojai", "movie", 2024)
    )
    connection.commit()

    # Validate that no duplicates exist
    cursor.execute("SELECT COUNT(*) as count FROM titles WHERE name = ?;", ("Ojai",))
    result = cursor.fetchone()
    print("Validation query result:", result)

    assert result["count"] == 1


def test_insert_rating(connection):
    """Test inserting a rating into the ratings table."""
    cursor = connection.cursor()

    # Assume a title exists with id=1
    cursor.execute(
        "INSERT INTO titles (imdb_title_id, type, name, year) VALUES (?, ?, ?, ?);",
        ("tt888888", "movie", "Another Movie", "2023")
    )
    connection.commit()

    rating_data = {
        "title_id": 1,
        "survey_id": "vfx_2024",
        "ratings": '{"artistry": 8, "technical_achievement": 9}',
        "comments": "Great visuals!"
    }

    cursor.execute(
        """
        INSERT INTO ratings (title_id, survey_id, ratings, comments)
        VALUES (:title_id, :survey_id, :ratings, :comments);
        """,
        rating_data
    )
    connection.commit()

    cursor.execute("SELECT * FROM ratings WHERE title_id = ?;", (1,))
    result = cursor.fetchone()
    assert result is not None
    assert result["comments"] == "Great visuals!"


def test_insert_survey(connection):
    """Test inserting a survey into the surveys table."""
    cursor = connection.cursor()

    survey_data = {
        "id": "vfx_2024",
        "name": "Visual Effects Survey",
        "version": "1.0",
        "description": "A survey for visual effects assessment.",
        "criteria": '[{"id": "artistry", "name": "Artistry", "range": [0, 10]}]'
    }

    cursor.execute(
        """
        INSERT INTO surveys (id, name, version, description, criteria)
        VALUES (:id, :name, :version, :description, :criteria);
        """,
        survey_data
    )
    connection.commit()

    cursor.execute("SELECT * FROM surveys WHERE id = ?;", ("vfx_2024",))
    result = cursor.fetchone()
    assert result is not None
    assert result["name"] == "Visual Effects Survey"

