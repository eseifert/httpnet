"""
Example payloads taken verbatim from the API documentation at
https://www.http.net/docs/api/ so that the tests are checked against the
data the API is documented to return.
"""

# Section "The Contact Object"
CONTACT = {
    'accountId': '15010100000001',
    'id': '15010100000010',
    'handle': 'JS15',
    'type': 'person',
    'name': 'John Smith',
    'organization': '',
    'street': ['Happy ave. 42'],
    'postalCode': '12345',
    'city': 'Where ever',
    'state': '',
    'country': 'de',
    'emailAddress': 'john@example.com',
    'phoneNumber': '+49 1234 567890',
    'faxNumber': '',
    'sipUri': '',
    'hidden': False,
    'usableBySubAccount': False,
    'addDate': '2015-01-01T00:00:00',
    'lastChangeDate': '2015-01-01T00:00:00',
}

# Section "The Domain Object". The documented "status" value of the example is
# "ok", which is not one of the documented domain statuses, so the documented
# status "active" is used here instead.
DOMAIN = {
    'id': '150101000000010',
    'accountId': '150101000000001',
    'name': 'example.com',
    'nameUnicode': 'example.com',
    'status': 'active',
    'transferLockEnabled': False,
    'authInfo': '1234,ABCD+xyz',
    'contacts': [
        {'contact': '150101000000021', 'type': 'owner'},
        {'contact': '150101000000020', 'type': 'admin'},
        {'contact': '150101000000022', 'type': 'tech'},
        {'contact': '150101000000023', 'type': 'zone'},
    ],
    'nameservers': [
        {'ips': [], 'name': 'ns.example.net'},
        {'name': 'ns.example.com', 'ips': ['192.0.2.1', '2001:db8:3fe:1001:7777:772e:2:85']},
    ],
    'createDate': '2014-01-01',
    'currentContractPeriodEnd': '2015-12-31',
    'nextContractPeriodStart': '2016-01-01',
    'deletionType': '',
    'deletionDate': '',
    'addDate': '2015-01-01T00:00:00',
    'lastChangeDate': '2014-12-15T00:00:00',
}

# Section "Job Object"
JOB = {
    'id': '150223248499677',
    'accountId': '15010100000001',
    'displayName': 'example.org',
    'domainNameAce': 'example.org',
    'domainNameUnicode': 'example.org',
    'handle': '',
    'type': 'domainTransferIn',
    'state': 'error',
    'subState': '',
    'comments': '',
    'errors': '[{"code":30003,"context":"example.org","details":[],'
              '"text":"The provided Authinfo is wrong"}]',
    'executionDate': '2015-02-23T17:39:23Z',
    'addDate': '2015-01-01T00:00:00Z',
    'lastChangeDate': '2015-01-01T00:00:00Z',
}

# Section "Creating New Zones"
ZONE_CREATE_REQUEST = {
    'nameserverSetId': '15010100000020',
    'useDefaultNameserverSet': False,
    'zoneConfig': {
        'name': 'example.com',
        'type': 'NATIVE',
        'emailAddress': 'admin@example.com',
    },
    'records': [
        {'name': 'www.example.com', 'type': 'A', 'content': '172.27.171.106', 'ttl': 86000},
        {'name': 'example.com', 'type': 'MX', 'content': 'smtp.example.com', 'ttl': 86000,
         'priority': 0},
    ],
}

# Section "Updating Zones"
ZONE_CONFIG = {
    'accountId': '15010100000001',
    'emailAddress': 'admin@example.com',
    'id': '15010100000010',
    'lastChangeDate': '2015-09-02T10:14:02Z',
    'masterIp': '',
    'name': 'example.com',
    'nameUnicode': 'example.com',
    'soaValues': {
        'expire': 3600000,
        'negativeTtl': 3600,
        'refresh': 86400,
        'retry': 7200,
        'ttl': 172800,
    },
    'status': 'active',
    'templateValues': None,
    'type': 'NATIVE',
    'zoneTransferWhitelist': [],
}

# Section "NameserverSet Object"
NAMESERVER_SET = {
    'id': '',
    'accountId': '',
    'name': 'Server 1',
    'defaultNameserverSet': False,
    'nameservers': ['ns1.example.com', 'ns2.example.com'],
}

# Section "The DomainSettings Object"
DOMAIN_SETTINGS = {
    'domainName': 'example.com',
    'domainNameUnicode': 'example.com',
    'storageQuota': -1,
    'storageQuotaAllocated': 1024,
    'mailboxQuota': -1,
    'addDate': '2016-01-01T15:57:35Z',
    'lastChangeDate': '2016-01-01T15:57:35Z',
}

# Section "Warnings and Errors"
ERROR_RESPONSE = {
    'status': 'error',
    'errors': [
        {
            'code': 32002,
            'contextObject': '',
            'contextPath': '/contact/type',
            'details': [],
            'text': 'Handle type is invalid',
            'value': 'asd',
        },
        {
            'code': 32022,
            'contextObject': '',
            'contextPath': '/contact/phone',
            'details': [],
            'text': 'Format of the phone number is invalid. '
                    'The E.123 international notation is required',
            'value': '+49',
        },
    ],
}
