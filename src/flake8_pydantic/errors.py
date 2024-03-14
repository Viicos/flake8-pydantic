from __future__ import annotations

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
    message = "Positional argument for Field default argument"


class PYD002(Error):
    error_code = "PYD002"
    message = "Non-annotated attribute inside Pydantic model"


class PYD003(Error):
    error_code = "PYD003"
    message = "Unecessary Field call to specify a default value"


class PYD004(Error):
    error_code = "PYD004"
    message = "Default argument specified in annotated"


class PYD005(Error):
    error_code = "PYD005"
    message = "Field name overrides annotation"


class PYD006(Error):
    error_code = "PYD006"
    message = "Duplicate field name"


class PYD010(Error):
    error_code = "PYD010"
    message = "Usage of __pydantic_config__"
