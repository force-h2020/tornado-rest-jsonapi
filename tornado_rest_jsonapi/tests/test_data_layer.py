from unittest.mock import Mock

from tornado.testing import AsyncTestCase, gen_test

from tornado_rest_jsonapi.data_layers.base import BaseDataLayer


class TestBaseDataLayer(AsyncTestCase):
    @gen_test
    def test_basic_expectations(self):
        handler = BaseDataLayer(
            dict(application=Mock(),
                 current_user=Mock()
                 ))

        with self.assertRaises(NotImplementedError):
            yield handler.create_object(dict(), dict())

        with self.assertRaises(NotImplementedError):
            yield handler.get_object(dict())

        with self.assertRaises(NotImplementedError):
            yield handler.delete_object(Mock(), dict())

        with self.assertRaises(NotImplementedError):
            yield handler.get_collection(Mock(), dict())
