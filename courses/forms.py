from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Course, Lesson, Exercise, Quiz, CourseRequest, Question, LessonTheory
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
        fields = ['view_type', 'phrase', 'translation', 'text_content', 'audio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['view_type'].required = True
        self.fields['phrase'].required = False
        self.fields['translation'].required = False
        self.fields['text_content'].required = False
        self.fields['audio'].required = False


class ExerciseForm(forms.ModelForm):
    lesson = forms.ModelChoiceField(
        queryset=Lesson.objects.none(),
        label="Select Lesson"
    )
    choices = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Exercise
        fields = ['exercise_type', 'exercise_text', 'correct_answer', 'lesson', 'choices']

    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        if course:
            self.fields['lesson'].queryset = course.lesson_set.all()

    def clean(self):
        cleaned_data = super().clean()
        exercise_type = cleaned_data.get('exercise_type')

        # Проверка для multiple_choice
        if exercise_type == 'multiple_choice':
            choices = self.clean_choices()
            correct_answer = cleaned_data.get('correct_answer')
            if correct_answer not in choices:
                self.add_error('correct_answer', "Правильный ответ должен быть одним из вариантов.")

        # Проверка для fill_in_the_blank
        elif exercise_type == 'fill_in_the_blank':
            blank_question = self.data.get('blank_question', '').strip()
            blank_correct_answer = self.data.get('blank_correct_answer', '').strip()

            if not blank_question or "____" not in blank_question:
                self.add_error('exercise_text', "Вопрос должен содержать пустое место (____).")
            if not blank_correct_answer:
                self.add_error('correct_answer', "Должен быть указан правильный ответ.")

            # Устанавливаем очищенные значения
            cleaned_data['exercise_text'] = blank_question
            cleaned_data['correct_answer'] = blank_correct_answer
            cleaned_data['choices'] = []  # Для этого типа вариантов ответа нет.

        # Проверка для true_false
        elif exercise_type == 'true_false':
            correct_answer_tf = self.data.get('correct_answer_tf', '').strip()

            if correct_answer_tf not in ['true', 'false']:
                self.add_error('correct_answer', "Правильный ответ должен быть True или False.")

            # Устанавливаем очищенные значения
            cleaned_data['correct_answer'] = correct_answer_tf
            cleaned_data['choices'] = []  # Для этого типа вариантов ответа нет.

        return cleaned_data

    def clean_choices(self):
        # Проверка на наличие вариантов ответа
        raw_choices = self.data.getlist('choices[]')
        choices = [choice.strip() for choice in raw_choices if choice.strip()]
        if len(choices) < 2:
            raise forms.ValidationError("Должно быть указано как минимум два варианта ответа.")
        return choices

    def clean_correct_answer(self):
        correct_answer = self.cleaned_data.get('correct_answer', '').strip()
        # Проверяем только для multiple_choice
        if self.cleaned_data.get('exercise_type') == 'multiple_choice':
            choices = self.clean_choices()
            if correct_answer not in choices:
                raise forms.ValidationError("Правильный ответ должен быть одним из вариантов.")
        return correct_answer


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'choices', 'correct_answer']