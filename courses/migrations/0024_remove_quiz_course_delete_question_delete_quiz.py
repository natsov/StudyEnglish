# Generated by Django 5.0.6 on 2024-12-15 06:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0023_exerciseresult_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quiz',
            name='course',
        ),
        migrations.DeleteModel(
            name='Question',
        ),
        migrations.DeleteModel(
            name='Quiz',
        ),
    ]
