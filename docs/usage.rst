=====
Usage
=====

To use django-admin-fast-search in a project, add it to your `INSTALLED_APPS`:

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
