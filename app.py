import os
import unittest
from http import HTTPStatus

from flask import Flask
from flask_request_id_header.middleware import RequestID


def create_app_with_middleware():
    app = Flask(__name__)

    # Configure and load Middleware
    app.config['REQUEST_ID_UNIQUE_VALUE_PREFIX'] = 'TEST-'
    RequestID(app)

    # Support running integration tests
    @app.cli.command()
    def test():
        """Run integration tests."""
        tests = unittest.TestLoader().discover(os.path.join(os.path.dirname(__file__), 'tests'))
        unittest.TextTestRunner(verbosity=2).run(tests)

    @app.route("/sample")
    def sample():
        return '', HTTPStatus.NO_CONTENT

    return app


if __name__ == "__main__":
    test_app = create_app_with_middleware()

    # Support PyCharm debugging
    if 'PYCHARM_HOSTED' in os.environ:
        # Exempting Bandit security issue (binding to all network interfaces)
        #
        # All interfaces option used because the network available within the container can vary across providers
        # This is only used when debugging with PyCharm. A standalone web server is used in production.
        test_app.run(host='0.0.0.0', port=9000, debug=True, use_debugger=False, use_reloader=False)  # nosec
