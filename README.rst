Description
===========

This package provides an unofficial Python client for the
`Partner API <https://www.http.net/docs/api/>`__ of http.net Internet GmbH.
So far, ``v1`` of the API (the only existing version) is supported.


Disclaimer
==========

This package is not related to http.net Internet GmbH. So far, it is just a
proof of concept and not tested in any way.


Installation
============

Use the package manager `pip <https://pip.pypa.io/en/stable/>`__ to install
``httpnet``:

.. code::

    pip install git+https://github.com/eseifert/httpnet.git


Usage
=====

First, we need a client instance:

.. code::

    >>> from httpnet.client import HttpNetClient
    >>> AUTH_TOKEN = '<your auth token>'
    >>> api = HttpNetClient(auth_token=AUTH_TOKEN)


Almost all services provide a common query interface:

.. code::

    >>> from httpnet.domain import ContactType
    >>> persons = api.domain_contacts.find(ContactType=str(ContactType.PERSON))
    >>> len(list(persons))
    42


Contributing
============

Pull requests are always welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.


License
=======

`MIT <https://choosealicense.com/licenses/mit/>`__

By submitting a pull request for this project, you agree to license your
contribution under the MIT license to this project.
