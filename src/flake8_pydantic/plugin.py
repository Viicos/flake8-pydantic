from __future__ import annotations

import ast
from collections.abc import Iterator
from importlib.metadata import version
from typing import Any

from .visitor import Visitor


class Plugin:
    name = "flake8-pydantic"
    version = version(name)

    def __init__(self, tree: ast.AST) -> None:
        self._tree = tree

    def run(self) -> Iterator[tuple[int, int, str, type[Any]]]:
        visitor = Visitor()
        visitor.visit(self._tree)
        for error in visitor.errors:
            yield *error.as_flake8_error(), type(self)
