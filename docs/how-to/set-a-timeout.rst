How to set a request timeout
============================

Pass the number of seconds as ``timeout``:

.. code-block:: python

    from httpnet.client import HttpNetClient

    api = HttpNetClient(auth_token='<your api key>', timeout=30)

Without a timeout the client waits up to 180 seconds for a response.

Set connect and read timeouts separately
----------------------------------------

Pass a tuple of ``(connect, read)`` seconds:

.. code-block:: python

    api = HttpNetClient(auth_token='<your api key>', timeout=(3.05, 60))

Use a short connect timeout to fail fast on network problems and a longer read
timeout for requests that take the API a while to answer.

Handle a timeout
----------------

A timeout surfaces as the exception of the underlying HTTP library:

.. code-block:: python

    import requests

    try:
        domains = list(api.domains.find())
    except requests.Timeout:
        print('The API did not answer in time')

.. note::

   Values of ``0`` or less are ignored and the default of 180 seconds is used
   instead. To fail immediately, catch the exception rather than setting a
   zero timeout.
