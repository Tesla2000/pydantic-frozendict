import json
from collections.abc import Iterator
from collections.abc import Mapping
from typing import Any

import pytest
from frozendict import frozendict
from pydantic import BaseModel
from pydantic import ValidationError
from pydantic_frozendict import PydanticFrozendict


class TestPydanticFrozendict:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        class Foo(BaseModel):
            dictionary: PydanticFrozendict[str, int]

        self.Foo = Foo

    def test_field_is_pydantic_frozendict(self) -> None:
        foo = self.Foo(dictionary={"a": 1})
        assert isinstance(foo.dictionary, PydanticFrozendict)

    def test_immutable(self) -> None:
        foo = self.Foo(dictionary={"a": 1})
        with pytest.raises(TypeError):
            foo.dictionary["b"] = 2  # type: ignore[index]

    def test_dict_input_converted(self) -> None:
        foo = self.Foo(dictionary={"a": 1, "b": 2})
        assert foo.dictionary == PydanticFrozendict({"a": 1, "b": 2})

    def test_frozendict_input(self) -> None:
        foo = self.Foo(dictionary=frozendict({"a": 1}))
        assert isinstance(foo.dictionary, PydanticFrozendict)
        assert foo.dictionary["a"] == 1

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
        assert isinstance(foo.dictionary, PydanticFrozendict)
        assert foo.dictionary["a"] == 1

    def test_invalid_key_type_raises_validation_error(self) -> None:
        class Foo(BaseModel):
            dictionary: PydanticFrozendict[int, str]

        with pytest.raises(ValidationError):
            Foo(dictionary={"not_an_int": "value"})

    def test_invalid_value_type_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError):
            self.Foo(dictionary={"a": "not_an_int"})

    def test_non_mapping_input_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError):
            self.Foo(dictionary="not_a_mapping")

    def test_empty_dict(self) -> None:
        foo = self.Foo(dictionary={})
        assert isinstance(foo.dictionary, PydanticFrozendict)
        assert len(foo.dictionary) == 0

    def test_untyped_accepts_any_keys_and_values(self) -> None:
        class Foo(BaseModel):
            dictionary: PydanticFrozendict[Any, Any]

        foo = Foo(dictionary={"a": 1, "b": [3, 4]})
        assert isinstance(foo.dictionary, PydanticFrozendict)

    def test_value_coercion(self) -> None:
        foo = self.Foo(dictionary={"a": "5"})
        assert foo.dictionary["a"] == 5

    def test_model_validate(self) -> None:
        foo = self.Foo.model_validate({"dictionary": {"a": 1}})
        assert isinstance(foo.dictionary, PydanticFrozendict)
        assert foo.dictionary["a"] == 1

    def test_model_dump(self) -> None:
        foo = self.Foo(dictionary={"a": 1})
        assert foo.model_dump()["dictionary"] == {"a": 1}

    def test_model_validate_json(self) -> None:
        foo = self.Foo.model_validate_json('{"dictionary": {"a": 1}}')
        assert isinstance(foo.dictionary, PydanticFrozendict)
        assert foo.dictionary["a"] == 1

    def test_model_dump_json(self) -> None:
        foo = self.Foo(dictionary={"a": 1})
        json_str = foo.model_dump_json()
        assert '"dictionary"' in json_str
        assert '"a"' in json_str

    def test_nested_pydantic_model_values(self) -> None:
        class Bar(BaseModel):
            value: int

        class Foo(BaseModel):
            dictionary: PydanticFrozendict[str, Bar]

        foo = Foo(dictionary={"x": Bar(value=42)})
        assert isinstance(foo.dictionary, PydanticFrozendict)
        assert foo.dictionary["x"].value == 42

    def test_multiple_entries(self) -> None:
        data = {str(i): i for i in range(10)}
        foo = self.Foo(dictionary=data)
        assert len(foo.dictionary) == 10
        assert all(foo.dictionary[k] == v for k, v in data.items())


class TestPydanticFrozendictNoTypeArgs:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        class Foo(BaseModel):
            dictionary: PydanticFrozendict  # type: ignore[type-arg]

        self.Foo = Foo

    def test_no_type_args_accepts_any_input(self) -> None:
        foo = self.Foo(dictionary={"a": 1, "b": "hello"})
        assert isinstance(foo.dictionary, PydanticFrozendict)

    def test_no_type_args_frozendict_input(self) -> None:
        foo = self.Foo(dictionary=frozendict({"x": [1, 2, 3]}))
        assert isinstance(foo.dictionary, PydanticFrozendict)
        assert foo.dictionary["x"] == [1, 2, 3]

    def test_no_type_args_non_mapping_raises(self) -> None:
        with pytest.raises(ValidationError):
            self.Foo(dictionary=42)


