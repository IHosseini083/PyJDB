from typing import TYPE_CHECKING, Any, Iterable, List, Tuple, Union, cast

if TYPE_CHECKING:
    from typesystem import ValidationError as TypesystemValidationError

    from .types import FieldValue
    from .typings import DictStrAny

__all__ = [
    "InvalidFormatError",
    "DuplicateConfigError",
    "ValidationError",
    "parse_typesystem_validation_error",
    "FrozenFieldError",
    "FieldNotFoundError",
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
    msg_template = "invalid format {fmt!r}, must be one of: {allowed}"

    def __init__(self, *, fmt: str, allowed: Iterable[str]) -> None:
        super().__init__(fmt=fmt, allowed=allowed)


class DuplicateConfigError(PyJDBTypeError):
    msg_template = (
        "Specifying config in two different places is confusing, "
        "you can either define a Config attribute or use class kwargs."
    )


class FrozenFieldError(PyJDBTypeError):
    msg_template = (
        "Field {name!r} doesn't support reassignment because its model is frozen."
    )

    def __init__(self, *, name: str) -> None:
        super().__init__(name=name)


class FieldNotFoundError(PyJDBValueError):
    msg_template = "Model {ob_name!r} has no field {field_name!r}"

    def __init__(self, *, ob_name: str, field_name: str) -> None:
        super().__init__(ob_name=ob_name, field_name=field_name)


class ValidationError(PyJDBValueError):
    msg_template = "  |-- {name!r}: <{value!r}> -> {message}"

    def __init__(self, *, errors: List[Tuple[str, Any, str]]) -> None:
        super().__init__(errors=errors)

    def messages(self) -> List[str]:
        return [
            self.msg_template.format(
                name=name,
                value=value,
                message=message,
            )
            for name, value, message in self.__dict__["errors"]
        ]

    def __str__(self) -> str:
        return "\n" + "\n".join(self.messages())


def parse_typesystem_validation_error(
    err: "TypesystemValidationError",
    context: Union["FieldValue", "DictStrAny"],
) -> "ValidationError":
    if isinstance(context, tuple):  # if the context is passed as a FieldValue
        context = cast("FieldValue", context)
        errors = [(context.name, context.value, next(iter(err.values())))]
    else:
        # Use 'Mapping.get' method to prevent KeyError in case
        # the field is required but user did not pass a value.
        errors = [(name, context.get(name), message) for name, message in err.items()]
    return ValidationError(errors=errors)
