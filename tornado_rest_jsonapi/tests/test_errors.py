import unittest

from tornado_rest_jsonapi.errors import jsonapi_errors
from tornado_rest_jsonapi.exceptions import ObjectNotFound


class TestErrors(unittest.TestCase):
    def test_jsonapi_errors(self):
        self.assertEqual(jsonapi_errors(ObjectNotFound()),
                         {"errors": [{
                             "title": "Object not found",
                             "status": '404',
                         }],
                         "jsonapi": {
                             "version": "1.0"
                         }})
