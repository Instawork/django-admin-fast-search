from django.db import models


# Put your test models here

class TestModel1(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phonenumber = models.CharField(max_length=20)


class TestModel2(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phonenumber = models.CharField(max_length=20)


class TestModel3(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phonenumber = models.CharField(max_length=20)

class TestModel4(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phonenumber = models.CharField(max_length=20)

    is_verified = models.BooleanField(default=False)
    activated_at = models.DateTimeField()
    date_created = models.DateTimeField(auto_now_add=True)

