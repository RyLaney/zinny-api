"""weights endpoints"""

import json
from flask import Blueprint, jsonify, request
from zinny_api.db.db_init import get_connection
from zinny_api.utils.import_helpers import (
    load_weight_presets_from_dir,
    process_weight_preset_file
)

from zinny_api.db.db_init import get_records


# pylint: disable=missing-function-docstring

weights_bp = Blueprint('api/v1/weights', __name__)


@weights_bp.route('/', methods=['GET'])
def get_weights():
    """Retrieve a list of all available weights."""
    weights = get_records("weight_presets")
    return jsonify(weights or [])


@weights_bp.route('/', methods=['POST'])
def add_weights():
    """Add a new weights."""
    preset_data = request.get_json() or request.form
    if not preset_data or not isinstance(preset_data, dict):
        raise ValueError("Invalid preset_data format. Expected a JSON object.")

    if not preset_data.get("name"):
        return jsonify({"error": "Weights Preset 'name' is required."}), 400

    weight_preset = {
        "name": preset_data.get("name", "Unnamed Weight Preset"),
        "description": preset_data.get("description", ""),
        "survey_id": preset_data.get("survey_id"),
        "weights": json.dumps(preset_data.get("criteria_weights", []))
    }

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO weight_presets (name, description, survey_id, weights)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
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
    conn.commit()
    weights_id = cursor.lastrowid
    conn.close()

    return jsonify({"message": "Weight presets added successfully.", "weights_id": weights_id})


@weights_bp.route('/<preset_id>', methods=['GET'])
def get_weight_preset(preset_id):
    """Retrieve a specific weight preset."""
    weights = get_records("weight_presets", conditions="id = ?", condition_values=(preset_id,))
    if not weights:
        return jsonify({"error": "Weights not found"}), 404
    return jsonify(weights[0])


@weights_bp.route('/import', methods=['POST'])
def import_weights_preset():
    """Import a single weight from a user-uploaded file."""
    file = request.files.get('file')
    if not file or not file.filename.endswith(".json"):
        return jsonify({"error": "Invalid file. Must be a .json file."}), 400

    conn = get_connection()
    cursor = conn.cursor()

    # Process the uploaded file
    message, status_code = process_weight_preset_file(cursor, file.stream)
    conn.commit()
    conn.close()

    return jsonify(message), status_code


@weights_bp.route('/load', methods=['POST'])
def load_weight_presets():
    """Load all weight presets from the data/weights directory."""
    print("Loading weight presets...")
    conn = get_connection()
    load_weight_presets_from_dir(conn)
    conn.close()
    return jsonify({"message": "Weight presets loaded successfully."})
