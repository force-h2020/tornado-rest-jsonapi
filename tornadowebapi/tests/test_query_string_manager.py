import unittest

from marshmallow_jsonapi import Schema
from tornadowebapi.exceptions import BadRequest, InvalidSort
from tornadowebapi.tests.resource_handlers import StudentSchema
from ..querystring import QueryStringManager as QSManager


class TestQueryStringManager(unittest.TestCase):
    def test_query_args(self):
        qs = QSManager({'page[number]': [b'1'],
                        'page[size]': [b'10'],
                        'foo': [b'bar', b'baz']
                        },
                       Schema)

        self.assertEqual(qs.query_args,
                         {'page[number]': '1',
                          'page[size]': '10',
                          'foo': ['bar', 'baz']}
                         )

    def test_pagination(self):
        qs = QSManager({'page[number]': [b'1'],
                        'page[size]': [b'10']},
                       Schema)
        self.assertEqual(
            qs.pagination['number'], 1
        )
        self.assertEqual(
            qs.pagination['size'], 10
        )

    def test_queryitems(self):
        qs = QSManager({'page[number]': [b'1'],
                        'page[size]': [b'10'],
                        'foo': [b'bar', b'baz']
                        },
                       Schema)

        items = qs.queryitems
        self.assertIn(("page[number]", '1'), items)
        self.assertIn(("page[size]", '10'), items)
        self.assertIn(("foo", 'bar'), items)
        self.assertIn(("foo", 'baz'), items)

    def test_incorrect_init(self):
        with self.assertRaises(ValueError):
            QSManager("hello", Schema)

    def test_empty_query_arg(self):
        qs = QSManager({'foo': [], 'bar': [b'3']}, Schema)
        self.assertEqual(qs.query_args, {"bar": "3"})

    def test_fields_comma_separated_values(self):
        qs = QSManager({'fields[user]': [b'name,email']}, Schema)
        self.assertEqual(qs.fields, {"user": ["name", "email"]})

        qs = QSManager({'fields[user]': [b'name']}, Schema)
        self.assertEqual(qs.fields, {"user": ["name"]})

    def test_incorrect_page_keys(self):
        with self.assertRaises(BadRequest):
            QSManager({'page[froop]': [b'1']}, Schema).pagination

    def test_sorting(self):
        self.assertEqual(QSManager({}, Schema).sorting, [])

        self.assertEqual(
            QSManager({"sort": [b"name,-age"]}, StudentSchema).sorting,
            [
                {
                    "order": 'asc',
                    'field': 'name'
                },
                {
                    "order": 'desc',
                    'field': 'age'
                }
            ])

        with self.assertRaises(InvalidSort):
            qs = QSManager({"sort": [b"created_at,-whatever"]}, StudentSchema)
            qs.sorting
