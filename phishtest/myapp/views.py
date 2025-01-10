import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, FileResponse
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import Course, Test, Question, Answer, UserProfile, PhishingEmail, CoursePage, UserTest
from .forms import CourseForm, TestForm, QuestionForm, AnswerForm, UserProfileForm, PhishingEmailForm, CoursePageForm, TakeTestForm
from actstream import action
from actstream.models import Action
from django.urls import reverse
from actstream.actions import follow
from django.utils import timezone
from django.views import View
from django.db.models import Avg

def home(request):
    return render(request, 'myapp/home.html')

@login_required
def user_profile_view(request):
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=user)
    groups = user.groups.all()
    return render(request, 'myapp/user_profile_view.html', {'user': user, 'user_profile': user_profile, 'groups': groups})

@login_required
@permission_required('auth.add_user', raise_exception=True)
def create_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = get_random_string(length=10)
        user = User.objects.create_user(username=username, email=email, password=password)

        UserProfile.objects.create(user=user)

        send_mail(
            'Your login credentials',
            f'Ваш username: {username}\nВаш пароль: {password}\nПожалуйста измените ваш пароль после первого входа.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return redirect('user_list')
    return render(request, 'myapp/create_user.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('home')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'myapp/change_password.html', {'form': form})

def course_list(request):
    courses = Course.objects.all().prefetch_related('tests')
    return render(request, 'myapp/course_list.html', {'courses': courses})

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'myapp/course_detail.html', {'course': course})

@login_required
@permission_required('myapp.add_course', raise_exception=True)
def course_create_update(request, course_id=None):
    if course_id:
        course = get_object_or_404(Course, id=course_id)
    else:
        course = Course()

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)

    return render(request, 'myapp/course_form.html', {'form': form})

def course_page_create_update(request, course_id, page_id=None):
    course = get_object_or_404(Course, id=course_id)
    if page_id:
        page = get_object_or_404(CoursePage, id=page_id, course=course)
    else:
        page = CoursePage(course=course)

    if request.method == 'POST':
        form = CoursePageForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = CoursePageForm(instance=page)

    return render(request, 'myapp/course_page_form.html', {'form': form, 'course': course})


def course_page_detail(request, course_id, page_id):
    course = get_object_or_404(Course, id=course_id)
    page = get_object_or_404(CoursePage, id=page_id, course=course)
    pages = list(course.pages.all())
    current_index = pages.index(page)

    previous_page = pages[current_index - 1] if current_index > 0 else None
    next_page = pages[current_index + 1] if current_index < len(pages) - 1 else None

    return render(request, 'myapp/course_page_detail.html', {
        'course': course,
        'page': page,
        'previous_page': previous_page,
        'next_page': next_page
    })

@login_required
@permission_required('myapp.delete_course', raise_exception=True)
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        course.delete()
        return redirect('course_list')
    return render(request, 'myapp/course_confirm_delete.html', {'course': course})

def test_list(request):
    tests = Test.objects.all()
    return render(request, 'myapp/test_list.html', {'tests': tests})

