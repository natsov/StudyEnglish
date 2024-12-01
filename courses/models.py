from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Model for storing information about users."""

    class ProfileType(models.TextChoices):
        GENERAL = 'General', 'General'
        EXPRESS = 'Express', 'Express'
        BUSINESS = 'Business', 'Business'

    country = models.CharField(max_length=100, blank=True, null=True)
    profile_type = models.CharField(
        max_length=10,
        choices=ProfileType.choices,
        default=None,
        blank=True,
        null=True,
    )
    is_teacher = models.BooleanField(default=False)  # Роль учителя

    def __str__(self):
        return self.username


class Course(models.Model):
    """Model for storing information about courses."""
    title = models.CharField(max_length=255)
    level = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)
    students = models.ManyToManyField(User, related_name='enrolled_courses', blank=True)

    def __str__(self):
        lesson_count = self.lesson_set.count()  # Количество уроков
        test_count = self.quiz_set.count()  # Количество тестов
        return (f"{self.title} | Уровень: {self.level} | Длительность: {self.duration} | "
                f"Уроки: {lesson_count} | Тесты: {test_count}")



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


class Test(models.Model):
    """Model for storing questions for english level test"""
    question_text = models.CharField(max_length=255)
    choices = models.JSONField()
    correct_answer = models.CharField(max_length=255)
    number_of_points = models.IntegerField()


class EnglishLevelInfo(models.Model):
    level = models.CharField(max_length=10)
    description = models.TextField()

    def __str__(self):
        return self.level


class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test_date = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField()
    level = models.CharField(max_length=2, choices=[('A1', 'A1'), ('A2', 'A2'), ('B1', 'B1'),
                                                   ('B2', 'B2'), ('C1', 'C1'), ('C2', 'C2')], default='A1')  # Добавили поле для уровня



class CourseRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Denied', 'Denied')],
        default='Pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.course.title} ({self.status})"
