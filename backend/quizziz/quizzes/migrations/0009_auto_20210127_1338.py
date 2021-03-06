# Generated by Django 3.1.5 on 2021-01-27 12:38

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0008_auto_20210127_1313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, max_length=120, populate_from='title', unique_with=['author']),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, max_length=120, populate_from='title', unique_with=['author']),
        ),
    ]
