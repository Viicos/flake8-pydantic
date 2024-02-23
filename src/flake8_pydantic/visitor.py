import ast
from collections import deque
from typing import Literal

from ._compat import TypeAlias
from ._utils import is_dataclass, is_pydantic_model
from .errors import PYD001, PYD002, PYD010, Error

ClassType: TypeAlias = Literal["pydantic_model", "dataclass", "other_class"]


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: list[Error] = []
        self.class_stack: deque[ClassType] = deque()

    def enter_class(self, node: ast.ClassDef) -> None:
        if is_pydantic_model(node):
            self.class_stack.append("pydantic_model")
        elif is_dataclass(node):
            self.class_stack.append("dataclass")
        else:
            self.class_stack.append("other_class")

    def leave_class(self) -> None:
        self.class_stack.pop()

    @property
    def current_class(self) -> ClassType:
        return self.class_stack[-1]

    def _check_pyd_001(self, node: ast.AnnAssign) -> None:
        if (
            self.current_class in {"pydantic_model", "dataclass"}
            and isinstance(node.value, ast.Call)
            and (
                (isinstance(node.value.func, ast.Name) and node.value.func.id == "Field")
                or (isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "Field")
            )
            and len(node.value.args) >= 1
        ):
            self.errors.append(PYD001.from_node(node))

    def _check_pyd_002(self, node: ast.ClassDef) -> None:
        if self.current_class == "pydantic_model":
            invalid_assignments = [
                assign
                for assign in node.body
                if isinstance(assign, ast.Assign)
                if isinstance(assign.targets[0], ast.Name)
                if not assign.targets[0].id.startswith("_")
            ]
            for assignment in invalid_assignments:
                self.errors.append(PYD002.from_node(assignment))

    def _check_pyd_010(self, node: ast.ClassDef) -> None:
        if self.current_class == "other_class":
            for stmt in node.body:
                if (
                    isinstance(stmt, ast.AnnAssign)
                    and isinstance(stmt.target, ast.Name)
                    and stmt.target.id == "__pydantic_config__"
                ):
                    # __pydantic_config__: ... = ...
                    self.errors.append(PYD010.from_node(stmt))
                if isinstance(stmt, ast.Assign) and any(
                    t.id == "__pydantic_config__" for t in stmt.targets if isinstance(t, ast.Name)
                ):
                    # __pydantic_config__ = ...
                    self.errors.append(PYD010.from_node(stmt))

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.enter_class(node)
        self._check_pyd_002(node)
        self._check_pyd_010(node)
        self.generic_visit(node)
        self.leave_class()

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._check_pyd_001(node)
        self.generic_visit(node)
