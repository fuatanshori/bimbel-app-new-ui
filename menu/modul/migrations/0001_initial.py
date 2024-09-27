# Generated by Django 5.0 on 2024-09-02 17:25

import django.core.validators
import django_ckeditor_5.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Modul',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama_modul', models.CharField(max_length=50)),
                ('description', django_ckeditor_5.fields.CKEditor5Field(null=True, verbose_name='description')),
                ('modul', models.FileField(upload_to='pdf', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])])),
                ('vidio', models.FileField(blank=True, null=True, upload_to='vidio', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4'])])),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Modul',
            },
        ),
    ]
