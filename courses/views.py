import random
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import View
from .models import Test
from courses.forms import RegisterForm


def main(request):
    return render(request, 'courses/home.html', {})


def placement_test(request):
    return render(request, 'courses/placement_test.html', {})


def general_english(request):
    return render(request, 'courses/general_english.html')


def express_english(request):
    return render(request, 'courses/express_english.html')


def business_english(request):
    return render(request, 'courses/business_english.html')


class Register(View):
    template_name = 'registration/register.html'

    def get(self, request):
        context = {
            'form': RegisterForm()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            # email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
        context = {
            'form': form
        }
        return render(request, self.template_name, context)


@login_required
def student_form(request):
    return render(request, 'courses/student_form.html')


# def test_view(request, id):
#     test_instance = Test.objects.get(pk=id)
#     if request.method == 'POST':
#         form = TestForm(request.POST, test_instance=test_instance)
#         if form.is_valid():
#             pass
#     else:
#         form = TestForm(test_instance=test_instance)
#     return render(request, 'test_template.html', {'form': form})

def show_random_question(request):
    user_points = 0  # Инициализируем переменную для баллов пользователя
    if request.method == 'POST':
        user_answer = request.POST.get('answer')
        random_question = Test.objects.get(id=request.POST.get('question_id'))
        if user_answer == random_question.correct_answer:
            user_points += random_question.points
    count = Test.objects.count()
    random_index = random.randint(0, count - 1)
    random_question = Test.objects.all()[random_index]

    return render(request, 'courses/random_question.html', {'question': random_question, 'user_points': user_points})
