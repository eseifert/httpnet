import inspect
import json
import re
import sys
from collections import ChainMap
from collections.abc import Iterator, Mapping, MutableMapping
from datetime import datetime
from enum import Enum
from types import UnionType
from typing import Any, ClassVar, Generic, TypeAlias, TypeVar, Union, get_args, get_origin

import dateutil.parser
import requests

if sys.version_info >= (3, 14):
    import annotationlib

JsonObject: TypeAlias = MutableMapping[str, Any]


class Platform(Enum):
    """
    Known deployments of the API. http.net Internet GmbH also operates the
    same API for hosting.de, only the base URL differs.
    """

    HTTP_NET = 'https://partner.http.net/api'
    HOSTING_DE = 'https://secure.hosting.de/api'

    def __repr__(self):
        return f'{self.__class__.__qualname__}.{self.name}'

    def __str__(self):
        return self.value


class Client:
    USER_AGENT = 'HTTP.NET Partner API Python client 1.0'
    BASE_URL = str(Platform.HTTP_NET)
    VERSION = 'v1'
    FORMAT = 'json'
    DEFAULT_TIMEOUT = 180

    def __init__(self, auth_token: str, owner_account_id: str | None = None,
                 timeout: float | tuple[float, float] | None = None,
                 base_url: Platform | str = Platform.HTTP_NET) -> None:
        self.auth_token = auth_token
        self.base_url = str(base_url).rstrip('/')
        self.owner_account_id = owner_account_id
        self.timeout: float | tuple[float, float] = Client.DEFAULT_TIMEOUT
        if isinstance(timeout, tuple):
            if all(t > 0 for t in timeout):
                self.timeout = timeout
        elif timeout is not None and timeout > 0:
            self.timeout = timeout
        self.__session = requests.Session()
        self.__session.headers.update({'User-Agent': Client.USER_AGENT})

    def call(self, service: str, method: str,
             parameters: Mapping[str, Any] | None = None) -> JsonObject:
        """
        Calls the method of a service.

        :param service: Name of the service
        :param method: Name of the method
        :param parameters: Mapping of input parameters
        :return: JSON data structure of the response
        """
        url = f'{self.base_url}/{service}/{Client.VERSION}/{Client.FORMAT}/{method}'
        request: ChainMap[str, Any] = ChainMap({
            'authToken': self.auth_token,
        })
        if self.owner_account_id:
            request['ownerAccountId'] = self.owner_account_id
        if parameters is not None:
            request.maps.append(dict(parameters))
        response = self.__session.post(url, data=json.dumps(dict(request)), timeout=self.timeout)
        response.raise_for_status()
        return response.json()


def camel_case(snake_str: str) -> str:
    first, *others = snake_str.split('_')
    return ''.join([first.lower(), *map(str.title, others)])


def snake_case(camel_str: str) -> str:
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def _declared_field_names(ns: Mapping[str, Any]) -> list[str]:
    """
    Extracts the names of all annotated fields from a class namespace while the
    class is being created. Since Python 3.14 (:pep:`649`) annotations are
    evaluated lazily and are no longer present in the namespace, so the
    annotation function has to be called instead. The string format is used
    because only the names are of interest and it also copes with annotations
    that reference names which do not exist yet.
    """
    annotations = ns.get('__annotations__')
    if annotations is None and sys.version_info >= (3, 14):
        annotate = ns.get('__annotate_func__')
        if annotate is not None:
            annotations = annotationlib.call_annotate_function(
                annotate, annotationlib.Format.STRING)
    return list(annotations or {})


def _field_types(cls: type) -> Mapping[str, Any]:
    """
    Returns the resolved types of all fields annotated in the body of ``cls``.
    Annotations inherited from base classes are not included.
    """
    return inspect.get_annotations(cls)


class ElementMeta(type):
    def __new__(mcs, typename: str, bases, ns):
        if ns.get('_root', False):
            return super().__new__(mcs, typename, bases, ns)
        fields = _declared_field_names(ns)
        ns['__slots__'] = fields
        # Mirror of ``__slots__`` that is visible to static type checkers.
        ns['_fields'] = tuple(fields)
        return super().__new__(mcs, typename, bases, ns)


def _from_json_value(value, type_):
    if value is None:
        return None
    if type_ is Any:
        return value
    origin = get_origin(type_)
    if origin in (Union, UnionType):
        args = get_args(type_)
        for arg in args:
            if arg is type(None):
                continue
            try:
                return _from_json_value(value, arg)
            except (AttributeError, TypeError, ValueError):
                continue
        # The API uses an empty string to denote an unset value, e.g. for the
        # deletion date of a domain that is not scheduled for deletion.
        if value == '' and type(None) in args:
            return None
        return value
    if origin is not None:
        args = get_args(type_)
        # Mappings have to be handled before the sequence case, iterating one
        # would yield its keys instead of its items.
        if isinstance(origin, type) and issubclass(origin, Mapping):
            value_type = args[1] if len(args) > 1 else None
            return {k: _from_json_value(v, value_type) for k, v in value.items()}
        return [_from_json_value(v, args[0]) for v in value] if args else list(value)
    if type_ is datetime and isinstance(value, str):
        return dateutil.parser.parse(value)
    if isinstance(type_, type) and issubclass(type_, Element):
        return type_.from_json(value)
    if not isinstance(type_, type):
        return value
    return type_(value)


