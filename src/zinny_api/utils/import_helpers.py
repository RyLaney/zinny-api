"""functions for importing data from files into the database."""

import os
import json
import csv
import re

def scrub_string(value):
    """Scrub a string to remove special characters and convert to lowercase."""
    if not value:
        return ""

    scrubbed = re.sub(r"\s+", "_", value)
    scrubbed = re.sub(r"[^a-zA-Z0-9_-]", "", scrubbed)
    return scrubbed.lower()


# Titles ########################################################

def process_title_file(cursor, file_stream, collection_name):
    """
    Parse and insert titles from a file stream into the database.

    Args:
        cursor: SQLite cursor for database operations.
        file_stream: File-like object containing CSV/TSV title data.
        collection_name: Name of the collection to associate titles with.

    Returns:
        Tuple: (message: dict, status_code: int)
    """
    try:
        # Detect delimiter based on the file name
        delimiter = "\t" if file_stream.name.endswith(".tsv") else ","
        reader = csv.DictReader(file_stream, delimiter=delimiter)

        # Ensure the collection exists
        cursor.execute(
            """
            INSERT OR IGNORE INTO collections (name, description)
            VALUES (?, ?);
            """,
            (collection_name, "Imported from user upload")
        )
        cursor.execute("SELECT id FROM collections WHERE name = ?;", (collection_name,))
        collection_id = cursor.fetchone()["id"]

        # Process each row in the file
        for row in reader:
            title_name = row.get("name") or row.get("primaryTitle")
            title_year = row.get("year") or row.get("startYear")
            title_type = row.get("type") or row.get("titleType")
            imdb_title_id = row.get("imdb_title_id") or row.get("tconst")

            if not title_name:
                continue  # Skip rows without a title

            # Check for existing title
            cursor.execute(
                """
                SELECT id FROM titles WHERE imdb_title_id = ? 
                    OR (name = ? AND year = ? AND type = ?);
                """,
                (imdb_title_id, title_name, title_year, title_type)
            )
            existing_title = cursor.fetchone()

            if existing_title:
                title_id = existing_title["id"]
            else:
                # Insert a new title
                cursor.execute(
                    """
                    INSERT INTO titles (imdb_title_id, name, type, year)
                    VALUES (?, ?, ?, ?);
                    """,
                    (imdb_title_id, title_name, title_type, title_year)
                )
                title_id = cursor.lastrowid

            # Link title to the collection
            cursor.execute(
                """
                INSERT OR IGNORE INTO collection_titles (title_id, collection_id)
                VALUES (?, ?);
                """,
                (title_id, collection_id)
            )

        return {"message": "Titles processed successfully", "collection_name": collection_name}, 200
    except Exception as e:
        return {"error": f"Error processing titles: {e}"}, 500

def load_titles_from_dir(conn, directory="data/titles/local"):
    """
    Load titles from CSV/TSV files in the specified directory.

    Args:
        conn: SQLite connection object.
        directory: Directory containing title files.

    Returns:
        dict: Summary message.
    """
    if not os.path.exists(directory):
        return {"error": f"Titles directory not found: {directory}"}, 404

    cursor = conn.cursor()
    results = []
    for file_name in os.listdir(directory):
        if file_name.endswith((".tsv", ".csv")):
            file_path = os.path.join(directory, file_name)
            collection_name = scrub_string(os.path.splitext(file_name)[0])
            # print(f"Processing file: {file_path}")

            with open(file_path, "r", encoding="utf-8") as file_stream:
                result = process_title_file(cursor, file_stream, collection_name)
                results.append(result)

    conn.commit()
    return {"message": "Titles loaded successfully", "results": results}


# Surveys ########################################################

def process_survey_file(cursor, file_stream):
    """Parse and insert a survey file into the database."""
    try:
        # Reset file stream to the beginning
        file_stream.seek(0)
        survey = json.load(file_stream)
        if not isinstance(survey, dict):
            raise ValueError("Invalid survey format. Expected a JSON object.")
    except (json.JSONDecodeError, ValueError) as e:
        return {"error": "Invalid JSON format.", "message": f"{e}"}, 400

    # Set up default values for missing fields
    survey = {
        "id": survey.get("id"),
        "name": survey.get("name", "Unnamed Survey"),
        "version": survey.get("version", "0.1"),
        "description": survey.get("description", ""),
        "criteria": json.dumps(survey.get("criteria", []))
    }

    try:
        cursor.execute(
            """
            INSERT INTO surveys (id, name, version, description, criteria)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                version = excluded.version,
                description = excluded.description,
                criteria = excluded.criteria;
            """,
            (
                survey["id"],
                survey["name"],
                survey["version"],
                survey["description"],
                survey["criteria"]
            )
        )
    except Exception as e:
        return {"error": f"Error inserting survey into database: {e}"}, 500

    return {"message": "Survey processed successfully", "survey_id": survey["id"]}, 200


