from httpnet.client import HttpNetClient


def test_client_exposes_all_services() -> None:
    api = HttpNetClient(auth_token='dummy')
    for attribute in ('domains', 'domain_contacts', 'domain_jobs',
                      'dns_zone_configs', 'dns_records', 'dns_zones',
                      'nameserver_sets', 'dns_templates',
                      'mailboxes', 'email_organizations', 'email_domain_settings'):
        assert hasattr(api, attribute)
