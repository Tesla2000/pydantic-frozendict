[![codecov](https://codecov.io/gh/Tesla2000/pydantic-frozendict/branch/main/graph/badge.svg)](https://codecov.io/gh/Tesla2000/pydantic-frozendict)

# pydantic-frozendict

Frozendict that can be used as pydantic field annotation without a need to use arbitrary type.

## Install

```bash
pip install pydantic-frozendict
```

## Usage

```python
from pydantic import BaseModel

from pydantic_frozendict import PydanticFrozendict


class Item(BaseModel):
    tags: PydanticFrozendict[str, int]


item = Item(tags={"a": 1})
assert item.tags["a"] == 1
```
