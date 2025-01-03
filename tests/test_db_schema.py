import os
import pytest
import sqlite3

from zinny_api.db.db_init import get_connection
from zinny_api.api.screen_types import screen_types_bp

from zinny_api.db.db_schema import (
    SCHEMA_TITLES_TABLE,
    SCHEMA_TITLE_TYPE_TABLE,
    SCHEMA_COLLECTIONS_TABLE,
    SCHEMA_SCREEN_TYPE_TABLE,
    SCHEMA_RATINGS_TABLE,
    SCHEMA_SURVEYS_TABLE,
    SCHEMA_WEIGHTS_TABLE
)

# pylint: disable=missing-function-docstring,line-too-long

@pytest.fixture
def mock_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    with conn:
        conn.executescript(
            SCHEMA_TITLES_TABLE
            + SCHEMA_TITLE_TYPE_TABLE
            + SCHEMA_COLLECTIONS_TABLE
            + SCHEMA_SCREEN_TYPE_TABLE
            + SCHEMA_RATINGS_TABLE
            + SCHEMA_SURVEYS_TABLE
            + SCHEMA_WEIGHTS_TABLE
        )
    yield conn
    conn.close()


def test_schema_integrity(mock_db):
    """Validate that the database schema matches expectations."""
    cursor = mock_db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row["name"] for row in cursor.fetchall()}
    expected_tables = {"titles", "title_types", "collections", "screen_types", "ratings", "surveys", "weight_presets"}
    assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"
