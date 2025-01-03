"""surveys endpoints"""

from flask import Blueprint
from flask import jsonify, request
from zinny_api.db.db_init import get_connection
from zinny_api.utils.import_helpers import load_surveys_from_dir, process_survey_file
from zinny_api.db.db_init import get_records


surveys_bp = Blueprint('api/v1/surveys', __name__)


# Custom error handler for the blueprint
@surveys_bp.errorhandler(Exception)
def handle_exception(e):
    """Return JSON for any uncaught exception."""
    response = {
        "error": str(e)
    }
    return jsonify(response), 500


@surveys_bp.route('/', methods=['GET'])
def get_surveys():
    """Retrieve a list of all available surveys."""
    surveys = get_records("surveys")
    return jsonify(surveys or [])


@surveys_bp.route('/<survey_id>', methods=['GET'])
def get_survey(survey_id):
    """Retrieve a specific survey."""
    surveys = get_records("surveys", conditions="id = ?", condition_values=(survey_id,))
    if not surveys:
        return jsonify({"error": "Survey not found"}), 404
    return jsonify(surveys[0])


@surveys_bp.route('/import', methods=['POST'])
def import_survey():
    """Import a single survey from a user-uploaded file."""
    file = request.files.get('file')
    if not file or not file.filename.endswith(".json"):
        return jsonify({"error": "Invalid file. Must be a .json file."}), 400

    conn = get_connection()
    cursor = conn.cursor()

    # Process the uploaded file
    message, status_code = process_survey_file(cursor, file.stream)
    conn.commit()
    conn.close()

    return jsonify(message), status_code


@surveys_bp.route("/load", methods=["POST"])
def load_surveys():
    """Import all surveys from the data/surveys directory."""
    conn = get_connection()
    load_surveys_from_dir(conn)
    conn.close()
    return jsonify({"message": "Surveys loaded successfully."})

@surveys_bp.route('/search', methods=['GET'])
def search_surveys():
    """
    Search surveys by query, with pagination support.

    Query Parameters:
        - query: Search query for the survey name (case-insensitive).
        - page: Page number for pagination (default: 1).
        - limit: Number of results per page (default: None).
    """
    query = request.args.get("query", "").lower()
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=None, type=int)

    conn = get_connection()
    cursor = conn.cursor()

    # Build the base SQL query
    base_query = """
        SELECT survey.id, survey.name, survey.description
        FROM surveys survey
    """
    where_clauses = []
    params = []

    # Add filters based on query parameters
    if query:
        where_clauses.append("LOWER(survey.name) LIKE ?")
        params.append(f"%{query}%")

    # Combine filters into WHERE clause
    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)


    # Add sorting and pagination
    if limit is None:
        base_query += " ORDER BY survey.name DESC"
    else:
        base_query += " ORDER BY survey.name DESC LIMIT ? OFFSET ?"
        params.extend([limit, (page - 1) * limit])
    
    print(base_query)
    print(params)

    # Execute the query
    cursor.execute(base_query, params)
    surveys = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({
        "page": page,
        "limit": limit,
        "results": surveys
    })
