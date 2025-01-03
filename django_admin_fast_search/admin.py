# -*- coding: utf-8 -*-
import logging
import django_filters

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import connections
from django.db.models import query
from django.utils.functional import cached_property

import re

logger = logging.getLogger("instawork.django_admin_fast_search.admin")

class FastSearch(admin.ModelAdmin):

    show_full_result_count = False
    change_list_template = "admin/custom_change_list.html"
    # Fields that will do a SQL LIKE query
    search_fields_contains = ()

    # Fields that will do an exact match (potentially using an index)
    search_fields_exact = ()

    # Fields that will do a SQL MATCH query using a fulltext index (MySQL only)
    search_fields_fulltext_index = ()

    def lookup_allowed(self, lookup, value):
        return True

    def get_list_filter(self, request):
        initial_list_filters = tuple(self.list_filter)

        new_filters = ()

        for field in self.search_fields:
            if field in self.search_fields_contains:
                filter_class = generic_filter_factory(filter_type="contains")
            elif field in self.search_fields_fulltext_index:
                filter_class = generic_filter_factory(filter_type="search")
            else:
                filter_class = generic_filter_factory(filter_type="exact")
            filter_class.title = field.replace("__", "→").replace("_", " ").upper()
            filter_class.parameter_name = field

            new_filters += (filter_class,)
        return new_filters + initial_list_filters

    def get_paginator(self, request, *args, **kwargs):
        """Return an approximate count on pagination only if no filters are specified"""
        if request.GET:
            return super().get_paginator(request, *args, **kwargs)
        return ApproximatePaginator(*args, **kwargs)


class ApproximatePaginator(Paginator):

    @cached_property
    def count(self):
        """Possibly return a faster approximate row count for MySQL, otherwise fallback to default behavior"""
        connection = connections[self.object_list.db]
        is_mysql = getattr(connection, 'vendor', None) == 'mysql'

        if is_mysql and self._can_approximate_count():
            return self._mysql_approximate_count(connection)

        return super().count

    def _mysql_approximate_count(self, connection):
        """Use MySQL information_schema to get an approximate row count on the table"""
        with connection.cursor() as cursor:
            table_name = self.object_list.model._meta.db_table
            cursor.execute(
                """SELECT TABLE_ROWS
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE() AND
                TABLE_NAME = %s
                """,
                (table_name,),
            )
            approx_count = cursor.fetchone()[0]
            return approx_count

    def _can_approximate_count(self):
        """
        Return True if the query doesn't have any filters and as such be approximated, otherwise return False.
        Inspiration from: https://github.com/adamchainz/django-mysql/blob/9464782c0f3fea1147149411d05e4c771250162f/src/django_mysql/models/query.py#L705
        """
        if not isinstance(self.object_list, query.QuerySet):
            return False

        q = self.object_list.query
        if q.where or q.high_mark is not None or q.low_mark != 0 or q.select or q.group_by or q.distinct:
            return False

        return True


def generic_filter_factory(filter_type):
    """
    Factory to generate GenericFilter classes. This helps us generate multiple independent copies of this class
    """

    class GenericExactFilter(admin.SimpleListFilter):
        title = None
        parameter_name = None

        template = "admin/custom_search_field.html"

        def lookups(self, request, model_admin):
            return (self.parameter_name, self.parameter_name),

        def queryset(self, request, queryset):
            if self.value():
                kwargs = {"{}".format(self.parameter_name): self.value()}
                return queryset.filter(**kwargs)
            return queryset

    class GenericContainsFilter(admin.SimpleListFilter):
        title = None
        parameter_name = None

        template = "admin/custom_search_field.html"

        def lookups(self, request, model_admin):
            return (self.parameter_name, self.parameter_name),

        def queryset(self, request, queryset):
            if self.value():
                kwargs = {"{}__icontains".format(self.parameter_name): self.value()}
                return queryset.filter(**kwargs)
            return queryset

    class GenericSearchFilter(admin.SimpleListFilter):
        title = None
        parameter_name = None

        template = "admin/custom_search_field.html"

        def lookups(self, request, model_admin):
            return (self.parameter_name, self.parameter_name),

        def queryset(self, request, queryset):
            if self.value():

                # remove operators with special meaning in boolean search mode.
                # Operators are: +, -, > <, ( ), ~, *, ", @distance
                # refer https://stackoverflow.com/a/26537463

                search_value = re.sub(r'[+\-><\(\)~*\"@]+', ' ', self.value())

                terms = search_value.strip().split(" ")
                query = " ".join([f'+"{term}"' for term in terms if term])
                logger.info(f"Query: {query}")

                kwargs = {f"{self.parameter_name}__search": f"{query}"}
                return queryset.filter(**kwargs)
            return queryset

    if filter_type == "contains":
        return GenericContainsFilter
    elif filter_type == "search":
        return GenericSearchFilter
    else:
        return GenericExactFilter




