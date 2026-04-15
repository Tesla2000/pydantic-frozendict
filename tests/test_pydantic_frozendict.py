from collections.abc import Iterator
from collections.abc import Mapping
from typing import Any
from unittest import TestCase

from frozendict import frozendict
from pydantic import BaseModel
from pydantic import ValidationError
from pydantic_frozendict import PydanticFrozendict


class TestPydanticFrozendict(TestCase):
    def setUp(self) -> None:
        class Foo(BaseModel):
            dictionary: PydanticFrozendict[str, int]

        self.Foo = Foo

    def test_field_is_pydantic_frozendict(self) -> None:
        foo = self.Foo(dictionary={"a": 1})
        self.assertIsInstance(foo.dictionary, PydanticFrozendict)

    def test_immutable(self) -> None:
        foo = self.Foo(dictionary={"a": 1})
        with self.assertRaises(TypeError):
            foo.dictionary["b"] = 2  # type: ignore[index]

    def test_dict_input_converted(self) -> None:
        foo = self.Foo(dictionary={"a": 1, "b": 2})
        self.assertEqual(foo.dictionary, PydanticFrozendict({"a": 1, "b": 2}))

    def test_frozendict_input(self) -> None:
        foo = self.Foo(dictionary=frozendict({"a": 1}))
        self.assertIsInstance(foo.dictionary, PydanticFrozendict)
        self.assertEqual(foo.dictionary["a"], 1)

    def test_custom_mapping_input(self) -> None:
        class CustomMapping(Mapping[str, int]):
            def __init__(self, data: dict[str, int]) -> None:
                self._data = data

            def __getitem__(self, key: str) -> int:
                return self._data[key]

            def __iter__(self) -> Iterator[str]:
                return iter(self._data)

            def __len__(self) -> int:
                return len(self._data)

        foo = self.Foo(dictionary=CustomMapping({"a": 1}))
        self.assertIsInstance(foo.dictionary, PydanticFrozendict)
        self.assertEqual(foo.dictionary["a"], 1)

    def test_invalid_key_type_raises_validation_error(self) -> None:
        class Foo(BaseModel):
            dictionary: PydanticFrozendict[int, str]

        with self.assertRaises(ValidationError):
            Foo(dictionary={"not_an_int": "value"})

    def test_invalid_value_type_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            self.Foo(dictionary={"a": "not_an_int"})

    def test_non_mapping_input_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            self.Foo(dictionary="not_a_mapping")

    def test_empty_dict(self) -> None:
        foo = self.Foo(dictionary={})
        self.assertIsInstance(foo.dictionary, PydanticFrozendict)
        self.assertEqual(len(foo.dictionary), 0)

    def test_untyped_accepts_any_keys_and_values(self) -> None:
        class Foo(BaseModel):
            dictionary: PydanticFrozendict[Any, Any]

        foo = Foo(dictionary={"a": 1, "b": [3, 4]})
        self.assertIsInstance(foo.dictionary, PydanticFrozendict)

    def test_value_coercion(self) -> None:
        foo = self.Foo(dictionary={"a": "5"})
        self.assertEqual(foo.dictionary["a"], 5)

    def test_model_validate(self) -> None:
        foo = self.Foo.model_validate({"dictionary": {"a": 1}})
        self.assertIsInstance(foo.dictionary, PydanticFrozendict)
        self.assertEqual(foo.dictionary["a"], 1)

    def test_model_dump(self) -> None:
        foo = self.Foo(dictionary={"a": 1})
        dumped = foo.model_dump()
        self.assertEqual(dumped["dictionary"], {"a": 1})

    def test_model_validate_json(self) -> None:
        foo = self.Foo.model_validate_json('{"dictionary": {"a": 1}}')
        self.assertIsInstance(foo.dictionary, PydanticFrozendict)
        self.assertEqual(foo.dictionary["a"], 1)

    def test_model_dump_json(self) -> None:
        foo = self.Foo(dictionary={"a": 1})
        json_str = foo.model_dump_json()
        self.assertIn('"dictionary"', json_str)
        self.assertIn('"a"', json_str)

    def test_nested_pydantic_model_values(self) -> None:
        class Bar(BaseModel):
            value: int

        class Foo(BaseModel):
            dictionary: PydanticFrozendict[str, Bar]

        foo = Foo(dictionary={"x": Bar(value=42)})
        self.assertIsInstance(foo.dictionary, PydanticFrozendict)
        self.assertEqual(foo.dictionary["x"].value, 42)

    def test_multiple_entries(self) -> None:
        data = {str(i): i for i in range(10)}
        foo = self.Foo(dictionary=data)
        self.assertEqual(len(foo.dictionary), 10)
        self.assertTrue(all(foo.dictionary[k] == v for k, v in data.items()))


