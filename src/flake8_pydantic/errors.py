import ast
from abc import ABC
from dataclasses import dataclass
from typing import ClassVar

from ._compat import Self


@dataclass
class Error(ABC):
    error_code: ClassVar[str]
    message: ClassVar[str]
    lineno: int
    col_offset: int

    @classmethod
    def from_node(cls, node: ast.AST) -> Self:
        return cls(lineno=node.lineno, col_offset=node.col_offset)

    def as_flake8_error(self) -> tuple[int, int, str]:
        return (self.lineno, self.col_offset, f"{self.error_code} {self.message}")


class PYD001(Error):
    error_code = "PYD001"
    message = "Non-annotated attribute"
