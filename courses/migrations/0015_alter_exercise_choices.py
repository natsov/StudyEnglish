# Generated by Django 5.0.6 on 2024-12-07 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0014_exercise_choices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercise',
            name='choices',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
