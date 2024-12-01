from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Avg
from django.views.generic import View
from courses.forms import RegisterForm, CourseRequestForm
from .models import Lesson, Exercise, Quiz, TestResult, CourseRequest, Course, Test, EnglishLevelInfo
from .forms import CourseForm, LessonForm, ExerciseForm, QuizForm
from .decorators import teacher_required
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from datetime import timedelta


def main(request):
    user = request.user

    # Проверяем, аутентифицирован ли пользователь
    if isinstance(user, AnonymousUser):
        # Если пользователь анонимный, просто показываем страницу без кнопки
        return render(request, 'courses/home.html', {'show_button': False})

    last_test_result = TestResult.objects.filter(user=user).order_by('-test_date').first()
    test_passed = last_test_result and (timezone.now() - last_test_result.test_date < timedelta(days=7))

    form_filled = bool(user.first_name and user.last_name and user.email)

    show_button = test_passed and form_filled

    return render(request, 'courses/home.html', {'show_button': show_button})


@login_required
def placement_test(request):
    user = request.user
    last_test_result = TestResult.objects.filter(user=user).order_by('-test_date').first()
    if last_test_result:
        # Проверяем, проходил ли пользователь тест менее чем неделю назад
        time_since_last_test = timezone.now() - last_test_result.test_date
        if time_since_last_test < timedelta(days=7):
            error_message = "You can only take the test once a week."
            return render(request, 'courses/placement_test.html', {'error_message': error_message})
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

