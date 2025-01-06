"""Database init and utils."""

import sqlite3
import os
import importlib
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


def get_system_data_paths(create_udp=True, create_pdp=False):
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

    return {"udp": udp, "pdp": pdp}

def get_userdata_path():
    udp = get_system_data_paths(create_udp=True, create_pdp=False)["udp"]
    return udp

def get_progdata_path():
    pdp = get_system_data_paths(create_udp=False, create_pdp=True)["pdp"]
    return pdp

def get_database_path():
    """Determine the zinny_apiropriate database path based on the platform."""

    userdata_path = get_userdata_path()
    zinny_api_dir = os.path.join(userdata_path, 'db')
    os.makedirs(zinny_api_dir, exist_ok=True)

    return os.path.join(zinny_api_dir, 'zinny-1.0.sqlite')

def get_resource_paths(package, data_type, scopes=None):
    if scopes is None:
        scopes = ['shared', 'local']

    package_root = importlib.resources.files(package)
    if not os.path.exists(package_root):
        return None
    paths = {}
    for scope in scopes:
        paths[scope] = package_root.joinpath('data', data_type, scope)
    return paths

# /opt/conda/miniconda3/envs/zinny-dev/lib/python3.11/site-packages/zinny_surveys/data/surveys/shared
# /opt/conda/miniconda3/envs/zinny-dev/lib/python3.11/site-packages/zinny_surveys/data/surveys/shared'

DATABASE_PATH = get_database_path()
SURVEYS_PATHS = get_resource_paths('zinny_surveys', 'surveys')
WEIGHTS_PATHS = get_resource_paths('zinny_surveys', 'weights')
TITLES_PATHS = get_resource_paths('zinny_api', 'titles')

# TODO: use proj_data_path for surveys in import_helpers.py
# def load_survey(file_name):
#     import json
#     data_path = get_progdata_path()
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
                load_surveys_from_dir(conn, directory=SURVEYS_PATHS[data_scope])
                load_weight_presets_from_dir(conn, directory=WEIGHTS_PATHS[data_scope])
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
