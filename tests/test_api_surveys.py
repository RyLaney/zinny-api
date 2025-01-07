"""Testing /survey endpoints."""

import os
import io
import json
from unittest.mock import patch
import pytest

from zinny_api.config import SURVEY_PATHS
from zinny_api.db.db_schema import SCHEMA_SURVEYS_TABLE
from zinny_api.db.db_init import get_connection

from tests.util_db_helpers import add_survey_test_data
from .data_samples import SURVEY_VFX_SAMPLE, SURVEY_VFX_EXTENDED_SAMPLE, SURVEY_PICTURE_SAMPLE


# pylint: disable=redefined-outer-name,line-too-long
# pylint: disable=missing-function-docstring,unused-argument


@pytest.fixture(scope="function")
def setup_database(monkeypatch):
    """Set up a fresh database for each test."""
    test_db_path = "/tmp/test_database.db"
    # Monkeypatch the DATABASE_PATH to point to test_db_path
    monkeypatch.setattr("zinny_api.db.db_init.DATABASE_PATH", test_db_path)

    print(f"Using database path: {test_db_path}")
    schema = SCHEMA_SURVEYS_TABLE
    # Ensure a clean slate
    conn = get_connection()  # uses the monkeypatched DATABASE_PATH
    with conn:
        conn.executescript(schema)
        print("Inserting sample data...")
        add_survey_test_data(conn, SURVEY_VFX_SAMPLE)
        add_survey_test_data(conn, SURVEY_VFX_EXTENDED_SAMPLE)
        add_survey_test_data(conn, SURVEY_PICTURE_SAMPLE)
    conn.close()

    yield

    # Clean up after tests
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

@pytest.fixture
def client(setup_database):
    # pylint: disable=import-outside-toplevel
    from flask import Flask
    from zinny_api.api.surveys import surveys_bp

    app = Flask(__name__)
    app.register_blueprint(surveys_bp, url_prefix='/api/v1/surveys')

    with app.test_client() as client:
        yield client


@pytest.fixture(scope="function", autouse=True)
def patch_survey_paths(tmp_path):
    """Patch survey paths to use temporary directories."""
    with patch.dict(SURVEY_PATHS, {
        "shared": tmp_path / "shared",
        "local": tmp_path / "local"
    }):
        os.makedirs(SURVEY_PATHS["shared"], exist_ok=True)
        os.makedirs(SURVEY_PATHS["local"], exist_ok=True)
        yield SURVEY_PATHS


def test_get_surveys(client, setup_database):
    """Test fetching all surveys from the API."""
    response = client.get('/api/v1/surveys/')
    assert response.status_code == 200
    data = response.get_json()
    assert any(survey["id"] == "vfx_basic" for survey in data)
    assert any(survey["id"] == "picture" for survey in data)


def test_get_survey_invalid(client):
    """Test the /surveys/<id> endpoint with an invalid ID."""
    response = client.get('/api/v1/surveys/this-survey-does-not-exist')
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == "Survey not found"


def test_get_survey_by_id(client):
    """Test the /surveys/<id> endpoint with a valid ID."""
    response = client.get('/api/v1/surveys/vfx_basic')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == "vfx_basic"


def test_search_surveys(client, setup_database):
    """Test searching surveys by name."""
    response = client.get('/api/v1/surveys/search?query=Picture')
    assert response.status_code == 200
    data = response.get_json()
    results = data["results"]
    assert len(results) == 1
    assert results[0]["id"] == "picture"

    # Test case-insensitive search
    response = client.get('/api/v1/surveys/search?query=picture')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["results"]) == 1

    # Test pagination
    response = client.get('/api/v1/surveys/search?query=a&limit=1&page=1')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["results"]) == 1
    assert data["page"] == 1
    assert data["limit"] == 1

    response = client.get('/api/v1/surveys/search?query=a&limit=1&page=2')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["results"]) == 1
    assert data["page"] == 2


def test_import_survey(client):
    """Test the /surveys/import endpoint with a valid survey file."""
    survey_data = {"id": "user_survey", "name": "User Survey", "description": "A user-imported survey."}
    survey_file = io.BytesIO(json.dumps(survey_data).encode('utf-8'))  # Simulate file upload

    response = client.post(
        '/api/v1/surveys/import',
        data={"file": (survey_file, "user_survey.json")},
        content_type='multipart/form-data'
    )
    assert response.status_code == 200

    result = response.get_json()
    assert result["message"] == "Survey processed successfully"
    assert result["survey_id"] == "user_survey"


