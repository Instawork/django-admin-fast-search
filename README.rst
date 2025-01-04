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
        'django_admin_fast_search',
        ...
    )

Use it in your Django admin for search fields:

.. code-block:: python

   from django_admin_fast_search.admin import FastSearch

   class MyModelAdmin(FastSearch, admin.ModelAdmin):
       list_display = ['name', 'email']

       search_fields_contains = ("address",)
       search_fields_exact = ("id", "email")
       search_fields_fulltext_index = ("name",)
       search_fields = search_fields_fulltext_index + search_fields_exact + search_fields_contains


Use it for list filters with django_filters_

.. code-block:: python

   from django_filters import BooleanFilter, FilterSet
   from django_admin_fast_search.admin import FastSearchFilterMixin

   class MyModelFilter(FastSearchFilterMixin, FilterSet):
       is_verified = BooleanFilter(label="Verified?")

       company_name = CharFilter(field_name="company__name", lookup_expr="icontains")
       company_pincode = CharFilter(field_name="company__location_pincode", lookup_expr="exact")

       exclude_industry = CharFilter(field_name="industry", lookup_expr="icontains", label="Exclude Industry", exclude=True)

       status = MultipleChoiceFilter(
           field_name="status",
           lookup_expr="exact",
           label="Status",
           choices=MyModel.STATUS_CHOICES,
       )

       created_at = DateFilter(field_name="created_at", lookup_expr="gt", label="Signed up After")

       class Meta:
           model = MyModel
           fields = [
               "is_verified",
               "company_name",
               "company_pincode",
               "exclude_industry",
               "status",
               "created_at",
           ]


   class MyModelAdmin(FastSearch, admin.ModelAdmin):
       list_display = ['name', 'email']

       list_filter = ["company_tier", *MyModelFilter.as_admin_filters()]

       # or only use class-based filters

       list_filter = MyModelFilter.as_admin_filters()


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
.. _django_filters: https://django-filter.readthedocs.io/en/stable/
