from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('create_user/', views.create_user, name='create_user'),
    path('change_password/', views.change_password, name='change_password'),
    path('courses/', views.course_list, name='course_list'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/create/', views.course_create_update, name='course_create'),
    path('course/<int:course_id>/update/', views.course_update, name='course_update'),
    path('course/<int:course_id>/delete/', views.course_delete, name='course_delete'),
    path('course/<int:course_id>/page/create/', views.course_page_create_update, name='course_page_create'),
    path('course/<int:course_id>/page/<int:page_id>/update/', views.course_page_create_update, name='course_page_update'),
    path('course/<int:course_id>/page/<int:page_id>/', views.course_page_detail, name='course_page_detail'),
    path('tests/', views.test_list, name='test_list'),
    path('test/<int:test_id>/', views.test_detail, name='test_detail'),
    path('test/create/', views.test_create_update, name='test_create'),
    path('test/<int:test_id>/update/', views.test_create_update, name='test_update'),
    path('test/<int:test_id>/delete/', views.test_delete, name='test_delete'),
    path('test/<int:test_id>/questions/', views.question_list, name='question_list'),
    path('test/<int:test_id>/question/create/', views.question_create_update, name='question_create'),
    path('test/<int:test_id>/question/<int:question_id>/update/', views.question_create_update, name='question_update'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
    path('question/<int:question_id>/delete/', views.question_delete, name='question_delete'),
    path('question/<int:question_id>/answers/', views.answer_list, name='answer_list'),
    path('question/<int:question_id>/answer/create/', views.answer_create_update, name='answer_create'),
    path('question/<int:question_id>/answer/<int:answer_id>/update/', views.answer_create_update, name='answer_update'),
    path('answer/<int:answer_id>/delete/', views.answer_delete, name='answer_delete'),
    path('send_phishing_email/', views.send_phishing_email, name='send_phishing_email'),
    path('track_phishing_email/<int:email_id>/<int:user_id>/', views.track_phishing_email, name='track_phishing_email'),
    path('track_email_open/<int:email_id>/<int:user_id>/', views.TrackEmailOpenView.as_view(), name='track_email_open'),
    path('download_phishing_attachment/<int:email_id>/<int:user_id>/', views.download_phishing_attachment, name='download_phishing_attachment'),
    path('activity_report/', views.activity_report, name='activity_report'),
    path('test/<int:test_id>/take/', views.take_test, name='take_test'),
    path('user_test_results/', views.user_test_results, name='user_test_results'),
    path('test_results_report/', views.test_results_report, name='test_results_report'),
    path('users/', views.user_list, name='user_list'),
    path('user/create/', views.user_create, name='user_create'),
    path('user/<int:pk>/update/', views.user_update, name='user_update'),
    path('user/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('user/<int:pk>/', views.user_detail, name='user_detail'),
    path('user/<int:pk>/profile/', views.user_profile, name='user_profile'),
    path('user/profile/edit/', views.user_profile_edit, name='user_profile_edit'),
    path('user/profile/view/', views.user_profile_view, name='user_profile_view'),
    path('user/<int:pk>/edit_groups/', views.user_edit_groups, name='user_edit_groups'),
    path('send_notification/', views.send_notification, name='send_notification'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('external_api_integration/', views.external_api_integration, name='external_api_integration'),
    path('user_progress/', views.user_progress, name='user_progress'),
    path('user_progress_report/', views.user_progress_report, name='user_progress_report'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('signup/', views.user_create, name='signup'),
    path('track_phishing_email/<int:email_id>/<int:user_id>/', views.track_phishing_email, name='track_phishing_email'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

