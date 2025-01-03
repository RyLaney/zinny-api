"""handle error routes"""
from flask import Blueprint, render_template, jsonify, request

# pylint: disable=unused-argument,missing-function-docstring

errors_bp = Blueprint("errors", __name__)


@errors_bp.app_errorhandler(404)
def handle_404(error):
    """Handle 404 errors."""
    if request.accept_mimetypes["application/json"] >= request.accept_mimetypes["text/html"]:
        # Respond with JSON if the request prefers JSON
        return jsonify({"error": "Resource not found"}), 404
    # Otherwise, render the HTML error page
    return render_template("404.html"), 404


@errors_bp.app_errorhandler(500)
def handle_500(error):
    """Handle 500 errors."""
    if request.accept_mimetypes["application/json"] >= request.accept_mimetypes["text/html"]:
        # Respond with JSON if the request prefers JSON
        return jsonify({"error": "Internal server error"}), 500
    # Otherwise, render the HTML error page
    return render_template("500.html"), 500
