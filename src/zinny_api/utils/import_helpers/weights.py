"""functions for importing data from files into the database."""

import os
import json

# from .common import scrub_string


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
