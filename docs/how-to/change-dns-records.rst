How to change DNS records
=========================

Records are managed through their zone. Pass the zone configuration together
with the records to add, modify or delete.

Add a record
------------

.. code-block:: python

    from httpnet.dns import DnsRecord, RecordType

    zone_config = api.dns_zone_configs.get('15010100000010')
    record = DnsRecord(name='mail.example.com', type=RecordType.A,
                       content='192.0.2.2', ttl=86400)

    zone = api.dns_zones.update(zone_config, records_to_add=[record])

Delete a record
---------------

Identify the record by its ID, or by name, type and content:

.. code-block:: python

    obsolete = DnsRecord(name='old.example.com', type=RecordType.A,
                         content='192.0.2.9')

    zone = api.dns_zones.update(zone_config, records_to_delete=[obsolete])

Deleting a record that does not exist is an error.

Modify a record
---------------

Pass the record with its ID and the new values:

.. code-block:: python

    changed = DnsRecord(id='15010100000020', name='www.example.com',
                        type=RecordType.A, content='192.0.2.3', ttl=3600)

    zone = api.dns_zones.update(zone_config, records_to_modify=[changed])

Do several changes in one request
---------------------------------

.. code-block:: python

    zone = api.dns_zones.update(
        zone_config,
        records_to_add=[DnsRecord(name='new.example.com', type=RecordType.A,
                                  content='192.0.2.4')],
        records_to_modify=[changed],
        records_to_delete=[obsolete],
    )

Records that appear in none of the three lists are left untouched.

Replace the content of records across all zones
-----------------------------------------------

To repoint every ``MX`` record from one host to another:

.. code-block:: python

    from httpnet.dns import RecordType

    api.dns_zones.change_content(
        record_type=RecordType.MX,
        old_content='mail.oldserver.example',
        new_content='mail.newserver.example',
        include_templates=True,
        include_sub_accounts=False,
    )

Find the records of a zone
--------------------------

.. code-block:: python

    for record in api.dns_records.find(ZoneConfigId='15010100000010'):
        print(record.type, record.name, record.content)
