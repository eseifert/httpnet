"""
Tests based on the example payloads of the API documentation, cf. `apidata`.
"""

from datetime import datetime, timezone

import apidata
import pytest

from httpnet._core import ServiceException
from httpnet.client import HttpNetClient
from httpnet.dns import DnsRecord, NameserverSet, RecordType, Zone, ZoneConfig, ZoneConfigType
from httpnet.domain import (
    Contact,
    ContactType,
    DeletionType,
    Domain,
    DomainContactType,
    DomainStatus,
    Job,
)
from httpnet.email import DomainSettings


@pytest.fixture
def api(session) -> HttpNetClient:
    return HttpNetClient(auth_token='token')


def zone_from(request) -> Zone:
    """Builds a Zone from a documented zoneCreate request."""
    return Zone(
        zone_config=ZoneConfig(name=request['zoneConfig']['name'],
                               type=ZoneConfigType(request['zoneConfig']['type']),
                               email_address=request['zoneConfig']['emailAddress']),
        records=[
            DnsRecord(name=r['name'], type=RecordType(r['type']), content=r['content'],
                      ttl=r['ttl'], priority=r.get('priority'))
            for r in request['records']
        ],
    )


class TestDocumentedObjects:
    def test_contact(self) -> None:
        contact = Contact.from_json(apidata.CONTACT)
        assert contact.id == '15010100000010'
        assert contact.handle == 'JS15'
        assert contact.type is ContactType.PERSON
        assert contact.street == ['Happy ave. 42']
        assert contact.hidden is False
        assert contact.add_date == datetime(2015, 1, 1)

    def test_contact_round_trip_keeps_documented_field_names(self) -> None:
        json = Contact.from_json(apidata.CONTACT).to_json()
        # Fields that are empty in the documented example are dropped, since the
        # API treats missing and empty fields alike.
        assert set(json) <= set(apidata.CONTACT)
        assert json['emailAddress'] == 'john@example.com'
        assert json['usableBySubAccount'] is False
        assert json['type'] == 'person'

    def test_domain(self) -> None:
        domain = Domain.from_json(apidata.DOMAIN)
        assert domain.name == 'example.com'
        assert domain.status is DomainStatus.ACTIVE
        assert domain.transfer_lock_enabled is False
        assert [c.type for c in domain.contacts] == [
            DomainContactType.OWNER, DomainContactType.ADMIN,
            DomainContactType.TECH, DomainContactType.ZONE,
        ]
        assert [n.name for n in domain.nameservers] == ['ns.example.net', 'ns.example.com']
        assert domain.nameservers[1].ips == ['192.0.2.1', '2001:db8:3fe:1001:7777:772e:2:85']
        assert domain.create_date == datetime(2014, 1, 1)

    def test_domain_without_scheduled_deletion(self) -> None:
        domain = Domain.from_json(apidata.DOMAIN)
        # The documentation describes both fields as empty when the domain is
        # not scheduled for removal.
        assert domain.deletion_type is DeletionType.NONE
        assert domain.deletion_date is None

    def test_job(self) -> None:
        job = Job.from_json(apidata.JOB)
        assert job.id == '150223248499677'
        assert job.display_name == 'example.org'
        assert job.execution_date == datetime(2015, 2, 23, 17, 39, 23, tzinfo=timezone.utc)

    def test_zone_config(self) -> None:
        zone_config = ZoneConfig.from_json(apidata.ZONE_CONFIG)
        assert zone_config.name == 'example.com'
        assert zone_config.type is ZoneConfigType.NATIVE
        assert zone_config.soa_values.refresh == 86400
        assert zone_config.soa_values.negative_ttl == 3600
        assert zone_config.template_values is None
        assert zone_config.zone_transfer_whitelist == []

    def test_nameserver_set(self) -> None:
        nameserver_set = NameserverSet.from_json(apidata.NAMESERVER_SET)
        assert nameserver_set.name == 'Server 1'
        assert nameserver_set.default_nameserver_set is False
        assert nameserver_set.nameservers == ['ns1.example.com', 'ns2.example.com']

    def test_domain_settings(self) -> None:
        settings = DomainSettings.from_json(apidata.DOMAIN_SETTINGS)
        assert settings.domain_name == 'example.com'
        # -1 means unlimited according to the documentation.
        assert settings.storage_quota == -1
        assert settings.storage_quota_allocated == 1024
        assert settings.to_json()['domainName'] == 'example.com'


