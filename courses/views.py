from django.shortcuts import render


def post_list(request):
    return render(request, 'courses/post_list.html', {})

