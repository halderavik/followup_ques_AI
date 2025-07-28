import os
from flask import Flask, request
from dotenv import load_dotenv
from .log_config import setup_logging

load_dotenv()

def create_app() -> Flask:
    """
    Application factory for the Survey Intelligence API.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__, static_folder='../static', static_url_path='')

    # Configure logging
    setup_logging()
    app.logger.info('Survey Intelligence API starting up.')

    # DeepSeek API key is loaded directly by the service
    # No need to store in app config since users don't provide it

    # Request/response logging
    @app.before_request
    def log_request():
        app.logger.info(f"Request: {request.method} {request.path} - Body: {request.get_data(as_text=True)}")

    @app.after_request
    def log_response(response):
        app.logger.info(f"Response: {request.method} {request.path} - Status: {response.status_code}")
        return response

    # Register blueprints/routes here (to be added)
    from .routes import bp as api_bp
    app.register_blueprint(api_bp)

    return app 