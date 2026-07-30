How to schedule a domain deletion
=================================

Delete a domain immediately
---------------------------

.. code-block:: python

    api.domains.delete('example.com')

The deletion date is set to the next possible date.

Delete a domain on a given date
-------------------------------

.. code-block:: python

    from datetime import datetime

    api.domains.delete('example.com', exec_date=datetime(2026, 12, 31))

Withdraw a domain instead
-------------------------

Withdrawal hands the domain back to the registry rather than deleting it:

.. code-block:: python

    api.domains.withdraw('example.com', disconnect=False)

Pass ``disconnect=True`` to remove the domain from the name servers after the
withdrawal, and ``exec_date`` to schedule it:

.. code-block:: python

    api.domains.withdraw('example.com', disconnect=True,
                         exec_date=datetime(2026, 12, 31))

Cancel a scheduled deletion
---------------------------

This cancels both deletions and withdrawals:

.. code-block:: python

    api.domains.cancel_deletion('example.com')

Check whether a domain is scheduled for removal
-----------------------------------------------

.. code-block:: python

    from httpnet.domain import DeletionType

    domain = api.domains.get('example.com')
    if domain.deletion_type not in (None, DeletionType.NONE):
        print(domain.deletion_type, domain.deletion_date)

Restore a deleted domain
------------------------

A deleted domain stays restorable for a grace period:

.. code-block:: python

    api.domains.restore('example.com')

Follow up on the result
-----------------------

Deletion is asynchronous. Watch the job that carries it out:

.. code-block:: python

    for job in api.domain_jobs.find(DomainNameAce='example.com', sort='~JobAddDate'):
        print(job.type, job.state, job.execution_date)
        break
