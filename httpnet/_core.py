import json
import re
from collections import ChainMap
from datetime import datetime
from enum import Enum
from typing import Generic, Iterable, Iterator, Mapping, MutableMapping, \
    Optional, Sequence, Tuple, TypeVar, Union

import dateutil.parser
import requests


JsonObject = MutableMapping


class Client:
    USER_AGENT = 'HTTP.NET Partner API Python client 1.0'
    BASE_URL = 'https://partner.http.net/api'
    VERSION = 'v1'
    FORMAT = 'json'
    DEFAULT_TIMEOUT = 180

    def __init__(self, auth_token: str, owner_account_id: Optional[str] = None,
                 timeout: Optional[Union[float, Tuple[float, float]]] = None) -> None:
        self.auth_token = auth_token
        self.owner_account_id = owner_account_id
        self.timeout = timeout if timeout and timeout > 0 else Client.DEFAULT_TIMEOUT
        self.__session = requests.Session()
        self.__session.headers.update({'User-Agent': Client.USER_AGENT})

    def call(self, service: str, method: str, parameters: Optional[Mapping] = None) -> JsonObject:
        """
        Calls the method of a service.

        :param service: Name of the service
        :param method: Name of the method
        :param parameters: Mapping of input parameters
        :return: JSON data structure of the response
        """
        url = f'{Client.BASE_URL}/{service}/{Client.VERSION}/{Client.FORMAT}/{method}'
        request = ChainMap({
            'authToken': self.auth_token,
        })
        if self.owner_account_id:
            request['ownerAccountId'] = self.owner_account_id
        if parameters is not None:
            request.maps.append(parameters)
        response = self.__session.post(url, data=json.dumps(dict(request)), timeout=self.timeout)
        response.raise_for_status()
        return response.json()


def camel_case(snake_str: str) -> str:
    first, *others = snake_str.split('_')
    return ''.join([first.lower(), *map(str.title, others)])


def snake_case(camel_str: str) -> str:
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class ElementMeta(type):
    def __new__(mcs, typename: str, bases, ns):
        if ns.get('_root', False):
            return super().__new__(mcs, typename, bases, ns)
        fields = list(ns.get('__annotations__', {}).keys())
        ns['__slots__'] = fields
        return super().__new__(mcs, typename, bases, ns)


def _from_json_value(value, type_):
    if type_ is type(None) and value is None:
        return None
    if repr(type_).startswith('typing.Union['):
        for t in reversed(type_.__args__):
            try:
                return _from_json_value(value, t)
            except (AttributeError, TypeError):
                continue
    if isinstance(type_, (type(Iterable), type(Sequence))):
        return [_from_json_value(v, type_.__args__[0]) for v in value]
    if type_ is datetime and isinstance(value, str):
        return dateutil.parser.parse(value)
    if issubclass(type_, Element):
        return type_.from_json(value)
    return type_(value)


def _to_json_value(value, type_):
    if value is None or isinstance(value, (str, int)):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Element):
        return value.to_json()
    if isinstance(value, list):
        return [_to_json_value(v, type_.__args__[0]) for v in value]
    if isinstance(value, dict):
        return {k: _to_json_value(v, type_.__args__[1]) for k, v in value.items()}
    if isinstance(value, Enum):
        return str(value)
    raise TypeError(f'Unknown type: {type_}')


class Element(metaclass=ElementMeta):
    _root = True

    def __init__(self, **kwargs) -> None:
        for field in self.__slots__:
            setattr(self, field, None)
        for field, value in kwargs.items():
            setattr(self, field, value)

    def __repr__(self) -> str:
        params = ', '.join([f'{field}={getattr(self, field)!r}' for field in self.__slots__])
        return f'{self.__class__.__qualname__}({params})'

    def to_json(self) -> JsonObject:
        fields = {}
        for field, type_ in self.__annotations__.items():
            value = getattr(self, field, None)
            if value is not None:
                field_id = camel_case(field)
                fields[field_id] = _to_json_value(value, type_)
        return fields

    @classmethod
    def from_json(cls, data: JsonObject):
        fields = {}
        for field_id, value in data.items():
            field = snake_case(field_id)
            try:
                field_type = cls.__annotations__[field]
            except KeyError as e:
                raise KeyError(f'No field "{field}"" defined in API model "{cls.__qualname__}"')
            fields[field] = _from_json_value(value, field_type)
        return cls(**fields)


class ServiceException(Exception):
    pass


T = TypeVar('T', bound=Element)


class Service(Generic[T]):
    _MAX_PAGES = 1000000

    def __init__(self, client: Client) -> None:
        self._client = client
        self._element_class = self.__orig_bases__[0].__args__[0]

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

    def _call(self, method: str, parameters: Optional[Mapping] = None) -> Mapping:
        response = self._client.call(self._service_domain, method, parameters)
        if response.get('status').lower() not in {'success', 'pending'}:
            error_messages = [f'{error["text"]} ({error["code"]}).' for error in response['errors']]
            raise ServiceException(' '.join(error_messages))
        return response

    def get(self, key: str) -> T:
        response = self._call(
            method=self._get_method_name,
            parameters={self._id_name: key}
        )
        response_body = response['response']
        return self._element_class.from_json(response_body)

    def create(self, element: T) -> None:
        self._call(
            method=self._create_method_name,
            parameters={self._element_name: element.to_dict()}
        )

    def update(self, key: str, item: T) -> None:
        self._call(
            method=self._update_method_name,
            parameters={self._element_name: key}
        )

    def delete(self, key: str) -> None:
        self._call(
            method=self._delete_method_name,
            parameters={self._id_name: key}
        )

    def find(self, limit: Optional[int] = None, page: Optional[int] = None,
             sort: Optional[str] = None, **filters) -> Iterator[T]:
        parameters = {}
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
