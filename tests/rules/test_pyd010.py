import ast

import pytest

from flake8_pydantic.errors import PYD010, Error
from flake8_pydantic.visitor import Visitor

PYD010_1 = """
class Model(TypedDict):
    __pydantic_config__ = {}
"""

PYD010_2 = """
class Model(TypedDict):
    __pydantic_config__: dict = {}
"""

# Works with any class, as we can't accurately determine if in a `TypedDict` subclass
PYD010_3 = """
class Model:
    __pydantic_config__: dict = {}
"""


@pytest.mark.parametrize(
    ["source", "expected"],
    [
        (PYD010_1, [PYD010(3, 4)]),
        (PYD010_2, [PYD010(3, 4)]),
        (PYD010_3, [PYD010(3, 4)]),
    ],
)
def test_pyd010(source: str, expected: list[Error]) -> None:
    module = ast.parse(source)
    visitor = Visitor()
    visitor.visit(module)

    assert visitor.errors == expected
