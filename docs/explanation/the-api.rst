The API behind the package
==========================

``httpnet`` is a thin layer over an HTTP API. Understanding the shape of that
API explains most of the shape of the package.

One URL scheme, one verb
------------------------

Every endpoint of the Partner API has the form::

    https://partner.http.net/api/<service>/<version>/<format>/<method>

and is called with ``POST``. There is no REST-style mapping of HTTP verbs onto
operations: creating, reading and deleting a zone are three different
*methods*, all of them ``POST`` requests. Parameters are not encoded in the URL
or the query string, they are sent as a JSON document in the request body,
together with the API key.

This is why the package has no notion of resources and URLs. A service knows
the names of the methods that belong to its element — ``zoneCreate``,
``zoneUpdate``, ``zoneDelete`` — and derives them from the class name of the
element. A service for an element named ``Widget`` calls ``widgetCreate``,
``widgetUpdate``, ``widgetsFind`` and so on. Where the API deviates from that
pattern, the service overrides the derived name.

The same API, two platforms
---------------------------

http.net Internet GmbH runs the same API for hosting.de under a different host
name. Nothing else differs: the same services, the same methods, the same
objects. That is why the platform is a single parameter of the client rather
than a separate implementation, and why the client accepts an arbitrary base
URL as well.

Errors are not HTTP status codes
--------------------------------

A request that the API understood but rejected still answers with HTTP 200. The
outcome is in the ``status`` field of the response body, which is ``success``,
``pending`` or ``error``. Only transport-level problems — a malformed request,
an unknown method, a server that is down — produce a non-200 status code.

The package mirrors that split. A ``status`` of ``error`` raises a
:class:`~httpnet._core.ServiceException`, everything else stays with the
underlying HTTP library and surfaces as one of its exceptions. Catching only
:class:`~httpnet._core.ServiceException` therefore leaves network failures
uncaught, which is deliberate: the two kinds of failure usually call for
different reactions.

A rejected request reports *every* problem it has, not just the first. The API
collects all errors and warnings, so a contact with a bad type and a bad phone
number produces two error objects in one response. The exception message joins
them, which is why it can be longer than a single sentence.

Listings are uniform
--------------------

Every service that lists things does so with the same four parameters —
``filter``, ``limit``, ``page`` and ``sort`` — and answers with the same
envelope of ``data``, ``limit``, ``page``, ``totalEntries`` and ``totalPages``.
Only the field names you may filter and sort by differ between listings.

That uniformity is the reason :meth:`~httpnet._core.Service.find` and
:meth:`~httpnet._core.Service.count` are implemented once on the base class and
work for every service. It is also why ``totalEntries`` can be used to give
services a length: the count is free, the API reports it for every listing
whether you want it or not.
