httpnet._core
=============

.. module:: httpnet._core

The base classes the services and elements of the other modules are built on.
The module is private, but :class:`Platform` is re-exported by
:mod:`httpnet.client` and the members documented here describe the behavior
every service and element inherits.

Client
------

.. autoclass:: Client
   :members:

.. autoclass:: Platform
   :members:
   :undoc-members:

Elements
--------

.. autoclass:: Element
   :members:

Services
--------

The services are split by the operations the API offers for their elements.
:class:`Service` provides reading, the other classes add the write operations.
A service that deviates from the generic scheme derives from :class:`Service`
and declares its own methods, cf. :doc:`../explanation/service-classes`.

.. autoclass:: Service
   :members:
   :special-members: __iter__, __len__

.. autoclass:: CreatableService
   :members:

.. autoclass:: UpdatableService
   :members:

.. autoclass:: DeletableService
   :members:

.. autoclass:: CrudService
   :members:

Exceptions
----------

.. autoclass:: ServiceException
   :members:
   :show-inheritance:

Utilities
---------

.. autofunction:: camel_case

.. autofunction:: snake_case
