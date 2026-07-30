Why services come in several kinds
==================================

Every service inherits reading — :meth:`~httpnet._core.Service.get`,
:meth:`~httpnet._core.Service.find`, :meth:`~httpnet._core.Service.count` and
iteration — from :class:`~httpnet._core.Service`. Writing is spread over three
further base classes, and a service inherits only the ones that apply to it.

The obvious design does not work
--------------------------------

The obvious design gives the base class all four operations and lets every
service inherit them. It falls apart as soon as the services are compared with
what the API actually offers.

Contacts cannot be deleted at all; the API documentation says so outright and
expects unused contacts to expire on their own. Zone configurations and records
have no create, update or delete of their own, because both are managed through
their zone. Jobs are created by the API itself and can only be read. Domain
settings exist for every domain and can only be listed and updated — there is
nothing to create or delete.

Of the services that do write, several do not fit a uniform signature. Deleting
a zone takes the ID of its configuration, deleting a mailbox takes either an ID
or an address plus an optional date, and deleting a domain takes a name and an
optional date. Creating a zone takes a zone plus two parameters that select
name servers and answers with the created zone; updating one takes a
configuration and three separate lists of records.

A base class that declares ``create``, ``update`` and ``delete`` therefore
forces every one of these services to contradict it. Some had to override the
methods with stubs raising :exc:`NotImplementedError` merely to say "not here",
and the ones that genuinely write had to change the signature they inherited.
Both are violations of the Liskov substitution principle, and a type checker
flags them as such: code written against the base class cannot safely be handed
a subclass.

Capability by inheritance
-------------------------

Splitting the write operations into :class:`~httpnet._core.CreatableService`,
:class:`~httpnet._core.UpdatableService` and
:class:`~httpnet._core.DeletableService` makes the type say what is true.
:class:`~httpnet._core.CrudService` combines all three for the services that do
fit the generic scheme.

A service that does not support an operation simply does not inherit it, so the
attribute is absent rather than present-but-raising. A service whose signature
differs derives from :class:`~httpnet._core.Service` and declares its own
methods, with no inherited declaration to contradict. Whether an operation is
available becomes visible in the class definition and checkable statically,
instead of being discovered at runtime.

The generic operations
----------------------

Where the generic scheme does apply, it is strikingly regular. Creating and
updating both send the complete element under the name of its type —
``{"contact": {...}}``, ``{"nameserverSet": {...}}`` — and both answer with the
stored object. Updating identifies the element by the ID it carries rather than
by a separate key parameter, which is why
:meth:`~httpnet._core.UpdatableService.update` takes only the element.

That regularity is what makes a single implementation on a base class possible
at all. The names of the methods, the name of the parameter and the name of the
ID field are all derived from the class name of the element.

Elements are not active objects
-------------------------------

An element has no reference to the service or the client it came from. It
cannot save or delete itself; those operations live on the service. The
separation keeps elements to what they are — a typed view of a JSON document —
and means an element can be built locally, inspected and passed around without
any connection to a server.
