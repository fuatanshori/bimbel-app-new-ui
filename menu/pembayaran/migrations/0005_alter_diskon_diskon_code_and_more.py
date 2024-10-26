# Generated by Django 5.0 on 2024-10-24 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pembayaran', '0004_alter_transaksi_diskon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diskon',
            name='diskon_code',
            field=models.CharField(db_collation='utf8mb4_bin', max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='diskon',
            unique_together={('tarif', 'diskon_code')},
        ),
    ]
