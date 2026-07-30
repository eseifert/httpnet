How to act on behalf of a subaccount
====================================

Pass the ID of the subaccount as ``owner_account_id``:

.. code-block:: python

    from httpnet.client import HttpNetClient

    api = HttpNetClient(auth_token='<your api key>',
                        owner_account_id='15010100000042')

    for domain in api.domains:
        print(domain.name)

Every request this client makes is executed for that subaccount.

Switch between accounts
-----------------------

The account is fixed for the lifetime of a client, so create one client per
account:

.. code-block:: python

    own = HttpNetClient(auth_token=API_KEY)
    customer = HttpNetClient(auth_token=API_KEY, owner_account_id='15010100000042')

    print(len(own.domains), len(customer.domains))

Work through a list of subaccounts
----------------------------------

.. code-block:: python

    ACCOUNT_IDS = ['15010100000042', '15010100000043']

    for account_id in ACCOUNT_IDS:
        api = HttpNetClient(auth_token=API_KEY, owner_account_id=account_id)
        print(account_id, len(api.domains))
