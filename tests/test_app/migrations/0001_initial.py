# Generated by Django 2.2 on 2021-08-19 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestModel1',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('phonenumber', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='TestModel2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('phonenumber', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='TestModel3',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('phonenumber', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='TestModel4',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('phonenumber', models.CharField(max_length=20)),
                ('is_verified', models.BooleanField(default=False)),
                ('activated_at', models.DateTimeField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
