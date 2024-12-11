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

    def get_blocks(self):
        """Divide lessons and tests into blocks."""
        blocks = {f"Block {i}": {'lessons': [], 'tests': []} for i in range(1, 4)}

        # Group lessons into blocks
        for lesson in self.lesson_set.all():
            block_key = f"Block {lesson.block}"
            blocks[block_key]['lessons'].append(lesson)

        # Group quizzes into blocks
        for test in self.quiz_set.all():
            block_key = f"Block {test.block}"
            blocks[block_key]['tests'].append(test)

        # Return as a sorted list
        return sorted(blocks.items(), key=lambda x: x[0])

    def __str__(self):
        lesson_count = self.lesson_set.count()  # Количество уроков
        test_count = self.quiz_set.count()  # Количество тестов
        return (f"{self.title} | Уровень: {self.level} | Длительность: {self.duration} | "
                f"Уроки: {lesson_count} | Тесты: {test_count}")


class Lesson(models.Model):
    """Model for storing information about lessons in a course."""
    BLOCK_CHOICES = [(1, 'Block 1'), (2, 'Block 2'), (3, 'Block 3')]

    title = models.CharField(max_length=255)
    duration = models.IntegerField()
    content = models.TextField()
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    block = models.IntegerField(choices=BLOCK_CHOICES, default=1)

    def __str__(self):
        return f"{self.title} (Block {self.block})"

    @property
    def theories(self):
        return self.lesson_theory.all()


class LessonTheory(models.Model):
    """Model for the theory related to the lesson."""
    VIEW_TYPE_CHOICES = [
        ('table', 'Phrase and Translation'),
        ('text', 'Textual Theory'),
    ]

    lesson = models.ForeignKey('Lesson', related_name='lesson_theory', on_delete=models.CASCADE)
    view_type = models.CharField(max_length=10, choices=VIEW_TYPE_CHOICES)
    phrase = models.CharField(max_length=255, blank=True, null=True)
    translation = models.CharField(max_length=255, blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    audio = models.FileField(upload_to='theory_audio/', blank=True, null=True)

    def __str__(self):
        return f"Theory for {self.lesson.title} ({self.view_type})"


class Exercise(models.Model):
    """Model for exercises related to lessons (block-specific)."""
    EXERCISE_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('fill_in_the_blank', 'Fill in the Blank'),
        ('true_false', 'True/False'),
    ]

    exercise_type = models.CharField(max_length=50, choices=EXERCISE_TYPE_CHOICES)
    exercise_text = models.TextField()
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    choices = models.JSONField(default=list, blank=True)
    correct_answer = models.CharField(max_length=255)
    def __str__(self):
        return f"Exercise: {self.exercise_text}"


class Quiz(models.Model):
    """Модель для квизов, связанных с курсом."""
    title = models.CharField(max_length=255)
    description = models.TextField()
    course = models.ForeignKey('Course', on_delete=models.CASCADE)  # Связь с курсом

    def __str__(self):
        return f"Quiz: {self.title} ({self.course})"


class Question(models.Model):
    """Модель для вопросов в квизах."""
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('short_answer', 'Short Answer'),
        ('true_false', 'True/False'),
    ]

    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='short_answer')
    choices = models.JSONField(blank=True, null=True)  # Для вариантов ответов в multiple choice
    correct_answer = models.CharField(max_length=255)  # Для правильного ответа
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)

    def __str__(self):
        return f"Question: {self.question_text[:50]}..."

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


class ExerciseResult(models.Model):
    """Модель для хранения результатов выполнения упражнений."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_results')
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE)
    exercise = models.ForeignKey('Exercise', on_delete=models.CASCADE)
    user_answer = models.TextField()
    is_correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.user.username} | Lesson: {self.lesson.title} | Exercise: {self.exercise.exercise_text}"