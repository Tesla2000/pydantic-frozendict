from unittest import TestCase


class TestImport(TestCase):
    @staticmethod
    def test_import():
        import pydantic_frozendict

        _ = pydantic_frozendict
