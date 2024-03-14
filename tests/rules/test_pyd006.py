from __future__ import annotations

import ast

import pytest

from flake8_pydantic.errors import PYD006, Error
from flake8_pydantic.visitor import Visitor

PYD006_1 = """
class Model(BaseModel):
    x: int
    x: str = "1"
"""

PYD006_2 = """
class Model(BaseModel):
    x: int
    y: int
"""


@pytest.mark.parametrize(
    ["source", "expected"],
    [
        (PYD006_1, [PYD006(4, 4)]),
        (PYD006_2, []),
    ],
)
def test_pyd006(source: str, expected: list[Error]) -> None:
    module = ast.parse(source)
    visitor = Visitor()
    visitor.visit(module)

    assert visitor.errors == expected