class TestPydanticFrozendictUntyped:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        class Foo(BaseModel):
            dictionary: PydanticFrozendict[Any, Any]

        self.Foo = Foo

    def test_untyped_dict_input(self) -> None:
        foo = self.Foo(dictionary={"a": 1, "b": "hello"})
        assert isinstance(foo.dictionary, PydanticFrozendict)

    def test_untyped_frozendict_input(self) -> None:
        foo = self.Foo(dictionary=frozendict({"x": [1, 2, 3]}))
        assert isinstance(foo.dictionary, PydanticFrozendict)
        assert foo.dictionary["x"] == [1, 2, 3]

    def test_untyped_preserves_value_types_without_coercion(self) -> None:
        foo = self.Foo(dictionary={"int": 1, "str": "s", "list": [1, 2]})
        assert isinstance(foo.dictionary["int"], int)
        assert isinstance(foo.dictionary["str"], str)
        assert isinstance(foo.dictionary["list"], list)

    def test_untyped_list_of_tuples_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError):
            self.Foo(dictionary=[("a", 1), ("b", 2)])

    def test_untyped_non_mapping_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError):
            self.Foo(dictionary=42)

    def test_untyped_model_dump_returns_plain_dict(self) -> None:
        foo = self.Foo(dictionary={"a": 1})
        dumped = foo.model_dump()
        assert isinstance(dumped["dictionary"], dict)
        assert not isinstance(dumped["dictionary"], frozendict)

    def test_untyped_model_dump_json_and_validate_round_trip(self) -> None:
        foo = self.Foo(dictionary={"a": 1, "b": 2})
        restored = self.Foo.model_validate_json(foo.model_dump_json())
        assert isinstance(restored.dictionary, PydanticFrozendict)
        assert dict(restored.dictionary) == {"a": 1, "b": 2}


class TestPydanticFrozendictFrozendictInput:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        class Foo(BaseModel):
            dictionary: PydanticFrozendict[str, int]

        self.Foo = Foo

    def test_frozendict_result_is_pydantic_frozendict_not_plain_frozendict(
        self,
    ) -> None:
        foo = self.Foo(dictionary=frozendict({"a": 1}))
        assert isinstance(foo.dictionary, PydanticFrozendict)
        assert type(foo.dictionary) is not frozendict

    def test_frozendict_values_are_validated(self) -> None:
        with pytest.raises(ValidationError):
            self.Foo(dictionary=frozendict({"a": "not_an_int"}))

    def test_frozendict_value_coercion(self) -> None:
        foo = self.Foo(dictionary=frozendict({"a": "5"}))
        assert foo.dictionary["a"] == 5

    def test_frozendict_preserves_all_entries(self) -> None:
        data = frozendict({"x": 10, "y": 20, "z": 30})
        foo = self.Foo(dictionary=data)
        assert dict(foo.dictionary) == dict(data)


class TestPydanticFrozendictListOfTuples:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        class Foo(BaseModel):
            dictionary: PydanticFrozendict[str, int]

        self.Foo = Foo

    def test_list_of_tuples_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError):
            self.Foo(dictionary=[("a", 1), ("b", 2)])

    def test_untyped_list_of_tuples_raises_validation_error(self) -> None:
        class Foo(BaseModel):
            dictionary: PydanticFrozendict[Any, Any]

        with pytest.raises(ValidationError):
            Foo(dictionary=[("a", 1)])

    def test_empty_list_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError):
            self.Foo(dictionary=[])


class TestPydanticFrozendictSerialization:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        class Foo(BaseModel):
            dictionary: PydanticFrozendict[str, int]

        self.Foo = Foo

    def test_model_dump_value_is_plain_dict(self) -> None:
        foo = self.Foo(dictionary={"a": 1})
        dumped = foo.model_dump()
        assert isinstance(dumped["dictionary"], dict)
        assert not isinstance(dumped["dictionary"], frozendict)

    def test_model_dump_preserves_entries(self) -> None:
        foo = self.Foo(dictionary={"a": 1, "b": 2})
        assert foo.model_dump()["dictionary"] == {"a": 1, "b": 2}

    def test_model_dump_json_is_valid_json_object(self) -> None:
        foo = self.Foo(dictionary={"a": 1})
        parsed = json.loads(foo.model_dump_json())
        assert parsed["dictionary"] == {"a": 1}

    def test_json_round_trip_produces_pydantic_frozendict(self) -> None:
        foo = self.Foo(dictionary={"a": 1, "b": 2})
        restored = self.Foo.model_validate_json(foo.model_dump_json())
        assert isinstance(restored.dictionary, PydanticFrozendict)
        assert dict(restored.dictionary) == {"a": 1, "b": 2}

    def test_model_dump_then_validate_round_trip(self) -> None:
        foo = self.Foo(dictionary={"a": 1, "b": 2})
        restored = self.Foo.model_validate(foo.model_dump())
        assert isinstance(restored.dictionary, PydanticFrozendict)
        assert dict(restored.dictionary) == {"a": 1, "b": 2}
