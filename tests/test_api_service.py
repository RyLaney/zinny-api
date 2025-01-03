"""Testing /service endpoints."""

import pytest
from flask import Flask
from zinny_api.api.service import service_bp

# pylint: disable=redefined-outer-name,line-too-long

@pytest.fixture
def client():
    """Create a Flask test client for testing."""
    app = Flask(__name__)
    app.register_blueprint(service_bp, url_prefix='/api/v1/service')
    with app.test_client() as client:
        yield client


def test_stop_server(client):
    """Test the /service/stop endpoint."""
    response = client.post('/api/v1/service/stop')
    # Werkzeug does not actually shut down in test mode, but we can check the response
    assert response.status_code == 200
    # assert response.data.decode() == "Server shutting down..."
