How to create a zone from a template
====================================

Create a template
-----------------

A template is a name plus a list of record templates. Placeholders
(``##DOMAIN##``, ``##IPV4##``, ``##IPV6##``, ``##MX_IPV4##``, ``##MX_IPV6##``)
are filled in when a zone is created from it:

.. code-block:: python

    from httpnet.dns import RecordTemplate, RecordType, Template

    template = api.dns_templates.create(
        Template(name='Standard hosting'),
        record_templates=[
            RecordTemplate(name='##DOMAIN##', type=RecordType.A,
                           content='##IPV4##', ttl=86400),
            RecordTemplate(name='www.##DOMAIN##', type=RecordType.A,
                           content='##IPV4##', ttl=86400),
            RecordTemplate(name='##DOMAIN##', type=RecordType.MX,
                           content='##MX_IPV4##', ttl=86400, priority=10),
        ],
    )

Create a zone from it
---------------------

Set the template values on the zone configuration and supply a replacement for
every placeholder the template uses:

.. code-block:: python

    from httpnet.dns import (
        TemplateReplacements, TemplateValues, Zone, ZoneConfig, ZoneConfigType,
    )

    zone_config = ZoneConfig(
        name='example.com',
        type=ZoneConfigType.NATIVE,
        template_values=TemplateValues(
            template_id=template.id,
            tie_to_template=True,
            template_replacements=TemplateReplacements(
                ipv4_replacement='192.0.2.1',
                mail_ipv4_replacement='192.0.2.2',
            ),
        ),
    )

    zone = api.dns_zones.create(Zone(zone_config=zone_config, records=[]),
                                use_default_nameserver_set=True)

Missing a replacement for a placeholder the template uses is an error.

Keep zones in sync with the template
------------------------------------

Set ``tie_to_template=True`` as above. Changes to the template are then applied
to the zone automatically.

Detach a zone from its template:

.. code-block:: python

    api.dns_zones.untie_from_templates(zone_config_names=['example.com'])

Attach it again:

.. code-block:: python

    api.dns_zones.tie_to_templates(zone_config_names=['example.com'])

Update a template
-----------------

.. code-block:: python

    api.dns_templates.update(
        template,
        record_templates_to_add=[
            RecordTemplate(name='ipv6.##DOMAIN##', type=RecordType.AAAA,
                           content='##IPV6##', ttl=86400),
        ],
        record_templates_to_delete=[],
        replacements=TemplateReplacements(ipv6_replacement='2001:db8::1'),
    )

Pass ``replacements`` when you add a placeholder that tied zones have no value
for yet. It is used as the default for those zones.

Delete a template
-----------------

.. code-block:: python

    api.dns_templates.delete(template_id=template.id)

Deleting a template deletes every record that was created from its record
templates. Zones that are still tied to it prevent the deletion.
