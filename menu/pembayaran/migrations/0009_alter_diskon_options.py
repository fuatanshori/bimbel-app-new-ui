# Generated by Django 5.0 on 2024-09-29 16:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pembayaran', '0008_alter_tarif_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='diskon',
            options={'ordering': ['-created_at'], 'verbose_name_plural': 'Diskon'},
        ),
    ]
