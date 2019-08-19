from datetime import datetime
from enum import Enum
from typing import Iterable, Optional, Sequence
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
    account_id: Optional[str]
    id: Optional[str]
    handle: Optional[str]
    type: ContactType
    name: str
    organization: Optional[str]
    street: Sequence[str]
    postal_code: Optional[str]
    city: str
    state: Optional[str]
    country: str
    email_address: str
    phone_number: str
    fax_number: Optional[str]
    sip_uri: Optional[str]
    hidden: Optional[bool]
    usable_by_sub_account: Optional[bool]
    add_date: Optional[datetime]
    last_change_date: Optional[datetime]
    # undocumented
    ext_aero_identification_number: Optional[str]
    ext_aero_password: Optional[str]
    ext_ca_legal_type: Optional[str]
    ext_cat_intended_usage: Optional[str]
    ext_company_number: Optional[str]
    ext_company_number_country: Optional[str]
    ext_country_of_birth: Optional[str]
    ext_date_of_birth: Optional[datetime]
    ext_foreign_resident_identification_number: Optional[str]
    ext_gender: Optional[str]
    ext_identification_card_country: Optional[str]
    ext_identification_card_issue_date: Optional[datetime]
    ext_identification_card_issuing_authority: Optional[str]
    ext_identification_card_number: Optional[str]
    ext_identification_card_valid_until: Optional[datetime]
    ext_language: Optional[str]
    ext_place_of_birth: Optional[str]
    ext_place_of_birth_postal_code: Optional[str]
    ext_remarks: Optional[str]
    ext_tax_id: Optional[str]
    ext_tax_id_country: Optional[str]
    ext_trade_mark_country: Optional[str]
    ext_trade_mark_date_of_application: Optional[datetime]
    ext_trade_mark_date_of_registration: Optional[datetime]
    ext_trade_mark_name: Optional[str]
    ext_trade_mark_register_number: Optional[str]
    ext_trade_mark_registration_authority: Optional[str]
    ext_trading_name: Optional[str]
    ext_travel_unique_identification_number: Optional[str]
    ext_uk_type: Optional[str]
    ext_vat_id: Optional[str]
    ext_vat_id_country: Optional[str]
    ext_xxx_member_id: Optional[str]
    placeholder_for_unreadable_supplier_contact: Optional[str]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id and not self.handle:
            raise ValueError('Either "id" or "handle" are required')
        if self.type == ContactType.ORGANIZATION and not self.organization:
            raise ValueError(f'"The field organization" is required for when type is "{ContactType.ORGANIZATION}"')


class ContactService(Service[Contact]):
    def get(self, key: str) -> Contact:
        response = self._call(
            method=f'{self._element_name}sFind',
            parameters=dict(filter=dict(field='ContactId', value=key), limit=1)
        )
        response_body = response['response']
        if not response_body['data']:
            raise KeyError()
        return self._element_class.from_json(response_body['data'][0])

    def delete(self, key: str) -> Contact:
        raise NotImplementedError()


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
    ips: Optional[Iterable[str]]


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
    id: Optional[str]
    account_id: Optional[str]
    name_unicode: Optional[str]
    status: Optional[DomainStatus]
    auth_info: Optional[str]
    create_date: Optional[datetime]
    current_contract_period_end: Optional[datetime]
    next_contract_period_start: Optional[datetime]
    deletion_type: Optional[DeletionType]
    deletion_date: Optional[datetime]
    add_date: Optional[datetime]
    last_change_date: Optional[datetime]
    # undocumented
    bundle_id: Optional[str]
    deletion_scheduled_for: Optional[datetime]
    dns_sec_entries: Optional[Iterable[str]]
    latest_deletion_date_without_renew: Optional[datetime]
    paid_until: Optional[datetime]
    product_code: Optional[str]
    renew_on: Optional[datetime]
    restorable_until: Optional[datetime]
    restrictions: Optional[Iterable[str]]
    transfer_locked_by_owner_change_until: Optional[datetime]
    trustee_service_enabled: Optional[bool]

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

    def __repr__(self):
        return f'{self.__class__.__qualname__}.{self.name}'

    def __str__(self):
        return self.value


class DomainStatusResult(Element):
    domain_name: Optional[str]
    domain_name_unicode: Optional[str]
    domain_suffix: Optional[str]
    status: Optional[DomainAvailability]
    transfer_method: Optional[TransferMethod]


class FoaRecipientType(Enum):
    ADMIN = 'admin'
    OWNER = 'owner'
    BOTH = 'both'

    def __repr__(self):
        return f'{self.__class__.__qualname__}.{self.name}'

    def __str__(self):
        return self.value


class TransferData(Element):
    auth_info: Optional[str]
    foa_recipient: Optional[FoaRecipientType]


class DomainService(Service[Domain]):
    _id_name = 'domainName'

    def status(self, *names: str) -> Iterable[DomainStatusResult]:
        response = self._call(
            method='domainStatus',
            parameters={'domainNames': list(names)}
        )
        responses = response.get('responses', [])
        return [DomainStatusResult.from_json(dsr) for dsr in responses]

    def delete(self, name: str, exec_date: Optional[datetime] = None) -> None:
        parameters = {
            'domainName': name,
        }
        if exec_date is not None:
            parameters['execDate'] = exec_date.isoformat()
        self._call(
            method='domainDeletionCancel',
            parameters=parameters
        )

    def withdraw(self, name: str, disconnect: bool, exec_date: Optional[datetime] = None) -> None:
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
    sub_state: str
    comments: str
    errors: str
    execution_date: datetime
    add_date: datetime
    last_change_date: datetime
    # undocumented
    action: str
    client_transaction_id: str
    events: Iterable[JobEvent]
    object_id: str
    server_transaction_id: str
    triggered_by: JobTrigger
    warnings: str


class JobService(Service[Job]):
    def create(self, element: Job) -> None:
        raise NotImplementedError()

    def update(self, key: str, item: Job) -> None:
        raise NotImplementedError()

    def delete(self, key: str) -> None:
        raise NotImplementedError()
