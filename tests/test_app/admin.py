from django.contrib import admin

from django_admin_fast_search.admin import FastSearch

from .models import TestModel1, TestModel2, TestModel3


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
