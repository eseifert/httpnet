"""
Regression tests for the issues reported at
https://github.com/eseifert/httpnet/issues
"""

import apidata
import pytest

from httpnet.client import HttpNetClient
from httpnet.dns import SoaValues, Zone, ZoneConfig, ZoneConfigType


@pytest.fixture
def api(session) -> HttpNetClient:
    return HttpNetClient(auth_token='token')


class TestIssue1:
    """
    https://github.com/eseifert/httpnet/issues/1

    Retrieving zones failed with ``TypeError: issubclass() arg 1 must be a
    class``, because optional annotations like ``SoaValues | None`` were passed
    to ``issubclass()``.
    """

    def test_retrieving_a_zone_config(self, api, session) -> None:
        session.responses.append({'status': 'success', 'response': {
            'data': [apidata.ZONE_CONFIG], 'totalEntries': 1, 'totalPages': 1,
        }})
        zone_config = api.dns_zone_configs.get('15010100000010')
        assert zone_config.name == 'example.com'
        assert isinstance(zone_config.soa_values, SoaValues)

    def test_listing_zones(self, api, session) -> None:
        session.responses.append({'status': 'success', 'response': {
            'data': [{
                'zoneConfig': apidata.ZONE_CONFIG,
                'records': [{'id': '1', 'name': 'example.com', 'type': 'A',
                             'content': '172.27.171.106', 'ttl': 86000}],
            }],
            'totalEntries': 1,
            'totalPages': 1,
        }})
        zones = list(api.dns_zones.find())
        assert len(zones) == 1
        assert isinstance(zones[0], Zone)
        assert isinstance(zones[0].zone_config, ZoneConfig)
        assert zones[0].zone_config.type is ZoneConfigType.NATIVE
        assert zones[0].records[0].content == '172.27.171.106'

    def test_optional_element_field_that_is_absent(self) -> None:
        zone_config = ZoneConfig.from_json({'id': '1', 'name': 'example.com',
                                            'type': 'NATIVE', 'soaValues': None})
        assert zone_config.soa_values is None

    @pytest.mark.parametrize('field, attribute, value', [
        ('soaValues', 'soa_values', {'refresh': 86400, 'retry': 7200, 'expire': 3600000,
                                     'ttl': 172800, 'negativeTtl': 3600}),
        ('templateValues', 'template_values', {'templateId': '1', 'tieToTemplate': True}),
        ('zoneTransferWhitelist', 'zone_transfer_whitelist', ['192.0.2.1']),
        ('lastChangeDate', 'last_change_date', '2015-09-02T10:14:02Z'),
        ('type', 'type', 'NATIVE'),
    ])
    def test_every_kind_of_optional_annotation(self, field, attribute, value) -> None:
        # Optional elements, optional sequences, optional datetimes and optional
        # enums all used to end up in issubclass().
        zone_config = ZoneConfig.from_json({'name': 'example.com', field: value})
        assert getattr(zone_config, attribute) is not None


class TestIssue3:
    """
    https://github.com/eseifert/httpnet/issues/3

    ``len(api.domains)``, as shown in the README, raised "TypeError: object of
    type 'DomainService' has no len()".
    """

    def test_len_of_a_service(self, api, session) -> None:
        session.responses.append({'status': 'success', 'response': {
            'data': [apidata.DOMAIN], 'limit': 1, 'page': 1,
            'totalEntries': 123, 'totalPages': 123,
        }})
        assert len(api.domains) == 123

    def test_len_asks_for_a_single_element_only(self, api, session) -> None:
        session.responses.append({'status': 'success', 'response': {'totalEntries': 123}})
        len(api.dns_zones)
        body = session.calls[0]['body']
        assert session.calls[0]['url'].endswith('/zonesFind')
        assert body['limit'] == 1
        assert body['page'] == 1
        assert 'filter' not in body

    def test_count_can_be_filtered(self, api, session) -> None:
        session.responses.append({'status': 'success', 'response': {'totalEntries': 42}})
        count = api.domain_contacts.count(ContactType='person')
        assert count == 42
        assert session.calls[0]['body']['filter'] == {
            'subFilterConnective': 'AND',
            'subFilter': [{'field': 'ContactType', 'value': 'person'}],
        }

    def test_count_without_results(self, api, session) -> None:
        session.responses.append({'status': 'success', 'response': {'totalEntries': 0}})
        assert api.domains.count(Name='nonexistent.example') == 0

    def test_len_requires_one_request_per_call(self, api, session) -> None:
        session.responses.append({'status': 'success', 'response': {'totalEntries': 7}})
        session.responses.append({'status': 'success', 'response': {'totalEntries': 7}})
        assert len(api.domains) == len(api.domains)
        assert len(session.calls) == 2

    def test_iterating_a_service_still_works(self, api, session) -> None:
        # A sized iterable makes list() ask for the length first, so the count
        # request precedes the listing requests.
        session.responses.append({'status': 'success', 'response': {'totalEntries': 1}})
        session.responses.append({'status': 'success', 'response': {
            'data': [apidata.DOMAIN], 'totalEntries': 1, 'totalPages': 1,
        }})
        domains = list(api.domains)
        assert [d.name for d in domains] == ['example.com']
        assert [call['body'].get('limit') for call in session.calls] == [1, None]

    def test_find_does_not_trigger_a_count(self, api, session) -> None:
        session.responses.append({'status': 'success', 'response': {
            'data': [apidata.DOMAIN], 'totalEntries': 1, 'totalPages': 1,
        }})
        assert len(list(api.domains.find())) == 1
        assert len(session.calls) == 1
