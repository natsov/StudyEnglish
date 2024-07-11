from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    """Model for storing information about courses."""
    title = models.CharField(max_length=255)
    description = models.TextField()
    level = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_data = models.DateField()


class Lesson(models.Model):
    """Model for storing information about lessons in course"""
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.IntegerField()
    content = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class Exercise(models.Model):
    """Model for storing information about exercises in lesson"""
    exercise_type = models.CharField(max_length=100)
    exercise_text = models.TextField()
    correct_answer = models.CharField(max_length=255)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)


class Quiz(models.Model):
    """Model for storing quizzes for each course"""
    title = models.CharField(max_length=255)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class Question(models.Model):
    """Model for storing questions for each quiz"""
    question_text = models.CharField(max_length=255)
    choices = models.JSONField()
    correct_answer = models.CharField(max_length=255)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

