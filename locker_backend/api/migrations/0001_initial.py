# Generated by Django 5.1.1 on 2024-09-06 12:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Groups',
            fields=[
                ('groupId', models.AutoField(primary_key=True, serialize=False)),
                ('groupName', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'groups',
            },
        ),
        migrations.CreateModel(
            name='PasswordItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('itemName', models.CharField(max_length=100)),
                ('userName', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('groupId', models.ForeignKey(db_column='groupId', on_delete=django.db.models.deletion.CASCADE, to='api.groups')),
            ],
            options={
                'db_table': 'password-items',
            },
        ),
    ]
