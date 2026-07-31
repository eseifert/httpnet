from datetime import datetime

import pytest

from httpnet.client import HttpNetClient
from httpnet.dns import DnsRecord, RecordType, Zone, ZoneConfig, ZoneConfigType
from httpnet.domain import Contact, ContactType


class TestRoundTrip:
    def test_enum_field(self) -> None:
        record = DnsRecord.from_json({'id': '1', 'name': 'example.com', 'type': 'A',
                                      'content': '127.0.0.1'})
        assert record.type is RecordType.A
        assert record.to_json()['type'] == 'A'

    def test_datetime_field(self) -> None:
        record = DnsRecord.from_json({'name': 'example.com', 'type': 'A', 'content': '::1',
                                      'lastChangeDate': '2026-01-02T03:04:05'})
        assert record.last_change_date == datetime(2026, 1, 2, 3, 4, 5)
        assert record.to_json()['lastChangeDate'] == '2026-01-02T03:04:05'

    def test_optional_field_is_none_when_null(self) -> None:
        record = DnsRecord.from_json({'name': 'example.com', 'type': 'A', 'content': '::1',
                                      'ttl': None})
        assert record.ttl is None
        assert 'ttl' not in record.to_json()

    def test_optional_field_keeps_its_type(self) -> None:
        record = DnsRecord.from_json({'name': 'example.com', 'type': 'A', 'content': '::1',
                                      'ttl': 300})
        assert record.ttl == 300

    def test_nested_element_and_sequence(self) -> None:
        zone = Zone.from_json({
            'zoneConfig': {'id': 'z1', 'name': 'example.com', 'type': 'NATIVE',
                           'emailAddress': 'hostmaster@example.com', 'soaValues': None},
            'records': [
                {'name': 'example.com', 'type': 'A', 'content': '127.0.0.1'},
                {'name': 'www.example.com', 'type': 'CNAME', 'content': 'example.com'},
            ],
        })
        assert isinstance(zone.zone_config, ZoneConfig)
        assert zone.zone_config.type is ZoneConfigType.NATIVE
        assert [r.type for r in zone.records] == [RecordType.A, RecordType.CNAME]

        json = zone.to_json()
        assert json['zoneConfig']['name'] == 'example.com'
        assert json['records'][1] == {'name': 'www.example.com', 'type': 'CNAME',
                                      'content': 'example.com'}

    def test_sequence_of_strings(self) -> None:
        contact = Contact.from_json({'id': '1', 'type': 'person', 'name': 'Jane Doe',
                                     'street': ['Main St 1', 'Apt 2'], 'city': 'Berlin',
                                     'country': 'DE', 'emailAddress': 'jane@example.com',
                                     'phoneNumber': '+49 30 123456'})
        assert contact.street == ['Main St 1', 'Apt 2']
        assert contact.type is ContactType.PERSON
        assert contact.to_json()['street'] == ['Main St 1', 'Apt 2']

    def test_camel_case_mapping(self) -> None:
        record = DnsRecord(name='example.com', type=RecordType.A, content='::1',
                           zone_config_id='z1')
        assert record.to_json()['zoneConfigId'] == 'z1'


class TestServices:
    def test_zone_create_sends_serialized_zone(self, session) -> None:
        api = HttpNetClient(auth_token='token')
        session.responses.append({'status': 'success', 'response': {'records': []}})
        zone = Zone(zone_config=ZoneConfig(name='example.com', type=ZoneConfigType.NATIVE),
                    records=[DnsRecord(name='example.com', type=RecordType.A, content='::1')])
        api.dns_zones.create(zone, use_default_nameserver_set=True)

        body = session.calls[0]['body']
        assert session.calls[0]['url'].endswith('/dns/v1/json/zoneCreate')
        assert body['zoneConfig']['name'] == 'example.com'
        assert body['records'][0]['content'] == '::1'
        assert body['useDefaultNameserverSet'] is True

    def test_domain_service_uses_custom_id_name(self, session) -> None:
        api = HttpNetClient(auth_token='token')
        session.responses.append({'status': 'success', 'response': {
            'name': 'example.com',
            'transferLockEnabled': True,
            'contacts': [{'contact': '1', 'type': 'owner'}],
            'nameservers': [{'name': 'ns1.example.com'}],
        }})
        api.domains.get('example.com')
        assert session.calls[0]['body']['domainName'] == 'example.com'

    def test_record_service_uses_custom_element_name(self, session) -> None:
        api = HttpNetClient(auth_token='token')
        session.responses.append({'status': 'success', 'response': {'totalPages': 0}})
        list(api.dns_records)
        assert session.calls[0]['url'].endswith('/dns/v1/json/recordsFind')

    def test_services_without_write_support(self) -> None:
        api = HttpNetClient(auth_token='token')
        for service in (api.dns_zone_configs, api.dns_records, api.domain_jobs):
            assert not hasattr(service, 'create')
            assert not hasattr(service, 'delete')

    @pytest.mark.parametrize('name', ['domains', 'domain_contacts', 'domain_jobs',
                                      'dns_zone_configs', 'dns_records', 'dns_zones',
                                      'nameserver_sets', 'dns_templates', 'mailboxes',
                                      'email_organizations', 'email_domain_settings'])
    def test_every_service_resolves_its_element_class(self, name: str) -> None:
        api = HttpNetClient(auth_token='token')
        service = getattr(api, name)
        assert service._element_class is not None
        assert service._find_method_name.endswith('Find')

    @pytest.mark.parametrize('name, filter_name', [
        ('domain_contacts', 'ContactId'),
        ('domain_jobs', 'JobId'),
        ('dns_zone_configs', 'ZoneConfigId'),
        ('dns_records', 'RecordId'),
        # A zone is identified by its zone config, ``ZoneId`` is rejected.
        ('dns_zones', 'ZoneConfigId'),
        ('nameserver_sets', 'NameserverSetId'),
        ('dns_templates', 'TemplateId'),
        ('mailboxes', 'MailboxId'),
        # Domain settings carry no ID of their own.
        ('email_domain_settings', 'DomainName'),
    ])
    def test_get_filters_on_the_field_the_api_accepts(self, name: str, filter_name: str,
                                                      session) -> None:
        api = HttpNetClient(auth_token='token')
        session.responses.append({
            'status': 'success', 'response': {'data': [], 'totalPages': 0},
        })
        with pytest.raises(KeyError):
            getattr(api, name).get('id-1')
        assert session.calls[0]['body']['filter']['subFilter'] == [
            {'field': filter_name, 'value': 'id-1'}
        ]

    def test_domains_are_retrieved_through_domain_info(self, session) -> None:
        api = HttpNetClient(auth_token='token')
        session.responses.append({
            'status': 'success',
            'response': {'name': 'example.com', 'transferLockEnabled': True,
                         'contacts': [], 'nameservers': []},
        })
        domain = api.domains.get('example.com')
        assert domain.name == 'example.com'
        assert session.calls[0]['url'].endswith('/domain/v1/json/domainInfo')
        assert session.calls[0]['body']['domainName'] == 'example.com'
