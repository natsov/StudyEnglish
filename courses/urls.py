from django.urls import path, include
from . import views
from .views import Register

urlpatterns = [
    path('', views.main, name='main'),
    path('about', views.about, name='about_us'),
    path('general_english', views.general_english, name='general_english'),
    path('express_english', views.express_english, name='express_english'),
    path('business_english', views.business_english, name='business_english'),
    path('profile', views.profile_view, name='profile'),
    path('register', Register.as_view(), name='register'),

]
