"""functions for importing data from files into the database."""

import os
import json

# from .common import scrub_string


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
