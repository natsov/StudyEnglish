from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Course, Lesson, Exercise, Quiz, CourseRequest
from .models import Test

User = get_user_model()


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'level', 'duration']
        widgets = {
            'level': forms.Select(
                choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')]),
        }

class CourseRequestForm(forms.ModelForm):
    class Meta:
        model = CourseRequest
        fields = ['course']

    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        label="Выберите курс",
        widget=forms.Select(attrs={'class': 'form-control'}),
    )


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'duration', 'content']


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['exercise_type', 'exercise_text', 'correct_answer']
        widgets = {
            'answer_choices': forms.Textarea(attrs={'rows': 3}),
        }


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description']
        widgets = {
            'questions': forms.Textarea(attrs={'rows': 3}),
        }