def test_detail(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    return render(request, 'myapp/test_detail.html', {'test': test})

@login_required
@permission_required('myapp.add_test', raise_exception=True)
def test_create_update(request, test_id=None):
    if test_id:
        test = get_object_or_404(Test, id=test_id)
    else:
        test = Test()

    if request.method == 'POST':
        form = TestForm(request.POST, instance=test)
        if form.is_valid():
            form.save()
            return redirect('test_detail', test_id=test.id)
    else:
        form = TestForm(instance=test)

    return render(request, 'myapp/test_form.html', {'form': form})

@login_required
@permission_required('myapp.delete_test', raise_exception=True)
def test_delete(request, pk):
    test = get_object_or_404(Test, pk=pk)
    if request.method == "POST":
        test.delete()
        return redirect('test_list')
    return render(request, 'myapp/test_confirm_delete.html', {'test': test})


def question_list(request, test_pk):
    questions = Question.objects.filter(test_id=test_pk)
    return render(request, 'myapp/question_list.html', {'questions': questions, 'test_pk': test_pk})

def question_create_update(request, test_id, question_id=None):
    test = get_object_or_404(Test, id=test_id)
    if question_id:
        question = get_object_or_404(Question, id=question_id, test=test)
    else:
        question = Question(test=test)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('test_detail', test_id=test.id)
    else:
        form = QuestionForm(instance=question)

    return render(request, 'myapp/question_form.html', {'form': form, 'test': test})

def question_delete(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == "POST":
        question.delete()
        return redirect('question_list', test_pk=question.test.pk)
    return render(request, 'myapp/question_confirm_delete.html', {'question': question})

def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    return render(request, 'myapp/question_detail.html', {'question': question})

def answer_list(request, question_pk):
    answers = Answer.objects.filter(question_id=question_pk)
    return render(request, 'myapp/answer_list.html', {'answers': answers, 'question_pk': question_pk})

def answer_create_update(request, question_id, answer_id=None):
    question = get_object_or_404(Question, id=question_id)
    if answer_id:
        answer = get_object_or_404(Answer, id=answer_id, question=question)
    else:
        answer = Answer(question=question)

    if request.method == 'POST':
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            form.save()
            return redirect('question_detail', question_id=question.id)
    else:
        form = AnswerForm(instance=answer)

    return render(request, 'myapp/answer_form.html', {'form': form, 'question': question})

def answer_delete(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    if request.method == "POST":
        answer.delete()
        return redirect('answer_list', question_pk=answer.question.pk)
    return render(request, 'myapp/answer_confirm_delete.html', {'answer': answer})

@login_required
@permission_required('myapp.add_phishingemail', raise_exception=True)
def send_phishing_email(request):
    if request.method == "POST":
        form = PhishingEmailForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.cleaned_data.get('user')
            group = form.cleaned_data.get('group')

            if user:
                recipients = [user.email]
                phishing_email = form.save(commit=False)
                phishing_email.user = user
                phishing_email.save()
                action.send(request.user, verb='отправил фишинговое письмо', target=user)
            elif group:
                recipients = [member.email for member in group.user_set.all()]
                for member in group.user_set.all():
                    phishing_email = form.save(commit=False)
                    phishing_email.user = member
                    phishing_email.save()
                    action.send(request.user, verb='отправил фишинговое письмо', target=member)
            else:
                recipients = []

            email = EmailMessage(
                form.cleaned_data['subject'],
                form.cleaned_data['message'],
                settings.DEFAULT_FROM_EMAIL,
                recipients
            )
            email.content_subtype = "html"
            if 'attachment' in request.FILES:
                email.attach(request.FILES['attachment'].name, request.FILES['attachment'].read(), request.FILES['attachment'].content_type)

            tracking_url = reverse('track_phishing_email', kwargs={'email_id': phishing_email.id, 'user_id': user.id if user else group.id})
            email.body = email.body + f"\n\n<a href='{settings.BASE_URL}{tracking_url}'>Нажмите здесь для активации вашего аккаунта</a>"

            tracking_pixel_url = reverse('track_email_open', kwargs={'email_id': phishing_email.id, 'user_id': user.id if user else group.id})
            email.body = email.body + f"\n\n<img src='{settings.BASE_URL}{tracking_pixel_url}' alt='' width='1' height='1' style='display:none;'>"

            email.send()
            return HttpResponse('Фишинговое письмо отправлено')
    else:
        form = PhishingEmailForm()
    users = User.objects.all()
    groups = Group.objects.all()
    return render(request, 'myapp/send_phishing_email.html', {'form': form, 'users': users, 'groups': groups})

def track_phishing_email(request, email_id, user_id):
    phishing_email = get_object_or_404(PhishingEmail, id=email_id)
    user = get_object_or_404(User, id=user_id)
    action.send(user, verb='перешел по фишинговой ссылке', target=phishing_email)
    return redirect('home')

class TrackEmailOpenView(View):
    def get(self, request, email_id, user_id):
        email = get_object_or_404(PhishingEmail, id=email_id)
        follow(request.user, email, 'открыл фишинговое сообщение', timestamp=timezone.now())
        return HttpResponse(status=204)

def track_email_open(request, email_id, user_id):
    phishing_email = get_object_or_404(PhishingEmail, id=email_id)
    user = get_object_or_404(User, id=user_id)
    action.send(user, verb='открыл фишинговое сообщение', target=phishing_email)
    return HttpResponse(status=204)

def download_phishing_attachment(request, email_id, user_id):
    phishing_email = get_object_or_404(PhishingEmail, id=email_id)
    user = get_object_or_404(User, id=user_id)
    action.send(user, verb='загрузил фишинговый файл', target=phishing_email)

    if not phishing_email.attachment:
        raise Http404("No attachment found")

    return FileResponse(phishing_email.attachment.open(), as_attachment=True, filename=phishing_email.attachment.name)

@login_required
@permission_required('myapp.view_activity', raise_exception=True)
def activity_report(request):
    actions = Action.objects.all().order_by('-timestamp')
    return render(request, 'myapp/activity_report.html', {'actions': actions})

@login_required
def take_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = test.questions.all()
    if request.method == 'POST':
        form = TakeTestForm(request.POST, questions=questions)
        if form.is_valid():
            score = 0
            total_questions = questions.count()
            for question in questions:
                if question.question_type == 'text':
                    user_answer = request.POST.get(f'question_{question.id}')
                    correct_answers = question.answers.filter(is_correct=True)
                    if user_answer.lower() in [answer.text.lower() for answer in correct_answers]:
                        score += 1
                elif question.question_type == 'single_choice':
                    user_answer = request.POST.get(f'question_{question.id}')
                    if Answer.objects.filter(id=user_answer, is_correct=True).exists():
                        score += 1
                elif question.question_type == 'multiple_choice':
                    user_answers = request.POST.getlist(f'question_{question.id}')
                    correct_answers = question.answers.filter(is_correct=True)
                    if set(user_answers) == set([str(answer.id) for answer in correct_answers]):
                        score += 1
            user_test = UserTest.objects.create(user=request.user, test=test, score=(score / total_questions) * 100)
            return render(request, 'myapp/test_result.html', {'test': test, 'score': user_test.score})
    else:
        form = TakeTestForm(questions=questions)
    return render(request, 'myapp/take_test.html', {'form': form, 'test': test})

@login_required
def user_test_results(request):
    user_tests = UserTest.objects.filter(user=request.user).order_by('-completed_at')
    return render(request, 'myapp/user_test_results.html', {'user_tests': user_tests})

@login_required
@permission_required('myapp.view_testresult', raise_exception=True)
def test_results_report(request):
    results = UserTest.objects.all()
    average_scores = UserTest.objects.values('test__title').annotate(avg_score=Avg('score'))
    return render(request, 'myapp/test_results_report.html', {'results': results, 'average_scores': average_scores})

@login_required
@permission_required('auth.view_user', raise_exception=True)
def user_list(request):
    users = User.objects.all()
    return render(request, 'myapp/user_list.html', {'users': users})

def user_create(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserCreationForm()
    return render(request, 'myapp/user_form.html', {'form': form})

@login_required
@permission_required('myapp.change_user', raise_exception=True)
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserChangeForm(instance=user)
    return render(request, 'myapp/user_form.html', {'form': form})

@login_required
@permission_required('myapp.delete_user', raise_exception=True)
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        user.delete()
        return redirect('user_list')
    return render(request, 'myapp/user_confirm_delete.html', {'user': user})


@login_required
@permission_required('auth.view_user', raise_exception=True)
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    groups = user.groups.all()
    return render(request, 'myapp/user_detail.html', {'user': user, 'user_profile': user_profile, 'groups': groups})

@login_required
@permission_required('auth.change_user', raise_exception=True)
def user_edit_groups(request, pk):
    user = get_object_or_404(User, pk=pk)
    groups = Group.objects.all()
    if request.method == 'POST':
        selected_groups = request.POST.getlist('groups')
        user.groups.set(selected_groups)
        return redirect('user_detail', pk=user.pk)
    return render(request, 'myapp/user_edit_groups.html', {'user': user, 'groups': groups})

@login_required
def user_profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    user_profile = UserProfile.objects.get(user=user)
    return render(request, 'myapp/user_profile.html', {'user': user, 'user_profile': user_profile})


@login_required
def user_profile_edit(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile_view')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'myapp/user_profile_edit.html', {'form': form})

@login_required
@permission_required('myapp.add_notification', raise_exception=True)
def send_notification(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [User.objects.get(id=user_id).email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            return HttpResponse('Notification sent!')
        except Exception as e:
            return HttpResponse(f'Error sending notification: {e}', status=500)
    else:
        users = User.objects.all()
        return render(request, 'myapp/send_notification.html', {'users': users})

@login_required
@permission_required('auth.add_user', raise_exception=True)
def admin_dashboard(request):
    total_users = User.objects.count()
    total_courses = Course.objects.count()
    total_tests = Test.objects.count()
    total_test_results = UserTest.objects.count()
    recent_activities = Action.objects.all().order_by('-timestamp')[:10]

    context = {
        'total_users': total_users,
        'total_courses': total_courses,
        'total_tests': total_tests,
        'total_test_results': total_test_results,
        'recent_activities': recent_activities,
    }
    return render(request, 'myapp/admin_dashboard.html', context)

def external_api_integration(request):
    response = requests.get('https://api.example.com/data')
    data = response.json()
    return render(request, 'myapp/external_api_data.html', {'data': data})

@login_required
def user_progress(request):
    courses = Course.objects.all()
    progress_data = []
    for course in courses:
        tests = course.tests.all()
        if tests.exists():
            average_score = UserTest.objects.filter(test__in=tests, user=request.user).aggregate(Avg('score'))['score__avg']
        else:
            average_score = None
        progress_data.append({'course': course, 'average_score': average_score})
    return render(request, 'myapp/user_progress.html', {'progress_data': progress_data})

@login_required
@permission_required('myapp.view_usertest', raise_exception=True)
def user_progress_report(request):
    users = User.objects.all()
    progress_data = []

    for user in users:
        user_tests = UserTest.objects.filter(user=user)
        average_score = user_tests.aggregate(Avg('score'))['score__avg'] if user_tests else 0
        progress_data.append({
            'user': user,
            'average_score': average_score,
            'tests': user_tests
        })

    return render(request, 'myapp/user_progress_report.html', {'progress_data': progress_data})
