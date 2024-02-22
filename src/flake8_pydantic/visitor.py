import ast

from ._utils import get_decorator_names, is_pydantic_model
from .errors import PYD001, Error

CHECKED_CLASSES = {"BaseModel", "RootModel", "TypedDict", "dataclass"}


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: list[Error] = []

    def enter_class(self, class_type: str, body: list[ast.stmt]) -> None:
        self.current_class_type = class_type
        self.current_class_body = body

    def _check_pyd_001(self, node: ast.ClassDef):
        if is_pydantic_model(node):
            invalid_assignments = [
                assign
                for assign in node.body
                if isinstance(assign, ast.Assign)
                if isinstance(assign.targets[0], ast.Name)
                if not assign.targets[0].id.startswith("_")
            ]
            for assignment in invalid_assignments:
                self.errors.append(PYD001.from_node(assignment))

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_type = next((b.id for b in node.bases if isinstance(b, ast.Name) and b.id in CHECKED_CLASSES), None)
        if class_type is None:
            is_dataclass = "dataclass" in get_decorator_names(node.decorator_list)
            if is_dataclass:
                class_type = "dataclass"

        node.body

        self.generic_visit(node)
