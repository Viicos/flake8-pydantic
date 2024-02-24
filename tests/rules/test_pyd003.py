from __future__ import annotations

import ast

import pytest

from flake8_pydantic.errors import PYD003, Error
from flake8_pydantic.visitor import Visitor

PYD003_NOT_OK = """
class Model(BaseModel):
    a: int = Field(default=1)
"""

PYD003_OK = """
class Model(BaseModel):
    a: int = Field(default=1, description="")
"""


@pytest.mark.parametrize(
    ["source", "expected"],
    [
        (PYD003_NOT_OK, [PYD003(3, 4)]),
        (PYD003_OK, []),
    ],
)
def test_pyd003(source: str, expected: list[Error]) -> None:
    module = ast.parse(source)
    visitor = Visitor()
    visitor.visit(module)

    assert visitor.errors == expected
