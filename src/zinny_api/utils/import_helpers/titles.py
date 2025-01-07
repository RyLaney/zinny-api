"""functions for importing data from files into the database."""

import os
import csv

from .common import scrub_string


# Titles ########################################################

def process_title_file(cursor, file_stream, collection_name):
    """
    Parse and insert titles from a file stream into the database.

    Args:
        cursor: SQLite cursor for database operations.
        file_stream: File-like object containing CSV/TSV title data.
        collection_name: Name of the collection to associate titles with.

    Returns:
        Tuple: (message: dict, status_code: int)
    """
    try:
        # Detect delimiter based on the file name
        delimiter = "\t" if file_stream.name.endswith(".tsv") else ","
        reader = csv.DictReader(file_stream, delimiter=delimiter)

        # Ensure the collection exists
        cursor.execute(
            """
            INSERT OR IGNORE INTO collections (name, description)
            VALUES (?, ?);
            """,
            (collection_name, "Imported from user upload")
        )
        cursor.execute("SELECT id FROM collections WHERE name = ?;", (collection_name,))
        collection_id = cursor.fetchone()["id"]

        # Process each row in the file
        for row in reader:
            title_name = row.get("name") or row.get("primaryTitle")
            title_year = row.get("year") or row.get("startYear")
            title_type = row.get("type") or row.get("titleType")
            imdb_title_id = row.get("imdb_title_id") or row.get("tconst")

            if not title_name:
                continue  # Skip rows without a title

            # Check for existing title
            cursor.execute(
                """
                SELECT id FROM titles WHERE imdb_title_id = ? 
                    OR (name = ? AND year = ? AND type = ?);
                """,
                (imdb_title_id, title_name, title_year, title_type)
            )
            existing_title = cursor.fetchone()

            if existing_title:
                title_id = existing_title["id"]
            else:
                # Insert a new title
                cursor.execute(
                    """
                    INSERT INTO titles (imdb_title_id, name, type, year)
                    VALUES (?, ?, ?, ?);
                    """,
                    (imdb_title_id, title_name, title_type, title_year)
                )
                title_id = cursor.lastrowid

            # Link title to the collection
            cursor.execute(
                """
                INSERT OR IGNORE INTO collection_titles (title_id, collection_id)
                VALUES (?, ?);
                """,
                (title_id, collection_id)
            )

        return {"message": "Titles processed successfully", "collection_name": collection_name}, 200
    except Exception as e:
        return {"error": f"Error processing titles: {e}"}, 500

def load_titles_from_dir(conn, directory="data/titles/local"):
    """
    Load titles from CSV/TSV files in the specified directory.

    Args:
        conn: SQLite connection object.
        directory: Directory containing title files.

    Returns:
        dict: Summary message.
    """
    if not os.path.exists(directory):
        return {"error": f"Titles directory not found: {directory}"}, 404

    cursor = conn.cursor()
    results = []
    for file_name in os.listdir(directory):
        if file_name.endswith((".tsv", ".csv")):
            file_path = os.path.join(directory, file_name)
            collection_name = scrub_string(os.path.splitext(file_name)[0])
            # print(f"Processing file: {file_path}")

            with open(file_path, "r", encoding="utf-8") as file_stream:
                result = process_title_file(cursor, file_stream, collection_name)
                results.append(result)

    conn.commit()
    return {"message": "Titles loaded successfully", "results": results}
