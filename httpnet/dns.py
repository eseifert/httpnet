from collections.abc import Iterable
from datetime import datetime
from enum import Enum

from httpnet._core import CrudService, Element, Service


class SoaValues(Element):
    refresh: int
    retry: int
    expire: int
    ttl: int
    negative_ttl: int


class TemplateReplacements(Element):
    ipv4_replacement: str | None
    ipv6_replacement: str | None
    mail_ipv4_replacement: str | None
    mail_ipv6_replacement: str | None


class TemplateValues(Element):
    template_id: str | None
    template_name: str | None
    tie_to_template: bool | None
    template_replacements: TemplateReplacements | None


class ZoneConfigType(Enum):
    NATIVE = 'NATIVE'
    MASTER = 'MASTER'
    SLAVE = 'SLAVE'

    def __repr__(self):
        return f'{self.__class__.__qualname__}.{self.name}'

    def __str__(self):
        return self.value


class ZoneConfig(Element):
    id: str | None
    account_id: str | None
    status: str | None
    name: str | None
    name_unicode: str | None
    master_ip: str | None
    type: ZoneConfigType | None
    email_address: str | None
    zone_transfer_whitelist: Iterable[str] | None
    last_change_date: datetime | None
    soa_values: SoaValues | None
    template_values: TemplateValues | None
    # undocumented
    add_date: datetime | None
    dns_sec_mode: str | None
    dns_server_group_id: str | None


class RecordType(Enum):
    A = 'A'
    AAAA = 'AAAA'
    ALIAS = 'ALIAS'
    CAA = 'CAA'
    CNAME = 'CNAME'
    DS = 'DS'
    MX = 'MX'
    NS = 'NS'
    NULLMX = 'NULLMX'
    PTR = 'PTR'
    SOA = 'SOA'
    SRV = 'SRV'
    TLSA = 'TLSA'
    TXT = 'TXT'

    def __repr__(self):
        return f'{self.__class__.__qualname__}.{self.name}'

    def __str__(self):
        return self.value


class DnsRecord(Element):
    id: str | None
    zone_id: str | None
    record_template_id: str | None
    name: str | None
    type: RecordType | None
    content: str | None
    ttl: int | None
    priority: int | None
    last_change_date: datetime | None
    # undocumented
    zone_config_id: str | None
    account_id: str | None
    add_date: datetime | None


class Zone(Element):
    zone_config: ZoneConfig | None
    records: Iterable[DnsRecord]


class ZoneConfigService(Service[ZoneConfig]):
    """Zone configs are created, updated and deleted through :class:`ZoneService`."""

    def get(self, key: str, /) -> ZoneConfig:
        return next(self.find(ZoneConfigId=key))


class RecordService(Service[DnsRecord]):
    """Records are created, updated and deleted through :class:`ZoneService`."""

    @property
    def _element_name(self) -> str:
        return 'record'


