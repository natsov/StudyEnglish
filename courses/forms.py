from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Test

User = get_user_model()


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User


# class TestForm(forms.Form):
#     class Meta:
#         model = Test
#         fields = ('question_text','choices')

# class TestForm(forms.Form):
#     def __init__(self, *args, **kwargs):
#         test_instance = kwargs.pop('test_instance')
#         super(TestForm, self).__init__(*args, **kwargs)
#
#         self.fields['question_text'] = forms.CharField(label=test_instance.question_text)
#         self.fields['choices'] = forms.ChoiceField(choices=[(choice, choice) for choice in test_instance.choices])

