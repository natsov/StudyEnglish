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
    path('profile/', views.student_profile, name='student_profile'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('lesson/<int:lesson_id>/view-exercises/', views.view_lesson_exercises, name='view_lesson_exercises'),
    path('lesson/<int:lesson_id>/exercises/', views.exercise_view, name='exercise_view'),
    path('lesson/<int:lesson_id>/detail/', views.lesson_detail, name='lesson_detail'),

    # path('lesson/<int:lesson_id>/results/', views.exercise_result_view, name='exercise_result'),
    path('course/<int:course_id>/add-lesson-with-theory/', views.add_lesson_with_theory, name='add_lesson_with_theory'),

    ###Teachers urls####

    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/request/<int:request_id>/approve/', views.approve_request, name='approve_request'),
    path('teacher/request/<int:request_id>/deny/', views.deny_request, name='deny_request'),
    path('teacher/dashboard/<int:course_id>/', views.view_course, name='view_course'),
    path('lesson/<int:lesson_id>/add-exercise/', views.add_exercise, name='add_exercise'),
    path('course/<int:course_id>/add-quiz/', views.add_quiz, name='add_quiz'),
    path('quiz/edit/<int:quiz_id>/', views.edit_quiz, name='edit_quiz'),
    path('lesson/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('course/<int:course_id>/add-lesson/', views.add_lesson, name='add_lesson'),

]
