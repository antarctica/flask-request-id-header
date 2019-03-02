from typing import Optional
from uuid import UUID, uuid4

from flask import Flask as App


class RequestID(object):
    """
    Flask middleware to ensure all requests have a Request ID header present.

    Request IDs can be used when logging errors and allows users to trace requests through multiple
    layers such as load balancers and reverse proxies. The request ID header value may consist of multiple IDs encoded
    according to RFC 2616 [1].

    This middleware ensures there is always at least one, unique, value, whilst respecting any pre-existing values set
    by an upstream component or the client. If there isn't a pre-existing value, a single, unique, ID is generated.

    If there is a pre-existing value, it is split into multiple values as per RFC 2616 and each value checked for
    uniqueness. If no values are unique an additional, unique, value is added. A value is considered unique if it:

    1. is a valid UUID (version 4)
    2. or, the value is known to be from a component that assigns unique IDs, identified by a common prefix set in the
       'REQUEST_ID_UNIQUE_VALUE_PREFIX' Flask config value

    To use the Request ID in the current application: `print(request.environ.get("HTTP_X_REQUEST_ID"))`
    For use elsewhere, the Request ID header is included in the response back to the client.

    [1] http://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.2
    """

    def __init__(self, app: App):
        """
        :type app: App
        :param app: Flask application
        """
        self.app = app.wsgi_app
        self._unique_request_id_value_prefix = app.config['REQUEST_ID_UNIQUE_VALUE_PREFIX']
        self._header_name = "X-Request-ID"
        self._flask_header_name = f"HTTP_{ self._header_name.upper().replace('-', '_') }"

        app.wsgi_app = self

    def __call__(self, environ, start_response) -> App:
        request_id_header = self._compute_request_id_header(environ.get(self._flask_header_name))
        environ[self._flask_header_name] = request_id_header

        def new_start_response(status, response_headers, exc_info=None):
            response_headers.append((self._header_name, request_id_header))
            return start_response(status, response_headers, exc_info)

        return self.app(environ, new_start_response)

    def _compute_request_id_header(self, header_value: Optional[str] = None) -> str:
        """
        Ensures request ID header has at least one, unique, value

        :type header_value: Optional[str]
        :param header_value: Existing request ID HTTP header value

        :rtype: str
        :return: Computed Request ID HTTP header
        """
        if header_value is None:
            return self._generate_request_id()

        header_values = header_value.split(',')
        for request_id in header_values:
            if self._request_id_unique(request_id, self._unique_request_id_value_prefix):
                return header_value

        # Append an unique header value
        header_value = f"{ header_value },{ self._generate_request_id() }"

        return header_value

    @staticmethod
    def _request_id_unique(request_id: str, unique_request_id_value_prefix: Optional[str] = None) -> bool:
        """
        Checks whether a Request ID is unique

        :type request_id: str
        :param request_id: A request ID

        :type unique_request_id_value_prefix: Optional[str]
        :param unique_request_id_value_prefix: A prefix which indicates a request ID should be considered unique

        :rtype: bool
        :return: Whether the Request ID is unique or not
        """
        if unique_request_id_value_prefix is not None and unique_request_id_value_prefix in request_id:
            return True

        try:
            UUID(request_id, version=4)
            return True
        except ValueError:
            pass

        return False

    @staticmethod
    def _generate_request_id() -> str:
        """
        Generates a unique request ID value

        :rtype: str
        :return: unique request ID
        """
        return str(uuid4())