class BaseListFilter(admin.SimpleListFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def queryset(self, request, queryset):
        if hasattr(self, "admin_filter_instance"):
            try:
                value = self.admin_filter_instance.field.to_python(self.value())
                return self.admin_filter_instance.filter(queryset, value)
            except ValidationError:
                return queryset
        return queryset

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for attr_name, attr_value in kwargs.items():
            setattr(cls, attr_name, attr_value)


class FastSearchFilterMixin:
    @classmethod
    def as_admin_filters(cls):
        admin_filters = []
        for name, filter_instance in cls.base_filters.items():
            admin_filter_class = cls._create_admin_filter(name, filter_instance)
            if admin_filter_class:
                admin_filters.append(admin_filter_class)
        return admin_filters

    @classmethod
    def _create_admin_filter(cls, name, filter_instance):
        if isinstance(filter_instance, django_filters.BooleanFilter):
            return cls._create_boolean_list_filter(name, filter_instance)
        elif isinstance(filter_instance, django_filters.MultipleChoiceFilter):
            return cls._create_multiple_choice_list_filter(name, filter_instance)
        elif isinstance(filter_instance, django_filters.ChoiceFilter):
            return cls._create_choice_list_filter(name, filter_instance)
        elif isinstance(filter_instance, django_filters.CharFilter):
            return cls._create_char_list_filter(name, filter_instance)
        elif isinstance(filter_instance, django_filters.DateFilter):
            return cls._create_date_list_filter(name, filter_instance)
        else:
            raise NotImplementedError(f"Filter type {type(filter_instance)} is not supported yet.")

    @classmethod
    def _get_field_name_and_title(cls, name, filter_instance):
        field_name = filter_instance.field_name or name
        title = filter_instance.label or field_name.replace("__", " → ").replace("_", " ").title()
        return field_name, title

    @classmethod
    def _get_filter_class(cls, name, filter_instance, methods, base_class=BaseListFilter):
        field_name, title = cls._get_field_name_and_title(name, filter_instance)
        class_attrs = {
            "title": title,
            "parameter_name": name,
            "admin_filter_instance": filter_instance,
        }
        class_attrs.update(methods)

        return type(f'{name.title().replace("_", "")}ListFilter', (base_class,), class_attrs)

    @classmethod
    def _create_choice_list_filter(cls, name, filter_instance):
        choices = filter_instance.extra.get("choices") or filter_instance.field.choices

        def lookups(self, request, model_admin):
            return choices

        methods = {"lookups": lookups}

        return cls._get_filter_class(name, filter_instance, methods)

    @classmethod
    def _create_boolean_list_filter(cls, name, filter_instance):
        field_name, _ = cls._get_field_name_and_title(name, filter_instance)

        def lookups(self, request, model_admin):
            return (
                ("True", "Yes"),
                ("False", "No"),
            )

        methods = {"lookups": lookups}

        return cls._get_filter_class(name, filter_instance, methods)

    @classmethod
    def _create_char_list_filter(cls, name, filter_instance):
        def lookups(self, request, model_admin):
            return ((self.parameter_name, self.parameter_name),)

        methods = {
            "lookups": lookups,
            "template": "admin/custom_search_field.html",
        }

        return cls._get_filter_class(name, filter_instance, methods)

    @classmethod
    def _create_multiple_choice_list_filter(cls, name, filter_instance):
        choices = filter_instance.extra.get("choices") or filter_instance.field.choices

        def __init__(self, request, *args, **kwargs):
            super(self.__class__, self).__init__(request, *args, **kwargs)
            if self.parameter_name in self.used_parameters:
                self.used_parameters[self.parameter_name] = request.GET.getlist(self.parameter_name)

        def lookups(self, request, model_admin):
            return choices

        methods = {
            "lookups": lookups,
            "template": "admin/custom_multiselect_filter_field.html",
            "__init__": __init__,
        }

        return cls._get_filter_class(name, filter_instance, methods)

    @classmethod
    def _create_date_list_filter(cls, name, filter_instance):
        field_name, _ = cls._get_field_name_and_title(name, filter_instance)

        def lookups(self, request, model_admin):
            return ((self.parameter_name, self.parameter_name),)

        methods = {
            "lookups": lookups,
            "template": "admin/custom_date_filter_field.html",
        }

        return cls._get_filter_class(name, filter_instance, methods)
