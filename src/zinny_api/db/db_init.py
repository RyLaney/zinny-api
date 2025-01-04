"""Database init and utils."""

import sqlite3
import os
from pathlib import Path
import platform
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

# pylint: disable=line-too-long,missing-function-docstring


def get_app_name():
    try:
        return current_app.config.get("APP_NAME", "zinny")
    except RuntimeError:  # If current_app is unavailable
        return "zinny"


def get_data_paths(create_udp=True, create_pdp=False):
    """Returns the local user data path (udp) and global program data path (pdp) ."""
    system = platform.system()
    if system == "Windows":
        pdp = os.environ["PROGRAMDATA"]
        udp = os.path.join(os.environ["LOCALAPPDATA"])
    elif system == "Darwin":  # macOS
        pdp = "/Library/Application Support"
        udp = os.path.join(Path.home(), "Library", "Application Support")
    else:  # Linux and other Unix-like systems
        pdp = "/usr/share"
        udp = os.path.join(Path.home(), ".local", "share")

    app_name = get_app_name()

    # Append the app name to the paths
    pdp = os.path.join(pdp, app_name)
    udp = os.path.join(udp, app_name)

    # Create the directories if they don't exist
    _ = os.makedirs(pdp, exist_ok=True) if create_pdp else None
    _ = os.makedirs(udp, exist_ok=True) if create_udp else None

    current_app.config["DATA_PROG_PATH"] = pdp
    current_app.config["DATA_USER_PATH"] = udp

    return {"udp": udp, "pdp": pdp}

def get_user_data_path():
    udp = get_data_paths(create_udp=True, create_pdp=False)["udp"]
    return udp

def get_program_data_path():
    pdp = get_data_paths(create_udp=False, create_pdp=True)["pdp"]
    return pdp

def get_database_path():
    """Determine the zinny_apiropriate database path based on the platform."""

    user_data_path = get_user_data_path()
    zinny_api_dir = os.path.join(user_data_path, 'Zinny')
    os.makedirs(zinny_api_dir, exist_ok=True)

    return os.path.join(zinny_api_dir, 'zinny-1.0.sqlite')

DATABASE_PATH = get_database_path()
current_app.config["DATABASE_PATH"] = DATABASE_PATH

def get_survey_data_path():
    """Returns the program data path for surveys."""
    program_data_path = get_program_data_path()
    survey_path = os.path.join(program_data_path, 'data', 'surveys')
    if not os.path.exists(survey_path):
        return None
    # else
    return survey_path

# TODO: use proj_data_path for surveys in import_helpers.py
# def load_survey(file_name):
#     import json
#     data_path = get_program_data_path()
#     file_path = os.path.join(data_path, file_name)

#     with open(file_path, "r", encoding='utf-8') as f:
#         return json.load(f)

# # Example usage
# survey_data = load_survey("vfx.json")
# print(survey_data)


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
