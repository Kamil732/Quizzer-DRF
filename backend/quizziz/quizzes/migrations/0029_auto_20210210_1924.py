# Generated by Django 3.1.5 on 2021-02-10 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0028_quizpunctaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizpunctaction',
            name='from_score',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='quizpunctaction',
            name='to_score',
            field=models.PositiveIntegerField(),
        ),
    ]
