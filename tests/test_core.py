from datetime import datetime

import pytest

from httpnet._core import Client, CrudService, Element, Service, ServiceException


class Widget(Element):
    id: str | None
    name: str
    created: datetime | None


class WidgetService(CrudService[Widget]):
    pass


class ReadOnlyWidgetService(Service[Widget]):
    pass


class TestClient:
    def test_default_timeout_without_value(self) -> None:
        assert Client(auth_token='t').timeout == Client.DEFAULT_TIMEOUT

    def test_scalar_timeout_is_kept(self) -> None:
        assert Client(auth_token='t', timeout=5.0).timeout == 5.0

    def test_tuple_timeout_is_kept(self) -> None:
        # Regression: comparing a (connect, read) tuple against 0 used to raise a TypeError.
        assert Client(auth_token='t', timeout=(3.0, 10.0)).timeout == (3.0, 10.0)

    @pytest.mark.parametrize('timeout', [0, -1.0, (0.0, 10.0), (3.0, -1.0)])
    def test_non_positive_timeout_falls_back_to_default(self, timeout) -> None:
        assert Client(auth_token='t', timeout=timeout).timeout == Client.DEFAULT_TIMEOUT

    def test_call_sends_auth_token_and_parameters(self, client, session) -> None:
        client.call('dns', 'zonesFind', {'limit': 10})
        call = session.calls[0]
        assert call['url'] == 'https://partner.http.net/api/dns/v1/json/zonesFind'
        assert call['body'] == {'authToken': 'token', 'limit': 10}

    def test_call_includes_owner_account_id(self, session) -> None:
        client = Client(auth_token='token', owner_account_id='acct')
        client.call('dns', 'zonesFind')
        assert session.calls[0]['body']['ownerAccountId'] == 'acct'

    def test_parameters_cannot_override_auth_token(self, client, session) -> None:
        client.call('dns', 'zonesFind', {'authToken': 'evil'})
        assert session.calls[0]['body']['authToken'] == 'token'


class TestElement:
    def test_fields_are_derived_from_annotations(self) -> None:
        assert Widget._fields == ('id', 'name', 'created')

    def test_unset_fields_default_to_none(self) -> None:
        widget = Widget(name='gadget')
        assert widget.id is None
        assert widget.name == 'gadget'
        assert widget.created is None

    def test_repr_lists_all_fields(self) -> None:
        assert repr(Widget(name='gadget')) == "Widget(id=None, name='gadget', created=None)"

    def test_to_json_uses_camel_case_and_skips_none(self) -> None:
        widget = Widget(name='gadget', created=datetime(2026, 1, 2, 3, 4, 5))
        assert widget.to_json() == {'name': 'gadget', 'created': '2026-01-02T03:04:05'}

    def test_from_json_round_trip(self) -> None:
        widget = Widget.from_json({'id': '1', 'name': 'gadget', 'created': '2026-01-02T03:04:05'})
        assert widget.id == '1'
        assert widget.created == datetime(2026, 1, 2, 3, 4, 5)

    def test_from_json_rejects_unknown_field(self) -> None:
        with pytest.raises(KeyError, match='nope'):
            Widget.from_json({'nope': 'x'})


class TestService:
    def test_element_class_is_resolved_from_type_parameter(self, client) -> None:
        assert WidgetService(client)._element_class is Widget

    def test_unparameterized_service_is_rejected(self, client) -> None:
        class Bare(Service):
            pass

        with pytest.raises(TypeError, match='element type'):
            Bare(client)

    def test_method_names_are_derived_from_element(self, client) -> None:
        service = WidgetService(client)
        assert service._element_name == 'widget'
        assert service._id_name == 'widgetId'
        assert service._get_method_name == 'widgetInfo'
        assert service._find_method_name == 'widgetsFind'

    def test_get_returns_element(self, client, session) -> None:
        session.responses.append({'status': 'success', 'response': {'id': '1', 'name': 'gadget'}})
        widget = WidgetService(client).get('1')
        assert widget.name == 'gadget'
        assert session.calls[0]['body']['widgetId'] == '1'

    def test_find_stops_after_last_page(self, client, session) -> None:
        session.responses.append({
            'status': 'success',
            'response': {'data': [{'id': '1', 'name': 'a'}], 'totalPages': 2},
        })
        session.responses.append({
            'status': 'success',
            'response': {'data': [{'id': '2', 'name': 'b'}], 'totalPages': 2},
        })
        widgets = list(WidgetService(client))
        assert [w.id for w in widgets] == ['1', '2']
        assert [call['body']['page'] for call in session.calls] == [1, 2]

    def test_find_builds_filters_and_sorting(self, client, session) -> None:
        session.responses.append({'status': 'success', 'response': {'totalPages': 0}})
        list(WidgetService(client).find(limit=5, sort='~name', Name='gadget'))
        body = session.calls[0]['body']
        assert body['limit'] == 5
        assert body['sort'] == {'field': 'name', 'order': 'desc'}
        assert body['filter'] == {
            'subFilterConnective': 'AND',
            'subFilter': [{'field': 'Name', 'value': 'gadget'}],
        }

    def test_error_status_raises_with_messages(self, client, session) -> None:
        session.responses.append({
            'status': 'error',
            'errors': [{'text': 'Nope', 'code': 42}],
        })
        with pytest.raises(ServiceException, match=r'Nope \(42\)\.'):
            WidgetService(client).get('1')

    def test_missing_status_raises_service_exception(self, client, session) -> None:
        # Regression: a response without a status used to fail with an AttributeError.
        session.responses.append({'response': {}})
        with pytest.raises(ServiceException):
            WidgetService(client).get('1')

    def test_read_only_service_has_no_write_methods(self) -> None:
        assert not hasattr(ReadOnlyWidgetService, 'create')
        assert not hasattr(ReadOnlyWidgetService, 'update')
        assert not hasattr(ReadOnlyWidgetService, 'delete')


class TestCrudService:
    def test_create_serializes_element(self, client, session) -> None:
        # Regression: create() used to call the non-existent Element.to_dict().
        WidgetService(client).create(Widget(name='gadget'))
        call = session.calls[0]
        assert call['url'].endswith('/widgetCreate')
        assert call['body']['widget'] == {'name': 'gadget'}

    def test_update_serializes_element(self, client, session) -> None:
        # Regression: update() used to send the key instead of the element.
        WidgetService(client).update(Widget(id='1', name='gadget'))
        call = session.calls[0]
        assert call['url'].endswith('/widgetUpdate')
        assert call['body']['widget'] == {'id': '1', 'name': 'gadget'}

    def test_delete_sends_id(self, client, session) -> None:
        WidgetService(client).delete('1')
        call = session.calls[0]
        assert call['url'].endswith('/widgetDelete')
        assert call['body']['widgetId'] == '1'
