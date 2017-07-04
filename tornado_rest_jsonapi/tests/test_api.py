import unittest

from unittest.mock import Mock

from tornado_rest_jsonapi.api import Api
from tornado_rest_jsonapi.tests.resource_handlers import UserDetails


class TestApi(unittest.TestCase):
    def test_basic_usage(self):
        app = Mock()
        api = Api(app)

        # Register the classes.
        api.route(
            UserDetails,
            "user",
            "/users/(.*)/",
        )

        self.assertTrue(app.wildcard_router.add_rules.called)

    def test_double_registration(self):
        app = Mock()
        api = Api(app)

        api.route(
            UserDetails,
            "user",
            "/users/(.*)/",
        )
        with self.assertRaises(ValueError):
            api.route(
                UserDetails,
                "user",
                "/users/(.*)/",
            )

    def test_incorrect_class_registration(self):
        app = Mock()
        api = Api(app)

        with self.assertRaises(TypeError):
            api.route(
                "hello",
                "user",
                "/users/(.*)/",
            )

        with self.assertRaises(TypeError):
            api.route(
                int,
                "user",
                "/users/(.*)/",
            )

    def test_authenticator(self):
        app = Mock()
        api = Api(app)

        self.assertIsNotNone(api.authenticator)

    def test_empty_api_handlers(self):
        app = Mock()
        Api(app)
        self.assertFalse(app.wildcard_router.add_routes.called)
