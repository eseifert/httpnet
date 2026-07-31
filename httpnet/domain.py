from collections.abc import Iterable, Sequence
from datetime import datetime
from enum import Enum
from typing import Any

from httpnet._core import Element, Service


class ContactType(Enum):
    PERSON = 'person'
    ORGANIZATION = 'org'
    ROLE = 'role'

    def __repr__(self):
        return f'{self.__class__.__qualname__}.{self.name}'

    def __str__(self):
        return self.value


class Contact(Element):
    account_id: str | None
    id: str | None
    handle: str | None
    type: ContactType
    name: str
    organization: str | None
    street: Sequence[str]
    postal_code: str | None
    city: str
    state: str | None
    country: str
    email_address: str
    phone_number: str
    fax_number: str | None
    sip_uri: str | None
    hidden: bool | None
    usable_by_sub_account: bool | None
    add_date: datetime | None
    last_change_date: datetime | None
    # undocumented
    comments: str | None
    disclose: bool | None
    email_is_verified: bool | None
    ext_aero_identification_number: str | None
    ext_aero_password: str | None
    ext_ca_legal_type: str | None
    ext_cat_intended_usage: str | None
    ext_company_number: str | None
    ext_company_number_country: str | None
    ext_country_of_birth: str | None
    ext_date_of_birth: datetime | None
    ext_foreign_resident_identification_number: str | None
    ext_gender: str | None
    ext_identification_card_country: str | None
    ext_identification_card_issue_date: datetime | None
    ext_identification_card_issuing_authority: str | None
    ext_identification_card_number: str | None
    ext_identification_card_valid_until: datetime | None
    ext_language: str | None
    ext_nationality: str | None
    ext_place_of_birth: str | None
    ext_place_of_birth_postal_code: str | None
    ext_remarks: str | None
    ext_tax_id: str | None
    ext_tax_id_country: str | None
    ext_trade_mark_country: str | None
    ext_trade_mark_date_of_application: datetime | None
    ext_trade_mark_date_of_registration: datetime | None
    ext_trade_mark_name: str | None
    ext_trade_mark_register_number: str | None
    ext_trade_mark_registration_authority: str | None
    ext_trading_name: str | None
    ext_travel_unique_identification_number: str | None
    ext_uk_type: str | None
    ext_vat_id: str | None
    ext_vat_id_country: str | None
    ext_xxx_member_id: str | None
    placeholder_for_unreadable_supplier_contact: str | None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id and not self.handle:
            raise ValueError('Either "id" or "handle" are required')
        if self.type == ContactType.ORGANIZATION and not self.organization:
            raise ValueError(f'"The field organization" is required for when type is "{ContactType.ORGANIZATION}"')


class ContactService(Service[Contact]):
    def get(self, key: str, /) -> Contact:
        response = self._call(
            method=f'{self._element_name}sFind',
            parameters=dict(filter=dict(field='ContactId', value=key), limit=1)
        )
        response_body = response['response']
        if not response_body['data']:
            raise KeyError(key)
        return self._element_class.from_json(response_body['data'][0])


class DomainContactType(Enum):
    OWNER = 'owner'
    ADMIN = 'admin'
    TECH = 'tech'
    ZONE = 'zone'

    def __repr__(self):
        return f'{self.__class__.__qualname__}.{self.name}'

    def __str__(self):
        return self.value


class DomainContact(Element):
    type: DomainContactType
    contact: str


class NameServer(Element):
    name: str
    ips: Iterable[str] | None


class DomainStatus(Enum):
    ORDERED = 'ordered'
    ACTIVE = 'active'
    RESTORABLE = 'restorable'
    FAILED = 'failed'

    def __repr__(self):
        return f'{self.__class__.__qualname__}.{self.name}'

    def __str__(self):
        return self.value


class DeletionType(Enum):
    NONE = ''
    DELETE = 'delete'
    WITHDRAW = 'withdraw'

    def __repr__(self):
        return f'{self.__class__.__qualname__}.{self.name}'

    def __str__(self):
        return self.value


class Domain(Element):
    name: str
    transfer_lock_enabled: bool
    contacts: Iterable[DomainContact]
    nameservers: Iterable[NameServer]
    id: str | None
    account_id: str | None
    name_unicode: str | None
    status: DomainStatus | None
    auth_info: str | None
    create_date: datetime | None
    current_contract_period_end: datetime | None
    next_contract_period_start: datetime | None
    deletion_type: DeletionType | None
    deletion_date: datetime | None
    add_date: datetime | None
    last_change_date: datetime | None
    # undocumented
    bundle_id: str | None
    deletion_scheduled_for: datetime | None
    dns_sec_entries: Iterable[str] | None
    latest_deletion_date_without_renew: datetime | None
    paid_until: datetime | None
    product_code: str | None
    renew_on: datetime | None
    restorable_until: datetime | None
    restrictions: Iterable[str] | None
    transfer_locked_by_owner_change_until: datetime | None
    trustee_service_enabled: bool | None

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if not self.name:
            raise ValueError('The field "name" is required')
        if self.transfer_lock_enabled is None:
            raise ValueError('The field "transfer_lock_enabled" is required')
        if self.contacts is None:
            raise ValueError('The field "contacts" is required')
        if self.nameservers is None:
            raise ValueError('The field "nameservers" is required')


