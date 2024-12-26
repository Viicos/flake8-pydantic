# Changelog

## 0.4.0 (2024-12-26)

- Update dependencies (#18)
  Apply new Ruff and mymy changes
- Add support for Python 3.13 (#17)
- Ignore non-annotated `model_config` attributes (#16)

## 0.3.1 (2024-05-06)

- Improve Pydantic model detection robustness (#11)
- Fix crash in the visitor implementation (#10)

## 0.3.0 (2024-03-14)

Add a new rule:
- `PYD006` - *Duplicate field name*

Will raise an error with the following:

```python
class Model(BaseModel):
    x: int
    x: int = 1
```

## 0.2.0 (2024-02-24)

Add three new rules:
- `PYD003` - *Unecessary Field call to specify a default value*
- `PYD004` - *Default argument specified in annotated*
- `PYD005` - *Field name overrides annotation*

- Drop support for Python 3.8

## 0.1.0.post0 (2024-02-23)

- Add missing `readme` metadata entry

## 0.1.0 (2024-02-23)

- Initial release
