"""Main application file for the Zinny Flask server."""

from flask import Flask
from .db.db_init import init_db

from . import api
from . import config

# from zinny_api import routes
# from .routes.errors import errors_bp

# pylint: disable=import-outside-toplevel,line-too-long

# Application Factory
def create_app():
    """Init the zinny_api."""
    flask_app = Flask(__name__)
    flask_app.config["API_TITLE"] = "Zinny API"
    flask_app.config["API_VERSION"] = "1.0"

    # flask_app.register_blueprint(errors_bp)

    # Initialize the database
    with flask_app.app_context():
        print("Initializing database")
        init_db(load_data=True)

    # Register blueprints
    flask_app.register_blueprint(api.titles.titles_bp, url_prefix='/api/v1/titles')
    flask_app.register_blueprint(api.title_types.title_types_bp, url_prefix='/api/v1/title-types')
    flask_app.register_blueprint(api.screen_types.screen_types_bp, url_prefix='/api/v1/screen-types')
    flask_app.register_blueprint(api.surveys.surveys_bp, url_prefix='/api/v1/surveys')
    flask_app.register_blueprint(api.weights.weights_bp, url_prefix='/api/v1/weights')
    flask_app.register_blueprint(api.ratings.ratings_bp, url_prefix='/api/v1/ratings')
    flask_app.register_blueprint(api.service.service_bp, url_prefix='/api/v1/service')

    # set survey and weights files
    # Default configuration
    flask_app.config.from_mapping(
        DATABASE='zinny-1.0.sqlite',
    )
    flask_app.config["SURVEYS_PATH"] = "zinny_api/v1/data/surveys"
    flask_app.config["WEIGHTS_PATH"] = "zinny_api/v1/data/weights"

    return flask_app
