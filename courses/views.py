import pdb
import random
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import View
from .models import Test, EnglishLevelInfo
from courses.forms import RegisterForm


def main(request):
    return render(request, 'courses/home.html', {})

@login_required
def placement_test(request):
    if 'question_index' not in request.session:
        request.session['question_index'] = 0  # Начинаем с первого вопроса
    question_index = request.session['question_index']
    question = Test.objects.all()[question_index]  # Получаем вопрос по индексу
    return render(request, 'courses/placement_test.html', {'question': question, 'question_index': question_index})


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


def show_random_question(request):
    if 'user_points' not in request.session:
        request.session['user_points'] = 0

    total_questions = Test.objects.count()

    if 'question_id' not in request.session:
        request.session['question_id'] = 1

    question_id = request.session['question_id']

    if request.method == 'POST':
        user_answer = request.POST.get('answer')
        question = Test.objects.get(id=question_id)
        if user_answer == question.correct_answer:
            request.session['user_points'] += question.number_of_points

        request.session['question_id'] += 1
        question_id = request.session['question_id']

    if question_id > total_questions:
        return redirect('result_test')

    question = Test.objects.get(id=question_id)

    return render(request, 'courses/random_question.html',
                  {'question': question, 'user_points': request.session['user_points'],
                   'total_questions': total_questions, 'question_id': question_id})


def result_test(request):
    user_points = request.session.get('user_points')
    tests = Test.objects.all()  # Получаем все объекты Test из базы данных

    total_points = sum(test.number_of_points for test in tests)

    percentage = (user_points / total_points) * 100

    if percentage < 30:
        level = 'A1'
    elif 30 <= percentage < 45:
        level = 'A2'
    elif 45 <= percentage < 60:
        level = 'B1'
    elif 60 <= percentage < 75:
        level = 'B2'
    elif 75 <= percentage < 90:
        level = 'C1'
    else:
        level = 'C2'

    english_level_info = EnglishLevelInfo.objects.get(level=level)

    return render(request, 'courses/result_test.html', {'user_points': user_points, 'level': level, 'english_level_info': english_level_info})