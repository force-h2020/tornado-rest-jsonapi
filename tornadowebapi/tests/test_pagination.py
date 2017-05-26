import unittest

from marshmallow_jsonapi import Schema
from ..pagination import pagination_links
from ..querystring import QueryStringManager as QSManager


class TestPagination(unittest.TestCase):
    def test_no_pagination_need(self):
        qs = QSManager({"page[size]": [b"80"]}, Schema)
        links = pagination_links(50, qs, "http://example.com/foos")
        self.assertEqual(links, {
            "self": "http://example.com/foos?page%5Bsize%5D=80"
        })

    def test_pagination(self):
        self.maxDiff = None
        qs = QSManager({"page[size]": [b"10"]}, Schema)
        links = pagination_links(50, qs, "http://example.com/foos")
        self.assertEqual(links, {
            "self": "http://example.com/foos?page%5Bsize%5D=10",
            "first": "http://example.com/foos?page%5Bsize%5D=10",
            "next": "http://example.com/foos?page%5Bnumber%5D=1&page%5Bsize%5D=10",  # noqa
            "last": "http://example.com/foos?page%5Bnumber%5D=4&page%5Bsize%5D=10"  # noqa
        })

        qs = QSManager({"page[size]": [b"10"],
                        "page[number]": [b'1']}, Schema)
        links = pagination_links(50, qs, "http://example.com/foos")
        self.assertEqual(links, {
            "self": "http://example.com/foos?page%5Bnumber%5D=1&page%5Bsize%5D=10",  # noqa
            "first": "http://example.com/foos?page%5Bsize%5D=10",
            "prev": "http://example.com/foos?page%5Bnumber%5D=0&page%5Bsize%5D=10",  # noqa
            "next": "http://example.com/foos?page%5Bnumber%5D=2&page%5Bsize%5D=10",  # noqa
            "last": "http://example.com/foos?page%5Bnumber%5D=4&page%5Bsize%5D=10"  # noqa
        })

        qs = QSManager({"page[size]": [b"10"],
                        "page[number]": [b'2']}, Schema)
        links = pagination_links(50, qs, "http://example.com/foos")
        self.assertEqual(links, {
            "self": "http://example.com/foos?page%5Bnumber%5D=2&page%5Bsize%5D=10",  # noqa
            "first": "http://example.com/foos?page%5Bsize%5D=10",
            "prev": "http://example.com/foos?page%5Bnumber%5D=1&page%5Bsize%5D=10",  # noqa
            "next": "http://example.com/foos?page%5Bnumber%5D=3&page%5Bsize%5D=10",  # noqa
            "last": "http://example.com/foos?page%5Bnumber%5D=4&page%5Bsize%5D=10"  # noqa
        })

        qs = QSManager({"page[size]": [b"10"],
                        "page[number]": [b'4']}, Schema)
        links = pagination_links(50, qs, "http://example.com/foos")
        self.assertEqual(links, {
            "self": "http://example.com/foos?page%5Bnumber%5D=4&page%5Bsize%5D=10",  # noqa
            "first": "http://example.com/foos?page%5Bsize%5D=10",
            "prev": "http://example.com/foos?page%5Bnumber%5D=3&page%5Bsize%5D=10",  # noqa
            "last": "http://example.com/foos?page%5Bnumber%5D=4&page%5Bsize%5D=10"  # noqa
        })
