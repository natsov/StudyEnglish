from django.urls import path, include
from . import views
from .views import Register, Login

urlpatterns = [
    path('', views.main, name='main'),
    path('accounts/login/', Login.as_view(), name='login'),
    path('placement_test', views.placement_test, name='placement_test'),
    path('general_english', views.general_english, name='general_english'),
    path('express_english', views.express_english, name='express_english'),
    path('business_english', views.business_english, name='business_english'),
    path('register', Register.as_view(), name='register'),
    path('placement_test', views.placement_test, name='placement_test'),
    path('random_question', views.show_random_question, name='random_question'),
    path('result_test', views.result_test, name='result_test'),
    path('user_form', views.user_form, name='user_form'),
    path('info_email/', views.info_email, name='info_email'),
    path('send_application/<int:course_id>/', views.send_application, name='send_application'),
    path('create_request/', views.create_course_request, name='create_course_request'),
    path('profile/', views.student_profile, name='student_profile'),

    ###Teachers urls####

    # Панель управления учителя
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),

    # Управление курсами
    path('teacher/course/create/', views.create_course, name='create_course'),
    path('teacher/course/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('teacher/course/<int:course_id>/delete/', views.delete_course, name='delete_course'),

    # Управление запросами пользователей
    path('teacher/request/<int:request_id>/approve/', views.approve_request, name='approve_request'),
    path('teacher/request/<int:request_id>/deny/', views.deny_request, name='deny_request'),

    # Управление уроками
    path('teacher/lesson/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('teacher/lesson/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),

    # Управление квизами
    path('teacher/quiz/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('teacher/quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),

    # Управление упражнениями
    path('teacher/lesson/<int:lesson_id>/exercise/create/', views.create_exercise, name='create_exercise'),
    path('teacher/exercise/<int:exercise_id>/edit/', views.edit_exercise, name='edit_exercise'),
    path('teacher/exercise/<int:exercise_id>/delete/', views.delete_exercise, name='delete_exercise'),

    # path('random_question/<int:question_id>/', views.show_random_question, name='random_question'),
]
