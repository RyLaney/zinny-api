"""Database init and utils."""

import sqlite3
import os
from pathlib import Path
from flask import current_app

from zinny_api.utils.import_helpers import (
    load_titles_from_dir,
    load_surveys_from_dir,
    load_weight_presets_from_dir,
    load_title_types_from_dir
)


from .db_schema import (
    SCHEMA_TITLES_TABLE,
    SCHEMA_TITLE_TYPE_TABLE,
    SCHEMA_COLLECTIONS_TABLE,
    SCHEMA_SCREEN_TYPE_TABLE,
    SCHEMA_RATINGS_TABLE,
    SCHEMA_SURVEYS_TABLE,
    SCHEMA_WEIGHTS_TABLE
)

# pylint: disable=line-too-long


def get_database_path():
    """Determine the zinny_apiropriate database path based on the platform."""
    if os.name == 'nt':  # Windows
        base_dir = os.getenv('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
    else:  # UNIX-like (Linux, macOS)
        base_dir = os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))

    zinny_api_dir = os.path.join(base_dir, 'zinny')
    Path(zinny_api_dir).mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    return os.path.join(zinny_api_dir, 'database.db')

DATABASE_PATH = get_database_path()


def get_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return results as dictionaries
    return conn

def init_db(load_data=False, data_path=None):
    """Initialize the database schema."""
    schema = (
        SCHEMA_TITLES_TABLE +
        SCHEMA_TITLE_TYPE_TABLE +
        SCHEMA_COLLECTIONS_TABLE +
        SCHEMA_SCREEN_TYPE_TABLE +
        SCHEMA_RATINGS_TABLE +
        SCHEMA_SURVEYS_TABLE +
        SCHEMA_WEIGHTS_TABLE
    )
    if data_path is None:
        data_path = os.path.join(current_app.root_path, "data")

    conn = get_connection()
    with conn:
        conn.executescript(schema)

        if load_data:
            print("Loading initial data...")
            for data_scope in ("shared", "local"):
                load_titles_from_dir(conn, directory=os.path.join(data_path, "titles", data_scope))
                load_surveys_from_dir(conn, directory=os.path.join(data_path, "surveys", data_scope))
                load_weight_presets_from_dir(conn, directory=os.path.join(data_path, "weights", data_scope))
                load_title_types_from_dir(conn, directory=os.path.join(data_path, "title_types", data_scope))

    conn.close()

def get_records(table_name, conditions=None, condition_values=None, order_by="id"):
    """
    Generic function to fetch records from a database table.
    :param table_name: Name of the database table.
    :param conditions: SQL WHERE clause (optional).
    :param condition_values: Values for the SQL WHERE clause (optional).
    :param order_by: Column to order results by (default is "id").
    :return: List of records as dictionaries.
    """
    query = f"SELECT * FROM {table_name}"
    if conditions:
        query += f" WHERE {conditions}"
    query += f" ORDER BY {order_by}"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, condition_values or ())
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records
