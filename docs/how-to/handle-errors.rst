How to handle errors
====================

Catch API errors
----------------

The API reports problems with your request as a
:class:`~httpnet._core.ServiceException`:

.. code-block:: python

    from httpnet._core import ServiceException

    try:
        contact = api.domain_contacts.get('15010100000010')
    except ServiceException as e:
        print('The API rejected the request:', e)

The message contains every error the API reported, each with its code:

.. code-block:: text

    Handle type is invalid (32002). Format of the phone number is invalid. The
    E.123 international notation is required (32022).

Catch transport errors
----------------------

Network problems and HTTP status codes are raised by the underlying HTTP
library:

.. code-block:: python

    import requests
    from httpnet._core import ServiceException

    try:
        domains = list(api.domains.find())
    except ServiceException as e:
        print('The API rejected the request:', e)
    except requests.HTTPError as e:
        print('The server answered with an error:', e.response.status_code)
    except requests.RequestException as e:
        print('The request could not be made:', e)

Handle a missing object
-----------------------

Fetching an object that does not exist raises a
:class:`~httpnet._core.ServiceException`, except for contacts, where it raises
a :exc:`KeyError`:

.. code-block:: python

    try:
        contact = api.domain_contacts.get('does-not-exist')
    except KeyError:
        contact = None

Check for existence without fetching
------------------------------------

.. code-block:: python

    if api.domains.count(DomainNameAce='example.com'):
        print('The domain is in this account')

Retry a failed request
----------------------

.. code-block:: python

    import time

    import requests

    def with_retries(call, attempts=3, delay=5):
        for attempt in range(attempts):
            try:
                return call()
            except (requests.Timeout, requests.ConnectionError):
                if attempt == attempts - 1:
                    raise
                time.sleep(delay * (attempt + 1))

    domain = with_retries(lambda: api.domains.get('example.com'))

Retry transport errors, but not a
:class:`~httpnet._core.ServiceException` — the API rejected that request and
will reject it again.
