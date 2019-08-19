from datetime import datetime
from enum import Enum
from typing import Iterable, Optional
from httpnet._core import Element, Service


class SpamFilter(Element):
    banned_files_checks: Optional[bool]
    delete_spam: Optional[bool]
    header_checks: Optional[bool]
    malware_checks: Optional[bool]
    modify_subject_on_spam: Optional[bool]
    spam_checks: Optional[bool]
    spam_level: Optional[str]
    use_greylisting: Optional[bool]


class MailboxType(Enum):
    IMAP = 'ImapMailbox'
    EXCHANGE = 'ExchangeMailbox'
    FORWARDER = 'Forwarder'

    def __repr__(self):
        return f'{self.__class__.__qualname__}.{self.name}'

    def __str__(self):
        return self.value


class ForwarderType(Enum):
    INTERNAL = 'internalForwarder'
    EXTERNAL = 'externalForwarder'

    def __repr__(self):
        return f'{self.__class__.__qualname__}.{self.name}'

    def __str__(self):
        return self.value


class Mailbox(Element):
    id: Optional[str]
    account_id: Optional[str]
    email_address: str
    email_address_unicode: Optional[str]
    domain_name: Optional[str]
    domain_name_unicode: Optional[str]
    status: Optional[str]
    spam_filter: Optional[SpamFilter]
    type: Optional[MailboxType]
    product_code: Optional[str]
    forwarder_targets: Optional[Iterable[str]]  # only IMAP and Forwarder
    smtp_forwarder_target: Optional[str]  # only IMAP
    is_admin: Optional[bool]  # only IMAP
    first_name: Optional[str]  # only Exchange
    last_name: Optional[str]  # only Exchange
    exchange_guid: Optional[str]  # only Exchange
    organization_id: Optional[str]  # only Exchange
    forwarder_type: Optional[ForwarderType]  # only Forwarder
    password: Optional[str]
    storage_quota: int
    storage_quota_used: Optional[int]
    paid_until: Optional[datetime]
    renew_on: Optional[datetime]
    deletion_scheduled_for: Optional[datetime]
    restorable_until: Optional[datetime]
    add_date: Optional[datetime]
    last_change_date: Optional[datetime]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.type == MailboxType.IMAP:
            if self.forwarder_targets is None:
                raise ValueError('List of forwarder targets is required for IMAP mailboxes.')
        elif self.type == MailboxType.EXCHANGE:
            if self.first_name is None:
                raise ValueError('First name is required for Exchange mailboxes.')
            if self.last_name is None:
                raise ValueError('Last name is required for Exchange mailboxes.')
        elif self.type == MailboxType.FORWARDER:
            if self.forwarder_targets is None:
                raise ValueError('List of forwarder targets is required for Forwarder mailboxes.')


class MailboxService(Service[Mailbox]):
    _find_method_name = 'mailboxesFind'

    def delete(self, mailbox_id: Optional[str] = None, email_address: Optional[str] = None,
               exec_date: Optional[datetime] = None) -> Mailbox:
        parameters = {}
        if mailbox_id:
            parameters['mailboxId'] = mailbox_id
        elif email_address:
            parameters['emailAddress'] = email_address
        else:
            raise ValueError('Either mailbox id or email address are required.')
        if exec_date is not None:
            parameters['execDate'] = exec_date.isoformat()
        response = self._call(
            method='mailboxDelete',
            parameters=parameters
        )
        return Mailbox.from_json(response.get('response', {}))

    def cancel_deletion(self, mailbox_id: Optional[str] = None, email_address: Optional[str] = None) -> Mailbox:
        parameters = {}
        if mailbox_id:
            parameters['mailboxId'] = mailbox_id
        elif email_address:
            parameters['emailAddress'] = email_address
        else:
            raise ValueError('Either mailbox id or email address are required.')
        response = self._call(
            method='mailboxDeletionCancel',
            parameters=parameters
        )
        return Mailbox.from_json(response.get('response', {}))

    def restore(self, mailbox_id: Optional[str] = None, email_address: Optional[str] = None) -> Mailbox:
        parameters = {}
        if mailbox_id:
            parameters['mailboxId'] = mailbox_id
        elif email_address:
            parameters['emailAddress'] = email_address
        else:
            raise ValueError('Either mailbox id or email address are required.')
        response = self._call(
            method='mailboxRestore',
            parameters=parameters
        )
        return Mailbox.from_json(response.get('response', {}))

    def purge_restorable(self, mailbox_id: Optional[str] = None, email_address: Optional[str] = None) -> None:
        parameters = {}
        if mailbox_id:
            parameters['mailboxId'] = mailbox_id
        elif email_address:
            parameters['emailAddress'] = email_address
        else:
            raise ValueError('Either mailbox id or email address are required.')
        self._call(
            method='mailboxPurgeRestorable',
            parameters=parameters
        )


class Organization(Element):
    id: Optional[str]
    account_id: Optional[str]
    comment: Optional[str]
    name: str
    status: Optional[str]
    member_domains: Optional[Iterable[str]]
    add_date: Optional[datetime]
    last_change_date: Optional[datetime]


class OrganizationService(Service[Organization]):
    pass


class DomainSettings(Element):
    domainName: str
    domainNameUnicode: Optional[str]
    storageQuota: Optional[int]
    storageQuotaAllocated: Optional[int]
    mailboxQuota: Optional[int]
    exchangeMailboxQuota: Optional[int]
    exchangeStorageQuotaAllocated: Optional[int]
    exchangeStorageQuota: Optional[int]
    addDate: Optional[datetime]
    lastChangeDate: Optional[datetime]


class DomainSettingsService(Service[DomainSettings]):
    pass
