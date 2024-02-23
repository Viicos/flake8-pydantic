from __future__ import annotations

import ast

import pytest

from flake8_pydantic.errors import PYD002, Error
from flake8_pydantic.visitor import Visitor

PYD002_MODEL = """
class Model(BaseModel):
    a = 1
"""

PYD002_MODEL_PRIVATE_FIELD = """
class Model(BaseModel):
    _a = 1
"""

PYD002_DATACLASS = """
@dataclass
class Model:
    a = 1
"""


@pytest.mark.parametrize(
    ["source", "expected"],
    [
        (PYD002_MODEL, [PYD002(3, 4)]),
        (PYD002_MODEL_PRIVATE_FIELD, []),
        (PYD002_DATACLASS, []),
    ],
)
def test_pyd002(source: str, expected: list[Error]) -> None:
    module = ast.parse(source)
    visitor = Visitor()
    visitor.visit(module)

    assert visitor.errors == expected
