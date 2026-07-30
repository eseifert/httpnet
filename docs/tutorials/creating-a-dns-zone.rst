Creating a DNS zone
===================

In this tutorial you will create a DNS zone with two records, add a third
record to it and then delete the zone again. At the end your account will be in
exactly the state it was in before.

You need a domain in your account that does not have a DNS zone yet, or a name
you are happy to experiment with. This tutorial uses ``example.com``. Replace
it with your own name everywhere it appears.

.. warning::

   Unlike the first tutorial, the steps here change data in your account. A
   zone you create here is a real zone. The last step deletes it again.

Start a session
---------------

Use the virtual environment from the first tutorial and create a client:

.. code-block:: pycon

    >>> from httpnet.client import HttpNetClient
    >>> api = HttpNetClient(auth_token='<your api key>')

Check that no zone exists for your name yet:

.. code-block:: pycon

    >>> api.dns_zone_configs.count(ZoneName='example.com')
    0

A ``0`` means you are good to go.

Describe the zone
-----------------

A zone consists of a configuration and a list of records. Build the
configuration first:

.. code-block:: pycon

    >>> from httpnet.dns import ZoneConfig, ZoneConfigType
    >>> zone_config = ZoneConfig(
    ...     name='example.com',
    ...     type=ZoneConfigType.NATIVE,
    ...     email_address='hostmaster@example.com',
    ... )
    >>> zone_config.name
    'example.com'

Nothing has been sent yet. ``zone_config`` is a plain Python object you can
still change.

Now describe two records, a web server and a mail server:

.. code-block:: pycon

    >>> from httpnet.dns import DnsRecord, RecordType
    >>> records = [
    ...     DnsRecord(name='www.example.com', type=RecordType.A,
    ...               content='192.0.2.1', ttl=86400),
    ...     DnsRecord(name='example.com', type=RecordType.MX,
    ...               content='smtp.example.com', ttl=86400, priority=10),
    ... ]
    >>> len(records)
    2

Put the two pieces together into a zone:

.. code-block:: pycon

    >>> from httpnet.dns import Zone
    >>> zone = Zone(zone_config=zone_config, records=records)

Create the zone
---------------

Send it to the API. Let the API create the NS records for you from the default
name server set of your account:

.. code-block:: pycon

    >>> created = api.dns_zones.create(zone, use_default_nameserver_set=True)
    >>> created.zone_config.id
    '15010100000010'

The ID that comes back is the proof that the zone now exists on the server.
Write it down, you will need it in a moment:

.. code-block:: pycon

    >>> zone_config_id = created.zone_config.id

Look at what the API made of your two records:

.. code-block:: pycon

    >>> for record in created.records:
    ...     print(record.type, record.name, record.content)
    ...
    RecordType.NS example.com ns1.example.net
    RecordType.NS example.com ns2.example.net
    RecordType.A www.example.com 192.0.2.1
    RecordType.MX example.com smtp.example.com

Your two records are there, and the two NS records were added for you.

.. note::

   Creating a zone is processed asynchronously. The zone exists immediately,
   but it may take a moment before the name servers answer queries for it.

Add a record
------------

Records are not managed on their own, they are managed through their zone. To
add one, send the zone configuration back together with the records you want
added:

.. code-block:: pycon

    >>> new_record = DnsRecord(name='mail.example.com', type=RecordType.A,
    ...                        content='192.0.2.2', ttl=86400)
    >>> updated = api.dns_zones.update(created.zone_config,
    ...                                records_to_add=[new_record])
    >>> len(updated.records)
    5

The record count went from four to five. Confirm the new record is among them:

.. code-block:: pycon

    >>> [r.name for r in updated.records if r.type is RecordType.A]
    ['www.example.com', 'mail.example.com']

Read the zone back
------------------

Fetch the zone fresh from the server to be sure of what is stored:

.. code-block:: pycon

    >>> zone_config = api.dns_zone_configs.get(zone_config_id)
    >>> zone_config.name
    'example.com'
    >>> zone_config.type
    ZoneConfigType.NATIVE

Delete the zone
---------------

Clean up after yourself:

.. code-block:: pycon

    >>> api.dns_zones.delete(zone_config_id)

Check that it is gone:

.. code-block:: pycon

    >>> api.dns_zone_configs.count(ZoneName='example.com')
    0

You are back to where you started.

.. note::

   A deleted zone is kept in a restorable state for a while before it is
   removed for good, so the name may not be immediately reusable.

What you have learned
---------------------

You built objects locally, sent them to the API, read the created objects back
and cleaned up. You also saw that records belong to their zone: you add and
remove them by updating the zone, not by talking to a record service.

From here, the :doc:`how-to guides <../how-to/index>` show you how to solve
individual problems, and the :doc:`reference <../reference/index>` lists every
field of every object.
