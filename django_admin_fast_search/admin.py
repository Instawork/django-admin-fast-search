# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db.models import Q


class FastSearch(admin.ModelAdmin):

    show_full_result_count = False
    change_list_template = "admin/custom_change_list.html"

    def lookup_allowed(self, lookup, value):
        return True

    def get_list_filter(self, request):
        initial_list_filters = self.list_filter

        new_filters = ()

        for field in self.search_fields:
            filter_class = generic_filter_factory()
            filter_class.title = field.replace("__", "→").replace("_", " ").upper()
            filter_class.parameter_name = field

            new_filters += (filter_class,)

        return new_filters + initial_list_filters


def generic_filter_factory():
    """
    Factory to generate GenericFilter classes. This helps us generate multiple independent copies of this class
    """
    class GenericFilter(admin.SimpleListFilter):
        title = None
        parameter_name = None

        template = "admin/custom_search_field.html"

        def lookups(self, request, model_admin):
            return (self.parameter_name, self.parameter_name),

        def queryset(self, request, queryset):
            print(self.value())

            if self.value():
                kwargs = {"{}".format(self.parameter_name): self.value()}
                return queryset.filter(**kwargs)
            return queryset

    return GenericFilter
