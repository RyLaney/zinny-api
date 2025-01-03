"""title_types endpoints"""

from flask import Blueprint, jsonify, request
from zinny_api.db.db_init import get_connection
from zinny_api.utils.import_helpers import load_title_types_from_dir

from zinny_api.db.db_init import get_records


# pylint: disable=missing-function-docstring,line-too-long

title_types_bp = Blueprint('api/v1/title-types', __name__)


@title_types_bp.route('/', methods=['GET'])
def get_title_types():
    """Retrieve a list of all available title_types."""
    title_types = get_records("title_types", order_by="type")
    return jsonify(title_types or [])


@title_types_bp.route('/', methods=['POST'])
def add_title_types():
    """Add a new title_types."""
    title_type_data = request.get_json() or request.form
    if not title_type_data or not isinstance(title_type_data, dict):
        raise ValueError("Invalid title_type data format. Expected a JSON object.")

    if not title_type_data.get("type") or not title_type_data.get("display_name"):
        return jsonify({"error": "title_types 'type' and 'display_name' are required."}), 400

    title_type_item = {
        "type": title_type_data.get("type"),
        "display_name": title_type_data.get("display_name"),
    }

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO title_types (type, display_name)
        VALUES (?, ?)
        ON CONFLICT(type) DO UPDATE SET
            type = excluded.type,
            display_name = excluded.display_name
        """,
        (
            title_type_item["type"],
            title_type_item["display_name"],
        )
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "title_type_item added successfully.", "title_type_item": title_type_item})


@title_types_bp.route('/<title_type>', methods=['GET'])
def get_title_type(title_type):
    """Retrieve a specific title_type preset."""
    title_types = get_records("title_types", conditions="type = ?", condition_values=(title_type,), order_by="type")
    if not title_types:
        return jsonify({"error": "title_types not found"}), 404
    return jsonify(title_types[0])


@title_types_bp.route('/load', methods=['POST'])
def load_title_types():
    """Load all title_types from the data/title_types directory."""
    print("Loading title_types...")
    conn = get_connection()
    load_title_types_from_dir(conn)
    conn.close()
    return jsonify({"message": "title_types loaded successfully."})
