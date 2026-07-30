Reference
=========

Technical description of the package. The pages follow the structure of the
codebase: one page per module.

.. toctree::
   :maxdepth: 2

   client
   core
   domain
   dns
   email

Conventions
-----------

The following conventions apply throughout the package.

Naming
    Fields of the API are named in ``camelCase``, their Python counterparts in
    ``snake_case``. ``emailAddress`` becomes ``email_address``. Service methods
    that take a field name of the API, such as the filters of
    :meth:`~httpnet._core.Service.find`, expect the name as the API spells it.

Optional fields
    Every field an element declares exists on every instance. Fields that the
    API did not send are ``None``.

Identifiers
    Objects are identified by string IDs. Some services accept a name instead,
    which is noted at the respective method.

Processing
    Methods that the API processes asynchronously return once the request has
    been accepted, not once it has been carried out. The
    :class:`~httpnet.domain.Job` objects of
    :attr:`~httpnet.client.HttpNetClient.domain_jobs` report the outcome.
