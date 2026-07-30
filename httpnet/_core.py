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


class Client:
    USER_AGENT = 'HTTP.NET Partner API Python client 1.0'
    BASE_URL = 'https://partner.http.net/api'
    VERSION = 'v1'
    FORMAT = 'json'
    DEFAULT_TIMEOUT = 180

    def __init__(self, auth_token: str, owner_account_id: str | None = None,
                 timeout: float | tuple[float, float] | None = None) -> None:
        self.auth_token = auth_token
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
        url = f'{Client.BASE_URL}/{service}/{Client.VERSION}/{Client.FORMAT}/{method}'
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
    origin = get_origin(type_)
    if origin in (Union, UnionType):
        for arg in get_args(type_):
            if arg is type(None):
                continue
            try:
                return _from_json_value(value, arg)
            except (AttributeError, TypeError, ValueError):
                continue
        return value
    if origin is not None:
        args = get_args(type_)
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
        fields: JsonObject = {}
        for field, type_ in _field_types(type(self)).items():
            value = getattr(self, field, None)
            if value is not None:
                field_id = camel_case(field)
                fields[field_id] = _to_json_value(value, type_)
        return fields

    @classmethod
    def from_json(cls, data: JsonObject):
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
    pass


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
        response = self._call(
            method=self._get_method_name,
            parameters={self._id_name: key}
        )
        response_body = response['response']
        return self._element_class.from_json(response_body)

    def find(self, limit: int | None = None, page: int | None = None,
             sort: str | None = None, **filters) -> Iterator[T]:
        parameters: JsonObject = {}
        if limit:
            parameters['limit'] = limit
        if page:
            page_range = range(page, page + 1)
        else:
            page_range = range(1, Service._MAX_PAGES)
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

    def __iter__(self) -> Iterator[T]:
        return self.find()


class CrudService(Service[T]):
    """
    A service whose elements follow the generic create/update/delete scheme of
    the API. Services that deviate from it derive from :class:`Service` and
    declare their own methods.
    """

    def create(self, element: T, /) -> None:
        self._call(
            method=self._create_method_name,
            parameters={self._element_name: element.to_json()}
        )

    def update(self, element: T, /) -> None:
        self._call(
            method=self._update_method_name,
            parameters={self._element_name: element.to_json()}
        )

    def delete(self, key: str, /) -> None:
        self._call(
            method=self._delete_method_name,
            parameters={self._id_name: key}
        )
