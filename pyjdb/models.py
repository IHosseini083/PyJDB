from abc import ABCMeta
from copy import deepcopy
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterator,
    Optional,
    Tuple,
    Type,
    no_type_check,
)

import typesystem

from .config import BaseConfig, inherit_config
from .errors import DuplicateConfigError, parse_typesystem_validation_error
from .fields import ModelField
from .utils import Repr

if TYPE_CHECKING:
    from .typings import DictStrAny, ReprArgs

_FIELDS_KEY = "__fields__"
_COLLECTION_KEY = "__collection__"
_SCHEMA_KEY = "__schema__"
_CONFIG_KEY = "__config__"


def iter_fields(namespace: "DictStrAny") -> Iterator[Tuple[str, ModelField]]:
    for name, value in namespace.items():
        if isinstance(value, ModelField):
            yield name, value


def validate_kwargs(
    kwargs: "DictStrAny",
    schema: typesystem.Schema,
    fields: Dict[str, ModelField],
) -> "DictStrAny":
    try:
        kwargs = schema.validate(kwargs)
    except typesystem.ValidationError as e:
        raise parse_typesystem_validation_error(
            e,
            kwargs,
        ) from None
    for key, value in fields.items():
        if value.validator.read_only and value.validator.has_default():
            kwargs[key] = value.validator.get_default_value()
    return kwargs


class ModelMeta(ABCMeta):
    @no_type_check
    def __new__(mcs, name: str, bases: tuple, namespace: dict, **kwargs):
        fields: Dict[str, ModelField] = {}
        config = BaseConfig
        hash_function: Optional[Callable[[Any], int]] = None

        # Update attributes from base classes
        for base in reversed(bases):
            if hasattr(base, _FIELDS_KEY):
                fields.update(deepcopy(base.__fields__))
                config = inherit_config(base.__config__, config)
                hash_function = base.__hash__

        # If the model is not BaseModel get its fields.
        module, qualname = namespace.get("__module__"), namespace.get("__qualname__")
        if (module, qualname) != ("pyjdb.models", "BaseModel"):
            for field_name, field in iter_fields(namespace):
                fields[field_name] = field

        # Get keyword arguments that are common between class kwargs
        # and BaseConfig attributes.
        config_kwargs = {
            key: kwargs.pop(key)
            for key in kwargs.keys() & BaseConfig.__valid_config_attrs__()
        }
        config_from_namespace = namespace.get("Config")
        if config_from_namespace and config_kwargs:
            raise DuplicateConfigError()
        # Inherit the user-defined Config attribute.
        config = inherit_config(config_from_namespace, config, **config_kwargs)

        # Generate the schema from fields
        schema = typesystem.Schema(fields={k: v.validator for k, v in fields.items()})

        # Check if user explicitly defined a new name for collection
        collection = namespace.get(_COLLECTION_KEY)
        if not collection:
            collection = qualname.lower()

        # If the '__hash__' method is not found and the model is meant
        # to be frozen/immutable (based on user configs), create a hash function for model.
        if not hash_function and config.frozen:
            # This is what makes the model hashable.
            def hash_function(obj: "BaseModel") -> int:
                # Generate unique hash value from model and its fields value.
                return hash(obj.__class__) + hash(tuple(obj.__data__.values()))

        # Create new namespace from generated attributes.
        new_namespace = {
            _FIELDS_KEY: fields,
            _COLLECTION_KEY: collection,
            _SCHEMA_KEY: schema,
            _CONFIG_KEY: config,
            "__hash__": hash_function,
            **namespace,
        }
        return super().__new__(mcs, name, bases, new_namespace, **kwargs)

    def __instancecheck__(self, inst: Any) -> bool:
        """
        Try to avoid calling the _abc_subclasscheck unless it's necessary.

        See https://github.com/python/cpython/issues/92810
        """
        # From what I have seen in the pydantic and other users report,
        # it seems that '__isinstancecheck__' method of ABC can be very
        # slow and even lead to memory leakage, particularly when the checks
        # return `False`. So we need to first make sure that the instance
        # has a '__fields__' attribute and then call the '_abc_subclasscheck',
        # otherwise it returns 'False' immediately.

        return hasattr(inst, _FIELDS_KEY) and super().__instancecheck__(inst)


object_setattr = object.__setattr__


class BaseModel(Repr, metaclass=ModelMeta):
    if TYPE_CHECKING:
        __fields__: Dict[str, ModelField]
        __collection__: str
        __schema__: typesystem.Schema
        __data__: "DictStrAny"
        __config__: Type[BaseConfig]

    Config = BaseConfig
    __slots__ = ("__data__",)

    def __init__(self, **data: Any) -> None:
        validated_kwargs = validate_kwargs(data, self.__schema__, self.__fields__)
        object_setattr(self, "__data__", validated_kwargs)

    def __repr_args__(self) -> "ReprArgs":
        return [(k, v) for k, v in self.__data__.items() if self.__fields__[k].repr_]

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        """This will add support for `dict(model)` to work."""
        yield from self.__data__.items()

    def __eq__(self, other: Any) -> bool:
        # This logic and even the used methods may change later.
        if isinstance(other, BaseModel):
            return self.__data__ == other.__data__
        else:
            return self.__data__ == other
