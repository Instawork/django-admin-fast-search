# -*- coding: utf-8 -*-
import logging

from django.contrib import admin
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
        initial_list_filters = self.list_filter

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
