# Generated by Django 5.1.1 on 2024-09-10 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='passworditems',
            name='comment',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='passworditems',
            name='url',
            field=models.CharField(max_length=255, null=True),
        ),
    ]