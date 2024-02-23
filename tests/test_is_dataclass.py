from __future__ import annotations

import ast
from typing import cast

import pytest

from flake8_pydantic._utils import is_dataclass

# Positive cases:
DATACLASS_1 = """
@dataclass
class Model:
    pass
"""

DATACLASS_2 = """
@pydantic_dataclass
class Model:
    pass
"""

DATACLASS_3 = """
@dataclasses.dataclass
class Model:
    pass
"""

DATACLASS_4 = """
@dataclasses.dataclass()
@otherdec(arg=1)
class Model:
    pass
"""


@pytest.mark.parametrize(
    ["source", "expected"],
    [
        (DATACLASS_1, True),
        (DATACLASS_2, True),
        (DATACLASS_3, True),
        (DATACLASS_4, True),
    ],
)
def test_is_dataclass(source: str, expected: bool) -> None:
    class_def = cast(ast.ClassDef, ast.parse(source).body[0])
    assert is_dataclass(class_def) == expected
