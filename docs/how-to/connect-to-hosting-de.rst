How to connect to hosting.de
============================

Pass the ``HOSTING_DE`` platform as ``base_url``:

.. code-block:: python

    from httpnet.client import HttpNetClient, Platform

    api = HttpNetClient(auth_token='<your api key>', base_url=Platform.HOSTING_DE)

Requests now go to ``https://secure.hosting.de/api`` instead of
``https://partner.http.net/api``.

Use another deployment
----------------------

Pass the base URL as a string:

.. code-block:: python

    api = HttpNetClient(auth_token='<your api key>',
                        base_url='https://api.example.com/api')

The client appends ``/<service>/v1/json/<method>`` to whatever you pass, so
give it the URL up to and including ``/api``.

Use both platforms at once
--------------------------

Create one client per platform. Each keeps its own base URL:

.. code-block:: python

    http_net = HttpNetClient(auth_token='<http.net api key>')
    hosting_de = HttpNetClient(auth_token='<hosting.de api key>',
                               base_url=Platform.HOSTING_DE)

    for domain in http_net.domains:
        print('http.net', domain.name)
    for domain in hosting_de.domains:
        print('hosting.de', domain.name)
