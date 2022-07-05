from typing import TYPE_CHECKING, Tuple, Type

from .utils import Repr

if TYPE_CHECKING:
    from .typings import ReprArgs, SetStr

    ConfigType = Type["BaseConfig"]


class BaseConfig(Repr):
    frozen: bool = False
    validate_assignment: bool = True

    @classmethod
    def __valid_config_attrs__(cls) -> "SetStr":
        return {
            attr
            for attr in dir(cls)
            # Skip the dunder methods and attributes.
            if not (attr.startswith("__") and attr.endswith("__"))
        }

    def __repr_args__(self) -> "ReprArgs":
        return [(attr, getattr(self, attr)) for attr in self.__valid_config_attrs__()]


# Taken from pydantic config system.
def inherit_config(
    self_config: "ConfigType",
    parent_config: "ConfigType",
    **namespace,
) -> "ConfigType":
    if not self_config:
        base_classes: Tuple["ConfigType", ...] = (parent_config,)
    elif self_config == parent_config:
        base_classes = (self_config,)
    else:
        base_classes = self_config, parent_config

    return type("Config", base_classes, namespace)  # type: ignore
