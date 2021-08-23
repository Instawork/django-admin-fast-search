from django.test import TestCase
from django.urls import reverse
from .factories import AuthSuperUserFactory, TestModel1Factory, TestModel2Factory


class AdminFastSearchFormRenderTests(TestCase):
    def setUp(self):
        admin_user = AuthSuperUserFactory()
        self.client.force_login(admin_user)

    def test_correct_filter_classes_used_model_1_admin(self):
        for _ in range(10):
            TestModel1Factory()
        url = reverse("admin:test_app_testmodel1_changelist")

        response = self.client.get(url)
        list_filters = response.context['cl'].list_filter
        assert (response.context['cl'].result_count) == 10
        assert len(list_filters) == 3

        for list_filter in list_filters:
            assert list_filter.__name__ == "GenericExactFilter"

    def test_correct_filter_classes_used_model_2_admin(self):
        for _ in range(10):
            TestModel2Factory()
        url = reverse("admin:test_app_testmodel2_changelist")
        response = self.client.get(url)
        list_filters = response.context['cl'].list_filter
        assert len(list_filters) == 3
        assert (response.context['cl'].result_count) == 10

        result_dict = {}
        for list_filter in list_filters:
            result_dict[list_filter.parameter_name] = list_filter.__name__

        assert result_dict['name'] == "GenericSearchFilter"
        assert result_dict['email'] == "GenericExactFilter"
        assert result_dict['phonenumber'] == "GenericContainsFilter"

    def test_filtered_correctly(self):
        user1 = TestModel2Factory(email="ubansal@instawork.com", phonenumber="9871049414", name="Utkarsh Bansal")
        user2 = TestModel2Factory(email="ubansal2@instawork.com", phonenumber="9999999999")
        user3 = TestModel2Factory(email="ubansal3@instawork.com", phonenumber="8888888888")
        url = reverse("admin:test_app_testmodel2_changelist") +"?email=ubansal@instawork.com"
        response = self.client.get(url)
        assert response.status_code == 200
        assert (response.context['cl'].result_count) == 1
        assert (response.context['cl'].result_list.first().id) == user1.id
        assert str(response.context['cl'].queryset.query) == 'SELECT "test_app_testmodel2"."id", "test_app_testmodel2"."name", "test_app_testmodel2"."email", "test_app_testmodel2"."phonenumber" FROM "test_app_testmodel2" WHERE "test_app_testmodel2"."email" = ubansal@instawork.com ORDER BY "test_app_testmodel2"."id" DESC'

        url = reverse("admin:test_app_testmodel2_changelist") + "?phonenumber=9414"
        response = self.client.get(url)
        assert response.status_code == 200
        assert (response.context['cl'].result_count) == 1
        assert (response.context['cl'].result_list.first().id) == user1.id
        assert str(response.context['cl'].queryset.query) == 'SELECT "test_app_testmodel2"."id", "test_app_testmodel2"."name", "test_app_testmodel2"."email", "test_app_testmodel2"."phonenumber" FROM "test_app_testmodel2" WHERE "test_app_testmodel2"."phonenumber" LIKE %9414% ESCAPE {} ORDER BY "test_app_testmodel2"."id" DESC'.format("'\\'")