class Login(View):
    template_name = 'registration/login.html'

    def get(self, request):
        context = {
            'form': AuthenticationForm()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_teacher:
                    return redirect('teacher_dashboard')  # Имя маршрута панели управления учителя
                else:
                    return redirect('/')  # Главная страница для студентов
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Please correct the errors below.')

        return render(request, self.template_name, {'form': form})


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
            user = form.save(commit=False)
            is_teacher = request.POST.get('is_teacher') == 'true'
            user.is_teacher = is_teacher
            user.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            if user.is_teacher:
                return redirect('teacher_dashboard')  # Используйте имя маршрута для teacher_dashboard
            else:
                return redirect('/')
        context = {
            'form': form
        }
        return render(request, self.template_name, context)


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

    # Логика вычисления уровня пользователя на основе процента
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
    user = request.user

    # Создаем запись в TestResult, включая уровень
    TestResult.objects.create(user=user, score=user_points, level=level)

    return render(request, 'courses/result_test.html',
                  {'user_points': user_points, 'level': level, 'english_level_info': english_level_info})


def user_form(request):
    user = request.user
    is_filled = all([user.first_name, user.last_name, user.email, user.country])

    # Обработка отправки формы
    if request.method == 'POST':
        user.first_name = request.POST.get('firstName')
        user.last_name = request.POST.get('lastName')
        user.email = request.POST.get('email')
        user.country = request.POST.get('country')
        user.profile_type = request.POST.get('courseType')  # Сохраняем выбранный тип курса
        user.save()
        return redirect('/')  # Перенаправление после успешного сохранения

    if is_filled:
        # Если форма уже заполнена, показываем сообщение
        return render(request, 'courses/form_filled.html', {'user': user})

    return render(request, 'courses/user_form.html', {'user': user})


def info_email(request):
    user = request.user
    course_name = None
    course_status = None
    show_apply_button = False

    # Получаем результат теста
    last_test_result = TestResult.objects.filter(user=user).order_by('-test_date').first()
    form_filled = bool(user.first_name and user.last_name and user.email)

    if last_test_result and (timezone.now() - last_test_result.test_date < timedelta(days=7)):
        test_passed = True
    else:
        test_passed = False

    # Логика для вычисления следующего уровня
    if last_test_result:
        current_level = last_test_result.level

        # Словарь для перехода к следующему уровню
        level_up_dict = {
            'A1': 'A2', 'A2': 'B1', 'B1': 'B2', 'B2': 'C1', 'C1': 'C2', 'C2': 'C2'
        }

        # Уровень на 1 выше
        next_level = level_up_dict.get(current_level, 'C2')  # Если уровень C2, оставляем C2

        # Получаем тип курса из профиля пользователя
        profile_type = user.profile.profile_type if hasattr(user, 'profile') else 'General'

        # Формируем новое название курса с уровнем на 1 выше и типом курса из профиля
        next_course_name = f'{next_level} {profile_type}'
    else:
        next_course_name = "Не найдено"

    # Поиск курса по названию и уровню
    course = Course.objects.filter(title=next_course_name).first()

    if course:  # Если курс найден
        course_name = course.title
        # Проверяем, подана ли уже заявка на курс
        user_request = CourseRequest.objects.filter(user=user, course=course).first()

        if user_request:
            course_status = user_request.status
            if course_status == 'Approved':
                show_apply_button = False  # Если заявка уже одобрена, скрываем кнопку
            elif course_status == 'Pending':
                show_apply_button = False  # Если заявка на рассмотрении, скрываем кнопку
            else:
                show_apply_button = True  # Если заявка отклонена, показываем кнопку
        else:
            show_apply_button = True  # Если заявки нет, показываем кнопку
    else:
        course_name = "Курс не найден"

    # Условие для отображения кнопки (если пройден тест и форма заполнена)
    show_button = test_passed and form_filled

    return render(request, 'courses/info_email.html', {
        'course_name': course_name,
        'course_status': course_status,
        'show_apply_button': show_apply_button,
        'show_button': show_button,
        'next_course_name': next_course_name,
        'course_id': course.id if course else None
    })


def send_application(request, course_id):
    user = request.user
    course = get_object_or_404(Course, id=course_id)  # Проверяем существование курса

    # Проверяем или создаём заявку
    course_request, created = CourseRequest.objects.get_or_create(
        user=user,
        course=course,
        defaults={'status': 'Pending'}
    )

    if created:
        messages.success(request, "Ваша заявка успешно отправлена!")
    elif course_request.status == 'Pending':
        messages.info(request, "Вы уже отправили заявку на этот курс. Ожидайте ответа.")
    elif course_request.status == 'Rejected':
        # Повторная отправка при отклонённой заявке (если допустимо)
        course_request.status = 'Pending'
        course_request.save()
        messages.success(request, "Ваша заявка была обновлена и отправлена повторно.")
    else:
        messages.warning(request, f"Ваша заявка имеет статус: {course_request.status}. Изменения невозможны.")

    # Перенаправляем на страницу информации с параметром course_id
    return redirect(f"{request.path_info}?course_id={course_id}")


def student_profile(request):
    user = request.user

    # Убедимся, что пользователь авторизован
    if not user.is_authenticated:
        return redirect('login')  # Перенаправляем на страницу входа

    # Получаем курсы, на которые записан студент
    enrolled_courses = user.enrolled_courses.all()

    # Получаем результаты тестов
    test_results = TestResult.objects.filter(user=user).order_by('-test_date')

    # Общая статистика
    total_courses = enrolled_courses.count()
    average_score = test_results.aggregate(Avg('score'))['score__avg'] if test_results else None

    context = {
        'user': user,
        'enrolled_courses': enrolled_courses,
        'test_results': test_results,
        'total_courses': total_courses,
        'average_score': average_score,
    }
    return render(request, 'courses/student_profile.html', context)


def create_course_request(request):
    if request.method == 'POST':
        form = CourseRequestForm(request.POST)
        if form.is_valid():
            course_request = form.save(commit=False)
            course_request.user = request.user
            course_request.save()
            messages.success(request, "Заявка успешно создана!")
            return redirect('info_email')
    else:
        form = CourseRequestForm()
    return render(request, 'courses/create_request.html', {'form': form})


@teacher_required
def teacher_dashboard(request):
    """Отображение панели управления учителя."""
    # Получаем все курсы, на которые записаны студенты данного учителя
    courses = Course.objects.filter(students=request.user).prefetch_related('students')

    # Получаем все заявки на курсы для этого учителя
    user_requests = CourseRequest.objects.filter(course__students=request.user, status='Pending')

    context = {
        'courses': courses,
        'user_requests': user_requests,
    }
    return render(request, 'teacher/teacher_dashboard.html', context)


# Создание нового курса
@teacher_required
def create_course(request):
    """Создание нового курса."""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.author = request.user
            course.save()
            return redirect('teacher_dashboard')
    else:
        form = CourseForm()
    return render(request, 'teacher/create_course.html', {'form': form})

# Редактирование курса
@teacher_required
def edit_course(request, course_id):
    """Редактирование существующего курса."""
    course = get_object_or_404(Course, id=course_id, author=request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('teacher_dashboard')
    else:
        form = CourseForm(instance=course)
    return render(request, 'teacher/edit_course.html', {'form': form, 'course': course})

# Удаление курса
@teacher_required
def delete_course(request, course_id):
    """Удаление курса."""
    course = get_object_or_404(Course, id=course_id, author=request.user)
    course.delete()
    return redirect('teacher_dashboard')

# Создание урока для курса
@teacher_required
def create_lesson(request, course_id):
    """Создание урока для курса."""
    course = get_object_or_404(Course, id=course_id, author=request.user)
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            return redirect('edit_course', course_id=course.id)
    else:
        form = LessonForm()
    return render(request, 'teacher/create_lesson.html', {'form': form, 'course': course})

# Создание задания для урока
@teacher_required
@teacher_required
def create_exercise(request, lesson_id):
    """Создание упражнения для урока."""
    lesson = get_object_or_404(Lesson, id=lesson_id, course__author=request.user)
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.lesson = lesson
            exercise.save()
            return redirect('edit_lesson', lesson_id=lesson.id)
    else:
        form = ExerciseForm()
    return render(request, 'teacher/create_exercise.html', {'form': form, 'lesson': lesson})



@teacher_required
def edit_exercise(request, exercise_id):
    """Редактирование существующего упражнения."""
    exercise = get_object_or_404(Exercise, id=exercise_id, lesson__course__author=request.user)
    if request.method == 'POST':
        form = ExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            form.save()
            return redirect('edit_lesson', lesson_id=exercise.lesson.id)
    else:
        form = ExerciseForm(instance=exercise)
    return render(request, 'teacher/edit_exercise.html', {'form': form, 'exercise': exercise})


@teacher_required
def delete_exercise(request, exercise_id):
    """Удаление упражнения."""
    exercise = get_object_or_404(Exercise, id=exercise_id, lesson__course__author=request.user)
    lesson_id = exercise.lesson.id
    exercise.delete()
    return redirect('edit_lesson', lesson_id=lesson_id)


# Создание квиза для курса
@teacher_required
def create_quiz(request, course_id):
    """Создание квиза для курса."""
    course = get_object_or_404(Course, id=course_id, author=request.user)
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.course = course
            quiz.save()
            return redirect('edit_course', course_id=course.id)
    else:
        form = QuizForm()
    return render(request, 'teacher/create_quiz.html', {'form': form, 'course': course})


@teacher_required
def approve_request(request, request_id):
    """Одобрение запроса пользователя на участие в курсе."""
    course_request = get_object_or_404(CourseRequest, id=request_id, course__author=request.user)
    course_request.status = 'Approved'
    course_request.save()

    # Добавляем студента в курс
    course_request.course.students.add(course_request.user)
    return redirect('teacher_dashboard')


@teacher_required
def deny_request(request, request_id):
    """Отклонение запроса пользователя на участие в курсе."""
    course_request = get_object_or_404(CourseRequest, id=request_id, course__author=request.user)
    course_request.status = 'Denied'
    course_request.save()
    return redirect('teacher_dashboard')

@teacher_required
def edit_lesson(request, lesson_id):
    """Редактирование существующего урока."""
    lesson = get_object_or_404(Lesson, id=lesson_id, course__author=request.user)
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            return redirect('edit_course', course_id=lesson.course.id)
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'teacher/edit_lesson.html', {'form': form, 'lesson': lesson})


@teacher_required
def delete_lesson(request, lesson_id):
    """Удаление урока."""
    lesson = get_object_or_404(Lesson, id=lesson_id, course__author=request.user)
    course_id = lesson.course.id
    lesson.delete()
    return redirect('edit_course', course_id=course_id)


# Редактирование квиза
@teacher_required
def edit_quiz(request, quiz_id):
    """Редактирование квиза для курса."""
    quiz = get_object_or_404(Quiz, id=quiz_id, course__author=request.user)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            return redirect('edit_course', course_id=quiz.course.id)
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'teacher/edit_quiz.html', {'form': form, 'quiz': quiz})

# Удаление квиза
@teacher_required
def delete_quiz(request, quiz_id):
    """Удаление квиза."""
    quiz = get_object_or_404(Quiz, id=quiz_id, course__author=request.user)
    course_id = quiz.course.id
    quiz.delete()
    return redirect('edit_course', course_id=course_id)


@teacher_required
def course_detail(request, course_id):
    """Детальная информация о курсе."""
    course = get_object_or_404(Course, id=course_id, author=request.user)
    return render(request, 'teacher/course_detail.html', {'course': course})



