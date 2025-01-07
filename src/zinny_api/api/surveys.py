"""surveys endpoints"""

import json
from flask import Blueprint
from flask import jsonify, request
from zinny_api.db.db_init import get_connection
from zinny_api.utils.import_helpers import load_surveys_from_dir, process_survey_file
from zinny_api.db.db_init import get_records

surveys_bp = Blueprint('api/v1/surveys', __name__)


def expand_survey(survey_id):
    """
    Recursively expand a survey by merging attributes from its parent (if any).
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM surveys WHERE id = ?;", (survey_id,))
    survey = cursor.fetchone()
    if not survey:
        conn.close()
        return None  # Return None for not-found case, allowing caller to handle it

    survey = dict(survey)
    survey["criteria"] = json.loads(survey["criteria"])
    survey["defaults"] = json.loads(survey["defaults"]) if survey["defaults"] else {}

    parent_id = survey.get("extends")
    if parent_id:
        parent_survey = expand_survey(parent_id)
        if not parent_survey:  
            # here the None return in the parent survey and so we throw to send a 500
            conn.close()
            raise ValueError(f"Parent survey with ID '{parent_id}' not found.")

        # else: found parent survey
        # Merge parent defaults and criteria into the current survey
        survey["defaults"] = {**parent_survey["defaults"], **survey["defaults"]}
        parent_criteria_ids = {c["id"] for c in parent_survey["criteria"]}
        survey["criteria"] = [
            c for c in survey["criteria"] if c["id"] not in parent_criteria_ids
        ] + parent_survey["criteria"]

    conn.close()
    return survey


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
    expanded = request.args.get("expanded", "false").lower() == "true"

    surveys = get_records("surveys")
    if expanded:
        surveys = [expand_survey(s["id"]) for s in surveys]

    return jsonify(surveys or [])


@surveys_bp.route('/<survey_id>', methods=['GET'])
def get_survey(survey_id):
    """Retrieve a specific survey."""
    expanded = request.args.get("expanded", "true").lower() == "true"

    if expanded:
        try:
            survey = expand_survey(survey_id)
            if not survey:
                return jsonify({"error": "Survey not found"}), 404
            return jsonify(survey)
        except ValueError as e:
            # Handle missing parent surveys
            return jsonify({"error": str(e)}), 500

    # else:  # not expanded
    surveys = get_records("surveys", conditions="id = ?", condition_values=(survey_id,))
    if not surveys:
        return jsonify({"error": "Survey not found"}), 404

    survey = surveys[0]

    # Parse the JSON fields
    if survey.get("criteria"):
        survey["criteria"] = json.loads(survey["criteria"])
    if survey.get("defaults"):
        survey["defaults"] = json.loads(survey["defaults"])

    return jsonify(survey)


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

    # Execute the query
    cursor.execute(base_query, params)
    surveys = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({
        "page": page,
        "limit": limit,
        "results": surveys
    })
