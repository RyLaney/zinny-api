"""ratings endpoints"""

import json
import sqlite3
from flask import Blueprint
from flask import jsonify, request
from zinny_api.db.db_init import get_connection


ratings_bp = Blueprint('api/v1/ratings', __name__)


# Custom error handler for the blueprint
@ratings_bp.errorhandler(Exception)
def handle_exception(e):
    """Return JSON for any uncaught exception."""
    response = {
        "error": str(e)
    }
    return jsonify(response), 500



@ratings_bp.route('/', methods=['GET'])
def get_ratings():
    """
    Retrieve ratings.
    - Without query parameters: Return all ratings.
    - With `title_id` and `survey_id`: Return a specific rating.
    """
    title_id = request.args.get("title_id")
    survey_id = request.args.get("survey_id")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        if title_id and survey_id:
            # Fetch a specific rating by title_id and survey_id
            cursor.execute(
                """
                SELECT * FROM ratings
                WHERE title_id = ? AND survey_id = ?;
                """,
                (title_id, survey_id)
            )
            rating = cursor.fetchone()
            if rating:
                ratings_dict = dict(rating)
                ratings_dict["ratings"] = json.loads(ratings_dict["ratings"])
                print(ratings_dict)

                return jsonify(dict(ratings_dict))
            else:
                # return jsonify({"error": "Rating not found"}), 404
                return jsonify({}), 200

        # else: Fetch all ratings
        cursor.execute("SELECT * FROM ratings;")
        ratings = [dict(row) for row in cursor.fetchall()]
        for rating in ratings:
            rating["ratings"] = json.loads(rating["ratings"])
            print(rating)

        return jsonify(ratings)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()


@ratings_bp.route('/<int:rating_id>', methods=['GET'])
def get_rating(rating_id):
    """Retrieve a specific rating by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM ratings WHERE id = ?;", (rating_id,))
        rating = cursor.fetchone()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

    if rating:
        rating_dict = dict(rating)
        rating_dict["ratings"] = json.loads(rating_dict["ratings"])
        return jsonify(rating_dict)
    # else:
    return jsonify({"error": "Rating not found"}), 404


@ratings_bp.route("/", methods=["POST"])
def save_rating():
    """Save a rating for a title."""
    data = request.get_json()

    title_id = data.get("title_id")
    survey_id = data.get("survey_id")
    ratings = json.dumps(data.get("ratings"))
    comments = data.get("comments", "")
    screen_type_id = data.get("screen_type_id", None)
    screen_type = data.get("screen_type", None)
    conn = get_connection()
    cursor = conn.cursor()

    if not screen_type_id and screen_type:
        # lookup screen_type_id from screen_type
        cursor.execute("SELECT id FROM screen_types WHERE type = ?;", (screen_type,))
        screen_type_id_row_object = cursor.fetchone()
        if not screen_type_id_row_object:
            return jsonify({"error": "Invalid 'screen_type'."}), 400
        screen_type_id = screen_type_id_row_object[0]

    elif screen_type_id and not screen_type:
        # lookup screen_type from screen_type_id
        cursor.execute("SELECT type FROM screen_types WHERE id = ?;", (screen_type_id,))
        screen_type = cursor.fetchone()
        if not screen_type:
            return jsonify({"error": "Invalid 'screen_type_id'."}), 400

    if not title_id or not survey_id or not ratings:
        message = "Missing required fields."
        message += f" title_id: {title_id}, survey_id: {survey_id}, ratings: {ratings}"
        return jsonify({"error": message}), 400

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO ratings (title_id, survey_id, screen_type_id, ratings, comments)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(title_id, survey_id) DO UPDATE SET
                screen_type_id = excluded.screen_type_id,
                ratings = excluded.ratings,
                comments = excluded.comments;
            """,
            (title_id, survey_id, screen_type_id, ratings, comments)
        )
        conn.commit()

        # Fetch the ID of the affected record
        cursor.execute(
            """
            SELECT id FROM ratings
            WHERE title_id = ? AND survey_id = ?;
            """,
            (title_id, survey_id)
        )
        rating_id = cursor.fetchone()[0]
             
    except sqlite3.IntegrityError as e:
        return {"error": f"Failed to save rating: {str(e)}"}, 500
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 500
    finally:
        conn.close()

    return jsonify({"message": "Rating saved successfully.", "rating_id": rating_id}), 201


@ratings_bp.route('/<int:rating_id>', methods=['PUT'])
def update_rating(rating_id):
    """Update an existing rating."""
    data = request.get_json()
    print(data)
    if not data or not data.get("ratings"):
        return jsonify({"error": "Missing required field: ratings."}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM ratings WHERE id = ?;", (rating_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Rating not found"}), 404

        cursor.execute(
            """
            UPDATE ratings
            SET ratings = ?, comments = ?
            WHERE id = ?;
            """,
            (
                data["ratings"],
                data.get("comments", ""),
                rating_id
            )
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

    return jsonify({"message": "Rating updated successfully"})


@ratings_bp.route('/<int:rating_id>', methods=['DELETE'])
def delete_rating(rating_id):
    """Delete a rating."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM ratings WHERE id = ?;", (rating_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Rating not found"}), 404
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

    return jsonify({"message": "Rating deleted successfully"})


@ratings_bp.route('/export', methods=['GET'])
def export_ratings():
    """Export all ratings as JSON."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 
            t.name AS title_name,
            t.year AS title_year,
            s.name AS survey_name, 
            r.survey_id,
            r.ratings,
            r.comments
        FROM ratings r
        INNER JOIN titles t ON r.title_id = t.id
        INNER JOIN surveys s ON r.survey_id = s.id
        """
    )
    ratings = [
        {
            "title_name": row["title_name"],
            "title_year": row["title_year"],
            "survey_name": row["survey_name"],
            "survey_id": row["survey_id"],
            "ratings": json.loads(row["ratings"]),
            "comments": row["comments"]
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return jsonify(ratings)
