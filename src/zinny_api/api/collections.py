"""collections endpoints"""

# import os
import json

from flask import Blueprint, jsonify, request
from zinny_api.db.db_init import get_records
from zinny_api.db.db_init import get_connection
from zinny_api.utils.import_helpers import scrub_string


# pylint: disable=line-too-long

collections_bp = Blueprint("collections", __name__)


@collections_bp.route("/", methods=["POST"])
def create_collection():
    """Create a new collection."""
    data = request.get_json()
    name = data.get("name")
    description = data.get("description", "")

    if not name:
        return jsonify({"error": "Collection name is required."}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO collections (name, description) VALUES (?, ?);",
            (name, description)
        )
        conn.commit()
        collection_id = cursor.lastrowid
    finally:
        conn.close()

    return jsonify({"message": "Collection created successfully.", "collection_id": collection_id}), 201


@collections_bp.route("/<int:collection_id>", methods=["DELETE"])
def delete_collection(collection_id):
    """Delete a collection."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM collections WHERE id = ?;", (collection_id,))
        conn.commit()
    finally:
        conn.close()

    return jsonify({"message": "Collection deleted successfully."})


@collections_bp.route("/", methods=["GET"])
def get_collections():
    """Get all collections."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM collections;")
    collections = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(collections or [])


@collections_bp.route('/<int:collection_id>', methods=['GET'])
def get_weight_preset(collection_id):
    """Retrieve a specific weight preset."""
    collections = get_records("collections", conditions="id = ?", condition_values=(collection_id,))
    if not collections:
        return jsonify({"error": "Collection not found"}), 404
    return jsonify(collections[0])


@collections_bp.route("/<int:collection_id>/titles", methods=["GET"])
def get_titles_in_collection(collection_id):
    """Get titles in a collection."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT t.id, t.name, t.year
        FROM collection_titles ct
        INNER JOIN titles t ON ct.title_id = t.id
        WHERE ct.collection_id = ?;
        """,
        (collection_id,)
    )
    titles = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(titles)


@collections_bp.route("/<int:collection_id>/titles", methods=["POST"])
def add_titles_to_collection(collection_id):
    """Add titles to a collection."""
    data = request.get_json()
    title_ids = data.get("title_ids", [])

    if not title_ids:
        return jsonify({"error": "No title IDs provided."}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        for title_id in title_ids:
            cursor.execute(
                "INSERT OR IGNORE INTO collection_titles (collection_id, title_id) VALUES (?, ?);",
                (collection_id, title_id)
            )
        conn.commit()
    finally:
        conn.close()

    return jsonify({"message": "Titles added to collection successfully."})


@collections_bp.route("/<int:collection_id>/titles", methods=["DELETE"])
def remove_titles_from_collection(collection_id):
    """Remove titles from a collection."""
    data = request.get_json()
    title_ids = data.get("title_ids", [])

    if not title_ids:
        return jsonify({"error": "No title IDs provided."}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.executemany(
            "DELETE FROM collection_titles WHERE collection_id = ? AND title_id = ?;",
            [(collection_id, title_id) for title_id in title_ids]
        )
        conn.commit()
    finally:
        conn.close()

    return jsonify({"message": "Titles removed from collection successfully."})


@collections_bp.route('/import', methods=['POST'])
def import_collection():
    """Import a collection from a JSON file."""
    file = request.files.get('file')
    if not file or not file.filename.endswith(".json"):
        return jsonify({"error": "Invalid file provided. Must be a .json file."}), 400

    try:
        collection_data = json.load(file.stream)
        collection_id = collection_data.get("id")
        collection_name = collection_data.get("name")
        collection_description = collection_data.get("description", "")
        items = collection_data.get("items", [])

        if not collection_id or not collection_name:
            return jsonify({"error": "Invalid collection data. Missing required fields."}), 400

        conn = get_connection()
        cursor = conn.cursor()

        # Insert collection into the database
        cursor.execute(
            "INSERT OR IGNORE INTO collections (id, name, description) VALUES (?, ?, ?);",
            (collection_id, collection_name, collection_description)
        )

        # Add items to the collection
        for item in items:
            title_name = item.get("name")
            title_year = item.get("year")
            if not title_name or not title_year:
                continue  # Skip invalid items

            # Ensure title exists in the titles table
            cursor.execute(
                "INSERT OR IGNORE INTO titles (name, year) VALUES (?, ?);",
                (title_name, title_year)
            )

            # Link title to the collection
            cursor.execute(
                """
                INSERT OR IGNORE INTO collection_titles (collection_id, title_id)
                SELECT ?, id FROM titles WHERE name = ? AND year = ?;
                """,
                (collection_id, title_name, title_year)
            )

        conn.commit()
        conn.close()
        # # ALSO Save the file to the local directory for collections
        # local_path = COLLECTION_PATHS["local"]
        # os.makedirs(local_path, exist_ok=True)
        flie_name = f"{scrub_string(collection_name)}.json"
        # file_path = os.path.join(local_path, flie_name)
        # with open(file_path, 'w', encoding="utf-8") as f:
        #     json.dump(collection_data, f, indent=4)
        
        return jsonify({"message": "Collection imported successfully", "collection": collection_data}), 200

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format."}), 400

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500





@collections_bp.route('/export', methods=['GET'])
def export_collections():
    """Export all collections as JSON."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM collections;")
    collections = cursor.fetchall()

    exported_data = []
    for collection in collections:
        cursor.execute(
            """
            SELECT t.name, t.year
            FROM collection_titles ct
            INNER JOIN titles t ON ct.title_id = t.id
            WHERE ct.collection_id = ?;
            """,
            (collection["id"],)
        )
        items = [dict(row) for row in cursor.fetchall()]
        exported_data.append({
            "id": collection["id"],
            "name": collection["name"],
            "description": collection["description"],
            "items": items
        })

    conn.close()
    return jsonify(exported_data)


@collections_bp.route('/export/<int:collection_id>', methods=['GET'])
def export_collection(collection_id):
    """Export a single collection as JSON."""
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch collection details
    cursor.execute("SELECT * FROM collections WHERE id = ?;", (collection_id,))
    collection = cursor.fetchone()
    if not collection:
        conn.close()
        return jsonify({"error": "Collection not found"}), 404

    # Fetch collection items
    cursor.execute(
        """
        SELECT t.name, t.year
        FROM collection_titles ct
        INNER JOIN titles t ON ct.title_id = t.id
        WHERE ct.collection_id = ?;
        """,
        (collection_id,)
    )
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({
        "id": collection["id"],
        "name": collection["name"],
        "description": collection["description"],
        "items": items
    })
