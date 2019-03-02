import unittest

from http import HTTPStatus
from uuid import UUID, uuid4

from app import create_app_with_middleware


class RequestIdMiddlewareTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app_with_middleware()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_request_id_no_existing_value(self):
        response = self.client.get(
            '/sample',
            base_url='http://localhost:9000'
        )

        # Check a single request ID value exists
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertIsInstance(response.headers['X-Request-ID'], str)
        request_id_header_values = response.headers['X-Request-ID'].split(',')
        self.assertEqual(len(request_id_header_values), 1)

        # Check single value is unique
        try:
            UUID(request_id_header_values[0], version=4)
        except ValueError:
            self.fail("Request ID value is not a UUID")

    def test_request_id_existing_non_unique_value(self):
        existing_header_values = [
            {
                'value': 'client-non-unique-value',
                'len': 1
            },
            {
                'value': 'client-non-unique-value1,client-non-unique-value2',
                'len': 2
            },
            {
                'value': 'x-1,x-2,x3,x-4,x-5,x-6,x-7,x-8',
                'len': 8
            }
        ]

        for existing_header_value in existing_header_values:
            with self.subTest(existing_header_value=existing_header_value):
                response = self.client.get(
                    '/sample',
                    base_url='http://localhost:9000',
                    headers={
                        'x-request-id': existing_header_value['value']
                    }
                )

                # Check n+1 request IDs exist
                self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
                self.assertIsInstance(response.headers['X-Request-ID'], str)
                request_id_header_values = response.headers['X-Request-ID'].split(',')
                self.assertEqual(len(request_id_header_values), existing_header_value['len'] + 1)

                # Check pre-existing request IDs are returned as-is
                original_request_id_values = request_id_header_values[:existing_header_value['len']]
                original_request_id_values = ','.join(original_request_id_values)
                self.assertEqual(original_request_id_values, existing_header_value['value'])

                # Check unique request ID was added
                unique_request_id_value = request_id_header_values[-1:][0]
                try:
                    UUID(unique_request_id_value, version=4)
                except ValueError:
                    self.fail("Unique request ID value is not a UUID")

    def test_request_id_existing_unique_value(self):
        existing_header_values = [
            {
                'value': f"{ uuid4() }",
                'len': 1
            },
            {
                'value': f"{ uuid4() },{ uuid4() }",
                'len': 2
            }
        ]

        for existing_header_value in existing_header_values:
            with self.subTest(existing_header_value=existing_header_value):
                response = self.client.get(
                    '/sample',
                    base_url='http://localhost:9000',
                    headers={
                        'x-request-id': existing_header_value['value']
                    }
                )

                # Check n+1 request IDs exist
                self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
                self.assertIsInstance(response.headers['X-Request-ID'], str)
                request_id_header_values = response.headers['X-Request-ID'].split(',')
                self.assertEqual(len(request_id_header_values), existing_header_value['len'])

                # Check pre-existing request IDs are returned as-is
                original_request_id_values = request_id_header_values[:existing_header_value['len']]
                original_request_id_values = ','.join(original_request_id_values)
                self.assertEqual(original_request_id_values, existing_header_value['value'])

    def test_request_id_existing_unique_prefix_value(self):
        existing_header_values = [
            {
                'value': 'TEST-',
                'len': 1
            },
            {
                'value': 'TEST-X',
                'len': 1
            },
            {
                'value': 'TEST-1,TEST-2',
                'len': 2
            },
            {
                'value': 'TEST-X,client-non-unique-value',
                'len': 2
            }
        ]

        for existing_header_value in existing_header_values:
            with self.subTest(existing_header_value=existing_header_value):
                response = self.client.get(
                    '/sample',
                    base_url='http://localhost:9000',
                    headers={
                        'x-request-id': existing_header_value['value']
                    }
                )

                # Check n+1 request IDs exist
                self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
                self.assertIsInstance(response.headers['X-Request-ID'], str)
                request_id_header_values = response.headers['X-Request-ID'].split(',')
                self.assertEqual(len(request_id_header_values), existing_header_value['len'])

                # Check pre-existing request IDs are returned as-is
                original_request_id_values = request_id_header_values[:existing_header_value['len']]
                original_request_id_values = ','.join(original_request_id_values)
                self.assertEqual(original_request_id_values, existing_header_value['value'])
