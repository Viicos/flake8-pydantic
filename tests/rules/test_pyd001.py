from __future__ import annotations

import ast

import pytest

from flake8_pydantic.errors import PYD001, Error
from flake8_pydantic.visitor import Visitor

PYD001_MODEL = """
class Model(BaseModel):
    a: int = Field(1)
"""

PYD001_DATACLASS = """
@dataclass
class Model:
    a: int = Field(1)
"""

PYD001_OK = """
class Model(BaseModel):
    a: int = Field(default=1)
"""


@pytest.mark.parametrize(
    ["source", "expected"],
    [
        (PYD001_MODEL, [PYD001(3, 4)]),
        (PYD001_DATACLASS, [PYD001(4, 4)]),
        (PYD001_OK, []),
    ],
)
def test_pyd001(source: str, expected: list[Error]) -> None:
    module = ast.parse(source)
    visitor = Visitor()
    visitor.visit(module)

    assert visitor.errors == expected
