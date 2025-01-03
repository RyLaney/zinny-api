"""service endpoints"""

# pylint: disable=import-error,unused-import
from flask import Blueprint, request

service_bp = Blueprint('api/v1/service', __name__)

@service_bp.route('/stop', methods=['POST'])
def stop_server():
    """Stop the Flask server."""
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
        return "Server shutting down..."
    return "Error: Unable to shut down server."