class TestPydanticFrozendictUntyped(TestCase):
    def setUp(self) -> None:
        class Foo(BaseModel):
            dictionary: PydanticFrozendict[Any, Any]

        self.Foo = Foo

    def test_untyped_dict_input(self) -> None:
        foo = self.Foo(dictionary={"a": 1, "b": "hello"})
        self.assertIsInstance(foo.dictionary, PydanticFrozendict)

    def test_untyped_frozendict_input(self) -> None:
        foo = self.Foo(dictionary=frozendict({"x": [1, 2, 3]}))
        self.assertIsInstance(foo.dictionary, PydanticFrozendict)
        self.assertEqual(foo.dictionary["x"], [1, 2, 3])

    def test_untyped_preserves_value_types_without_coercion(self) -> None:
        foo = self.Foo(dictionary={"int": 1, "str": "s", "list": [1, 2]})
        self.assertIsInstance(foo.dictionary["int"], int)
        self.assertIsInstance(foo.dictionary["str"], str)
        self.assertIsInstance(foo.dictionary["list"], list)

    def test_untyped_list_of_tuples_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            self.Foo(dictionary=[("a", 1), ("b", 2)])

    def test_untyped_non_mapping_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            self.Foo(dictionary=42)

    def test_untyped_model_dump_returns_plain_dict(self) -> None:
        foo = self.Foo(dictionary={"a": 1})
        dumped = foo.model_dump()
        self.assertIsInstance(dumped["dictionary"], dict)
        self.assertNotIsInstance(dumped["dictionary"], frozendict)

    def test_untyped_model_dump_json_and_validate_round_trip(self) -> None:
        foo = self.Foo(dictionary={"a": 1, "b": 2})
        json_str = foo.model_dump_json()
        restored = self.Foo.model_validate_json(json_str)
        self.assertIsInstance(restored.dictionary, PydanticFrozendict)
        self.assertEqual(dict(restored.dictionary), {"a": 1, "b": 2})


class TestPydanticFrozendictFrozendictInput(TestCase):
    def setUp(self) -> None:
        class Foo(BaseModel):
            dictionary: PydanticFrozendict[str, int]

        self.Foo = Foo

    def test_frozendict_result_is_pydantic_frozendict_not_plain_frozendict(
        self,
    ) -> None:
        foo = self.Foo(dictionary=frozendict({"a": 1}))
        self.assertIsInstance(foo.dictionary, PydanticFrozendict)
        self.assertNotEqual(type(foo.dictionary), frozendict)

    def test_frozendict_values_are_validated(self) -> None:
        with self.assertRaises(ValidationError):
            self.Foo(dictionary=frozendict({"a": "not_an_int"}))

    def test_frozendict_value_coercion(self) -> None:
        foo = self.Foo(dictionary=frozendict({"a": "5"}))
        self.assertEqual(foo.dictionary["a"], 5)

    def test_frozendict_preserves_all_entries(self) -> None:
        data = frozendict({"x": 10, "y": 20, "z": 30})
        foo = self.Foo(dictionary=data)
        self.assertEqual(dict(foo.dictionary), dict(data))


class TestPydanticFrozendictListOfTuples(TestCase):
    def setUp(self) -> None:
        class Foo(BaseModel):
            dictionary: PydanticFrozendict[str, int]

        self.Foo = Foo

    def test_list_of_tuples_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            self.Foo(dictionary=[("a", 1), ("b", 2)])

    def test_untyped_list_of_tuples_raises_validation_error(self) -> None:
        class Foo(BaseModel):
            dictionary: PydanticFrozendict[Any, Any]

        with self.assertRaises(ValidationError):
            Foo(dictionary=[("a", 1)])

    def test_empty_list_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            self.Foo(dictionary=[])


class TestPydanticFrozendictSerialization(TestCase):
    def setUp(self) -> None:
        class Foo(BaseModel):
            dictionary: PydanticFrozendict[str, int]

        self.Foo = Foo

    def test_model_dump_value_is_plain_dict(self) -> None:
        foo = self.Foo(dictionary={"a": 1})
        dumped = foo.model_dump()
        self.assertIsInstance(dumped["dictionary"], dict)
        self.assertNotIsInstance(dumped["dictionary"], frozendict)

    def test_model_dump_preserves_entries(self) -> None:
        foo = self.Foo(dictionary={"a": 1, "b": 2})
        self.assertEqual(foo.model_dump()["dictionary"], {"a": 1, "b": 2})

    def test_model_dump_json_is_valid_json_object(self) -> None:
        import json

        foo = self.Foo(dictionary={"a": 1})
        parsed = json.loads(foo.model_dump_json())
        self.assertEqual(parsed["dictionary"], {"a": 1})

    def test_json_round_trip_produces_pydantic_frozendict(self) -> None:
        foo = self.Foo(dictionary={"a": 1, "b": 2})
        restored = self.Foo.model_validate_json(foo.model_dump_json())
        self.assertIsInstance(restored.dictionary, PydanticFrozendict)
        self.assertEqual(dict(restored.dictionary), {"a": 1, "b": 2})

    def test_model_dump_then_validate_round_trip(self) -> None:
        foo = self.Foo(dictionary={"a": 1, "b": 2})
        restored = self.Foo.model_validate(foo.model_dump())
        self.assertIsInstance(restored.dictionary, PydanticFrozendict)
        self.assertEqual(dict(restored.dictionary), {"a": 1, "b": 2})
