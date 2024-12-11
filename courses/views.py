from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import View
from courses.forms import RegisterForm, LessonTheoryForm
from .models import Lesson, Exercise, Quiz, TestResult, CourseRequest, Course, Test, EnglishLevelInfo, Question, \
    ExerciseResult, LessonTheory
from .forms import LessonForm, ExerciseForm, QuizForm
from .decorators import teacher_required
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from datetime import timedelta
import re


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
    course = get_object_or_404(Course, id=course_id)

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

    return redirect(f"{request.path_info}?course_id={course_id}")


def student_profile(request):
    user = request.user

    if not user.is_authenticated:
        return redirect('login')

    enrolled_courses = user.enrolled_courses.all()
    test_results = TestResult.objects.filter(user=user).order_by('-test_date')
    last_level_test = test_results.first()

    context = {
        'user': user,
        'enrolled_courses': enrolled_courses,
        'last_level_test': last_level_test,
    }
    return render(request, 'courses/student_profile.html', context)




@teacher_required
def teacher_dashboard(request):
    user = request.user
    profile_type = user.profile_type

    if profile_type:
        courses = Course.objects.filter(title__icontains=profile_type)
    else:
        courses = Course.objects.none()
    level_info = []
    levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

    for course in courses:
        match = re.search(r'(A1|A2|B1|B2|C1|C2)', course.title)
        if match:
            level = match.group(0)
            lessons_count = Lesson.objects.filter(course=course).count()
            exercises_count = Exercise.objects.filter(lesson__course=course).count()
            quizzes_count = Quiz.objects.filter(course=course).count()

            level_info.append({
                'course': course,
                'level': level,
                'lessons_count': lessons_count,
                'exercises_count': exercises_count,
                'quizzes_count': quizzes_count,
            })

    return render(request, 'teacher/teacher_dashboard.html', {
        'courses': courses,
        'profile_type': profile_type,
        'level_info': level_info,
    })


@teacher_required
def approve_request(request, request_id):
    try:
        course_request = get_object_or_404(CourseRequest, id=request_id)
        course = course_request.course

        if course_request.user not in course.students.all():
            course.students.add(course_request.user)
            print(f"User {course_request.user} added to course {course.title}")
        course_request.status = 'Approved'
        course_request.save()
        print(f"Request {course_request.id} approved successfully.")
        messages.success(request, f"Заявка {course_request.user.username} на курс '{course.title}' одобрена.")
    except Exception as e:
        print(f"Error: {e}")
        messages.error(request, "Произошла ошибка.")
    return redirect('teacher_dashboard')


@teacher_required
def deny_request(request, request_id):
    """Отклонение запроса пользователя на участие в курсе."""
    course_request = get_object_or_404(CourseRequest, id=request_id, course__author=request.user)
    course_request.status = 'Denied'
    course_request.save()
    messages.success(request, f"Заявка пользователя {course_request.user.username} на курс '{course_request.course.title}' была отклонена.")
    return redirect('teacher_dashboard')

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = Lesson.objects.filter(course=course)
    quizzes = Quiz.objects.filter(course=course)

    content = []
    for lesson in lessons:
        associated_quizzes = quizzes.filter(title__startswith=lesson.title.split()[0])
        content.append({
            'lesson': lesson,
            'quizzes': associated_quizzes
        })

    context = {
        'course': course,
        'content': content,
        'blocks': [1, 2, 3], 
    }
    return render(request, 'courses/course_detail.html', context)


