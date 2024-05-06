from __future__ import annotations

import ast


def get_decorator_names(decorator_list: list[ast.expr]) -> set[str]:
    names: set[str] = set()
    for dec in decorator_list:
        if isinstance(dec, ast.Call):
            names.add(dec.func.attr if isinstance(dec.func, ast.Attribute) else dec.func.id)  # type: ignore
        elif isinstance(dec, ast.Name):
            names.add(dec.id)
        elif isinstance(dec, ast.Attribute):
            names.add(dec.attr)

    return names


def _has_pydantic_model_base(node: ast.ClassDef, *, include_root_model: bool) -> bool:
    model_class_names = {"BaseModel"}
    if include_root_model:
        model_class_names.add("RootModel")

    for base in node.bases:
        if isinstance(base, ast.Name) and base.id in model_class_names:
            return True
        if isinstance(base, ast.Attribute) and base.attr in model_class_names:
            return True
    return False


def _has_model_config(node: ast.ClassDef) -> bool:
    for stmt in node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name) and stmt.target.id == "model_config":
            # model_config: ... = ...
            return True
        if isinstance(stmt, ast.Assign) and any(
            t.id == "model_config" for t in stmt.targets if isinstance(t, ast.Name)
        ):
            # model_config = ...
            return True
    return False


PYDANTIC_FIELD_ARGUMENTS = {
    "default",
    "default_factory",
    "alias",
    "alias_priority",
    "validation_alias",
    "title",
    "description",
    "examples",
    "exclude",
    "discriminator",
    "json_schema_extra",
    "frozen",
    "validate_default",
    "repr",
    "init",
    "init_var",
    "kw_only",
    "pattern",
    "strict",
    "gt",
    "ge",
    "lt",
    "le",
    "multiple_of",
    "allow_inf_nan",
    "max_digits",
    "decimal_places",
    "min_length",
    "max_length",
    "union_mode",
}


def _has_field_function(node: ast.ClassDef) -> bool:
    for stmt in node.body:
        if (
            isinstance(stmt, (ast.Assign, ast.AnnAssign))
            and isinstance(stmt.value, ast.Call)
            and (
                (isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == "Field")  # f = Field(...)
                or (
                    isinstance(stmt.value.func, ast.Attribute) and stmt.value.func.attr == "Field"
                )  # f = pydantic.Field(...)
            )
            and all(kw.arg in PYDANTIC_FIELD_ARGUMENTS for kw in stmt.value.keywords if kw.arg is not None)
        ):
            return True

    return False


def _has_annotated_field(node: ast.ClassDef) -> bool:
    for stmt in node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.annotation, ast.Subscript):
            if isinstance(stmt.annotation.value, ast.Name) and stmt.annotation.value.id == "Annotated":
                # f: Annotated[...]
                return True
            if isinstance(stmt.annotation.value, ast.Attribute) and stmt.annotation.value.attr == "Annotated":
                # f: typing.Annotated[...]
                return True
    return False


PYDANTIC_DECORATORS = {
    "computed_field",
    "field_serializer",
    "model_serializer",
    "field_validator",
    "model_validator",
}


def _has_pydantic_decorator(node: ast.ClassDef) -> bool:
    for stmt in node.body:
        if isinstance(stmt, ast.FunctionDef):
            decorator_names = get_decorator_names(stmt.decorator_list)
            if PYDANTIC_DECORATORS & decorator_names:
                return True
    return False


PYDANTIC_METHODS = {
    "model_construct",
    "model_copy",
    "model_dump",
    "model_dump_json",
    "model_json_schema",
    "model_parametrized_name",
    "model_rebuild",
    "model_validate",
    "model_validate_json",
    "model_validate_strings",
}


def _has_pydantic_method(node: ast.ClassDef) -> bool:
    for stmt in node.body:
        if isinstance(stmt, ast.FunctionDef) and (
            stmt.name.startswith(("__pydantic_", "__get_pydantic_")) or stmt.name in PYDANTIC_METHODS
        ):
            return True
    return False


def is_pydantic_model(node: ast.ClassDef, *, include_root_model: bool = True) -> bool:
    """Determine if a class definition is a Pydantic model.

    Multiple heuristics are use to determine if this is the case:
    - The class inherits from `BaseModel` (or `RootModel` if `include_root_model` is `True`).
    - The class has a `model_config` attribute set.
    - The class has a field defined with the `Field` function.
    - The class has a field making use of `Annotated`.
    - The class makes use of Pydantic decorators, such as `computed_field` or `model_validator`.
    - The class overrides any of the Pydantic methods, such as `model_dump`.
    """
    if not node.bases:
        return False

    return (
        _has_pydantic_model_base(node, include_root_model=include_root_model)
        or _has_model_config(node)
        or _has_field_function(node)
        or _has_annotated_field(node)
        or _has_pydantic_decorator(node)
        or _has_pydantic_method(node)
    )


def is_dataclass(node: ast.ClassDef) -> bool:
    """Determine if a class is a dataclass."""

    return bool({"dataclass", "pydantic_dataclass"} & get_decorator_names(node.decorator_list))


def is_function(node: ast.Call, function_name: str) -> bool:
    return (
        isinstance(node.func, ast.Name)
        and node.func.id == function_name
        or isinstance(node.func, ast.Attribute)
        and node.func.attr == function_name
    )


def is_name(node: ast.expr, name: str) -> bool:
    return isinstance(node, ast.Name) and node.id == name or isinstance(node, ast.Attribute) and node.attr == name


def extract_annotations(node: ast.expr) -> set[str]:
    annotations: set[str] = set()

    if isinstance(node, ast.Name):
        # foo: date = ...
        annotations.add(node.id)
    if isinstance(node, ast.BinOp):
        # foo: date | None = ...
        annotations |= extract_annotations(node.left)
        annotations |= extract_annotations(node.right)
    if isinstance(node, ast.Subscript):
        # foo: dict[str, date]
        # foo: Annotated[list[date], ...]
        if isinstance(node.slice, ast.Tuple):
            for elt in node.slice.elts:
                annotations |= extract_annotations(elt)
        if isinstance(node.slice, ast.Name):
            annotations.add(node.slice.id)

    return annotations
