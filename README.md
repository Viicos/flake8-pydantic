# Flake8 Pydantic

[![Python versions](https://img.shields.io/pypi/pyversions/flake8-pydantic.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/flake8-pydantic.svg)](https://pypi.org/project/flake8-pydantic/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A `flake8` plugin to check Pydantic related code.

## Class detection

`flake8_pydantic` parses the [AST](https://docs.python.org/3/library/ast.html) to emit linting errors. As such,
it cannot accurately determine if a class is defined as a Pydantic model. However, it tries its best, using the following heuristics:
- The class inherits from `BaseModel` or `RootModel`.
- The class has a `model_config` attribute set.
- The class has a field defined with the `Field` function.
- The class has a field making use of `Annotated`.
- The class makes use of Pydantic decorators, such as `computed_field` or `model_validator`.
- The class overrides any of the Pydantic methods, such as `model_dump`.

## Error codes

### `PYD001` - *Positional argument for Field default argument*

Raise an error if the `default` argument of the [`Field`](https://docs.pydantic.dev/latest/api/fields/#pydantic.fields.Field) function is positional.

```python
class Model(BaseModel):
    foo: int = Field(1)
```

Although allowed at runtime by Pydantic, it does not comply with the [typing specification (PEP 681)](https://typing.readthedocs.io/en/latest/spec/dataclasses.html#field-specifier-parameters) and type checkers will not be able to synthesize a correct `__init__` method.

Instead, consider using an explicit keyword argument:

```python
class Model(BaseModel):
    foo: int = Field(default=1)
```

### `PYD002` - *Non-annotated attribute inside Pydantic model*

Raise an error if a non-annotated attribute is defined inside a Pydantic model class.

```python
class Model(BaseModel):
    foo = 1  # Will error at runtime
```

### `PYD003` - *Unecessary Field call to specify a default value*

Raise an error if the [`Field`](https://docs.pydantic.dev/latest/api/fields/#pydantic.fields.Field) function
is used only to specify a default value.

```python
class Model(BaseModel):
    foo: int = Field(default=1)
```

Instead, consider specifying the default value directly:

```python
class Model(BaseModel):
    foo: int = 1
```

### `PYD004` - *Default argument specified in annotated*

Raise an error if the `default` argument of the [`Field`](https://docs.pydantic.dev/latest/api/fields/#pydantic.fields.Field) function is used together with [`Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated).

```python
class Model(BaseModel):
    foo: Annotated[int, Field(default=1, description="desc")]
```

To make type checkers aware of the default value, consider specifying the default value directly:

```python
class Model(BaseModel):
    foo: Annotated[int, Field(description="desc")] = 1
```

### `PYD005` - *Field name overrides annotation*

Raise an error if the field name clashes with the annotation.

```python
from datetime import date

class Model(BaseModel):
    date: date | None = None
```

Because of how Python [evaluates](https://docs.python.org/3/reference/simple_stmts.html#annassign)
annotated assignments, unexpected issues can happen when using an annotation name that clashes with a field
name. Pydantic will try its best to warn you about such issues, but can fail in complex scenarios (and the
issue may even be silently ignored).

Instead, consider, using an [alias](https://docs.pydantic.dev/latest/concepts/fields/#field-aliases) or referencing your type under a different name:

```python
from datetime import date

date_ = date

class Model(BaseModel):
    date_aliased: date | None = Field(default=None, alias="date")
    # or
    date: date_ | None = None
```

### `PYD010` - *Usage of `__pydantic_config__`*

Raise an error if a Pydantic configuration is set with [`__pydantic_config__`](https://docs.pydantic.dev/dev/concepts/config/#configuration-with-dataclass-from-the-standard-library-or-typeddict).

```python
class Model(TypedDict):
    __pydantic_config__ = {}  # Type checkers will emit an error
```

Although allowed at runtime by Python, type checkers will emit an error as it is not allowed to assign values when defining a [`TypedDict`](https://docs.python.org/3/library/typing.html#typing.TypedDict).

Instead, consider using the [`with_config`](https://docs.pydantic.dev/dev/api/config/#pydantic.config.with_config) decorator:

```python
@with_config({"str_to_lower": True})
class Model(TypedDict):
    pass
```

And many more to come.

## Roadmap

Once the rules of the plugin gets stable, the goal will be to implement them in [Ruff](https://github.com/astral-sh/ruff), with autofixes when possible.
