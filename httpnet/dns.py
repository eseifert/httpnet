from datetime import datetime
from enum import Enum
from typing import Iterable, Optional
from httpnet._core import Element, Service


class SoaValues(Element):
    refresh: int
    retry: int
    expire: int
    ttl: int
    negative_ttl: int


class TemplateReplacements(Element):
    ipv4_replacement: Optional[str]
    ipv6_replacement: Optional[str]
    mail_ipv4_replacement: Optional[str]
    mail_ipv6_replacement: Optional[str]


class TemplateValues(Element):
    template_id: Optional[str]
    template_name: Optional[str]
    tie_to_template: Optional[bool]
    template_replacements: Optional[TemplateReplacements]


class ZoneConfigType(Enum):
    NATIVE = 'NATIVE'
    MASTER = 'MASTER'
    SLAVE = 'SLAVE'

    def __repr__(self):
        return f'{self.__class__.__qualname__}.{self.name}'

    def __str__(self):
        return self.value


class ZoneConfig(Element):
    id: Optional[str]
    account_id: Optional[str]
    status: Optional[str]
    name: Optional[str]
    name_unicode: Optional[str]
    master_ip: Optional[str]
    type: Optional[ZoneConfigType]
    email_address: Optional[str]
    zone_transfer_whitelist: Optional[Iterable[str]]
    last_change_date: Optional[datetime]
    soa_values: Optional[SoaValues]
    template_values: Optional[TemplateValues]
    # undocumented
    add_date: Optional[datetime]
    dns_sec_mode: Optional[str]
    dns_server_group_id: Optional[str]


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
    id: Optional[str]
    zone_id: Optional[str]
    record_template_id: Optional[str]
    name: Optional[str]
    type: Optional[RecordType]
    content: Optional[str]
    ttl: Optional[int]
    priority: Optional[int]
    last_change_date: Optional[datetime]
    # undocumented
    zone_config_id: Optional[str]
    account_id: Optional[str]
    add_date: Optional[datetime]


class Zone(Element):
    zone_config: Optional[ZoneConfig]
    records: Iterable[DnsRecord]


class ZoneConfigService(Service[ZoneConfig]):
    def get(self, key: str) -> ZoneConfig:
        return next(self.find(ZoneConfigId=key))

    def create(self, element: ZoneConfig) -> None:
        raise NotImplementedError()

    def update(self, key: str, item: ZoneConfig) -> None:
        raise NotImplementedError()

    def delete(self, key: str) -> None:
        raise NotImplementedError()


class RecordService(Service[DnsRecord]):
    @property
    def _element_name(self) -> str:
        return 'record'

    def create(self, element: ZoneConfig) -> None:
        raise NotImplementedError()

    def update(self, key: str, item: ZoneConfig) -> None:
        raise NotImplementedError()

    def delete(self, key: str) -> None:
        raise NotImplementedError()


class ZoneService(Service[Zone]):
    def create(self, zone: Zone, nameserver_set_id: Optional[str] = None,
               use_default_nameserver_set: Optional[bool] = None) -> Zone:
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

    def recreate(self, zone: Zone, nameserver_set_id: Optional[str] = None,
                 use_default_nameserver_set: Optional[bool] = None) -> Zone:
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

    def update(self, zone_config: ZoneConfig, records_to_add: Iterable[DnsRecord],
               records_to_delete: Iterable[DnsRecord]) -> Zone:
        response = self._call(
            method='zoneUpdate',
            parameters={
                'zoneConfig': zone_config.to_json(),
                'recordsToAdd': [r.to_json() for r in records_to_add],
                'recordsToDelete': [r.to_json() for r in records_to_delete],
            }
        )
        return Zone.from_json(response.get('response', {}))

    def delete(self, zone_config_id: str) -> None:
        self._call(
            method='zoneDelete',
            parameters={'zoneConfigId': zone_config_id}
        )

    def purge_restorable(self, zone_config_id: str) -> None:
        self._call(
            method='zonePurgeRestorable',
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

    def untie_from_templates(self, zone_config_ids: Optional[Iterable[str]] = None,
                             zone_config_names: Optional[Iterable[str]] = None) -> None:
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

    def tie_to_templates(self, zone_config_ids: Optional[Iterable[str]] = None,
                         zone_config_names: Optional[Iterable[str]] = None) -> None:
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
    id: Optional[str]
    account_id: Optional[str]
    name: str
    default_nameserver_set: Optional[bool]
    nameservers: Iterable[str]


class NameserverSetService(Service[NameserverSet]):
    def get_default(self) -> NameserverSet:
        response = self._call(
            method='nameserverSetGetDefault',
        )
        return NameserverSet.from_json(response.get('response', {}))


class Template(Element):
    id: Optional[str]
    account_id: Optional[str]
    name: Optional[str]
    # undocumented
    email_address: Optional[str]
    add_date: Optional[datetime]
    last_change_date: Optional[datetime]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id and not self.name:
            raise ValueError('Either id or name are required.')


class RecordTemplate(Element):
    id: Optional[str]
    template_id: Optional[str]
    name: Optional[str]
    type: RecordType
    content: str
    ttl: Optional[int]
    priority: Optional[int]


class TemplateService(Service[Template]):
    def create(self, template: Template, record_templates: Iterable[RecordTemplate]) -> Template:
        response = self._call(
            method='templateCreate',
            parameters={
                'dnsTemplate': template,
                'recordTemplates': list(record_templates)
            }
        )
        return Template.from_json(response.get('response', {}))

    def recreate(self, template: Template, record_templates: Iterable[RecordTemplate],
                 replacements: Optional[TemplateReplacements] = None) -> Template:
        parameters = {
            'dnsTemplate': template,
            'recordTemplates': list(record_templates)
        }
        if replacements:
            parameters['replacements'] = replacements
        response = self._call(
            method='templateRecreate',
            parameters=parameters
        )
        return Template.from_json(response.get('response', {}))

    def update(self, template: Template,
               record_templates_to_add: Iterable[RecordTemplate],
               record_templates_to_delete: Iterable[RecordTemplate],
               replacements: Optional[TemplateReplacements] = None) -> Zone:
        parameters = {
            'dnsTemplate': template.to_json(),
            'recordTemplatesToAdd': [r.to_json() for r in record_templates_to_add],
            'recordTemplatesToDelete': [r.to_json() for r in record_templates_to_delete],
        }
        if replacements:
            parameters['replacements'] = replacements
        response = self._call(
            method='templateUpdate',
            parameters=parameters
        )
        return Zone.from_json(response.get('response', {}))

    def delete(self, template_id: Optional[str] = None, template_name: Optional[str] = None) -> None:
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
