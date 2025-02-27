# Generated by Django 5.0.6 on 2024-12-11 00:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0019_alter_lessontheory_audio_alter_lessontheory_lesson_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='content',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='lessontheory',
            name='audio',
            field=models.FileField(blank=True, null=True, upload_to='theory_audio/'),
        ),
        migrations.AlterField(
            model_name='lessontheory',
            name='lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_theory', to='courses.lesson'),
        ),
        migrations.AlterField(
            model_name='lessontheory',
            name='view_type',
            field=models.CharField(choices=[('table', 'Phrase and Translation'), ('text', 'Textual Theory')], max_length=10),
        ),
    ]