def _to_json_value(value, type_):
    if value is None or isinstance(value, (str, int, float)):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Element):
        return value.to_json()
    if isinstance(value, (list, tuple)):
        args = get_args(type_)
        item_type = args[0] if args else None
        return [_to_json_value(v, item_type) for v in value]
    if isinstance(value, Mapping):
        args = get_args(type_)
        value_type = args[1] if len(args) > 1 else None
        return {k: _to_json_value(v, value_type) for k, v in value.items()}
    if isinstance(value, Enum):
        return str(value)
    raise TypeError(f'Unknown type: {type_}')


class Element(metaclass=ElementMeta):
    """
    Base class of all objects the API exchanges. Subclasses declare their
    fields as class annotations, from which the conversion to and from JSON is
    derived. Fields that are not passed to the constructor are ``None``.
    """

    _root = True
    _fields: ClassVar[tuple[str, ...]] = ()

    def __init__(self, **kwargs) -> None:
        for field in self._fields:
            setattr(self, field, None)
        for field, value in kwargs.items():
            setattr(self, field, value)

    def __repr__(self) -> str:
        params = ', '.join([f'{field}={getattr(self, field)!r}' for field in self._fields])
        return f'{self.__class__.__qualname__}({params})'

    def to_json(self) -> JsonObject:
        """
        Converts this element to the JSON data structure of the API. Field
        names are converted from ``snake_case`` to ``camelCase``, fields that
        are ``None`` are omitted.

        :return: JSON data structure of this element
        """
        fields: JsonObject = {}
        for field, type_ in _field_types(type(self)).items():
            value = getattr(self, field, None)
            if value is not None:
                field_id = camel_case(field)
                fields[field_id] = _to_json_value(value, type_)
        return fields

    @classmethod
    def from_json(cls, data: JsonObject):
        """
        Creates an element from the JSON data structure of the API. Field names
        are converted from ``camelCase`` to ``snake_case``, values are
        converted to the types the fields are annotated with.

        :param data: JSON data structure as returned by the API
        :return: New element
        :raises KeyError: if the data contains a field this element does not
            declare
        """
        fields: JsonObject = {}
        field_types = _field_types(cls)
        for field_id, value in data.items():
            field = snake_case(field_id)
            try:
                field_type = field_types[field]
            except KeyError as e:
                raise KeyError(f'No field "{field}" defined in API model "{cls.__qualname__}"') from e
            fields[field] = _from_json_value(value, field_type)
        return cls(**fields)


class ServiceException(Exception):
    """
    Raised when the API rejects a request. The message contains every error the
    API reported, each followed by its error code in parentheses.
    """


T = TypeVar('T', bound=Element)


def _element_class_of(service_class: type) -> Any:
    """
    Determines the element class a service class has been parameterized with,
    e.g. ``Contact`` for ``class ContactService(Service[Contact])``.
    """
    for klass in service_class.__mro__:
        # Only the class's own bases matter, inherited ones would yield the type
        # variable of the generic base class instead of a concrete element class.
        for base in klass.__dict__.get('__orig_bases__', ()):
            for arg in get_args(base):
                if isinstance(arg, type) and issubclass(arg, Element):
                    return arg
    raise TypeError(f'{service_class.__qualname__} does not specify an element type')


