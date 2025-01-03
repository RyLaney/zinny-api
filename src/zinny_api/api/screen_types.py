"""screen_types endpoints"""

from flask import Blueprint, jsonify, request
from zinny_api.db.db_init import get_connection
# from zinny_api.utils.import_helpers import load_screen_types_from_dir

from zinny_api.db.db_init import get_records


# pylint: disable=missing-function-docstring,line-too-long

screen_types_bp = Blueprint('api/v1/screen-types', __name__)


@screen_types_bp.route('/', methods=['GET'])
def get_screen_types():
    """Retrieve a list of all available screen_types."""
    screen_types = get_records("screen_types", order_by="type")
    return jsonify(screen_types or [])


@screen_types_bp.route('/', methods=['POST'])
def add_screen_types():
    """Add a new screen_types."""
    screen_type_data = request.get_json() or request.form
    if not screen_type_data or not isinstance(screen_type_data, dict):
        raise ValueError("Invalid screen_type data format. Expected a JSON object.")

    if not screen_type_data.get("type") or not screen_type_data.get("display_name"):
        return jsonify({"error": "screen_types 'type' and 'display_name' are required."}), 400

    screen_type_item = {
        "type": screen_type_data.get("type"),
        "display_name": screen_type_data.get("display_name"),
        "description": screen_type_data.get("description"),
    }

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO screen_types (type, display_name, description)
        VALUES (?, ?, ?)
        ON CONFLICT(type) DO UPDATE SET
            type = excluded.type,
            display_name = excluded.display_name,
            description = excluded.description;
        """,
        (
            screen_type_item["type"],
            screen_type_item["display_name"],
            screen_type_item["description"]
        )
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "screen_type_item added successfully.", "screen_type_item": screen_type_item})


@screen_types_bp.route('/<screen_type>', methods=['GET'])
def get_screen_type(screen_type):
    """Retrieve a specific screen_type preset."""
    screen_types = get_records("screen_types", conditions="type = ?", condition_values=(screen_type,), order_by="type")
    if not screen_types:
        return jsonify({"error": "screen_types not found"}), 404
    return jsonify(screen_types[0])


# @screen_types_bp.route('/load', methods=['POST'])
# def load_screen_types():
#     """Load all screen_types from the data/screen_types directory."""
#     print("Loading screen_types...")
#     conn = get_connection()
#     load_screen_types_from_dir(conn)
#     conn.close()
#     return jsonify({"message": "screen_types loaded successfully."})
