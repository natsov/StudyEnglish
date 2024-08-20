from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import View

from courses.forms import RegisterForm


def main(request):
    return render(request, 'courses/home.html', {})


def about(request):
    return render(request, 'courses/about.html', {})


def general_english(request):
    return render(request, 'courses/general_english.html')


def express_english(request):
    return render(request, 'courses/express_english.html')


def business_english(request):
    return render(request, 'courses/business_english.html')


@login_required
def profile_view(request):
    return render(request, 'courses/profile.html')


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