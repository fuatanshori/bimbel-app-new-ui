# Generated by Django 5.0 on 2024-09-28 01:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pembayaran', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='diskon',
            name='is_publis',
            field=models.BooleanField(default=False),
        ),
    ]