from typing import Any, NamedTuple


class FieldValue(NamedTuple):
    """A namedtuple of field's name and value."""

    name: str
    value: Any
