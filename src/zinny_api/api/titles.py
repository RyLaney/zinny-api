"""titles endpoints"""

from flask import Blueprint, jsonify, request
from zinny_api.db.db_init import get_connection
from zinny_api.utils.import_helpers import load_titles_from_dir

# pylint: disable=line-too-long

titles_bp = Blueprint('api/v1/titles', __name__)


@titles_bp.route('/', methods=['GET'])
def get_titles():
    """Retrieve a list of all titles."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM titles;")
    titles = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(titles)


@titles_bp.route('/', methods=['POST'])
def add_title():
    """Add a new title."""
    data = request.get_json() or request.form
    if not data or not data.get("name"):
        return jsonify({"error": "Title is required."}), 400

    imdb_title_id = data.get("imdb_title_id")
    title_name = data["name"]
    title_year = data.get("year")
    title_type = data.get("type")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id FROM titles 
        WHERE name = ? AND (year = ? OR year IS NULL);
        """,
        (title_name, title_year)
    )
    existing = cursor.fetchone()

    if existing:
        return jsonify({"error": "Duplicate title found."}), 400

    cursor.execute(
        """
        INSERT INTO titles (imdb_title_id, name, year, type)
        VALUES (?, ?, ?, ?);
        """,
        (imdb_title_id, title_name, title_year, title_type)
    )
    conn.commit()
    title_id = cursor.lastrowid
    conn.close()

    return jsonify({"message": "Title added successfully.", "title_id": title_id})


@titles_bp.route('/<int:title_id>', methods=['GET'])
def get_title(title_id):
    """Retrieve details of a specific title."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM titles WHERE id = ?;", (title_id,))
    title = cursor.fetchone()
    conn.close()
    if title:
        return jsonify(dict(title))
    return jsonify({"error": "Title not found"}), 404


@titles_bp.route('/import', methods=['POST'])
def import_titles():
    """Import titles from a CSV or TSV file."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if not file.filename.endswith(('.csv', '.tsv')):
        return jsonify({"error": "Invalid file format. Only CSV or TSV files are allowed."}), 400

    delimiter = ',' if file.filename.endswith('.csv') else '\t'
    has_headers = request.args.get('has_headers', 'true').lower() == 'true'
    imported_count = 0

    conn = get_connection()
    cursor = conn.cursor()
    columns = None
    try:
        first_line = True
        for line in file.stream:
            line = line.decode('utf-8').strip()

            # Skip header row if detected
            if first_line:
                if has_headers:
                    if "imdb_title_id" in line or "tconst" in line:  # Basic heuristic for headers
                        first_line = False
                        columns = line.split(delimiter)
                        continue
                else: # no_headers Assume default columns
                    columns = ["imdb_title_id", "type", "name", "year"]

            fields = line.split(delimiter)
            if len(fields) < 4:  # Ensure expected columns are present
                continue

            fields = dict(zip(columns, fields))
            imdb_title_id = fields.get("imdb_title_id") or fields.get("tconst")
            title_type = fields.get("type") or fields.get("titleType")
            title_name = fields.get("name")  or fields.get("primaryTitle")
            title_year = fields.get("year") or fields.get("startYear")


            try:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO titles (imdb_title_id, type, name, year)
                    VALUES (?, ?, ?, ?);
                    """,
                    (imdb_title_id, title_type, title_name, title_year)
                )
                imported_count += cursor.rowcount
            except Exception as e:  # pylint: disable=broad-except
                print(f"Failed to import row: {str(e)}")
                continue  # Skip problematic rows

        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Failed to import: {str(e)}"}), 500
    finally:
        conn.close()

    return jsonify({"message": f"{imported_count} titles imported successfully."}), 200


@titles_bp.route('/<int:title_id>', methods=['PUT'])
def update_title(title_id):
    """Update an existing title."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM titles WHERE id = ?;", (title_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Title not found"}), 404

    cursor.execute(
        """
        UPDATE titles
        SET type = ?, name = ?, year = ?
        WHERE id = ?;
        """,
        (
            data.get("type"),
            data.get("name"),
            data.get("year"),
            title_id
        )
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Title updated successfully"})

@titles_bp.route('/<int:title_id>', methods=['POST', 'DELETE'])
def delete_title(title_id):
    """Delete a title."""
    if request.method == 'POST' and request.form.get('_method') != 'DELETE':
        return jsonify({"error": "Invalid method override"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM titles WHERE id = ?;", (title_id,))
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "Title not found"}), 404

    conn.commit()
    conn.close()
    return jsonify({"message": "Title deleted successfully"})

@titles_bp.route('/search', methods=['GET'])
def search_titles():
    """
    Search titles by query, filter by year range, type, and survey, with pagination support.
    """
    query = request.args.get("query", "").lower()
    year_start = request.args.get("year_start", type=int)
    year_end = request.args.get("year_end", type=int)
    title_type = request.args.get("type")
    survey_id = request.args.get("survey_id")
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)

    conn = get_connection()
    cursor = conn.cursor()

    # Base query
    base_query = """
        SELECT DISTINCT t.id, t.name, t.year, t.type
        FROM titles t
        LEFT JOIN (
            SELECT DISTINCT title_id, survey_id FROM ratings
        ) r ON t.id = r.title_id
    """
    where_clauses = []
    params = []

    # Add filters
    if query:
        where_clauses.append("LOWER(t.name) LIKE ?")
        params.append(f"%{query}%")
    if year_start is not None:
        where_clauses.append("t.year >= ?")
        params.append(year_start)
    if year_end is not None:
        where_clauses.append("t.year <= ?")
        params.append(year_end)
    if title_type:
        where_clauses.append("t.type = ?")
        params.append(title_type)
    if survey_id:
        where_clauses.append("r.survey_id = ?")
        params.append(survey_id)

    # Combine WHERE clauses
    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    # Add sorting and pagination
    base_query += " ORDER BY t.year DESC LIMIT ? OFFSET ?"
    params.extend([limit, (page - 1) * limit])

    # Execute the query
    cursor.execute(base_query, params)
    titles = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({
        "page": page,
        "limit": limit,
        "results": titles
    })


@titles_bp.route("/load", methods=["POST"])
def load_titles():
    """Import all titles from the data/titles directory."""
    conn = get_connection()
    load_titles_from_dir(conn)
    conn.close()
    return jsonify({"message": "Titles loaded successfully."})


# @titles_bp.route('/import', methods=['POST'])
# def import_titles():
#     """Import titles from a TSV/CSV file."""
#     file = request.files.get('file')
#     if not file:
#         return jsonify({"error": "No file provided."}), 400

#     cursor = get_connection().cursor()
#     response = load_title_from_file(cursor, file.filename)
#     cursor.close()

#     return jsonify(response)
