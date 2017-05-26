import unittest

from tornadowebapi.registry import Registry
from tornadowebapi.tests.resource_handlers import StudentDetails


class TestRegistry(unittest.TestCase):
    def test_instantiation(self):
        reg = Registry()

        # Register the classes.
        reg.register(StudentDetails, "/students/(.*)/")

        api_handlers = reg.api_handlers("/foo")
        self.assertEqual(len(api_handlers), 1)

    def test_double_registration(self):
        reg = Registry()

        reg.register(StudentDetails, "/students/(.*)/")
        with self.assertRaises(ValueError):
            reg.register(StudentDetails, "/students/(.*)/")

    def test_incorrect_class_registration(self):
        reg = Registry()

        with self.assertRaises(TypeError):
            reg.register("hello", "/students/(.*)/")

        with self.assertRaises(TypeError):
            reg.register(int, "/students/(.*)/")

    def test_authenticator(self):
        reg = Registry()

        self.assertIsNotNone(reg.authenticator)

    def test_empty_api_handlers(self):
        reg = Registry()
        api_handlers = reg.api_handlers("/foo")
        self.assertEqual(len(api_handlers), 0)
