"""Testing app/utils/import_helpers.py."""

# import os
import io
import json
# from unittest.mock import patch
import pytest
import sqlite3


from zinny_api.db.db_init import get_connection
from zinny_api.db.db_schema import (
    SCHEMA_TITLES_TABLE,
    SCHEMA_TITLE_TYPE_TABLE,
    SCHEMA_COLLECTIONS_TABLE,
    SCHEMA_SCREEN_TYPE_TABLE,
    SCHEMA_RATINGS_TABLE,
    SCHEMA_SURVEYS_TABLE,
    SCHEMA_WEIGHTS_TABLE
)
from zinny_api.utils.import_helpers import (
    process_survey_file,
    process_weight_preset_file,
    process_title_file,
    process_title_type_file,
    load_surveys_from_dir,
    load_weight_presets_from_dir,
    load_titles_from_dir,
    load_title_types_from_dir
)


from .data_samples import (
    TITLES_2024VFX_SAMPLE,
    SURVEY_VFX_SAMPLE,
    WEIGHTS_VFX_DEFAULT,
    TITLE_TYPES_SAMPLE
)



# pylint: disable=missing-function-docstring, redefined-outer-name

@pytest.fixture
def mock_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    with conn:
        conn.executescript(
            SCHEMA_TITLES_TABLE
            + SCHEMA_TITLE_TYPE_TABLE
            + SCHEMA_COLLECTIONS_TABLE
            + SCHEMA_SCREEN_TYPE_TABLE
            + SCHEMA_RATINGS_TABLE
            + SCHEMA_SURVEYS_TABLE
            + SCHEMA_WEIGHTS_TABLE
        )
    yield conn
    conn.close()


def test_process_survey_file(mock_db):
    cursor = mock_db.cursor()
    file_stream = io.StringIO(json.dumps(SURVEY_VFX_SAMPLE))
    response, status_code = process_survey_file(cursor, file_stream)
    assert status_code == 200
    assert response["message"] == "Survey processed successfully"
    assert response["survey_id"] == SURVEY_VFX_SAMPLE["id"]


def test_process_weight_preset_file(mock_db):
    cursor = mock_db.cursor()
    file_stream = io.StringIO(json.dumps(WEIGHTS_VFX_DEFAULT))
    response, status_code = process_weight_preset_file(cursor, file_stream)
    assert status_code == 200
    assert response["message"] == "Weight Preset processed successfully"
    assert response["weight_preset"]["name"] == WEIGHTS_VFX_DEFAULT["name"]


def test_process_title_file(mock_db):
    cursor = mock_db.cursor()
    file_stream = io.StringIO(json.dumps(TITLES_2024VFX_SAMPLE))
    file_stream.name =  "TITLES_2024VFX_SAMPLE.json"
    response, status_code = process_title_file(cursor, file_stream, "test_collection")
    print(response)
    assert status_code == 200
    assert response["message"] == "Titles processed successfully"
    assert response["collection_name"] == "test_collection"


def test_process_title_type_file(mock_db):
    cursor = mock_db.cursor()
    file_stream = io.StringIO(json.dumps(TITLE_TYPES_SAMPLE))
    response, status_code = process_title_type_file(cursor, file_stream)
    assert status_code == 200
    assert response["message"] == "Title Type processed successfully"


def test_load_surveys_from_dir(mock_db, tmp_path):
    survey_path = tmp_path / "surveys"
    survey_path.mkdir()
    (survey_path / "vfx.json").write_text(json.dumps(SURVEY_VFX_SAMPLE))
    response = load_surveys_from_dir(mock_db, directory=str(survey_path))
    assert response["message"] == "Surveys loaded"
    assert len(response["results"]) == 1


def test_load_weight_presets_from_dir(mock_db, tmp_path):
    weights_path = tmp_path / "weights"
    weights_path.mkdir()
    (weights_path / "vfx_weights.json").write_text(json.dumps(WEIGHTS_VFX_DEFAULT))
    response = load_weight_presets_from_dir(mock_db, directory=str(weights_path))
    assert response["message"] == "Weight Presets loaded"
    assert len(response["results"]) == 1


def test_load_titles_from_dir(mock_db, tmp_path):
    titles_path = tmp_path / "titles"
    titles_path.mkdir()
    (titles_path / "test_titles.tsv").write_text("name\tyear\ttype\nOjai\t2024\tmovie")
    response = load_titles_from_dir(mock_db, directory=str(titles_path))
    assert response["message"] == "Titles loaded successfully"
    assert len(response["results"]) == 1


def test_load_title_types_from_dir(mock_db, tmp_path):
    title_types_path = tmp_path / "title_types"
    title_types_path.mkdir()
    (title_types_path / "types.json").write_text(json.dumps(TITLE_TYPES_SAMPLE))
    response = load_title_types_from_dir(mock_db, directory=str(title_types_path))
    assert response["message"] == "Title Type loaded"
    assert len(response["results"]) == 1
