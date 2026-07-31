Description
===========

This package provides an unofficial Python client for the
`Partner API <https://www.http.net/docs/api/>`__ of http.net Internet GmbH.
So far, ``v1`` of the API (the only existing version) is supported. The same
API is also used by `hosting.de <https://www.hosting.de/api/>`__.

The full documentation, consisting of tutorials, how-to guides, a reference and
background explanations, is built from the ``docs`` directory and can be
published on Read the Docs.


Disclaimer
==========

This package is not related to http.net Internet GmbH.

The reading part of the API has been exercised against a live account: every
listing, every ``get`` and the availability check answer and convert correctly.
The writing part is covered by unit tests only and has not been tried against a
real account. Where the live API turned out to differ from its documentation,
the deviations are collected under `Where the API differs from its
documentation
<https://httpnet.readthedocs.io/en/latest/explanation/differences-to-the-documentation.html>`__.


Installation
============

``httpnet`` requires Python 3.10 or newer. Use the package manager
`pip <https://pip.pypa.io/en/stable/>`__ to install it:

.. code::

    pip install git+https://github.com/eseifert/httpnet.git

or add it to a project managed by `uv <https://docs.astral.sh/uv/>`__:

.. code::

    uv add git+https://github.com/eseifert/httpnet.git


Usage
=====

First, we need a client instance:

.. code::

    >>> from httpnet.client import HttpNetClient
    >>> AUTH_TOKEN = '<your auth token>'
    >>> api = HttpNetClient(auth_token=AUTH_TOKEN)

http.net Internet GmbH operates the same API for
`hosting.de <https://www.hosting.de/api/>`__. To use it, pass the respective
platform:

.. code::

    >>> from httpnet.client import HttpNetClient, Platform
    >>> api = HttpNetClient(auth_token=AUTH_TOKEN, base_url=Platform.HOSTING_DE)

The client provides access to all service categories in the API. They can be
counted and are iterable:

.. code::

    >>> len(api.domains)
    123
    >>> for domain in api.dns_zones:
    ...     print(domain.zone_config.name)

Almost all services provide a common query interface. ``find`` returns an
iterator, ``count`` returns the number of matches without retrieving them:

.. code::

    >>> from httpnet.domain import ContactType
    >>> persons = api.domain_contacts.find(ContactType=str(ContactType.PERSON))
    >>> next(persons).handle
    'JS15'
    >>> api.domain_contacts.count(ContactType=str(ContactType.PERSON))
    42


Contributing
============

Pull requests are always welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

The project is developed with `uv <https://docs.astral.sh/uv/>`__. To set up a
development environment and run the checks:

.. code::

    uv sync             # create the virtual environment
    uv run pytest       # run the test suite
    uv run ruff check   # lint
    uv run ruff format  # format
    uv run ty check     # type check

To build the documentation:

.. code::

    uv run sphinx-build --builder html --fail-on-warning docs docs/_build/html


License
=======

`MIT <https://choosealicense.com/licenses/mit/>`__

By submitting a pull request for this project, you agree to license your
contribution under the MIT license to this project.
