# Generated by Django 5.1.1 on 2024-09-11 12:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='passwordhistory',
            old_name='passwordOld',
            new_name='old_passwords',
        ),
    ]