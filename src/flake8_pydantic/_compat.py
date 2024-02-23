import sys

if sys.version_info >= (3, 11):
    from typing import Self, TypeAlias
else:
    from typing_extensions import Self, TypeAlias

__all__ = ("Self", "TypeAlias")
