from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('about', views.about, name='about_us'),
    path('user_login', views.user_login, name='user_login'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('general_english', views.general_english, name='general_english'),
    path('express_english', views.express_english, name='express_english'),
    path('business_english', views.business_english, name='business_english'),
]
