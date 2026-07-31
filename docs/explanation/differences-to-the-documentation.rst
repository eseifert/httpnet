Where the API differs from its documentation
============================================

The models and service classes of this package were written from the `official
API documentation <https://www.http.net/docs/api/>`__. The live API does not
match it everywhere. This page collects the deviations the package has to work
around, so that the special cases in the code do not look arbitrary.

How these were established
--------------------------

The documented objects and methods were read from the API documentation as it
stood on 2026-07-31. The behaviour of the live API was observed by calling
``partner.http.net`` with a single account on the same day, using only reading
methods. The sample was 63 domains, 20 contacts, 155 jobs, 71 zone
configurations, 1222 records and 1 template.

Two limits follow from that. Anything the account does not hold could not be
checked — it has no mailboxes, so the mail service is covered far less
thoroughly than the domain and DNS services. And a field that never appeared
may still exist for products the account does not use. The list below is a
lower bound, not a closed set.

Undocumented fields
-------------------

The API returns fields the documentation does not list.
:meth:`~httpnet._core.Element.from_json` rejects any field its element does not
declare, so each of these made an entire listing unreadable until it was added.
Elements mark them with an ``# undocumented`` comment.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Element
     - Fields the documentation does not list
   * - :class:`~httpnet.domain.Contact`
     - ``comments``, ``disclose``, ``emailIsVerified``, and the whole block of
       ``ext…`` fields carrying registry-specific data
   * - :class:`~httpnet.domain.Domain`
     - ``bundleId``, ``deletionScheduledFor``, ``dnsSecEntries``,
       ``latestDeletionDateWithoutRenew``, ``paidUntil``, ``productCode``,
       ``renewOn``, ``restorableUntil``, ``restrictions``,
       ``transferLockedByOwnerChangeUntil``, ``trusteeServiceEnabled``
   * - :class:`~httpnet.domain.Job`
     - ``action``, ``comments``, ``events``, ``objectId``, ``objectType``,
       ``subState``, ``status``, ``subStatus``, ``triggeredBy``
   * - :class:`~httpnet.domain.DomainStatusResult`
     - ``earlyAccessStart``, ``extension``, ``generalAvailabilityStart``,
       ``landrushStart``, ``launchPhase``, ``premiumPrices``, ``registrarTag``,
       ``sunriseStart``, ``transferOwnerHandling``
   * - :class:`~httpnet.dns.ZoneConfig`
     - ``addDate``, ``restorableUntil``
   * - :class:`~httpnet.dns.DnsRecord`
     - ``comments``, ``zoneConfigId``, ``accountId``, ``addDate``
   * - :class:`~httpnet.dns.NameserverSet`
     - ``type``, ``addDate``, ``lastChangeDate``
   * - :class:`~httpnet.dns.Template`
     - ``emailAddress``, ``addDate``, ``lastChangeDate``

``premiumPrices`` is the one field that is not modelled. It is a deeply nested
price structure — amounts per operation, currencies, exchange rates and
promotion periods — sent only for premium domains. It is declared as a plain
mapping and passed through unchanged.

Two fields for one thing
------------------------

:class:`~httpnet.domain.Job` reports ``state`` and ``status`` side by side, and
likewise ``subState`` and ``subStatus``. Both pairs arrive in the same
response, and only ``state`` is documented. The element declares all four
rather than guess which is authoritative.

Fields that are documented but never sent
-----------------------------------------

:class:`~httpnet.dns.DnsRecord` declares ``zone_id`` because the documentation
lists it, but it appeared in none of the 1222 records that were read. The API
identifies the zone of a record with the undocumented ``zoneConfigId`` instead.
The documented field is kept, since an element that does not declare a field
cannot receive it.

Most elements cannot be retrieved individually
----------------------------------------------

The API names its methods after the element, and the package derives those
names from the class name of the element. That pattern suggests a ``widgetInfo``
for every ``Widget``, but the documentation describes only two such methods,
``domainInfo`` and ``contactInfo``. There is no listing of the others, and
calling them confirms they do not exist — the following all answer with HTTP
404:

    ``jobInfo``, ``zoneConfigInfo``, ``recordInfo``, ``zoneInfo``,
    ``nameserverSetInfo``, ``templateInfo``, ``mailboxInfo``,
    ``organizationInfo``, ``domainSettingsInfo``