@teacher_required
def add_exercise(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course
    print(request.POST) 

    if request.method == 'POST':
        print("POST data received:", request.POST)
        exercise_type = request.POST.get('exercise_type')

        if exercise_type == 'multiple_choice':
            form = ExerciseForm(request.POST, course=course)
            if form.is_valid():
                exercise = form.save(commit=False)
                exercise.lesson = lesson
                exercise.save()
                print("Multiple Choice Exercise saved with ID:", exercise.id)
                return redirect('view_course', course_id=course.id)

        elif exercise_type == 'fill_in_the_blank':
            blank_question = request.POST.get('blank_question')
            blank_correct_answer = request.POST.get('blank_correct_answer')
            exercise = Exercise.objects.create(
                lesson=lesson,
                exercise_type='fill_in_the_blank',
                exercise_text=blank_question,
                correct_answer=blank_correct_answer,
            )
            print("Fill in the Blank Exercise saved with ID:", exercise.id)
            return redirect('view_course', course_id=course.id)

        elif exercise_type == 'true_false':
            correct_answer_tf = request.POST.get('correct_answer_tf')
            exercise_text = request.POST.get('exercise_text')
            exercise = Exercise.objects.create(
                lesson=lesson,
                exercise_type='true_false',
                exercise_text=exercise_text,
                correct_answer=correct_answer_tf,
            )
            print("True/False Exercise saved with ID:", exercise.id)
            return redirect('view_course', course_id=course.id)

        else:
            print("Invalid exercise type")
            return redirect('add_exercise', lesson_id=lesson.id)

    else:
        form = ExerciseForm(course=course)

    return render(request, 'teacher/add_exercise.html', {'form': form, 'lesson': lesson, 'course': course})


@teacher_required
def add_quiz(request, course_id):
    course = Course.objects.get(id=course_id)

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.course = course
            quiz.save()
            return redirect('teacher_dashboard')
    else:
        form = QuizForm()

    return render(request, 'teacher/add_quiz.html', {'form': form, 'course': course})

@teacher_required
def add_lesson(request, course_id):
    course = Course.objects.get(id=course_id)

    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            return redirect('teacher_dashboard')
    else:
        form = LessonForm()

    return render(
        request,
        'teacher/add_lesson.html',
        {'form': form, 'course': course}
    )


@teacher_required
def view_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = Lesson.objects.filter(course=course)
    quizzes = Quiz.objects.filter(course=course)

    return render(request, 'teacher/view_course.html', {
        'course': course,
        'lessons': lessons,
        'quizzes': quizzes
    })

@teacher_required
def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            return redirect('view_course', course_id=lesson.course.id)
    else:
        form = LessonForm(instance=lesson)

    return render(request, 'teacher/edit_lesson.html', {'form': form, 'lesson': lesson})


@teacher_required
def add_quiz(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        # Создание квиза
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.course = course  # Привязываем квиз к курсу
            quiz.save()

            # Обрабатываем добавление вопросов
            question_count = len(request.POST) // 5  # Ожидаем, что каждый вопрос будет иметь 5 полей

            for i in range(1, question_count + 1):
                question_text = request.POST.get(f'question_text_{i}')
                question_type = request.POST.get(f'question_type_{i}')
                choices = request.POST.get(f'choices_{i}')
                correct_answer = request.POST.get(f'correct_answer_{i}')
                correct_answer_tf = request.POST.get(f'correct_answer_tf_{i}')

                # Проверяем, что правильный ответ указан
                if question_type in ['short_answer', 'true_false']:
                    if not correct_answer and not correct_answer_tf:
                        form.add_error(f'correct_answer_{i}', 'Correct answer is required.')

                # Обработка типа вопроса и создание соответствующего вопроса
                if question_type == 'multiple_choice':
                    if choices:  # Проверяем, что choices не пустое
                        choices_list = [choice.strip() for choice in choices.split(',')]  # Разделяем варианты по запятой
                        question = Question.objects.create(
                            question_text=question_text,
                            question_type=question_type,
                            choices=choices_list,
                            correct_answer=correct_answer,
                            quiz=quiz
                        )
                    else:
                        # В случае отсутствия вариантов для multiple choice
                        form.add_error(f'choices_{i}', 'Choices are required for multiple choice questions.')
                elif question_type == 'short_answer':
                    if correct_answer:  # Обрабатываем вопрос с правильным ответом
                        question = Question.objects.create(
                            question_text=question_text,
                            question_type=question_type,
                            correct_answer=correct_answer,
                            quiz=quiz
                        )
                    else:
                        form.add_error(f'correct_answer_{i}', 'Correct answer is required for short answer questions.')
                elif question_type == 'true_false':
                    if correct_answer_tf:  # Обрабатываем вопрос с правильным ответом для True/False
                        question = Question.objects.create(
                            question_text=question_text,
                            question_type=question_type,
                            correct_answer=correct_answer_tf,
                            quiz=quiz
                        )
                    else:
                        form.add_error(f'correct_answer_tf_{i}', 'Correct answer is required for true/false questions.')

            if form.errors:
                return render(request, 'teacher/add_quiz.html', {'form': form, 'course': course})

            return redirect('teacher_dashboard')  # После добавления квиза и вопросов возвращаемся на панель учителя

    else:
        form = QuizForm()

    return render(request, 'teacher/add_quiz.html', {'form': form, 'course': course})

@teacher_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            for question in quiz.questions.all():
                question_id = request.POST.get(f'question_id_{question.id}')
                question_text = request.POST.get(f'question_text_{question.id}')
                question_type = request.POST.get(f'question_type_{question.id}')
                choices = request.POST.get(f'choices_{question.id}')
                correct_answer = request.POST.get(f'correct_answer_{question.id}')
                correct_answer_tf = request.POST.get(f'correct_answer_tf_{question.id}')
                if not question_text or not question_type:
                    continue
                if question_id:
                    question = get_object_or_404(Question, id=question_id)
                else:
                    question = Question(quiz=quiz)
                question.question_text = question_text
                question.question_type = question_type
                if question_type == 'true_false':
                    question.correct_answer = correct_answer_tf or "false"
                else:
                    question.correct_answer = correct_answer or ""
                if question_type == 'multiple_choice' and choices:
                    question.choices = [choice.strip() for choice in choices.split(',')]
                question.save()
            return redirect('teacher_dashboard')
    else:
        form = QuizForm(instance=quiz)

    return render(request, 'teacher/edit_quiz.html', {
        'form': form,
        'quiz': quiz,
    })


def view_lesson_exercises(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    return render(request, 'courses/view_lesson_exercises.html', {'lesson': lesson})



@login_required
def exercise_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == "POST":
        exercises = lesson.exercise_set.all()
        total_questions = exercises.count()
        correct_answers = 0
        user_answers = {}

        for exercise in exercises:
            user_answer = request.POST.get(f"answer_{exercise.id}", "").strip()
            is_correct = user_answer.lower() == exercise.correct_answer.lower()
            user_answers[exercise.id] = user_answer
            ExerciseResult.objects.create(
                user=request.user,
                lesson=lesson,
                exercise=exercise,
                user_answer=user_answer,
                is_correct=is_correct
            )
            if is_correct:
                correct_answers += 1

        score = int((correct_answers / total_questions) * 100)

        return render(request, 'courses/exercise_result.html', {
            'lesson': lesson,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'score': score,
            'user_answers': user_answers,
        })

    return render(request, 'courses/exercise_form.html', {
        'lesson': lesson,
    })


def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    lesson_theory = LessonTheory.objects.filter(lesson=lesson)

    return render(request, 'courses/lesson_detail.html', {
        'lesson': lesson,
        'lesson_theory': lesson_theory,
    })

@teacher_required
def add_lesson_with_theory(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        lesson_form = LessonForm(request.POST)
        if lesson_form.is_valid():
            lesson = lesson_form.save(commit=False)
            lesson.course = course
            lesson.save()

            view_type = request.POST.get('theory_type')  # Изменено: используем корректное имя
            if view_type == 'simple':
                text_content = request.POST.get('simple_theory', '')  # Совпадает с именем в HTML
                audio = request.FILES.get('audio_file', None)  # Совпадает с именем в HTML
                LessonTheory.objects.create(
                    lesson=lesson,
                    view_type='text',
                    text_content=text_content,
                    audio=audio
                )
            elif view_type == 'table':
                phrases = request.POST.getlist('table_key[]')  # Совпадает с именем в HTML
                translations = request.POST.getlist('table_value[]')  # Совпадает с именем в HTML
                for phrase, translation in zip(phrases, translations):
                    LessonTheory.objects.create(
                        lesson=lesson,
                        view_type='table',
                        phrase=phrase,
                        translation=translation
                    )

            return redirect('view_course', course_id=course.id)

    lesson_form = LessonForm()
    return render(request, 'teacher/add_lesson_with_theory.html', {
        'lesson_form': lesson_form,
        'course': course,
    })

