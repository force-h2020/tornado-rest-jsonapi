import urllib.parse
from collections import OrderedDict
from unittest import mock
import http.client


from tornado.testing import LogTrapTestCase
from tornadowebapi.registry import Registry
from tornadowebapi.tests import resource_handlers
from tornadowebapi.tests.utils import AsyncHTTPTestCase
from tornado import web, escape


class TestBase(AsyncHTTPTestCase, LogTrapTestCase):
    def setUp(self):
        super().setUp()
        resource_handlers.StudentDetails.model_connector.collection = \
            OrderedDict()
        resource_handlers.StudentDetails.model_connector.id = 0

    def get_app(self):
        registry = Registry()
        registry.register(
            resource_handlers.StudentList,
            "/students/",
        )
        registry.register(
            resource_handlers.StudentDetails,
            "/students/(.*)/",
        )
        handlers = registry.api_handlers('/')
        app = web.Application(handlers=handlers, debug=True)
        app.hub = mock.Mock()
        return app

    def _create_one_student(self, name, age):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "data": {
                    "type": "student",
                    "attributes": {
                        "name": name,
                        "age": age,
                    }
                }
            })
        )
        location = urllib.parse.urlparse(res.headers["Location"]).path
        return location


class TestCRUDAPI(TestBase):
    def test_items(self):
        res = self.fetch("/api/v1/students/")

        self.assertEqual(res.code, http.client.OK)
        payload = escape.json_decode(res.body)
        self.assertIn("/api/v1/students/", payload['links']['self'])
        del payload['links']
        self.assertEqual(payload,
                         {'data': [],
                          'jsonapi': {
                              'version': '1.0'
                          }})

        resource = resource_handlers.StudentDetails
        connector = resource.model_connector

        connector.collection[1] = dict(
            id="1",
            name="john wick",
            age=39)
        connector.collection[2] = dict(
            id="2",
            name="john wick 2",
            age=39)
        connector.collection[3] = dict(
            id="3",
            name="john wick 3",
            age=39)

        res = self.fetch("/api/v1/students/")
        self.assertEqual(res.code, http.client.OK)

    def test_create(self):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "data": {
                    "type": "student",
                    "attributes": {
                        "name": "john wick",
                        "age": 19,
                    }
                }
            })
        )

        self.assertEqual(res.code, http.client.CREATED)
        self.assertIn("api/v1/students/0/", res.headers["Location"])

        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "data": {
                    "type": "student",
                    "attributes": {
                        "name": "john wick",
                        "age": 19,
                    }
                }
            })
        )
        self.assertEqual(res.code, http.client.CREATED)
        self.assertIn("api/v1/students/1/", res.headers["Location"])

        res = self.fetch("/api/v1/students/")
        self.assertEqual(res.code, http.client.OK)
        payload = escape.json_decode(res.body)
        self.assertIn('/api/v1/students/', payload['links']['self'])
        del payload["links"]
        self.assertEqual(
            payload,
            {
                'data': [
                    {
                        'attributes': {
                            'age': 19,
                            'name': 'john wick'
                        },
                        'id': 0,
                        'type': 'student'
                    },
                    {
                        'attributes': {
                            'age': 19,
                            'name': 'john wick'
                        },
                        'id': 1,
                        'type': 'student'
                    }
                ],
                'jsonapi': {'version': '1.0'}
            }
        )

        # Missing mandatory entry
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                'data': {
                    "type": "student",
                    "attributes": {
                        "name": "john wick",
                    }
                }
            })
        )
        self.assertEqual(res.code, http.client.BAD_REQUEST)

    def test_retrieve(self):
        location = self._create_one_student("john wick", 19)

        res = self.fetch(location)
        self.assertEqual(res.code, http.client.OK)

        self.assertEqual(
            escape.json_decode(res.body),
            {
                "data": {
                    "type": "student",
                    "id": 0,
                    "attributes": {
                        "name": "john wick",
                        "age": 19
                    }
                },
                "jsonapi": {
                    "version": "1.0"
                }
            })

        res = self.fetch("/api/v1/students/1/")
        self.assertEqual(res.code, http.client.NOT_FOUND)
        # self.assertNotIn("Content-Type", res.headers)

    def test_post_on_resource(self):
        location = self._create_one_student("john wick", 19)
        res = self.fetch(
            location,
            method="POST",
            body=escape.json_encode({
                'data': {
                    "type": "student",
                    "attributes": {
                        "name": "john wick 2",
                        "age": 34,
                    }
                }
            })
        )

        self.assertEqual(res.code, http.client.CONFLICT)

    def test_update(self):
        location = self._create_one_student("john wick", 19)
        res = self.fetch(
            location,
            method="PATCH",
            body=escape.json_encode({
                'data': {
                    "type": "student",
                    "id": 0,
                    "attributes": {
                        "age": 49,
                    }
                }
            })
        )
        self.assertEqual(res.code, http.client.OK)

        res = self.fetch(location)
        self.assertEqual(escape.json_decode(res.body),
                         {
                             "data": {
                                 "type": "student",
                                 "id": 0,
                                 "attributes": {
                                     "name": "john wick",
                                     "age": 49
                                 }
                             },
                             "jsonapi": {
                                 "version": "1.0"
                             }
                         })

    def test_update_errors(self):
        location = self._create_one_student("john wick", 19)
        res = self.fetch(
            location,
            method="PATCH",
            body=escape.json_encode({
                "data": {
                    "type": "student",
                    "id": 0,
                    "attributes": {
                        "age": "hello",
                    }
                }
            })
        )
        self.assertEqual(res.code, http.client.BAD_REQUEST)

        res = self.fetch(
            "/api/v1/students/1/",
            method="PATCH",
            body=escape.json_encode({
                "data": {
                    "type": "student",
                    "id": 1,
                    "attributes": {
                        "age": 34,
                    }
                }
            })
        )
        self.assertEqual(res.code, http.client.NOT_FOUND)

    def test_delete(self):
        location = self._create_one_student("john wick", 19)

        res = self.fetch(location, method="DELETE")
        self.assertEqual(res.code, http.client.NO_CONTENT)

        res = self.fetch(location)
        self.assertEqual(res.code, http.client.NOT_FOUND)

        res = self.fetch("/api/v1/students/1/", method="DELETE")
        self.assertEqual(res.code, http.client.NOT_FOUND)

    def test_delete_collection(self):
        res = self.fetch("/api/v1/students/", method="DELETE")
        self.assertEqual(res.code, http.client.METHOD_NOT_ALLOWED)

    def test_put_collection(self):
        res = self.fetch("/api/v1/students/",
                         method="PUT",
                         body=escape.json_encode({}))
        self.assertEqual(res.code, http.client.METHOD_NOT_ALLOWED)

    def test_post_non_json(self):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body="hello"
        )
        self.assertEqual(res.code, http.client.BAD_REQUEST)


