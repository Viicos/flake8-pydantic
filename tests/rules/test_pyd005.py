from __future__ import annotations

import ast

import pytest

from flake8_pydantic.errors import PYD005, Error
from flake8_pydantic.visitor import Visitor

PYD005_1 = """
class Model(BaseModel):
    date: date
"""

PYD005_2 = """
class Model(BaseModel):
    date: dict[str, date]
"""

PYD005_3 = """
class Model(BaseModel):
    date: Annotated[list[date], ...]
"""

PYD005_4 = """
class Model(BaseModel):
    date: int = 1
    foo: date
"""

PYD005_5 = """
class Model(BaseModel):
    date: Union[date, None] = None
"""

PYD005_6 = """
class Model(BaseModel):
    date: int | date | None = None
"""

# OK:

PYD005_7 = """
class Model(BaseModel):
    foo: date | None = None
    date: int
"""


@pytest.mark.parametrize(
    ["source", "expected"],
    [
        (PYD005_1, [PYD005(3, 4)]),
        (PYD005_2, [PYD005(3, 4)]),
        (PYD005_3, [PYD005(3, 4)]),
        (PYD005_4, [PYD005(4, 4)]),
        (PYD005_5, [PYD005(3, 4)]),
        (PYD005_6, [PYD005(3, 4)]),
        (PYD005_7, []),
    ],
)
def test_pyd003(source: str, expected: list[Error]) -> None:
    module = ast.parse(source)
    visitor = Visitor()
    visitor.visit(module)

    assert visitor.errors == expected
