"""functions for importing data from files into the database."""

import os
import json
# from .common import scrub_string


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
        "criteria": json.dumps(survey.get("criteria", [])),
        "defaults": json.dumps(survey.get("defaults", {})),
        "extends": survey.get("extends")  # Can be None
    }

    try:
        cursor.execute(
            """
            INSERT INTO surveys (id, name, version, description, criteria, defaults, extends)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                version = excluded.version,
                description = excluded.description,
                criteria = excluded.criteria,
                defaults = excluded.defaults,
                extends = excluded.extends;
            """,
            (
                survey["id"],
                survey["name"],
                survey["version"],
                survey["description"],
                survey["criteria"],
                survey["defaults"],
                survey["extends"]
            )
        )
    except Exception as e:
        print(e)
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
            with open(file_path, "r", encoding="utf-8") as file_stream:
                result = process_survey_file(cursor, file_stream)
                results.append(result)

    conn.commit()
    return {"message": "Surveys loaded", "results": results}
