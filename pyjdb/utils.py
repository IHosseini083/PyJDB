from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from .typings import ReprArgs


class Repr:
    """Mixin to provide __repr__ method."""

    __slots__: Tuple[str, ...] = tuple()

    def __repr_name__(self) -> str:
        """Return the name of the class."""
        return self.__class__.__name__

    def __repr_args__(self) -> "ReprArgs":
        """Return a list of 2 length tuples containing name and value of attributes."""
        attrs = ((name, getattr(self, name)) for name in self.__slots__)
        return [(name, value) for name, value in attrs if value is not None]

    def __get_str__(self, joiner: str) -> str:
        """Generate a string representation from the attributes."""
        attrs = self.__repr_args__()
        return joiner.join(repr(v) if not a else f"{a}={v!r}" for a, v in attrs)

    def __repr__(self) -> str:
        return f"{self.__repr_name__()}({self.__get_str__(', ')})"
