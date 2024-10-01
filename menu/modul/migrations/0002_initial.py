# Generated by Django 5.0 on 2024-10-01 11:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mapel', '0001_initial'),
        ('modul', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='modul',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='modul',
            name='mata_pelajaran',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mapel.matapelajaran'),
        ),
    ]
