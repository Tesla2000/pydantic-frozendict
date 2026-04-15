from unittest import TestCase


class TestImport(TestCase):
    @staticmethod
    def test_import() -> None:
        import pydantic_frozendict

        _ = pydantic_frozendict
