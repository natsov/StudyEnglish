from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Course, Lesson, Exercise, CourseRequest, LessonTheory
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
        fields = ['title', 'duration', 'block']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['block'].required = True


class LessonTheoryForm(forms.ModelForm):
    class Meta:
        model = LessonTheory
        fields = ['view_type', 'phrase', 'translation', 'text_content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['view_type'].required = True
        self.fields['phrase'].required = False
        self.fields['translation'].required = False
        self.fields['text_content'].required = False


import ast  # Для безопасного преобразования строки в список

class ExerciseForm(forms.ModelForm):
    exercise_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        label="Exercise Text"
    )
    correct_answer = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Correct Answer"
    )
    choices = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,
        help_text="Enter choices as a Python list, e.g., ['choice1', 'choice2'].",
        label="Choices"
    )

    class Meta:
        model = Exercise
        fields = ['exercise_text', 'correct_answer', 'choices']

    def __init__(self, *args, **kwargs):
        self.exercise_type = kwargs.pop('exercise_type', None)
        super().__init__(*args, **kwargs)

        # Поле choices обязательно только для multiple_choice
        if self.exercise_type == 'multiple_choice':
            self.fields['choices'].required = True
        else:
            self.fields.pop('choices', None)

        # Преобразование choices обратно в строку для редактирования
        if 'instance' in kwargs:
            instance = kwargs['instance']
            if instance and instance.choices:
                self.initial['choices'] = repr(instance.choices)

    def clean_choices(self):
        """Преобразует строку в список и валидирует choices."""
        raw_choices = self.cleaned_data.get('choices', '')
        try:
            # Преобразуем строку в список через ast.literal_eval
            choices = ast.literal_eval(raw_choices)
            if not isinstance(choices, list):
                raise ValueError("Choices must be a list.")
            if len(choices) < 2:
                raise forms.ValidationError("Provide at least two choices.")
            return choices
        except (ValueError, SyntaxError):
            raise forms.ValidationError("Invalid format for choices. Use Python list format.")

    def clean(self):
        """Общая валидация формы."""
        cleaned_data = super().clean()
        correct_answer = cleaned_data.get('correct_answer', '').strip()
        exercise_text = cleaned_data.get('exercise_text', '').strip()
        choices = cleaned_data.get('choices', [])

        # Проверка для multiple_choice
        if self.exercise_type == 'multiple_choice':
            if correct_answer not in choices:
                self.add_error('correct_answer', "Correct answer must be one of the choices.")

        # Проверка для fill_in_the_blank
        elif self.exercise_type == 'fill_in_the_blank':
            if "____" not in exercise_text:
                self.add_error('exercise_text', "Exercise text must contain '____' to represent the blank.")
            cleaned_data['choices'] = []

        # Проверка для true_false
        elif self.exercise_type == 'true_false':
            if correct_answer.lower() not in ['true', 'false']:
                self.add_error('correct_answer', "Correct answer must be 'true' or 'false'.")
            cleaned_data['choices'] = ['True', 'False']

        return cleaned_data

#
# class QuizForm(forms.ModelForm):
#     class Meta:
#         model = Quiz
#         fields = ['title', 'description']
#
# class QuestionForm(forms.ModelForm):
#     class Meta:
#         model = Question
#         fields = ['question_text', 'question_type', 'choices', 'correct_answer']