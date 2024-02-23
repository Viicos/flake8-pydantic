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