class DomainAvailability(Enum):
    ALREADY_REGISTERED = 'alreadyRegistered'
    REGISTERED = 'registered'
    NAME_CONTAINS_FORBIDDEN_CHARACTER = 'nameContainsForbiddenCharacter'
    AVAILABLE = 'available'
    SUFFIX_DOES_NOT_EXIST = 'suffixDoesNotExist'
    SUFFIX_CANNOT_BE_REGISTERED = 'suffixCannotBeRegistered'
    CAN_NOT_CHECK = 'canNotCheck'
    UNKNOWN = 'unknown'

    def __repr__(self):
        return f'{self.__class__.__qualname__}.{self.name}'

    def __str__(self):
        return self.value


class TransferMethod(Enum):
    OUT_OF_BAND = ''
    AUTH_INFO = 'authInfo'
    PUSH = 'push'
    # undocumented, reported for suffixes that are transferred by registrar tag
    PUSH_TAG = 'pushTag'

    def __repr__(self):
        return f'{self.__class__.__qualname__}.{self.name}'

    def __str__(self):
        return self.value


class DomainStatusResult(Element):
    domain_name: str | None
    domain_name_unicode: str | None
    domain_suffix: str | None
    status: DomainAvailability | None
    transfer_method: TransferMethod | None
    # undocumented
    early_access_start: datetime | None
    extension: str | None
    general_availability_start: datetime | None
    landrush_start: datetime | None
    launch_phase: str | None
    # Nested price structure that is only reported for premium domains. It is
    # passed through unchanged instead of being modelled.
    premium_prices: dict[str, Any] | None
    registrar_tag: str | None
    sunrise_start: datetime | None
    transfer_owner_handling: str | None


class FoaRecipientType(Enum):
    ADMIN = 'admin'
    OWNER = 'owner'
    BOTH = 'both'

    def __repr__(self):
        return f'{self.__class__.__qualname__}.{self.name}'

    def __str__(self):
        return self.value


class TransferData(Element):
    auth_info: str | None
    foa_recipient: FoaRecipientType | None


class DomainService(Service[Domain]):
    _id_name = 'domainName'

    def status(self, *names: str) -> Iterable[DomainStatusResult]:
        response = self._call(
            method='domainStatus',
            parameters={'domainNames': list(names)}
        )
        responses = response.get('responses', [])
        return [DomainStatusResult.from_json(dsr) for dsr in responses]

    def delete(self, name: str, exec_date: datetime | None = None) -> None:
        parameters = {
            'domainName': name,
        }
        if exec_date is not None:
            parameters['execDate'] = exec_date.isoformat()
        self._call(
            method='domainDelete',
            parameters=parameters
        )

    def withdraw(self, name: str, disconnect: bool, exec_date: datetime | None = None) -> None:
        parameters = {
            'domainName': name,
            'disconnect': disconnect,
        }
        if exec_date is not None:
            parameters['execDate'] = exec_date.isoformat()
        self._call(
            method='domainWithdraw',
            parameters=parameters
        )

    def cancel_deletion(self, name: str) -> None:
        self._call(
            method='domainDeletionCancel',
            parameters={'domainName': name}
        )

    def transfer(self, domain: Domain, transfer_data: TransferData) -> None:
        self._call(
            method='domainTransfer',
            parameters={'domain': domain.to_json(), 'transferData': transfer_data.to_json()}
        )

    def acknowledge_transfer(self, name: str) -> None:
        self._call(
            method='domainTransferOutAck',
            parameters={'domainName': name}
        )

    def restore(self, name: str) -> None:
        self._call(
            method='domainRestore',
            parameters={'domainName': name}
        )

    def request_authinfo2(self, name: str) -> None:
        self._call(
            method='domainCreateAuthInfo2',
            parameters={'domainName': name}
        )


class JobEvent(Element):
    action: str
    data: str
    execution_date: datetime


class JobTrigger(Element):
    account_id: str
    account_name: str
    api_key_id: str
    api_key_name: str
    user_id: str
    user_name: str


class Job(Element):
    id: str
    account_id: str
    display_name: str
    domain_name_ace: str
    domain_name_unicode: str
    handle: str
    type: str
    state: str
    errors: str
    warnings: str
    client_transaction_id: str
    server_transaction_id: str
    execution_date: datetime
    add_date: datetime
    last_change_date: datetime
    # undocumented
    action: str
    comments: str
    events: Iterable[JobEvent]
    object_id: str
    object_type: str
    # The API reports these alongside ``state``.
    sub_state: str
    status: str
    sub_status: str
    triggered_by: JobTrigger


class JobService(Service[Job]):
    """Jobs are created by the API itself and can only be queried."""
