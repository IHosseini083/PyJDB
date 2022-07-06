from typing import Any, Iterable

__all__ = [
    "InvalidFormatError",
    "DuplicateConfigError",
]


class PyJDBErrorMixin:
    msg_template: str

    def __init__(self, **context: Any) -> None:
        self.__dict__ = context

    def __str__(self) -> str:
        return self.msg_template.format(**self.__dict__)


class PyJDBValueError(PyJDBErrorMixin, ValueError):
    pass


class PyJDBTypeError(PyJDBErrorMixin, TypeError):
    pass


class InvalidFormatError(PyJDBValueError):
    msg_template = "invalid format {fmt!r} must be one of: {allowed}"

    def __init__(self, *, fmt: str, allowed: Iterable[str]) -> None:
        super().__init__(fmt=fmt, allowed=allowed)


class DuplicateConfigError(PyJDBTypeError):
    msg_template = (
        "Specifying config in two different places is confusing, "
        "you can either define a Config attribute or use class kwargs."
    )
