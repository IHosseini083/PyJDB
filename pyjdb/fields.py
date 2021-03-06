from abc import ABC
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generic,
    Optional,
    Pattern,
    Type,
    TypeVar,
    Union,
    overload,
)

import typesystem

from .errors import (
    FrozenFieldError,
    InvalidFormatError,
    parse_typesystem_validation_error,
)
from .types import FieldValue

if TYPE_CHECKING:
    from .models import BaseModel
    from .typings import IntOrFloat, SetStr

    from typing_extensions import Self

from .utils import Repr

_T = TypeVar("_T")

__all__ = [
    "ModelField",
    "String",
    "Boolean",
    "Integer",
    "Float",
]


class UndefinedType:
    """An object representing not yet defined values."""

    def __repr__(self) -> str:
        return "Undefined"

    def __copy__(self: _T) -> _T:
        return self

    def __reduce__(self) -> str:
        return "Undefined"

    def __bool__(self) -> bool:
        return False

    def __deepcopy__(self: _T, _: Any) -> _T:
        return self


Undefined = UndefinedType()


class ModelField(Repr, Generic[_T], ABC):
    name: str
    model: Type["BaseModel"]

    __slots__ = (
        "name",
        "validator",
        "repr_",
        "model",
    )

    def __init__(self, **kwargs) -> None:
        self.repr_: bool = kwargs.pop("repr_", True)
        default = kwargs.get("default")
        if default is Undefined:
            del kwargs["default"]
            default = None
        self.validator = self.get_validator(**kwargs)
        # Validate the default value if it's not None.
        if default is not None:
            try:
                self.validator.validate(default)
            except typesystem.ValidationError as e:
                raise parse_typesystem_validation_error(
                    e,
                    FieldValue(name="default", value=default),
                ) from None

    def get_validator(self, **kwargs) -> typesystem.Field:
        raise NotImplementedError()

    def __set_name__(self, owner: Type["BaseModel"], name: str) -> None:
        self.name = name
        self.model = owner

    @overload
    def __get__(self, inst: "BaseModel", owner: Type["BaseModel"]) -> _T:
        ...

    @overload
    def __get__(self, inst: None, owner: Type["BaseModel"]) -> "Self":  # type: ignore
        ...

    def __get__(
        self,
        inst: Optional["BaseModel"],
        owner: Type["BaseModel"],
    ) -> Union[_T, "Self"]:  # type: ignore
        if inst is None:
            # if accessed from directly from the model, return the field itself.
            return self
        return inst.__data__[self.name]

    def __set__(self, inst: "BaseModel", value: _T) -> None:
        if inst.__config__.frozen:
            raise FrozenFieldError(name=self.name)
        if not inst.__config__.validate_assignment:
            inst.__data__[self.name] = value
            return

        try:
            inst.__data__[self.name] = self.validator.validate(value)
        except typesystem.ValidationError as e:
            raise parse_typesystem_validation_error(
                e,
                FieldValue(name=self.name, value=value),
            ) from None

    def __delete__(self, inst: "BaseModel") -> None:
        del inst.__data__[self.name]


class String(ModelField[str]):
    ALLOWED_FORMATS: ClassVar["SetStr"] = {
        "date",
        "time",
        "datetime",
        "uuid",
        "email",
        "ipaddress",
        "url",
    }

    def __init__(
        self,
        *,
        default: str = Undefined,  # type: ignore
        nullable: bool = False,
        allow_blank: bool = False,
        trim_whitespace: bool = True,
        coerce_types: bool = True,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None,
        pattern: Optional[Union[str, Pattern]] = None,
        fmt: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if fmt and fmt not in self.ALLOWED_FORMATS:
            raise InvalidFormatError(
                fmt=fmt,
                allowed=self.ALLOWED_FORMATS,
            )
        super().__init__(
            allow_null=nullable,
            allow_blank=allow_blank,
            trim_whitespace=trim_whitespace,
            default=default,
            max_length=max_length,
            min_length=min_length,
            pattern=pattern,
            format=fmt,
            coerce_types=coerce_types,
            **kwargs,
        )

    def get_validator(self, **kwargs) -> typesystem.Field:
        return typesystem.String(**kwargs)


class Boolean(ModelField[bool]):
    def __init__(
        self,
        *,
        default: bool = Undefined,  # type: ignore
        nullable: bool = False,
        coerce_types: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(
            default=default,
            allow_null=nullable,
            coerce_types=coerce_types,
            **kwargs,
        )

    def get_validator(self, **kwargs) -> typesystem.Field:
        return typesystem.Boolean(**kwargs)


class Number(ModelField["IntOrFloat"], ABC):
    def __init__(
        self,
        *,
        default: "IntOrFloat" = Undefined,  # type: ignore
        nullable: bool = False,
        ge: Optional["IntOrFloat"] = None,
        le: Optional["IntOrFloat"] = None,
        gt: Optional["IntOrFloat"] = None,
        lt: Optional["IntOrFloat"] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            default=default,
            allow_null=nullable,
            minimum=ge,
            maximum=le,
            exclusive_minimum=gt,
            exclusive_maximum=lt,
            **kwargs,
        )


class Integer(Number):
    def get_validator(self, **kwargs) -> typesystem.Field:
        return typesystem.Integer(**kwargs)


class Float(Number):
    def get_validator(self, **kwargs) -> typesystem.Field:
        return typesystem.Float(**kwargs)
