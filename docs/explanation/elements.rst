Elements and their annotations
==============================

The objects the API sends and receives are represented by subclasses of
:class:`~httpnet._core.Element`. An element declares its fields as ordinary
class annotations and nothing else:

.. code-block:: python

    class DnsRecord(Element):
        id: str | None
        name: str | None
        type: RecordType | None
        content: str | None
        ttl: int | None

There is no field constructor, no schema object and no explicit list of names.
The annotations *are* the schema, and the conversion between JSON and Python
reads them at runtime.

Why annotations
---------------

The alternative would be a declarative field API, as data-mapping libraries
usually provide. Annotations were chosen because the API has a large number of
objects with a large number of fields, and because the mapping between the two
sides is mechanical: a JSON name in ``camelCase`` corresponds to a Python name
in ``snake_case``, a JSON string that a field types as ``datetime`` is parsed
as a date, a nested object whose field is typed as an element is converted
recursively.

The cost is that the conversion has to inspect types at runtime, which is
awkward in a language where annotations are not designed to be inspected. Most
of the subtleties below follow from that.

Unions and optionality
----------------------

Nearly every field is optional, because the API omits what is not set and
because most fields are output-only. An optional field is annotated ``X |
None``, and the conversion has to look inside that union to find ``X``.

Doing so by inspecting the textual representation of the annotation, as the
package once did, is fragile: ``typing.Optional[str]``, ``typing.Union[str,
None]`` and ``str | None`` describe the same type but look nothing alike. The
conversion therefore uses :func:`typing.get_origin` and :func:`typing.get_args`,
which answer the same question for all three spellings.

When a value fits none of the members of a union, the conversion falls back to
passing the value through unchanged rather than raising. The API occasionally
sends values the annotations do not anticipate, and losing a field is a smaller
problem than failing to parse the object that contains it.

The empty string
----------------

The API uses the empty string where a value is not set. A domain that is not
scheduled for deletion has ``"deletionDate": ""`` rather than ``null``.

For a field typed ``datetime | None`` there is no sensible way to read that as
a date, so it becomes ``None``. For a field typed ``str | None`` the empty
string is a perfectly good string and is kept. And for
:class:`~httpnet.domain.DeletionType`, which declares an explicit member for
the empty string, it becomes that member. The conversion arrives at all three
by trying the members of the union first and only treating the empty string as
absent when nothing else fits.

Deferred annotations
--------------------

Python 3.14 changed how annotations are stored. Under :pep:`649` they are no
longer evaluated when a class body runs; a class carries a function that
produces them on demand instead. Code that read ``__annotations__`` out of the
class namespace during class creation — as the metaclass of
:class:`~httpnet._core.Element` did — silently found nothing, and every element
ended up with no fields at all.

The field names are now taken from that function, in its string format, which
never fails even when an annotation mentions a name that does not exist yet.
The field *types* are resolved separately and lazily with
:func:`inspect.get_annotations`, at the moment an object is converted, by which
time every name the annotations refer to is defined.

This is also why the fields of a class are read from the class itself and never
inherited from a base class. Annotation lookup through the class hierarchy
behaves differently across Python versions, and elements have no inheritance to
speak of, so restricting the lookup avoids the question entirely.
