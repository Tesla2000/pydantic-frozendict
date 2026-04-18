from collections.abc import Hashable
from collections.abc import Mapping
from types import GenericAlias
from typing import Any
from typing import get_args
from typing import TypeVar

from frozendict import frozendict
from pydantic._internal._schema_generation_shared import (
    CallbackGetCoreSchemaHandler,
)
from pydantic_core import core_schema
from pydantic_core.core_schema import AfterValidatorFunctionSchema

K = TypeVar("K", bound=Hashable)
V = TypeVar("V", covariant=True)


class PydanticFrozendict(frozendict[K, V]):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: GenericAlias, handler: CallbackGetCoreSchemaHandler
    ) -> AfterValidatorFunctionSchema:
        args = get_args(source_type)
        if len(args) == 2:
            key_schema = handler.generate_schema(args[0])
            value_schema = handler.generate_schema(args[1])
        else:
            key_schema = core_schema.any_schema()
            value_schema = core_schema.any_schema()

        def _to_dict(value: Any) -> Any:
            if isinstance(value, Mapping):
                return dict(value)
            return value

        def _to_frozendict(value: Any) -> "PydanticFrozendict[Any, Any]":
            return cls(value)

        def _to_serializable_dict(value: Any) -> dict[Any, Any]:
            return dict(value)

        dict_schema = core_schema.dict_schema(key_schema, value_schema)

        return core_schema.no_info_after_validator_function(
            _to_frozendict,
            core_schema.no_info_before_validator_function(
                _to_dict, dict_schema
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                _to_serializable_dict, return_schema=dict_schema
            ),
        )


__all__ = [
    "PydanticFrozendict",
]
