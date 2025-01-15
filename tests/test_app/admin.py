from django.contrib import admin

from django_admin_fast_search.admin import FastSearch, FastSearchFilterSet
from django_filters import FilterSet, CharFilter, BooleanFilter, DateFilter, ModelChoiceFilter

from .models import TestModel1, TestModel2, TestModel3, TestModel4

class TestModel4Filter(FastSearchFilterSet):
    name = CharFilter(lookup_expr="icontains")
    email = CharFilter(lookup_expr="exact")
    phonenumber = CharFilter(lookup_expr="exact")

    is_verified = BooleanFilter()
    activation_date = DateFilter(field_name="activated_at", lookup_expr="gt", label="Activated (after)")

    class Meta:
        model = TestModel4
        fields = [
            "name",
            "email",
            "phonenumber",
            "ref3",
            "is_verified",
            "activation_date",
        ]

@admin.register(TestModel1)
class TestModel1Admin(FastSearch):
    list_display = ("name", "email", "phonenumber")
    search_fields = ("name", "email", "phonenumber")


@admin.register(TestModel2)
class TestModel2Admin(FastSearch):
    list_display = ("name", "email", "phonenumber")
    search_fields_exact = ("email",)
    search_fields_fulltext_index = ("name",)
    search_fields_contains = ("phonenumber", )
    search_fields = search_fields_exact + search_fields_contains + search_fields_fulltext_index


@admin.register(TestModel3)
class TestModel3Admin(FastSearch):
    list_display = ("name", "email", "phonenumber")
    search_fields = ("name", "email", "phonenumber")

@admin.register(TestModel4)
class TestModel4AdminWithFilters(FastSearch):
    list_display = ("name", "email", "phonenumber")

    list_filter = TestModel4Filter.as_admin_filters()
