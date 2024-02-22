from __future__ import annotations

import ast
from importlib.metadata import version
from typing import Any, Iterator


class Plugin:
    name = "flake8-pydantic"
    version = version(name)

    def __init__(self, tree: ast.AST) -> None:
        self._tree = tree

    def run(self) -> Iterator[tuple[int, int, str, type[Any]]]:
        pass
