"""Testing /weights endpoints."""

import os
import io
import json
import pytest

from zinny_api.db.db_init import get_connection
from zinny_api.db.db_schema import SCHEMA_WEIGHTS_TABLE
from tests.util_db_helpers import add_weights_test_data

from .data_samples import (
    WEIGHTS_PICTURE_DEFAULT,
    WEIGHTS_PICTURE_STORYTELLER,
    WEIGHTS_PICTURE_TECHNOLOGIST,
    WEIGHTS_VFX_DEFAULT,
)

# pylint: disable=redefined-outer-name,line-too-long
# pylint: disable=missing-function-docstring,unused-argument


@pytest.fixture(scope="function")
def setup_database(monkeypatch):
    """Set up a fresh database for weight tests."""
    test_db_path = "/tmp/test_database.db"
    monkeypatch.setattr("zinny_api.db.db_init.DATABASE_PATH", test_db_path)

    conn = get_connection()
    with conn:
        conn.executescript(SCHEMA_WEIGHTS_TABLE)
        print("Inserting sample weight data...")
        add_weights_test_data(conn, [
            WEIGHTS_VFX_DEFAULT,
            WEIGHTS_PICTURE_DEFAULT,
            WEIGHTS_PICTURE_STORYTELLER,
            WEIGHTS_PICTURE_TECHNOLOGIST,
        ])
        conn.commit()
    conn.close()

    yield

    if os.path.exists(test_db_path):
        os.remove(test_db_path)

@pytest.fixture
def client(setup_database):
    """Create a Flask test client for testing."""
    # pylint: disable=import-outside-toplevel
    from flask import Flask
    from zinny_api.api.weights import weights_bp

    app = Flask(__name__)
    app.register_blueprint(weights_bp, url_prefix='/api/v1/weights')

    with app.test_client() as client:
        yield client


def test_get_weights(client, setup_database):
    """Test fetching all weights from the API."""
    response = client.get('/api/v1/weights/')
    assert response.status_code == 200
    print(response.get_json())

    data = response.get_json()
    # assert any(weight["name"] == "Picture Overall (Even Weights)" for weight in data)
    assert any(weight["name"] == "Visual Effects default (Even Weights)" for weight in data)


def test_get_weight_by_id(client, setup_database):
    """Test fetching a specific weight by ID."""
    response = client.get('/api/v1/weights/2')
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Picture Overall (Even Weights)"
    assert data["survey_id"] == "picture_extended"


def test_get_weight_invalid(client, setup_database):
    """Test fetching a specific weight by ID."""
    response = client.get('/api/v1/weights/this-weight-does-not-exist')
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Weights not found"


def test_import_weights_into_db(client, setup_database):
    """Test importing weights directly into the database."""
    weights_data = {
        # "id": "user_weights",  # This should be auto-generated
        "name": "User Weights",
        "description": "Test weights for user.",
        "survey_id": "test_survey",
        "criteria_weights": {"artistry": 1.0, "technical_achievement": 0.5}
    }
    weights_file = io.BytesIO(json.dumps(weights_data).encode('utf-8'))  # Simulate file upload

    response = client.post(
        '/api/v1/weights/import',
        data={"file": (weights_file, "user_weight.json")},
        content_type='multipart/form-data'
    )
    assert response.status_code == 200

    result = response.get_json()
    assert result["message"] == "Weight Preset processed successfully"
    assert result["weight_preset"]['name'] == "User Weights"

    # Verify the weights were inserted into the database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weight_presets WHERE name = ?;", ("User Weights",))
    db_weights = cursor.fetchone()
    conn.close()

    assert db_weights is not None
    assert db_weights["name"] == "User Weights"
    assert json.loads(db_weights["weights"]) == weights_data["criteria_weights"]


def test_import_weights_invalid(client):
    """Test the /weights/import endpoint with an invalid weights file."""
    invalid_file = (io.BytesIO(b"not valid json"), "invalid_weights.json")

    response = client.post('/api/v1/weights/import', data={"file": invalid_file}, content_type='multipart/form-data')
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid JSON format."


def test_import_weights_sparse(client):
    """Test importing weights directly into the database."""
    weights_data = {
        # "id": "user_weights",  # This should be auto-generated
        "name": "User Weights",
        "criteria_weights": {"artistry": 1.0, "technical_achievement": 0.5}
    }
    weights_file = (io.BytesIO(json.dumps(weights_data).encode('utf-8')), "user_weights.json")

    response = client.post('/api/v1/weights/import', data={"file": weights_file}, content_type='multipart/form-data')
    assert response.status_code == 200

    result = response.get_json()
    assert result["message"] == "Weight Preset processed successfully"
    assert result["weight_preset"]['name'] == "User Weights"

    # Verify the weights were inserted into the database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weight_presets WHERE name = ?;", ("User Weights",))
    db_weights = cursor.fetchone()
    conn.close()

    assert db_weights is not None
    assert db_weights["name"] == "User Weights"
    assert db_weights["description"] == ""
    assert db_weights["survey_id"] is None
    assert json.loads(db_weights["weights"]) == weights_data["criteria_weights"]


def test_weights_preset_update(client):
    """Test updating an existing weight preset with new data."""
    # Initial preset to be added
    initial_preset = WEIGHTS_VFX_DEFAULT
    response = client.post('/api/v1/weights/', json=initial_preset)
    assert response.status_code == 200
    result = response.get_json()
    assert result["message"] == "Weight presets added successfully."
    initial_weights_id = result["weights_id"]

    # Update the existing preset
    updated_preset = initial_preset.copy()
    updated_preset["description"] = "Updated weights for VFX evaluation."
    updated_preset["survey_id"] = "vfx_basic"
    updated_preset["criteria_weights"] = {
        "artistry": 0.5,
        "contribution": 0.5,
        "fidelity": 0.5,
        "necessity": 0.5,
        "technical_achievement": 1.0
    }
    response = client.post('/api/v1/weights/', json=updated_preset)
    assert response.status_code == 200
    result = response.get_json()
    assert result["message"] == "Weight presets added successfully."
    print(result)
    updated_weights_id = result["weights_id"]

    # Verify that the same weights_id is used for the update
    assert initial_weights_id == updated_weights_id

    # Verify the updated values in the database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weight_presets WHERE name = ?;", (initial_preset['name'],))
    updated_data = cursor.fetchone()
    conn.close()

    assert updated_data is not None
    assert updated_data["description"] == "Updated weights for VFX evaluation."
    weights = json.loads(updated_data["weights"])
    assert weights == {
        "artistry": 0.5,
        "contribution": 0.5,
        "fidelity": 0.5,
        "necessity": 0.5,
        "technical_achievement": 1.0
    }
