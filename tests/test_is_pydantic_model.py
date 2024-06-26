from __future__ import annotations

import ast
from typing import cast

import pytest

from flake8_pydantic._utils import is_pydantic_model

# Positive cases:
SUBCLASSES_BASE_MODEL_1 = """
class Model(BaseModel):
    pass
"""

SUBCLASSES_BASE_MODEL_2 = """
class Model(pydantic.BaseModel):
    pass
"""

SUBCLASSES_ROOT_MODEL = """
class Model(RootModel):
    root: int
"""

HAS_ANNOTATED_MODEL_CONFIG = """
class SubModel(ParentModel):
    model_config: ModelConfig = {}
"""

HAS_MODEL_CONFIG = """
class SubModel(ParentModel):
    model_config = {}
"""

HAS_FIELD_FUNCTION_1 = """
class SubModel(ParentModel):
    a = Field(title="A")
"""

HAS_FIELD_FUNCTION_2 = """
class SubModel(ParentModel):
    a: int = Field(gt=1)
"""

HAS_FIELD_FUNCTION_3 = """
class SubModel(ParentModel):
    a = pydantic.Field(alias="b")
"""

HAS_FIELD_FUNCTION_4 = """
class SubModel(ParentModel):
    a: int = pydantic.Field(repr=True)
"""

HAS_FIELD_FUNCTION_5 = """
class SubModel(ParentModel):
    a: int = pydantic.Field()
"""

HAS_FIELD_FUNCTION_6 = """
class SubModel(ParentModel):
    a: int = pydantic.Field(1)
"""

USES_ANNOTATED_1 = """
class SubModel(ParentModel):
    a: Annotated[int, ""]
"""

USES_ANNOTATED_2 = """
class SubModel(ParentModel):
    a: typing.Annotated[int, ""]
"""

HAS_PYDANTIC_DECORATOR_1 = """
class SubModel(ParentModel):
    @computed_field
    @unrelated
    def func(): pass
"""

HAS_PYDANTIC_DECORATOR_2 = """
class SubModel(ParentModel):
    @pydantic.computed_field
    def func(): pass
"""

HAS_PYDANTIC_METHOD_1 = """
class SubModel(ParentModel):
    def model_dump(self): pass
"""

HAS_PYDANTIC_METHOD_2 = """
class SubModel(ParentModel):
    def __pydantic_some_method__(self): pass
"""

HAS_PYDANTIC_METHOD_3 = """
class SubModel(ParentModel):
    def __get_pydantic_core_schema__(self): pass
"""

# Negative cases:
NO_BASES = """
class Model:
    a = Field()
"""

UNRELATED_FIELD_ARG = """
class SubModel(ParentModel):
    a: int = Field(some_arg=1)
"""

UNRELATED_MODEL_METHOD = """
class SubModel(ParentModel):
    def model_unrelated(): pass
"""


@pytest.mark.parametrize(
    ["source", "expected"],
    [
        (SUBCLASSES_BASE_MODEL_1, True),
        (SUBCLASSES_BASE_MODEL_2, True),
        (SUBCLASSES_ROOT_MODEL, True),
        (HAS_ANNOTATED_MODEL_CONFIG, True),
        (HAS_MODEL_CONFIG, True),
        (HAS_FIELD_FUNCTION_1, True),
        (HAS_FIELD_FUNCTION_2, True),
        (HAS_FIELD_FUNCTION_3, True),
        (HAS_FIELD_FUNCTION_4, True),
        (HAS_FIELD_FUNCTION_5, True),
        (HAS_FIELD_FUNCTION_6, True),
        (USES_ANNOTATED_1, True),
        (USES_ANNOTATED_2, True),
        (HAS_PYDANTIC_DECORATOR_1, True),
        (HAS_PYDANTIC_DECORATOR_2, True),
        (HAS_PYDANTIC_METHOD_1, True),
        (HAS_PYDANTIC_METHOD_2, True),
        (HAS_PYDANTIC_METHOD_3, True),
        (NO_BASES, False),
        (UNRELATED_FIELD_ARG, False),
        (UNRELATED_MODEL_METHOD, False),
    ],
)
def test_is_pydantic_model(source: str, expected: bool) -> None:
    class_def = cast(ast.ClassDef, ast.parse(source).body[0])
    assert is_pydantic_model(class_def) == expected