This is a gap in the pattern rather than a contradiction of the documentation,
and it is why :meth:`~httpnet._core.Service.get` does not use the ``Info``
method by default. It filters the listing for the ID instead, which every
service supports, and raises :exc:`KeyError` when nothing matches.
:class:`~httpnet.domain.DomainService` overrides it to use ``domainInfo``,
which takes a domain name rather than an ID and reports an unknown name as a
:class:`~httpnet._core.ServiceException`.

Filter fields do not always follow the element
----------------------------------------------

Retrieving by ID relies on filtering a listing for ``<Element>Id``, which the
API spells with a leading capital. Unknown filter fields are rejected with
error 11102, which makes the accepted spelling easy to establish, and two
listings stand out:

``zonesFind``
    rejects ``ZoneId``. A zone is identified by its configuration, so the
    filter is ``ZoneConfigId``.

``domainSettingsFind``
    rejects ``DomainSettingsId`` and ``DomainNameUnicode``. Domain settings
    carry no ID of their own and are keyed by ``DomainName``.

:class:`~httpnet.dns.ZoneService` and
:class:`~httpnet.email.DomainSettingsService` override the derived name
accordingly.

Undocumented enumeration values
-------------------------------

``domainStatus`` reports ``transferMethod`` values beyond the documented ones.
Suffixes transferred by registrar tag, such as ``uk``, answer with ``pushTag``,
which :class:`~httpnet.domain.TransferMethod` declares as
:attr:`~httpnet.domain.TransferMethod.PUSH_TAG`.

:class:`~httpnet.dns.RecordType` deviates in both directions. The documentation
lists ``CERT``, ``DNSKEY``, ``NSEC``, ``NSEC3``, ``NSEC3PARAM``,
``OPENPGPKEY``, ``RRSIG`` and ``SSHFP``, which the enumeration now declares. It
does not list ``SOA``, yet every zone answers with the SOA record of its zone,
so that value is declared as well.

Missing values do not raise. A field annotated with an enumeration and ``None``
falls back to the raw string when the value does not convert, so the attribute
silently changes type from the enumeration to :class:`str` instead of failing.
That makes a missing value worth reporting rather than tolerating.

The mail service is modelled more loosely than it is documented
---------------------------------------------------------------

The documentation describes a separate object per mailbox type — ``ImapMailbox``,
``Forwarder``, ``SmtpForwarder``, ``MailingList`` and ``Catchall`` — each with
its own fields. :class:`~httpnet.email.Mailbox` collapses them into a single
element whose type-specific fields are optional, and
:class:`~httpnet.email.MailboxType` covers only ``ImapMailbox``, ``Forwarder``
and an ``ExchangeMailbox`` that the documentation does not describe. Mailing
lists, catchalls, SMTP forwarders and the documented ``autoResponder`` settings
are not modelled.

None of this could be checked against the live API, because the account holds
no mailboxes. It is recorded here as a known gap rather than a confirmed
deviation.

The email organization service does not answer
----------------------------------------------

:attr:`~httpnet.client.HttpNetClient.email_organizations` is the one service
that could not be made to work. ``organizationsFind`` answers with HTTP 404, as
do ``organizationFind``, ``organisationsFind``, ``exchangeOrganizationsFind``
and the same names under an ``exchange`` service. ``mailboxesFind`` and
``domainSettingsFind`` succeed against the same service, so the ``email``
service itself is reachable and the account is permitted to use it.

The documentation offers no help: it describes no organization object or method
for the mail service at all. The only documented ``Organization`` belongs to
the SSL service, where it is part of a certificate order and unrelated. Whether
the mail service names the method differently or does not offer it on this
platform could not be decided from outside.

Method names that do not match the documentation
------------------------------------------------

Two methods of :class:`~httpnet.dns.ZoneService` are spelled with a plural
``Templates`` where the documentation gives a singular ``Template``:

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Method
     - Name used by the package
     - Name in the documentation
   * - ``ZoneService.untie_from_templates``
     - ``zonesUntieFromTemplates``
     - ``zonesUntieFromTemplate``
   * - ``ZoneService.tie_to_templates``
     - ``zonesTieToTemplates``
     - ``zonesTieToTemplate``

Unlike every other item on this page, this one is **unverified**. Both methods
write, and the only way to find out which spelling the live API routes is to
call them, which would tie or untie zones. The package therefore keeps its
current names until someone can check them against a test account.

Services the package does not cover
-----------------------------------

The documentation describes an SSL service — certificate orders, CSRs,
validation and issued certificates — which the package does not implement at
all. Within DNS, the documented DNSSEC objects and the ``zoneRestore`` and
``zonePurgeRestorable`` methods are likewise absent.
