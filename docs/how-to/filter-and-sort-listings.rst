How to filter and sort listings
===============================

Filter by a field
-----------------

Pass the field name as a keyword argument to ``find``:

.. code-block:: python

    for domain in api.domains.find(DomainNameAce='example.com'):
        print(domain.name)

Field names are those of the API, not the Python attribute names, and they are
case insensitive.

Match with a wildcard
---------------------

An asterisk matches any number of characters:

.. code-block:: python

    for domain in api.domains.find(DomainNameAce='*.de'):
        print(domain.name)

Combine several fields
----------------------

Pass more than one keyword argument. All conditions have to match:

.. code-block:: python

    contacts = api.domain_contacts.find(ContactType='person', ContactCity='Berlin')

Sort the results
----------------

Pass the field to sort by as ``sort``:

.. code-block:: python

    for domain in api.domains.find(sort='DomainNameAce'):
        print(domain.name)

Prefix the field with ``~`` to sort in descending order:

.. code-block:: python

    for domain in api.domains.find(sort='~DomainAddDate'):
        print(domain.name, domain.add_date)

Count matches instead of fetching them
--------------------------------------

``count`` takes the same filters as ``find`` and returns a number:

.. code-block:: python

    print(api.domains.count(DomainNameAce='*.de'))

Use an enumeration as a filter value
------------------------------------

Convert it to a string first:

.. code-block:: python

    from httpnet.domain import ContactType

    persons = api.domain_contacts.find(ContactType=str(ContactType.PERSON))