def load_surveys_from_dir(conn, directory="data/surveys"):
    """Load surveys from JSON files in the specified directory."""
    if not os.path.exists(directory):
        return {"error": f"Directory not found: {directory}"}, 404

    cursor = conn.cursor()
    results = []
    for file_name in os.listdir(directory):
        if file_name.endswith(".json"):
            file_path = os.path.join(directory, file_name)
            # print(f"Processing survey file: {file_path}")
            with open(file_path, "r", encoding="utf-8") as file_stream:
                result = process_survey_file(cursor, file_stream)
                results.append(result)

    conn.commit()
    return {"message": "Surveys loaded", "results": results}


# Weight Presets ########################################################

def process_weight_preset_file(cursor, file_stream):
    """Parse and insert a weight_preset file into the database."""
    try:
        # Reset file stream to the beginning
        file_stream.seek(0)
        preset_data = json.load(file_stream)
        if not isinstance(preset_data, dict):
            raise ValueError("Invalid weights_preset format. Expected a JSON object.")
    except (json.JSONDecodeError, ValueError) as e:
        return {"error": "Invalid JSON format.", "message": f"{e}"}, 400

    # Set up default values for missing fields
    weight_preset = {
        "name": preset_data.get("name", "Unnamed Weight Preset"),
        "description": preset_data.get("description", ""),
        "survey_id": preset_data.get("survey_id"),
        "weights": json.dumps(preset_data.get("criteria_weights", []))
    }

    try:
        cursor.execute(
            """
            INSERT INTO weight_presets (name, description, survey_id, weights)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                description = excluded.description,
                survey_id = excluded.survey_id,
                weights = excluded.weights;
            """,
            (
                weight_preset["name"],
                weight_preset["description"],
                weight_preset["survey_id"],
                weight_preset["weights"]
            )
        )

    except Exception as e:
        return {"error": f"Error inserting weight_preset into database: {e}"}, 500

    return {
        "message": "Weight Preset processed successfully",
        "weight_preset": weight_preset
        }, 200


def load_weight_presets_from_dir(conn, directory="data/weight_presets"):
    """Load weight_presets from JSON files in the specified directory."""
    if not os.path.exists(directory):
        return {"error": f"Directory not found: {directory}"}, 404

    cursor = conn.cursor()
    results = []
    for file_name in os.listdir(directory):
        if file_name.endswith(".json"):
            file_path = os.path.join(directory, file_name)
            # print(f"Processing weight_preset file: {file_path}")
            with open(file_path, "r", encoding="utf-8") as file_stream:
                result = process_weight_preset_file(cursor, file_stream)
                results.append(result)

    conn.commit()
    return {"message": "Weight Presets loaded", "results": results}


# Title Types ########################################################

def process_title_type_file(cursor, file_stream):
    """Parse and insert a title_type file into the database."""
    # print("Processing title_type stream")

    try:
        # Reset file stream to the beginning
        file_stream.seek(0)
        title_types_data = json.load(file_stream)
        if not isinstance(title_types_data, list):
            raise ValueError("Invalid title_type format. Expected a JSON object.")

    except (json.JSONDecodeError, ValueError) as e:
        return {"error": "Invalid JSON format.", "message": f"{e}"}, 400

    try:
        for title_type in title_types_data:
            cursor.execute(
                """
                INSERT INTO title_types (type, display_name)
                VALUES (?, ?)
                ON CONFLICT(type) DO UPDATE SET
                    type = excluded.type,
                    display_name = excluded.display_name
                """,
                (
                    title_type["type"],
                    title_type["display_name"]
                )
            )

    except Exception as e:
        return {"error": f"Error inserting title_type into database: {e}"}, 500

    return {
        "message": "Title Type processed successfully",
        }, 200


def load_title_types_from_dir(conn, directory="data/title_types"):
    """Load title_types from JSON files in the specified directory."""
    if not os.path.exists(directory):
        return {"error": f"Directory not found: {directory}"}, 404

    cursor = conn.cursor()
    results = []
    for file_name in os.listdir(directory):
        if file_name.endswith(".json"):
            file_path = os.path.join(directory, file_name)
            # print(f"Loading title_type file: {file_path}")
            with open(file_path, "r", encoding="utf-8") as file_stream:
                result = process_title_type_file(cursor, file_stream)
                results.append(result)

    conn.commit()
    return {"message": "Title Type loaded", "results": results}
