import factory
from django.contrib.auth.models import User
from datetime import timezone
from tests.test_app.models import TestModel1, TestModel2, TestModel3, TestModel4

class AuthUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username =  factory.Faker("first_name")
    email = factory.Faker("email")


class AuthSuperUserFactory(AuthUserFactory):
    is_superuser = True
    is_staff = True


class TestModel1Factory(factory.django.DjangoModelFactory):
    class Meta:
        model = TestModel1

    name = factory.Faker("first_name")
    email = factory.Faker("email")
    phonenumber = factory.Faker("phone_number")


class TestModel2Factory(factory.django.DjangoModelFactory):
    class Meta:
        model = TestModel2

    name = factory.Faker("first_name")
    email = factory.Faker("email")
    phonenumber = factory.Faker("phone_number")

class TestModel3Factory(factory.django.DjangoModelFactory):
    class Meta:
        model = TestModel3

    name = factory.Faker("first_name")
    email = factory.Faker("email")
    phonenumber = factory.Faker("phone_number")


class TestModel4Factory(factory.django.DjangoModelFactory):
    class Meta:
        model = TestModel4

    name = factory.Faker("first_name")
    email = factory.Faker("email")
    phonenumber = factory.Faker("phone_number")

    ref3 = factory.SubFactory(TestModel3Factory)

    is_verified = factory.Faker("boolean")
    activated_at = factory.Faker("date_time_this_month", tzinfo=timezone.utc)