class TestDocumentedRequests:
    def test_zone_create_matches_documented_request(self, api, session) -> None:
        session.responses.append({'status': 'success', 'response': {'records': []}})
        request = apidata.ZONE_CREATE_REQUEST
        zone = zone_from(request)
        api.dns_zones.create(zone, nameserver_set_id=request['nameserverSetId'],
                             use_default_nameserver_set=request['useDefaultNameserverSet'])

        body = session.calls[0]['body']
        assert session.calls[0]['url'] == \
            'https://partner.http.net/api/dns/v1/json/zoneCreate'
        assert body['zoneConfig'] == request['zoneConfig']
        assert body['records'] == request['records']
        assert body['nameserverSetId'] == request['nameserverSetId']
        assert body['useDefaultNameserverSet'] is False

    def test_zone_update_always_sends_all_three_record_lists(self, api, session) -> None:
        # zoneUpdate documents recordsToAdd, recordsToModify and recordsToDelete
        # as required parameters.
        session.responses.append({'status': 'success', 'response': {'records': []}})
        api.dns_zones.update(ZoneConfig.from_json(apidata.ZONE_CONFIG))
        body = session.calls[0]['body']
        assert body['recordsToAdd'] == []
        assert body['recordsToModify'] == []
        assert body['recordsToDelete'] == []

    def test_domain_delete_calls_domain_delete(self, api, session) -> None:
        api.domains.delete('somedomain.de')
        assert session.calls[0]['url'].endswith('/domainDelete')
        assert session.calls[0]['body'] == {'authToken': 'token', 'domainName': 'somedomain.de'}

    def test_domain_delete_can_be_scheduled(self, api, session) -> None:
        api.domains.delete('somedomain.de', exec_date=datetime(2015, 1, 1))
        assert session.calls[0]['body']['execDate'] == '2015-01-01T00:00:00'

    def test_cancel_deletion_calls_domain_deletion_cancel(self, api, session) -> None:
        api.domains.cancel_deletion('example.de')
        assert session.calls[0]['url'].endswith('/domainDeletionCancel')
        assert session.calls[0]['body'] == {'authToken': 'token', 'domainName': 'example.de'}

    def test_nameserver_set_create(self, api, session) -> None:
        session.responses.append({'status': 'success', 'response': apidata.NAMESERVER_SET})
        created = api.nameserver_sets.create(NameserverSet(
            name='Server 1',
            default_nameserver_set=False,
            nameservers=['ns1.example.com', 'ns2.example.com'],
        ))
        body = session.calls[0]['body']
        assert session.calls[0]['url'].endswith('/dns/v1/json/nameserverSetCreate')
        assert body['nameserverSet']['name'] == 'Server 1'
        assert body['nameserverSet']['nameservers'] == ['ns1.example.com', 'ns2.example.com']
        # nameserverSetCreate responds with the created NameserverSet.
        assert isinstance(created, NameserverSet)
        assert created.name == 'Server 1'

    def test_domain_settings_update(self, api, session) -> None:
        session.responses.append({'status': 'success', 'response': apidata.DOMAIN_SETTINGS})
        updated = api.email_domain_settings.update(DomainSettings(
            domain_name='example.com', storage_quota=10240, mailbox_quota=10))
        body = session.calls[0]['body']
        assert session.calls[0]['url'].endswith('/email/v1/json/domainSettingsUpdate')
        assert body['domainSettings'] == {'domainName': 'example.com', 'storageQuota': 10240,
                                          'mailboxQuota': 10}
        assert isinstance(updated, DomainSettings)

    def test_mailbox_delete_requires_id_or_address(self, api, session) -> None:
        with pytest.raises(ValueError):
            api.mailboxes.delete()
        api.mailboxes.delete(mailbox_id='150101aaaaaaaaaa001',
                             exec_date=datetime(2016, 1, 15, 12, 0))
        body = session.calls[0]['body']
        assert body['mailboxId'] == '150101aaaaaaaaaa001'
        assert body['execDate'] == '2016-01-15T12:00:00'

    def test_find_uses_documented_listing_parameters(self, api, session) -> None:
        session.responses.append({'status': 'success', 'response': {
            'data': [apidata.CONTACT], 'limit': 10, 'page': 1,
            'totalEntries': 50, 'totalPages': 1, 'type': 'FindContactsResult',
        }})
        contacts = list(api.domain_contacts.find(limit=10, ContactId='15010100000010'))
        body = session.calls[0]['body']
        assert body['limit'] == 10
        assert body['page'] == 1
        assert body['filter'] == {
            'subFilterConnective': 'AND',
            'subFilter': [{'field': 'ContactId', 'value': '15010100000010'}],
        }
        assert [c.handle for c in contacts] == ['JS15']


class TestDocumentedCapabilities:
    """The services only offer the methods the API documents for them."""

    def test_contacts_cannot_be_deleted(self, api) -> None:
        assert not hasattr(api.domain_contacts, 'delete')

    def test_domain_settings_can_only_be_listed_and_updated(self, api) -> None:
        assert hasattr(api.email_domain_settings, 'update')
        assert not hasattr(api.email_domain_settings, 'create')
        assert not hasattr(api.email_domain_settings, 'delete')

    def test_zone_configs_and_records_are_managed_through_zones(self, api) -> None:
        for service in (api.dns_zone_configs, api.dns_records):
            assert not hasattr(service, 'create')
            assert not hasattr(service, 'update')
            assert not hasattr(service, 'delete')

    def test_jobs_are_read_only(self, api) -> None:
        assert not hasattr(api.domain_jobs, 'create')
        assert not hasattr(api.domain_jobs, 'update')
        assert not hasattr(api.domain_jobs, 'delete')

    def test_nameserver_sets_support_full_crud(self, api) -> None:
        for method in ('create', 'update', 'delete'):
            assert hasattr(api.nameserver_sets, method)


class TestDocumentedErrors:
    def test_error_response_reports_all_errors(self, api, session) -> None:
        session.responses.append(apidata.ERROR_RESPONSE)
        with pytest.raises(ServiceException) as exc_info:
            api.domain_contacts.get('15010100000010')
        message = str(exc_info.value)
        assert 'Handle type is invalid (32002).' in message
        assert 'Format of the phone number is invalid' in message

    def test_pending_status_is_not_an_error(self, api, session) -> None:
        session.responses.append({'status': 'pending', 'response': {}})
        api.domains.delete('example.com')
