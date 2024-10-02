from django.urls import path, include
from . import views
from .views import Register

urlpatterns = [
    path('', views.main, name='main'),
    path('placement_test', views.placement_test, name='placement_test'),
    path('general_english', views.general_english, name='general_english'),
    path('express_english', views.express_english, name='express_english'),
    path('business_english', views.business_english, name='business_english'),
    path('register', Register.as_view(), name='register'),
    path('student_form', views.student_form, name='student_form'),
    path('placement_test', views.placement_test, name='placement_test'),
    path('random_question', views.show_random_question, name='random_question'),
    path('result_test', views.result_test, name='result_test'),
    # path('random_question/<int:question_id>/', views.show_random_question, name='random_question'),
]
