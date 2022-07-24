<div align="center">
<h1><a href="https://github.com/IHosseini083/PyJDB"><b>PyJDB</b></a></h1>
<a href="https://github.com/IHosseini083/PyJDB/actions?query=workflow%3ATest+event%3Apush+branch%3Amain" target="_blank">
    <img src="https://github.com/IHosseini083/PyJDB/actions/workflows/test.yml/badge.svg" alt="Test">
</a>
<a href="https://www.python.org">
    <img src="https://img.shields.io/badge/Python-3.8+-3776AB.svg?style=flat&logo=python&logoColor=white" alt="Python">
</a>
<a href="https://github.com/psf/black">
    <img src="https://img.shields.io/static/v1?label=code%20style&message=black&color=black&style=flat" alt="Code Style: black">
</a>
<a href="https://github.com/pre-commit/pre-commit">
    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat" alt="pre-commit">
</a>
</div>

Python JSON Database (PyJDB) is an ORM to easily validate JSON data and even store and use that data
in a database-like manner. It uses [`typesystem`](https://github.com/encode/typesystem) library to power up
its data validation system.

Key features of _PyJDB_ are:

- It's fully type hinted and plays nicely with your IDE/Editor and preferred linters.
- It's designed to be easy to use and learn.
- Supports all JSON data types.
- Capable of handling nested models and references.

Projects we have inspired a lot from:

- [Pydantic](https://github.com/samuelcolvin/pydantic 'Data validation and settings management framework.')
- [ORM](https://github.com/encode/orm 'Async ORM for Python, with support for Postgres, MySQL, and SQLite.')

## Requirements

_PyJDB_ requires you to have Python 3.8+ installed.

Uses following external packages:

- [Typesystem](https://github.com/encode/typesystem) to validate fields.

## Installation

## Simple Example

Like other any ORM system you start by defining models and validating the data, models are a huge part of _PyJDB_ so let's
start using them ✌🏻

Assume we're going to receive some data about a user from our REST API, and we want to validate the incoming data to be
sure have the right parameters we need! first we create a file named `models.py` and start creating a model for users:

```python
from pyjdb import BaseModel, Boolean, Integer, String


class User(BaseModel):
    id = Integer()
    username = String()
    email = String(fmt="email")
    is_superuser = Boolean(default=False)
```

Then in another file named `users.py` we request the API and get back JSON response, after getting the response we
validate it with our `User` model that we created:

```python
import requests
from models import User

with requests.Session() as sess:
    # Setting cookies and auth tokens here...
    response = sess.get("http://example.com/api/v1/users?id=1").json()

# Now let's validate the response!
user = User(**response)
print(user)
```

Now go ahead and open up your terminal and run the `users.py` file to see the result:

```console
$ python users.py
```

If the validation is successful, you'll see the user instance printed:

```console
User(id=1, username="Pygrammer", email="IHosseini@pm.me", is_superuser=False)
```

But if the JSON response doesn't fulfill our constraints set in `User` model, you'll get a `pyjdb.errors.ValidationError`
error. e.g. the JSON response doesn't contain an `id` parameter:

```console
pyjdb.errors.ValidationError:
  |-- 'id': <None> -> This field is required.
```

## Contributing

If you like this project and want to improve its quality, please consider contributing to it by **_opening an issue_** or _**creating a pull request**_.

---

<p align="center">
<i>PyJDB is a <a href="https://en.wikipedia.org/wiki/MIT_License">MIT</a> licensed code.<br/>Designed with care.</i><br/>—⚡—
</p>
