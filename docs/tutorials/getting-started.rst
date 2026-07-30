Getting started
===============

In this tutorial you will connect to the API and look around your account. You
will count your domains, list them, pick one out and inspect the contacts and
name servers attached to it.

Everything you do here only reads data. Nothing in your account will change.

Install the package
-------------------

Create a directory for this tutorial, set up a virtual environment and install
``httpnet``:

.. code-block:: console

    $ mkdir httpnet-tutorial
    $ cd httpnet-tutorial
    $ python -m venv .venv
    $ source .venv/bin/activate
    $ pip install git+https://github.com/eseifert/httpnet.git

Check that the package can be imported:

.. code-block:: console

    $ python -c "import httpnet; print('ready')"
    ready

If you see ``ready``, the installation worked.

Connect to the API
------------------

Start a Python session:

.. code-block:: console

    $ python

Create a client with your API key:

.. code-block:: pycon

    >>> from httpnet.client import HttpNetClient
    >>> api = HttpNetClient(auth_token='<your api key>')
    >>> api
    <httpnet.client.HttpNetClient object at 0x7f4b2c0d1e50>

Nothing has been sent to the API yet. The client only starts talking to the
server when you ask it for data.

Count your domains
------------------

Ask the client how many domains your account holds:

.. code-block:: pycon

    >>> len(api.domains)
    123

That number is the answer to your first API request. If you get a number back,
your API key works.

If instead you see an error like this, the key was not accepted:

.. code-block:: pycon

    >>> len(api.domains)
    Traceback (most recent call last):
      ...
    httpnet._core.ServiceException: Authorization failed (10001).

Check the key and create the client again before you carry on.

List your domains
-----------------

Every service can be iterated over. Print the name of each domain:

.. code-block:: pycon

    >>> for domain in api.domains:
    ...     print(domain.name)
    ...
    example.com
    example.net
    example.org

The client fetches the results page by page while you iterate, so you do not
have to think about paging.

If your account holds many domains, this prints a long list. Stop it with
:kbd:`Ctrl-C` and ask for the first few instead:

.. code-block:: pycon

    >>> import itertools
    >>> for domain in itertools.islice(api.domains.find(), 3):
    ...     print(domain.name)
    ...
    example.com
    example.net
    example.org

Look at a single domain
-----------------------

Pick one of the names you just saw and fetch that domain:

.. code-block:: pycon

    >>> domain = api.domains.get('example.com')
    >>> domain.name
    'example.com'
    >>> domain.status
    DomainStatus.ACTIVE

The fields of the domain are ordinary Python attributes. Dates arrive as
:class:`~datetime.datetime` objects:

.. code-block:: pycon

    >>> domain.create_date
    datetime.datetime(2014, 1, 1, 0, 0)
    >>> domain.transfer_lock_enabled
    False

Inspect contacts and name servers
---------------------------------

A domain carries a list of contacts, each with a role:

.. code-block:: pycon

    >>> for contact in domain.contacts:
    ...     print(contact.type, contact.contact)
    ...
    DomainContactType.OWNER 150101000000021
    DomainContactType.ADMIN 150101000000020
    DomainContactType.TECH 150101000000022
    DomainContactType.ZONE 150101000000023

The values in the second column are contact IDs. Fetch the owner to see who it
belongs to:

.. code-block:: pycon

    >>> owner_id = domain.contacts[0].contact
    >>> owner = api.domain_contacts.get(owner_id)
    >>> owner.name
    'John Smith'
    >>> owner.city
    'Where ever'

The name servers of the domain work the same way:

.. code-block:: pycon

    >>> for nameserver in domain.nameservers:
    ...     print(nameserver.name, nameserver.ips)
    ...
    ns.example.net []
    ns.example.com ['192.0.2.1', '2001:db8:3fe:1001:7777:772e:2:85']

Narrow a listing down
---------------------

Listings can be filtered. Count how many of your contacts are persons rather
than organizations:

.. code-block:: pycon

    >>> from httpnet.domain import ContactType
    >>> api.domain_contacts.count(ContactType=str(ContactType.PERSON))
    42

Then fetch them:

.. code-block:: pycon

    >>> persons = api.domain_contacts.find(ContactType=str(ContactType.PERSON))
    >>> next(persons).handle
    'JS15'

``count`` gives you the number of matches without downloading them, ``find``
gives you the matches themselves.

Look at your DNS zones
----------------------

The DNS part of the API works just like the domain part:

.. code-block:: pycon

    >>> len(api.dns_zones)
    12

Fetch one zone and look at its records:

.. code-block:: pycon

    >>> zone = next(api.dns_zones.find(limit=1))
    >>> zone.zone_config.name
    'example.com'
    >>> for record in zone.records[:3]:
    ...     print(record.type, record.name, record.content)
    ...
    RecordType.A example.com 192.0.2.1
    RecordType.MX example.com smtp.example.com
    RecordType.NS example.com ns.example.net

What you have learned
---------------------

You created a client, made your first request, listed and filtered resources,
fetched a single object and followed a reference from one object to another.
That is the pattern the whole package follows: ``api.<service>`` gives you a
service, and every service offers ``get``, ``find``, ``count`` and iteration.

In the next tutorial you will change something: you will create a DNS zone and
delete it again.
