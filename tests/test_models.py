import pytest
import typesystem

from pyjdb import BaseModel, Boolean, Float, Integer, String
from pyjdb.errors import FieldNotFoundError
from pyjdb.models import _COLLECTION_KEY, _CONFIG_KEY, _FIELDS_KEY, _SCHEMA_KEY  # noqa


@pytest.fixture
def bare_model():
    class Model(BaseModel):
        pass

    return Model()


default_values = {
    "s": "pygrammer",
    "b": True,
    "i": 18,
    "f": 4.0,
}


@pytest.fixture
def multi_field_model():
    class Model(BaseModel):
        s = String()
        b = Boolean()
        i = Integer()
        f = Float()

    return Model(**default_values)


# Test attributes and methods that must be available in a model
@pytest.mark.parametrize(
    "attr",
    [
        _COLLECTION_KEY,
        _CONFIG_KEY,
        _FIELDS_KEY,
        _SCHEMA_KEY,
        "keys",
        "values",
        "items",
        "get",
        "__data__",
        "__eq__",
        "__ne__",
    ],
)
def test_attrs_and_methods(bare_model: BaseModel, attr: str) -> None:
    assert hasattr(bare_model, attr)


def test_dict_conversion(multi_field_model: BaseModel) -> None:
    assert dict(multi_field_model) == multi_field_model.__data__


def test__getitem__(multi_field_model: BaseModel) -> None:
    for k, v in default_values.items():
        assert multi_field_model[k] == v

    with pytest.raises(FieldNotFoundError):
        multi_field_model["x"]  # noqa


def test__len__(multi_field_model: BaseModel, bare_model: BaseModel) -> None:
    assert not len(bare_model)
    assert len(multi_field_model) == 4


def test__iter__(multi_field_model: BaseModel, bare_model: BaseModel) -> None:
    iter(multi_field_model)
    iter(bare_model)


def test__bool__(multi_field_model: BaseModel, bare_model: BaseModel) -> None:
    assert multi_field_model
    assert not bare_model


def test_membership(multi_field_model: BaseModel) -> None:
    assert "s" in multi_field_model
    assert "4" not in multi_field_model


def test_keys(multi_field_model: BaseModel, bare_model: BaseModel) -> None:
    assert not bare_model.keys()
    assert multi_field_model.keys() == {"s", "b", "i", "f"}


def test_get(multi_field_model: BaseModel, bare_model: BaseModel) -> None:
    assert bare_model.get("1") is None
    assert multi_field_model.get("s") == default_values["s"]


def test_inequality(multi_field_model: BaseModel, bare_model: BaseModel) -> None:
    assert multi_field_model != bare_model


def test_fields(multi_field_model: BaseModel, bare_model: BaseModel) -> None:
    string, boolean, integer, float_ = multi_field_model.__fields__.values()

    assert not bare_model.__fields__
    assert multi_field_model.__fields__.keys() == {"s", "b", "i", "f"}
    assert len(bare_model.__fields__.values()) == 0

    # test field names
    assert string.name == "s"
    assert boolean.name == "b"
    assert integer.name == "i"
    assert float_.name == "f"

    # test validators
    assert isinstance(string.validator, typesystem.String)
    assert isinstance(boolean.validator, typesystem.Boolean)
    assert isinstance(integer.validator, typesystem.Integer)
    assert isinstance(float_.validator, typesystem.Float)


def test_schema(bare_model: BaseModel) -> None:
    assert isinstance(bare_model.__schema__, typesystem.Schema)


# TODO: Add tests for model config and hashable models
