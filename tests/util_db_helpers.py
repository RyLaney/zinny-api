# tests/test_db_helpers.py

import json

# titles

def add_title_test_data(conn, title_data):
    """Insert a single title into the test database."""
    conn.execute(
        """
        INSERT INTO titles (imdb_title_id, name, type, year)
        VALUES (?, ?, ?, ?);
        """,
        (
            title_data.get("tconst"),  # Use "tconst" for IMDb-style data
            title_data.get("name") or title_data.get("primaryTitle"),
            title_data.get("type") or title_data.get("titleType", "movie"),
            title_data.get("year") or title_data.get("startYear")
        )
    )

def add_titles_test_data(conn, titles):
    """Insert multiple titles into the test database."""
    for title in titles:
        add_title_test_data(conn, title)

# surveys

def add_survey_test_data(conn, survey_data):
    """Insert a single survey into the test database."""
    # id, name and criteria are required fields
    # make sure to set defaults and extends to None if they are not provided



    conn.execute(
        """
        INSERT INTO surveys (id, name, version, description, extends, defaults, criteria)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        (
            survey_data.get("id"),
            survey_data.get("name"),
            survey_data.get("version"),
            survey_data.get("description"),
            survey_data.get("extends"),
            json.dumps(survey_data.get("defaults", {})),
            json.dumps(survey_data.get("criteria", [])),
        )
    )


def add_surveys_test_data(conn, surveys):
    """Insert multiple surveys into the test database."""
    for survey in surveys:
        add_survey_test_data(conn, survey)


# weights

def add_weight_test_data(conn, weight_data):
    """Insert a single weight preset into the test database."""
    conn.execute(
        """
        INSERT INTO weight_presets (name, description, survey_id, weights)
        VALUES (?, ?, ?, ?);
        """,
        (
            weight_data.get("name"),
            weight_data.get("description"),
            weight_data.get("survey_id"),
            json.dumps(weight_data.get("criteria_weights", {})),
        )
    )

def add_weights_test_data(conn, weights):
    """Insert multiple weight presets into the test database."""
    for weight in weights:
        add_weight_test_data(conn, weight)


# ratings

def add_rating_test_data(conn, rating_data):
    """Insert a single rating into the test database."""
    conn.execute(
        """
        INSERT INTO ratings (title_id, survey_id, ratings, comments)
        VALUES (?, ?, ?, ?);
        """,
        (
            rating_data.get("title_id"),
            rating_data.get("survey_id"),
            json.dumps(rating_data.get("ratings",{})),
            rating_data.get("comments")
        )
    )

def add_ratings_test_data(conn, ratings):
    """Insert multiple ratings into the test database."""
    for rating in ratings:
        add_rating_test_data(conn, rating)


# collections

def add_collection_test_data(conn, collection_data):
    """Insert a single collection and its titles into the database."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO collections (name, description) VALUES (?, ?);",
        (collection_data["name"], collection_data.get("description", ""))
    )
    collection_id = cursor.lastrowid

    for item in collection_data["items"]:
        cursor.execute(
            "INSERT INTO titles (name, year) VALUES (?, ?) ON CONFLICT(name, year) DO NOTHING;",
            (item.get("name"), item.get("year"))
        )
        cursor.execute(
            """
            INSERT INTO collection_titles (collection_id, title_id)
            SELECT ?, id FROM titles WHERE name = ? AND year = ?;
            """,
            (collection_id, item.get("name"), item.get("year"))
        )
    conn.commit()

def add_collections_test_data(conn, collections):
    """Insert multiple collections into the database."""
    for collection in collections:
        add_collection_test_data(conn, collection)

# title_types

def add_title_types_test_data(conn, title_types):
    """Insert multiple title types into the database."""
    for title_type in title_types:
        conn.execute(
            """
            INSERT INTO title_types (type, display_name)
            VALUES (?, ?);
            """,
            (title_type.get("type"), title_type.get("display_name"))
        )

# screen_types

def add_screen_types_test_data(conn, screen_types):
    """Insert multiple screen types into the database."""
    for screen_type in screen_types:
        conn.execute(
            """
            INSERT INTO screen_types (type, display_name)
            VALUES (?, ?);
            """,
            (screen_type.get("type"), screen_type.get("display_name"))
        )
