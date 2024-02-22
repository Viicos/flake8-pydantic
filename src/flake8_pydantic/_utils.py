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


def is_pydantic_model(node: ast.ClassDef, include_root_model: bool = True) -> bool:
    model_class_names = {"BaseModel"}
    if include_root_model:
        model_class_names.add("RootModel")
    return any(b.id in model_class_names for b in node.bases if isinstance(b, ast.Name))
