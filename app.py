from http import HTTPStatus

from flask import Flask
from flask_request_id_header.middleware import RequestID


def create_app_with_middleware():
    app = Flask(__name__)

    # Configure and load Middleware
    app.config['REQUEST_ID_UNIQUE_VALUE_PREFIX'] = 'TEST-'
    RequestID(app)

    @app.route("/sample")
    def sample():
        return '', HTTPStatus.NO_CONTENT

    return app
