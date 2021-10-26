# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db.models import Q

import re

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
                query = " ".join(["+" + term for term in terms if term])
                kwargs = {f"{self.parameter_name}__search": f"{query}"}
                return queryset.filter(**kwargs)
            return queryset

    if filter_type == "contains":
        return GenericContainsFilter
    elif filter_type == "search":
        return GenericSearchFilter
    else:
        return GenericExactFilter