def test_import_survey_invalid(client):
    """Test the /surveys/import endpoint with an invalid survey file."""
    invalid_file = io.BytesIO(b"not valid json")  # Simulate file upload

    response = client.post(
        '/api/v1/surveys/import',
        data={"file": (invalid_file, "invalid_survey.json")},
        content_type='multipart/form-data'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid JSON format."


# def test_load_surveys(client, patch_survey_paths, tmp_path):
#     """Test loading surveys from a directory."""
#     # Create sample survey files
#     survey_data = {"id": "sample_survey", "name": "Sample Survey", "description": "Sample survey data."}
#     sample_file = tmp_path / "shared" / "sample_survey.json"
#     sample_file.parent.mkdir(parents=True, exist_ok=True)
#     sample_file.write_text(json.dumps(survey_data))

#     response = client.post('/api/v1/surveys/load')
#     assert response.status_code == 200
#     result = response.get_json()
#     assert result["message"] == "Surveys loaded successfully."

#     # Verify the survey was added
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM surveys WHERE id = ?;", ("sample_survey",))
#     survey = cursor.fetchone()
#     assert survey is not None
#     assert survey["id"] == "sample_survey"
#     conn.close()


def test_import_survey_invalid_file_type(client):
    """Test the /surveys/import endpoint with a non-JSON file."""
    text_file = io.BytesIO(b"This is not JSON")  # Simulate a non-JSON file upload

    response = client.post(
        '/api/v1/surveys/import',
        data={"file": (text_file, "not_a_survey.txt")},
        content_type='multipart/form-data'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid file. Must be a .json file."


def test_import_survey_db_error(client):
    """Test importing a survey when the database fails."""
    survey_data = {"id": "user_survey", "name": "User Survey", "description": "Test"}
    survey_file = io.BytesIO(json.dumps(survey_data).encode('utf-8'))

    with patch("zinny_api.api.surveys.process_survey_file", side_effect=Exception("Database error")):
        response = client.post(
            '/api/v1/surveys/import',
            data={"file": (survey_file, "user_survey.json")},
            content_type='multipart/form-data'
        )

    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "Database error" in data["error"]


def test_get_survey_expanded(client, setup_database):
    """Test fetching an expanded survey by ID."""
    response = client.get('/api/v1/surveys/vfx_basic?expanded=true')
    assert response.status_code == 200
    data = response.get_json()

    # Assert base fields
    assert data["id"] == "vfx_basic"
    assert data["name"] == "Visual Effects Assessment"
    assert "criteria" in data
    assert isinstance(data["criteria"], list)
    assert len(data["criteria"]) > 0

    # Assert criteria expansion
    assert any(criterion["id"] == "artistry" for criterion in data["criteria"])
    assert any(criterion["id"] == "technical_achievement" for criterion in data["criteria"])



def test_get_survey_default_expanded(client, setup_database):
    """Test fetching a survey defaults to expanded when no parameter is provided."""
    response = client.get('/api/v1/surveys/vfx_basic')
    assert response.status_code == 200
    data = response.get_json()

    # Assert criteria expansion
    assert "criteria" in data
    assert isinstance(data["criteria"], list)
    assert len(data["criteria"]) > 0


def test_get_survey_extended(client, setup_database):
    """Test fetching an extended survey that inherits another."""
    # Fetch the extended survey
    response = client.get('/api/v1/surveys/vfx_extended?expanded=true')
    assert response.status_code == 200
    extended_data = response.get_json()

    # Assert extended survey metadata
    assert extended_data["id"] == "vfx_extended"
    assert extended_data["name"] == "Visual Effects - Extended"
    assert "extends" in extended_data
    assert extended_data["extends"] == "vfx_basic"

    # Assert extended criteria includes base criteria + extended criteria
    extended_criteria = {criterion["id"] for criterion in extended_data["criteria"]}
    expected_criteria = {"artistry", "technical_achievement", "fidelity", "necessity", "contribution"}
    assert extended_criteria == expected_criteria


def test_get_survey_base_only(client, setup_database):
    """Test fetching a base survey without expansion."""
    # Add base survey to the database

    # Fetch the base survey
    response = client.get('/api/v1/surveys/vfx_basic?expanded=false')
    assert response.status_code == 200
    base_data = response.get_json()

    # Assert base survey metadata
    assert base_data["id"] == "vfx_basic"
    assert base_data["name"] == "Visual Effects Assessment"

    # Assert criteria only includes base criteria
    base_criteria = {criterion["id"] for criterion in base_data["criteria"]}
    expected_criteria = {"artistry", "technical_achievement", "fidelity"}
    assert base_criteria == expected_criteria


def test_get_survey_with_invalid_extends(client, setup_database):
    """Test fetching a survey with an invalid 'extends' reference."""
    # Add extended survey with an invalid 'extends' reference to the database
    invalid_extended_survey = SURVEY_VFX_EXTENDED_SAMPLE.copy()
    invalid_extended_survey["extends"] = "nonexistent_survey"
    invalid_extended_survey["id"] = "broken_extends_survey"
    # print(invalid_extended_survey)

    conn = get_connection()
    with conn:
        add_survey_test_data(conn, invalid_extended_survey)
    conn.close()

    # Fetch the extended survey
    response = client.get('/api/v1/surveys/broken_extends_survey?expanded=true')
    print(response.get_json())
    assert response.status_code == 500
    error_data = response.get_json()

    # Assert error message
    assert "error" in error_data
    assert "Parent survey with ID" in error_data["error"]


def test_get_survey_no_extends(client, setup_database):
    """Test fetching a survey with no 'extends' reference."""

    # Fetch the survey
    response = client.get('/api/v1/surveys/vfx_basic?expanded=true')
    assert response.status_code == 200
    survey_data = response.get_json()

    # Assert no 'extends' field
    assert survey_data["extends"] is None
    assert survey_data["id"] == "vfx_basic"
