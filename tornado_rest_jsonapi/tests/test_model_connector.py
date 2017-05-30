from unittest.mock import Mock

from tornado.testing import AsyncTestCase, gen_test
from tornado_rest_jsonapi.model_connector import ModelConnector


class TestModelConnector(AsyncTestCase):
    @gen_test
    def test_basic_expectations(self):
        handler = ModelConnector(Mock(), Mock())
        with self.assertRaises(NotImplementedError):
            yield handler.create_object(Mock())

        with self.assertRaises(NotImplementedError):
            yield handler.retrieve_object(Mock())

        with self.assertRaises(NotImplementedError):
            yield handler.delete_object(Mock())

        with self.assertRaises(NotImplementedError):
            yield handler.retrieve_collection(Mock())
