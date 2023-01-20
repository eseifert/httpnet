from typing import Optional, Tuple, Union
from enum import Enum

from ._core import Client
from .domain import ContactService, DomainService, JobService
from .dns import ZoneConfigService, RecordService, ZoneService, NameserverSetService, TemplateService
from .email import MailboxService, OrganizationService, DomainSettingsService

from ._core import PlatformBaseUrl



class HttpNetClient:
    """
    A client for the http.net Partner API
    """

    def __init__(self, auth_token: str, base_url: PlatformBaseUrl, owner_account_id: Optional[str] = None,
                 timeout: Optional[Union[float, Tuple[float, float]]] = None) -> None:
        self.__client = Client(auth_token, base_url, owner_account_id=owner_account_id, timeout=timeout)

        # Domains
        self.domains = DomainService(self.__client)
        self.domain_contacts = ContactService(self.__client)
        self.domain_jobs = JobService(self.__client)

        # DNS
        self.dns_zone_configs = ZoneConfigService(self.__client)
        self.dns_records = RecordService(self.__client)
        self.dns_zones = ZoneService(self.__client)
        self.nameserver_sets = NameserverSetService(self.__client)
        self.dns_templates = TemplateService(self.__client)

        # Email
        self.mailboxes = MailboxService(self.__client)
        self.email_organizations = OrganizationService(self.__client)
        self.email_domain_settings = DomainSettingsService(self.__client)
