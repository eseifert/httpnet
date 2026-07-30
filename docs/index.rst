httpnet
=======

``httpnet`` is an unofficial Python client for the `Partner API
<https://www.http.net/docs/api/>`__ of http.net Internet GmbH. The same API is
operated for `hosting.de <https://www.hosting.de/api/>`__.

This documentation follows the `Diátaxis documentation system
<https://docs.divio.com/documentation-system/>`__ and is divided into four
parts, each of which serves a different need.

:doc:`Tutorials <tutorials/index>`
    Lessons that take you by the hand through a series of steps. Start here if
    you are new to the package.

:doc:`How-to guides <how-to/index>`
    Recipes that answer the question "How do I …?". They assume that you
    already know the basics.

:doc:`Reference <reference/index>`
    Technical description of the modules, classes and methods of the package.

:doc:`Explanation <explanation/index>`
    Background and discussion of how the package works and why it is built the
    way it is.

.. toctree::
   :maxdepth: 2
   :hidden:

   tutorials/index
   how-to/index
   reference/index
   explanation/index

Installation
------------

``httpnet`` requires Python 3.10 or newer:

.. code-block:: console

    $ pip install git+https://github.com/eseifert/httpnet.git

Using `uv <https://docs.astral.sh/uv/>`__:

.. code-block:: console

    $ uv add git+https://github.com/eseifert/httpnet.git

License
-------

`MIT <https://choosealicense.com/licenses/mit/>`__. This package is not related
to http.net Internet GmbH.
