Synchronous and asynchronous requests
=====================================

Some requests are answered when the work is done, others are answered when the
work has been accepted. The difference is not visible in the Python signature,
and it matters for anything that acts on the result.

Two kinds of request
--------------------

Requests the API can satisfy on its own are processed synchronously. Listings,
reading a single object, creating a name server set — all of these touch only
the systems of the provider, and their response reflects the finished state.
They answer with a ``status`` of ``success``.

Requests that involve a third party are processed asynchronously. Registering,
transferring or deleting a domain has to reach a registry; updating a contact
has to be pushed to every registry that contact is connected to. These answer
with a ``status`` of ``pending``. The response says the request was accepted
and well-formed. It does not say the domain was registered.

The package treats both as success, because both mean the request was not
rejected. Neither raises.

What pending means for the caller
---------------------------------

A method that returns after a pending response has returned a promise, not a
result. The object it hands back reflects the request that was made, not the
state of the world. Code that deletes a domain and immediately lists domains
may well still see it. Code that creates a zone and immediately queries the
name servers may not get an answer yet.

Where this bites hardest is in loops that verify their own work. A batch job
that updates a hundred contacts and then reads them back to confirm the change
will find most of them unchanged, because the updates are still travelling to
the registries.

Jobs
----

Asynchronous work is tracked by job objects, which the
:class:`~httpnet.domain.JobService` lists. A job records what was attempted,
which object it concerns, its current state, and the errors it ran into. An
update that touches several registries produces a separate job for each of
them, so one call can turn into several jobs.

Jobs are read-only. They are created by the API as a side effect of the work it
does, which is why the service that exposes them offers nothing but reading.

Poll messages
-------------

The API also pushes the outcome of asynchronous requests as poll messages, and
provides a ``clientTransactionId`` on every request so that responses and polls
can be matched back to the request that caused them.

Neither is supported by this package. Following an asynchronous operation
through to its conclusion currently means polling the job service. Whether that
is good enough depends on what the calling code does with the result: fire and
forget is fine, verifying the outcome is not.
