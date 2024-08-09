from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import *


def main(request):
    return render(request, 'courses/home.html', {})


def about(request):
    return render(request, 'courses/about.html', {})


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Редирект на домашнюю страницу после успешного входа
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'courses/user_login.html')


def sign_up(request):
    # if request.method == 'POST':
    #     form = UserCreationForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('login')  # Redirect to the login page after successful registration
    # else:
    #     form = UserCreationForm()
    return render(request, 'courses/sign_up.html')


def general_english(request):
    return render(request, 'courses/general_english.html')


def express_english(request):
    return render(request, 'courses/express_english.html')


def business_english(request):
    return render(request, 'courses/business_english.html')

