# Generated by Django 5.0 on 2024-09-28 01:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pembayaran', '0003_diskon_is_publis'),
    ]

    operations = [
        migrations.RenameField(
            model_name='diskon',
            old_name='is_publis',
            new_name='is_publish',
        ),
    ]