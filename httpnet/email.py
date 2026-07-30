from collections.abc import Iterable
from datetime import datetime
from enum import Enum

from httpnet._core import Element, Service


class SpamFilter(Element):
    banned_files_checks: bool | None
    delete_spam: bool | None
    header_checks: bool | None
    malware_checks: bool | None
    modify_subject_on_spam: bool | None
    spam_checks: bool | None
    spam_level: str | None
    use_greylisting: bool | None


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
    id: str | None
    account_id: str | None
    email_address: str
    email_address_unicode: str | None
    domain_name: str | None
    domain_name_unicode: str | None
    status: str | None
    spam_filter: SpamFilter | None
    type: MailboxType | None
    product_code: str | None
    forwarder_targets: Iterable[str] | None  # only IMAP and Forwarder
    smtp_forwarder_target: str | None  # only IMAP
    is_admin: bool | None  # only IMAP
    first_name: str | None  # only Exchange
    last_name: str | None  # only Exchange
    exchange_guid: str | None  # only Exchange
    organization_id: str | None  # only Exchange
    forwarder_type: ForwarderType | None  # only Forwarder
    password: str | None
    storage_quota: int
    storage_quota_used: int | None
    paid_until: datetime | None
    renew_on: datetime | None
    deletion_scheduled_for: datetime | None
    restorable_until: datetime | None
    add_date: datetime | None
    last_change_date: datetime | None

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

    def delete(self, mailbox_id: str | None = None, email_address: str | None = None,
               exec_date: datetime | None = None) -> Mailbox:
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

    def cancel_deletion(self, mailbox_id: str | None = None, email_address: str | None = None) -> Mailbox:
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

    def restore(self, mailbox_id: str | None = None, email_address: str | None = None) -> Mailbox:
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

    def purge_restorable(self, mailbox_id: str | None = None, email_address: str | None = None) -> None:
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
    id: str | None
    account_id: str | None
    comment: str | None
    name: str
    status: str | None
    member_domains: Iterable[str] | None
    add_date: datetime | None
    last_change_date: datetime | None


class OrganizationService(Service[Organization]):
    pass


class DomainSettings(Element):
    domainName: str
    domainNameUnicode: str | None
    storageQuota: int | None
    storageQuotaAllocated: int | None
    mailboxQuota: int | None
    exchangeMailboxQuota: int | None
    exchangeStorageQuotaAllocated: int | None
    exchangeStorageQuota: int | None
    addDate: datetime | None
    lastChangeDate: datetime | None


class DomainSettingsService(Service[DomainSettings]):
    pass
