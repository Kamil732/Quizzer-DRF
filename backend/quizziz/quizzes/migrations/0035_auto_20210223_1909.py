# Generated by Django 3.1.6 on 2021-02-23 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0034_psychologyresults_image_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quizpunctation',
            name='summery',
        ),
        migrations.AddField(
            model_name='quizpunctation',
            name='description',
            field=models.TextField(default='LOL'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='quizpunctation',
            name='result',
            field=models.CharField(default='lol', max_length=100),
            preserve_default=False,
        ),
    ]
