=============================
django-admin-fast-search
=============================

.. image:: https://badge.fury.io/py/django-admin-fast-search.svg
    :target: https://badge.fury.io/py/django-admin-fast-search

.. image:: https://travis-ci.org/utkbansal/django-admin-fast-search.svg?branch=master
    :target: https://travis-ci.org/utkbansal/django-admin-fast-search

.. image:: https://codecov.io/gh/utkbansal/django-admin-fast-search/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/utkbansal/django-admin-fast-search

Your project description goes here

Documentation
-------------

The full documentation is at https://django-admin-fast-search.readthedocs.io.

Quickstart
----------

Install django-admin-fast-search::

    pip install django-admin-fast-search

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_admin_fast_search.apps.DjangoAdminFastSearchConfig',
        ...
    )

Add django-admin-fast-search's URL patterns:

.. code-block:: python

    from django_admin_fast_search import urls as django_admin_fast_search_urls


    urlpatterns = [
        ...
        url(r'^', include(django_admin_fast_search_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox


Development commands
---------------------

::

    pip install -r requirements_dev.txt
    invoke -l


Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
