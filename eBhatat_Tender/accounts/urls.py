from . import views
from django.urls import path
app_name = "accounts"
urlpatterns = [
   path('updateProfile/', views.updateProfile, name="updateProfile"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('myprofile/', views.my_profile, name='myprofile'),
    path('register/', views.register, name='register'),
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('notifications/all/', views.view_all_notifications, name='view_all_notifications'),
    path('notifications/clear/', views.clear_notifications, name='clear_notifications'),
]