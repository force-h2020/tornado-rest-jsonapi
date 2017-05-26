import unittest

from ..import errors
from ..import exceptions


class TestExceptions(unittest.TestCase):
    def test_to_jsonapi(self):
        exc = exceptions.ObjectNotFound()
        self.assertEqual(
            exc.to_jsonapi(),
            [{
                "status": '404',
                "title": "Object not found"
            }])

    def test_from_message(self):
        exc = exceptions.ObjectNotFound.from_message("Could not find")
        self.assertEqual(len(exc.errors), 1)
        self.assertEqual(exc.to_jsonapi(),
                         [{
                             "status": '404',
                             "title": "Object not found",
                             "detail": "Could not find",
                         }])

    def test_multiple_errors(self):
        exc = exceptions.ValidationError(
            errors=[
                errors.Error(
                    title="error 1",
                    source=errors.Source(parameter="filter")
                    ),
                errors.Error(
                    title="error 2",
                    source=errors.Source(parameter="sort")
                ),
            ]
        )
        self.assertEqual(
            exc.to_jsonapi(),
            [
                {
                    "title": "error 1",
                    "source": {
                        "parameter": "filter"
                    }
                },
                {
                    "title": "error 2",
                    "source": {
                        "parameter": "sort"
                    }
                }
            ])

    def test_invalid_field_init(self):
        exc = exceptions.InvalidFields()
        self.assertEqual(
            exc.to_jsonapi(),
            [{
                "status": '400',
                "title": "Invalid fields querystring parameter",
                "source": {
                    "parameter": "fields"
                }
            }])

    def test_invalid_include_init(self):
        exc = exceptions.InvalidInclude()
        self.assertEqual(
            exc.to_jsonapi(),
            [{
                "status": '400',
                "title": "Invalid include querystring parameter",
                "source": {
                    "parameter": "include"
                }
            }])

    def test_invalid_filters_init(self):
        exc = exceptions.InvalidFilters()
        self.assertEqual(
            exc.to_jsonapi(),
            [{
                "status": '400',
                "title": "Invalid filters querystring parameter",
                "source": {
                    "parameter": "filters"
                }
            }])

    def test_invalid_sort_init(self):
        exc = exceptions.InvalidSort()
        self.assertEqual(
            exc.to_jsonapi(),
            [{
                "status": '400',
                "title": "Invalid sort querystring parameter",
                "source": {
                    "parameter": "sort"
                }
            }])