class TestFilteringAPI(TestBase):
    def setUp(self):
        super().setUp()

        for i in range(50):
            self._create_one_student("john wick {}".format(i), age=10+i)

    def test_no_filtering(self):
        res = self.fetch("/api/v1/students/")

        self.assertEqual(res.code, http.client.OK)
        payload = escape.json_decode(res.body)
        self.assertEqual(len(payload["data"]), 10)
        self.assertIn("?page%5Bnumber%5D=2", payload["links"]["last"])
        self.assertIn("?page%5Bnumber%5D=1", payload["links"]["next"])
        self.assertNotIn("prev", payload["links"])

        res = self.fetch("/api/v1/students/?page%5Bnumber%5D=1")
        payload = escape.json_decode(res.body)
        self.assertEqual(len(payload["data"]), 10)
        self.assertIn("?page%5Bnumber%5D=2", payload["links"]["last"])
        self.assertIn("?page%5Bnumber%5D=2", payload["links"]["next"])
        self.assertIn("?page%5Bnumber%5D=0", payload["links"]["prev"])


class TestErrors(TestBase):
    def test_invalid_type(self):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "data": {
                    "type": "gnaka",
                    "attributes": {
                        "name": "john wick",
                        "age": 19,
                    }
                }
            })
        )

        self.assertEqual(res.code, http.client.CONFLICT)
        payload = escape.json_decode(res.body)
        self.assertEqual(payload, {
            'errors': [{
                'detail': 'Invalid type. Expected "student".',
                'source': {'pointer': '/data/type'},
                'status': '409',
                'title': 'Incorrect type'}],
            'jsonapi': {'version': '1.0'}})

    def test_invalid_value(self):
        res = self.fetch(
            "/api/v1/students/",
            method="POST",
            body=escape.json_encode({
                "data": {
                    "type": "student",
                    "attributes": {
                        "name": "john wick",
                        "age": "hello",
                    }
                }
            })
        )

        self.assertEqual(res.code, http.client.BAD_REQUEST)

        payload = escape.json_decode(res.body)
        self.assertEqual(payload, {
            'errors': [{
                'detail': 'Not a valid integer.',
                'source': {'pointer': '/data/attributes/age'}}
                ],
            'jsonapi': {'version': '1.0'}})
