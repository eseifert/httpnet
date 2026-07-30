How to handle large result sets
===============================

Iterate instead of building a list
----------------------------------

``find`` returns an iterator that fetches one page at a time:

.. code-block:: python

    for domain in api.domains.find():
        process(domain)

Only one page is held in memory at a time. Avoid ``list(api.domains.find())``
for large accounts.

Fetch a fixed number of results
-------------------------------

.. code-block:: python

    import itertools

    first_ten = list(itertools.islice(api.domains.find(), 10))

Fetch a single page
-------------------

Pass ``page`` to stop after that page:

.. code-block:: python

    second_page = list(api.domains.find(limit=50, page=2))

Without ``page`` the iterator continues until the last page is reached.

Choose the page size
--------------------

``limit`` is the number of results per request. The API defaults to 25:

.. code-block:: python

    for domain in api.domains.find(limit=100):
        process(domain)

Larger pages mean fewer requests and more memory per request.

Get the total without downloading it
------------------------------------

.. code-block:: python

    total = api.domains.count()

``len(api.domains)`` does the same. Note that because the services are sized
iterables, ``list(api.domains)`` asks for the total before it starts
iterating. Use ``list(api.domains.find())`` to skip that extra request.

Process in batches
------------------

.. code-block:: python

    import itertools

    domains = api.domains.find(limit=100)
    while batch := list(itertools.islice(domains, 100)):
        process_batch(batch)
