from __future__ import annotations

import ast

import pytest

from flake8_pydantic.errors import PYD004, Error
from flake8_pydantic.visitor import Visitor

PYD004_1 = """
class Model(BaseModel):
    a: Annotated[int, Field(default=1, description="")]
"""

PYD004_2 = """
class Model(BaseModel):
    a: Annotated[int, Unrelated(), Field(default=1)]
"""


@pytest.mark.parametrize(
    ["source", "expected"],
    [
        (PYD004_1, [PYD004(3, 4)]),
        (PYD004_2, [PYD004(3, 4)]),
    ],
)
def test_pyd004(source: str, expected: list[Error]) -> None:
    module = ast.parse(source)
    visitor = Visitor()
    visitor.visit(module)

    assert visitor.errors == expected
