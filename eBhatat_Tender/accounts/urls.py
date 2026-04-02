from . import views
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
app_name = "accounts"
urlpatterns = [
   path('updateProfile/', views.updateProfile, name="updateProfile"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('myprofile/', views.my_profile, name='myprofile'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    path('register/', views.register, name='register'),
    path('check_username/', views.check_username, name='check_username'),
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('notifications/all/', views.view_all_notifications, name='view_all_notifications'),
    path('notifications/clear/', views.clear_notifications, name='clear_notifications'),
    
    # Password Change
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='password_change_form.html',
        success_url=reverse_lazy('accounts:password_change_done')
    ), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='password_change_done.html'
    ), name='password_change_done'),

    # Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset_form.html',
        email_template_name='password_reset_email.html',
        success_url=reverse_lazy('accounts:password_reset_done')
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html',
        success_url=reverse_lazy('accounts:password_reset_complete')
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),
]