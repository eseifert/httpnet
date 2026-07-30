httpnet.client
==============

.. module:: httpnet.client

Entry point of the package. A client instance offers one service per category
of the API.

.. autoclass:: httpnet.client.HttpNetClient

   .. attribute:: domains
      :type: httpnet.domain.DomainService

      Domains of the account.

   .. attribute:: domain_contacts
      :type: httpnet.domain.ContactService

      Contacts that can be assigned to domains.

   .. attribute:: domain_jobs
      :type: httpnet.domain.JobService

      Asynchronous operations of the domain service.

   .. attribute:: dns_zone_configs
      :type: httpnet.dns.ZoneConfigService

      Configurations of the DNS zones.

   .. attribute:: dns_records
      :type: httpnet.dns.RecordService

      Records of all DNS zones.

   .. attribute:: dns_zones
      :type: httpnet.dns.ZoneService

      DNS zones, i.e. a configuration together with its records.

   .. attribute:: nameserver_sets
      :type: httpnet.dns.NameserverSetService

      Reusable sets of name servers.

   .. attribute:: dns_templates
      :type: httpnet.dns.TemplateService

      Templates for creating and mass updating zones.

   .. attribute:: mailboxes
      :type: httpnet.email.MailboxService

      Mailboxes, forwarders, mailing lists and catchalls.

   .. attribute:: email_organizations
      :type: httpnet.email.OrganizationService

      Email organizations.

   .. attribute:: email_domain_settings
      :type: httpnet.email.DomainSettingsService

      Quotas of the email domains.

.. autoclass:: httpnet.client.Platform
   :members:
   :undoc-members:
