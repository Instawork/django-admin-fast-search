from django.test import TestCase
from django.urls import reverse
from .factories import AuthSuperUserFactory, TestModel1Factory, TestModel2Factory, TestModel4Factory
from unittest.mock import patch


class AdminFastSearchFormRenderTests(TestCase):
    def setUp(self):
        admin_user = AuthSuperUserFactory()
        self.client.force_login(admin_user)

    def test_correct_filter_classes_used_model_4_admin(self):
        for _ in range(10):
            TestModel4Factory()
        url = reverse("admin:test_app_testmodel4_changelist")

        response = self.client.get(url)
        list_filters = response.context['cl'].list_filter
        self.assertEqual(response.context['cl'].result_count, 10)

        expected_filter_names = ['name', 'email', 'phonenumber', 'is_verified', 'activation_date']
        self.assertEqual(len(list_filters), len(expected_filter_names))

        # Build a mapping of filter parameter names to their classes
        filter_dict = {}
        for list_filter in list_filters:
            # Each list_filter is an instance of SimpleListFilter, we can get parameter_name
            filter_dict[list_filter.parameter_name] = list_filter.__class__.__name__

        # Now check that each expected filter is present
        for filter_name in expected_filter_names:
            self.assertIn(filter_name, filter_dict)

    def test_filters_function_correctly_model_4_admin(self):
        user1 = TestModel4Factory(
            name="Alice Smith",
            email="alice@example.com",
            phonenumber="1234567890",
            is_verified=True,
            activated_at="2023-10-01"
        )
        user2 = TestModel4Factory(
            name="Bob Johnson",
            email="bob@example.com",
            phonenumber="0987654321",
            is_verified=False,
            activated_at="2023-09-15"
        )
        user3 = TestModel4Factory(
            name="Charlie Williams",
            email="charlie@example.com",
            phonenumber="5555555555",
            is_verified=True,
            activated_at="2023-08-20"
        )

        # Test name filter (icontains)
        url = reverse("admin:test_app_testmodel4_changelist") + "?name=Alice"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cl'].result_count, 1)
        self.assertEqual(response.context['cl'].result_list.first().id, user1.id)

        # Test email filter (exact)
        url = reverse("admin:test_app_testmodel4_changelist") + "?email=bob@example.com"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cl'].result_count, 1)
        self.assertEqual(response.context['cl'].result_list.first().id, user2.id)

        # Test email filter with invalid email (exact)
        url = reverse("admin:test_app_testmodel4_changelist") + "?email=john@example.com"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cl'].result_count, 0)

        # Test phonenumber filter (exact)
        url = reverse("admin:test_app_testmodel4_changelist") + "?phonenumber=5555555555"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cl'].result_count, 1)
        self.assertEqual(response.context['cl'].result_list.first().id, user3.id)

        # Test is_verified filter (BooleanFilter)
        url = reverse("admin:test_app_testmodel4_changelist") + "?is_verified=True"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cl'].result_count, 2)
        result_ids = [obj.id for obj in response.context['cl'].result_list]
        self.assertIn(user1.id, result_ids)
        self.assertIn(user3.id, result_ids)

        # Test activation_date filter (date_created > given date)
        url = reverse("admin:test_app_testmodel4_changelist") + "?activation_date=2023-09-20"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cl'].result_count, 1)
        self.assertEqual(response.context['cl'].result_list.first().id, user1.id)

    @patch("django_admin_fast_search.admin.ApproximatePaginator._mysql_approximate_count")
    def test_pagination_count_filters_model_4(self, mock_approximate_count):
        for _ in range(3):
            TestModel4Factory()

        url = reverse("admin:test_app_testmodel4_changelist")
        response = self.client.get(url)
        self.assertEqual(response.context['cl'].result_count, 3)
        self.assertEqual(mock_approximate_count.call_count, 0, "_mysql_approximate_count should not be called for SQLLite engines")

    def test_combined_filters_model_4(self):
        TestModel4Factory(
            name="Alice Smith",
            email="alice@example.com",
            phonenumber="1234567890",
            is_verified=True,
            activated_at="2023-10-01"
        )
        user2 = TestModel4Factory(
            name="Bob Johnson",
            email="bob@example.com",
            phonenumber="0987654321",
            is_verified=False,
            activated_at="2023-09-15"
        )
        TestModel4Factory(
            name="Charlie Williams",
            email="charlie@example.com",
            phonenumber="5555555555",
            is_verified=True,
            activated_at="2023-08-20"
        )


        # Test combined filters
        url = reverse("admin:test_app_testmodel4_changelist") + "?name=Bob&is_verified=False"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cl'].result_count, 1)
        self.assertEqual(response.context['cl'].result_list.first().id, user2.id)

    def test_invalid_inputs_model_4(self):
        TestModel4Factory(
            name="Alice Smith",
            email="alice@example.com",
            phonenumber="1234567890",
            is_verified=True,
            activated_at="2023-10-01"
        )

        # Test invalid phonenumber filter
        url = reverse("admin:test_app_testmodel4_changelist") + "?phonenumber=123"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cl'].result_count, 0)

