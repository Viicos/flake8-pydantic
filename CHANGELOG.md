# Changelog

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
