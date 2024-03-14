from __future__ import annotations

import ast
from collections import deque
from typing import Literal

from ._compat import TypeAlias
from ._utils import extract_annotations, is_dataclass, is_function, is_name, is_pydantic_model
from .errors import PYD001, PYD002, PYD003, PYD004, PYD005, PYD006, PYD010, Error

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
            and is_function(node.value, "Field")
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

    def _check_pyd_003(self, node: ast.AnnAssign) -> None:
        if (
            self.current_class in {"pydantic_model", "dataclass"}
            and isinstance(node.value, ast.Call)
            and is_function(node.value, "Field")
            and len(node.value.keywords) == 1
            and node.value.keywords[0].arg == "default"
        ):
            self.errors.append(PYD003.from_node(node))

    def _check_pyd_004(self, node: ast.AnnAssign) -> None:
        if (
            self.current_class in {"pydantic_model", "dataclass"}
            and isinstance(node.annotation, ast.Subscript)
            and is_name(node.annotation.value, "Annotated")
            and isinstance(node.annotation.slice, ast.Tuple)
        ):
            field_call = next(
                (
                    elt
                    for elt in node.annotation.slice.elts
                    if isinstance(elt, ast.Call)
                    and is_function(elt, "Field")
                    and any(k.arg == "default" for k in elt.keywords)
                ),
                None,
            )
            if field_call is not None:
                self.errors.append(PYD004.from_node(node))

    def _check_pyd_005(self, node: ast.ClassDef) -> None:
        if self.current_class in {"pydantic_model", "dataclass"}:
            previous_targets: set[str] = set()

            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                    # TODO only add before if AnnAssign?
                    # the following seems to work:
                    # date: date
                    previous_targets.add(stmt.target.id)
                    if previous_targets & extract_annotations(stmt.annotation):
                        self.errors.append(PYD005.from_node(stmt))

    def _check_pyd_006(self, node: ast.ClassDef) -> None:
        if self.current_class in {"pydantic_model", "dataclass"}:
            previous_targets: set[str] = set()

            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                    if stmt.target.id in previous_targets:
                        self.errors.append(PYD006.from_node(stmt))

                    previous_targets.add(stmt.target.id)

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
        self._check_pyd_005(node)
        self._check_pyd_006(node)
        self._check_pyd_010(node)
        self.generic_visit(node)
        self.leave_class()

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._check_pyd_001(node)
        self._check_pyd_003(node)
        self._check_pyd_004(node)
        self.generic_visit(node)
