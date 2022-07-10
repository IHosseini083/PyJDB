import pytest

from pyjdb import BaseModel, String
from pyjdb.errors import InvalidFormatError, ValidationError


def test_default_value() -> None:
    class User(BaseModel):
        username = String(default="admin")

    u = User()

    assert u.username == "admin"

    with pytest.raises(ValidationError):

        class User(BaseModel):  # type: ignore
            username = String(default=1)  # type: ignore

        # Raises 'ValidationError' because the default value is
        # not a str.
        User()


def test_nullable() -> None:
    class User(BaseModel):
        role = String(nullable=True)

    u = User()
    assert not u.role

    with pytest.raises(ValidationError):

        class User(BaseModel):  # type: ignore
            role = String()

        # Because nullable is 'False' here, 'role' field is
        # required and a 'ValidationError' will be raised.
        User()


def test_allow_blank() -> None:
    class User(BaseModel):
        role = String()

    with pytest.raises(ValidationError):
        User(role="")

    class User(BaseModel):  # type: ignore
        role = String(allow_blank=True)

    assert User().role == ""


def test_trim_whitespace() -> None:
    class User(BaseModel):
        role = String()

    assert User(role="  admin  ").role == "admin"


def test_coerce_types() -> None:
    class User(BaseModel):
        role = String(allow_blank=True)

    assert User(role=None).role == ""


def test_min_length() -> None:
    class User(BaseModel):
        password = String(min_length=8)

    with pytest.raises(ValidationError):
        User(password="123456")


def test_max_length() -> None:
    class User(BaseModel):
        secret = String(max_length=6)

    with pytest.raises(ValidationError):
        User(secret="strong_secret_code")


def test_pattern() -> None:
    class User(BaseModel):
        identity = String(pattern=r"^ID\d+")

    User(identity="ID435323")

    with pytest.raises(ValidationError):
        User(identity="54ID")


def test_invalid_fmt() -> None:
    with pytest.raises(InvalidFormatError):

        class User(BaseModel):
            info = String(fmt="text")

        User()


def test_fmt_date() -> None:
    # Validates ISO 8601 formatted dates. For example "2020-02-29".
    # Returns datetime.date instances.

    class User(BaseModel):
        created_at = String(fmt="date")

    with pytest.raises(ValidationError):
        User(created_at="91-1-12")

    User(created_at="1991-1-2")
    User(created_at="1991-03-12")


def test_fmt_time() -> None:
    # Validates ISO 8601 formatted times.
    # Returns datetime.time instances.

    class Offer(BaseModel):
        expires_at = String(fmt="time")

    with pytest.raises(ValidationError):
        Offer(expires_at=":43")

    Offer(expires_at="12:34:56")


def test_fmt_datetime() -> None:
    # Validates ISO 8601 formatted datetime. For example "2020-02-29T12:34:56Z".
    # Returns datetime.datetime instances.

    class User(BaseModel):
        created_at = String(fmt="datetime")

    with pytest.raises(ValidationError):
        User(created_at="1990-1-12 1:4:111")

    User(created_at="2002-12-12 12:49:55.123456")


def test_fmt_uuid() -> None:
    # Validates UUID in the format of 32 hexadecimal characters, separated by hyphens.
    # For example "cd11b0d7-d8b3-4b5c-8159-70f5c9ea96ab".

    class User(BaseModel):
        id = String(fmt="uuid")

    with pytest.raises(ValidationError):
        User(id="d0d496-00-11-b9-d90f4072c0")

    User(id="158b71a9-e817-446c-ba87-ae626c587234")


def test_fmt_email() -> None:
    class User(BaseModel):
        email = String(fmt="email")

    with pytest.raises(ValidationError):
        User(email="example.com")

    User(email="example@gmail.com")


def test_fmt_ip() -> None:
    # Validates IPv4 and IPv6 addresses.
    # Returns ipaddress.IPv4Address or ipaddress.IPv6Address based on input.

    class Device(BaseModel):
        ip = String(fmt="ipaddress")

    with pytest.raises(ValidationError):
        Device(ip="0.0.0")
        Device(ip="2001:0db8:85a3:0000:0000:7334")

    Device(ip="1.1.1.1")
    Device(ip="2001:db8:3333:4444:5555:6666:7777:8888")


def test_fmt_url() -> None:
    class Website(BaseModel):
        url = String(fmt="url")

    with pytest.raises(ValidationError):
        Website(url="example.com")
        Website(url="http:example.com")
        Website(url="http//example")

    Website(url="https://example.com")
