from ._core import Client, Platform
from .dns import NameserverSetService, RecordService, TemplateService, ZoneConfigService, ZoneService
from .domain import ContactService, DomainService, JobService
from .email import DomainSettingsService, MailboxService, OrganizationService

__all__ = ['HttpNetClient', 'Platform']


class HttpNetClient:
    """
    A client for the http.net Partner API.

    The same API is operated for hosting.de, pass ``Platform.HOSTING_DE`` as
    ``base_url`` to use it.
    """

    def __init__(self, auth_token: str, owner_account_id: str | None = None,
                 timeout: float | tuple[float, float] | None = None,
                 base_url: Platform | str = Platform.HTTP_NET) -> None:
        self.__client = Client(auth_token, owner_account_id=owner_account_id, timeout=timeout,
                               base_url=base_url)

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