class ZoneService(Service[Zone]):
    def create(self, zone: Zone, nameserver_set_id: str | None = None,
               use_default_nameserver_set: bool | None = None) -> Zone:
        parameters = zone.to_json()
        if nameserver_set_id is not None:
            parameters['nameserverSetId'] = nameserver_set_id
        if use_default_nameserver_set is not None:
            parameters['useDefaultNameserverSet'] = use_default_nameserver_set
        response = self._call(
            method='zoneCreate',
            parameters=parameters
        )
        return Zone.from_json(response.get('response', {}))

    def recreate(self, zone: Zone, nameserver_set_id: str | None = None,
                 use_default_nameserver_set: bool | None = None) -> Zone:
        parameters = zone.to_json()
        if nameserver_set_id is not None:
            parameters['nameserverSetId'] = nameserver_set_id
        if use_default_nameserver_set is not None:
            parameters['useDefaultNameserverSet'] = use_default_nameserver_set
        response = self._call(
            method='zoneRecreate',
            parameters=parameters
        )
        return Zone.from_json(response.get('response', {}))

    def update(self, zone_config: ZoneConfig, records_to_add: Iterable[DnsRecord] = (),
               records_to_delete: Iterable[DnsRecord] = (),
               records_to_modify: Iterable[DnsRecord] = ()) -> Zone:
        response = self._call(
            method='zoneUpdate',
            parameters={
                'zoneConfig': zone_config.to_json(),
                'recordsToAdd': [r.to_json() for r in records_to_add],
                'recordsToModify': [r.to_json() for r in records_to_modify],
                'recordsToDelete': [r.to_json() for r in records_to_delete],
            }
        )
        return Zone.from_json(response.get('response', {}))

    def delete(self, zone_config_id: str) -> None:
        self._call(
            method='zoneDelete',
            parameters={'zoneConfigId': zone_config_id}
        )

    def change_content(self, record_type: RecordType, old_content: str, new_content: str,
                       include_templates: bool, include_sub_accounts: bool) -> None:
        self._call(
            method='changeContent',
            parameters={
                'recordType': record_type,
                'oldContent': old_content,
                'newContent': new_content,
                'includeTemplates': include_templates,
                'includeSubAccounts': include_sub_accounts,
            }
        )

    def untie_from_templates(self, zone_config_ids: Iterable[str] | None = None,
                             zone_config_names: Iterable[str] | None = None) -> None:
        parameters = {}
        if zone_config_ids:
            parameters['zoneConfigIds'] = list(zone_config_ids)
        elif zone_config_names:
            parameters['zoneConfigNames'] = list(zone_config_names)
        else:
            raise ValueError('Either zone config ids or zone config names are required')
        self._call(
            method='zonesUntieFromTemplates',
            parameters=parameters
        )

    def tie_to_templates(self, zone_config_ids: Iterable[str] | None = None,
                         zone_config_names: Iterable[str] | None = None) -> None:
        parameters = {}
        if zone_config_ids:
            parameters['zoneConfigIds'] = list(zone_config_ids)
        elif zone_config_names:
            parameters['zoneConfigNames'] = list(zone_config_names)
        else:
            raise ValueError('Either zone config ids or zone config names are required')
        self._call(
            method='zonesTieToTemplates',
            parameters=parameters
        )


class NameserverSet(Element):
    id: str | None
    account_id: str | None
    name: str
    default_nameserver_set: bool | None
    nameservers: Iterable[str]


class NameserverSetService(CrudService[NameserverSet]):
    def get_default(self) -> NameserverSet:
        response = self._call(
            method='nameserverSetGetDefault',
        )
        return NameserverSet.from_json(response.get('response', {}))


class Template(Element):
    id: str | None
    account_id: str | None
    name: str | None
    # undocumented
    email_address: str | None
    add_date: datetime | None
    last_change_date: datetime | None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id and not self.name:
            raise ValueError('Either id or name are required.')


class RecordTemplate(Element):
    id: str | None
    template_id: str | None
    name: str | None
    type: RecordType
    content: str
    ttl: int | None
    priority: int | None


class TemplateService(Service[Template]):
    def create(self, template: Template, record_templates: Iterable[RecordTemplate]) -> Template:
        response = self._call(
            method='templateCreate',
            parameters={
                'dnsTemplate': template.to_json(),
                'recordTemplates': [r.to_json() for r in record_templates]
            }
        )
        return Template.from_json(response.get('response', {}))

    def recreate(self, template: Template, record_templates: Iterable[RecordTemplate],
                 replacements: TemplateReplacements | None = None) -> Template:
        parameters = {
            'dnsTemplate': template.to_json(),
            'recordTemplates': [r.to_json() for r in record_templates]
        }
        if replacements:
            parameters['replacements'] = replacements.to_json()
        response = self._call(
            method='templateRecreate',
            parameters=parameters
        )
        return Template.from_json(response.get('response', {}))

    def update(self, template: Template,
               record_templates_to_add: Iterable[RecordTemplate],
               record_templates_to_delete: Iterable[RecordTemplate],
               replacements: TemplateReplacements | None = None) -> Template:
        parameters = {
            'dnsTemplate': template.to_json(),
            'recordTemplatesToAdd': [r.to_json() for r in record_templates_to_add],
            'recordTemplatesToDelete': [r.to_json() for r in record_templates_to_delete],
        }
        if replacements:
            parameters['replacements'] = replacements.to_json()
        response = self._call(
            method='templateUpdate',
            parameters=parameters
        )
        return Template.from_json(response.get('response', {}))

    def delete(self, template_id: str | None = None, template_name: str | None = None) -> None:
        parameters = {}
        if template_id:
            parameters['templateId'] = template_id
        elif template_name:
            parameters['templateName'] = template_name
        else:
            raise ValueError('Either id or name are required.')
        self._call(
            method='templateDelete',
            parameters=parameters
        )