class Service(Generic[T]):
    _MAX_PAGES = 1000000

    def __init__(self, client: Client) -> None:
        self._client = client
        self._element_class: type[T] = _element_class_of(type(self))

    @property
    def _service_domain(self) -> str:
        module_name = self.__module__.rsplit('.', 1)[-1]
        return module_name[0].lower() + module_name[1:]

    @property
    def _element_name(self) -> str:
        class_name = self._element_class.__name__
        return class_name[0].lower() + class_name[1:]

    @property
    def _id_name(self) -> str:
        return f'{self._element_name}Id'

    @property
    def _get_method_name(self) -> str:
        return f'{self._element_name}Info'

    @property
    def _create_method_name(self) -> str:
        return f'{self._element_name}Create'

    @property
    def _update_method_name(self) -> str:
        return f'{self._element_name}Update'

    @property
    def _delete_method_name(self) -> str:
        return f'{self._element_name}Delete'

    @property
    def _find_method_name(self) -> str:
        if self._element_name.endswith('s'):
            return f'{self._element_name}Find'
        else:
            return f'{self._element_name}sFind'

    def _call(self, method: str, parameters: Mapping[str, Any] | None = None) -> JsonObject:
        response = self._client.call(self._service_domain, method, parameters)
        status = str(response.get('status', '')).lower()
        if status not in {'success', 'pending'}:
            errors = response.get('errors') or []
            error_messages = [f'{error["text"]} ({error["code"]}).' for error in errors]
            raise ServiceException(' '.join(error_messages) or f'API returned status "{status}".')
        return response

    def get(self, key: str, /) -> T:
        """
        Retrieves a single element by its ID.

        :param key: ID of the element
        :return: The element
        :raises ServiceException: if no element with this ID exists
        """
        response = self._call(
            method=self._get_method_name,
            parameters={self._id_name: key}
        )
        response_body = response['response']
        return self._element_class.from_json(response_body)

    def _find_parameters(self, limit: int | None = None, sort: str | None = None,
                         filters: Mapping[str, Any] | None = None) -> JsonObject:
        parameters: JsonObject = {}
        if limit:
            parameters['limit'] = limit
        if sort:
            if sort.startswith('~'):
                sort_params = dict(field=sort.lstrip('~'), order='desc')
            else:
                sort_params = dict(field=sort, order='asc')
            parameters['sort'] = sort_params
        if filters:
            parameters['filter'] = dict(
                subFilterConnective='AND',
                subFilter=[
                    dict(field=field, value=json.dumps(value).strip('"').replace(r'\"', '"'))
                    for field, value in filters.items()
                ]
            )
        return parameters

    def find(self, limit: int | None = None, page: int | None = None,
             sort: str | None = None, **filters) -> Iterator[T]:
        """
        Retrieves all elements matching the given filters. The results are
        fetched page by page while the returned iterator is consumed.

        :param limit: Number of elements per request, the API defaults to 25
        :param page: Number of the only page to retrieve. By default all pages
            are retrieved.
        :param sort: Name of the field to sort by, prefixed with ``~`` for
            descending order
        :param filters: Field names and values to filter by, as named by the
            API. An asterisk in a value matches any number of characters.
        :return: Iterator over the matching elements
        """
        parameters = self._find_parameters(limit=limit, sort=sort, filters=filters)
        if page:
            page_range = range(page, page + 1)
        else:
            page_range = range(1, Service._MAX_PAGES)
        for page in page_range:
            parameters['page'] = page
            response = self._call(
                method=self._find_method_name,
                parameters=parameters
            )
            response_body = response.get('response', {})
            for json_element in (response_body.get('data') or []):
                element = self._element_class.from_json(json_element)
                yield element
            total_pages = response_body.get('totalPages', 0)
            if total_pages == 0 or page == total_pages:
                break

    def count(self, sort: str | None = None, **filters) -> int:
        """
        Returns the number of elements matching the given filters without
        retrieving them. This is a single request, the API reports the total
        number of matches for every listing.

        :param sort: Name of the field to sort by, ignored for the result
        :param filters: Field names and values to filter by
        :return: Number of matching elements
        """
        response = self._call(
            method=self._find_method_name,
            parameters={**self._find_parameters(limit=1, sort=sort, filters=filters), 'page': 1}
        )
        return response.get('response', {}).get('totalEntries', 0)

    def __len__(self) -> int:
        """
        Returns the total number of elements of this service.

        Note that this makes the service a sized iterable, so ``list(service)``
        asks the API for the number of elements before it starts iterating.
        Use ``list(service.find())`` to avoid that additional request.
        """
        return self.count()

    def __iter__(self) -> Iterator[T]:
        return self.find()


class CreatableService(Service[T]):
    """
    A service whose ``<element>Create`` method takes a complete element and
    responds with the created one.
    """

    def create(self, element: T, /) -> T:
        """
        Creates a new element.

        :param element: Complete element to be created. Its ID is ignored.
        :return: The created element as stored by the API
        """
        response = self._call(
            method=self._create_method_name,
            parameters={self._element_name: element.to_json()}
        )
        return self._element_class.from_json(response.get('response', {}))


class UpdatableService(Service[T]):
    """
    A service whose ``<element>Update`` method takes a complete element and
    responds with the updated one. The element to be updated is identified by
    the ID it carries, all of its other fields are set to the given values.
    """

    def update(self, element: T, /) -> T:
        """
        Updates an existing element. The element is identified by the ID it
        carries. All of its other fields are set to the given values, fields
        that are not set are reset to their defaults.

        :param element: Complete element with the new values
        :return: The updated element as stored by the API
        """
        response = self._call(
            method=self._update_method_name,
            parameters={self._element_name: element.to_json()}
        )
        return self._element_class.from_json(response.get('response', {}))


class DeletableService(Service[T]):
    """
    A service whose ``<element>Delete`` method takes the ID of an element.
    """

    def delete(self, key: str, /) -> None:
        """
        Deletes an element.

        :param key: ID of the element to be deleted
        """
        self._call(
            method=self._delete_method_name,
            parameters={self._id_name: key}
        )


class CrudService(CreatableService[T], UpdatableService[T], DeletableService[T]):
    """
    A service that follows the generic create/update/delete scheme of the API.
    Services that deviate from it derive from :class:`Service` or from the
    individual base classes and declare their own methods.
    """
