from . import views
from django.urls import path

app_name = 'coreadmin'

urlpatterns = [
    path('', views.coreadmin_deshbord, name='deshbord'), # Main dashboard
    path('base/', views.coreadmin_dashboard, name='base'), # Base layout view
    
    # User Management
    path('users/', views.user_list, name='user_list'),
    
    # Tender Management
    path('tenders/', views.tender_list, name='tender_list'),
    
    # Approvals
    path('approvals/users/', views.user_approvals, name='user_approvals'),
    path('approvals/applications/', views.application_approvals, name='application_approvals'),
    path('approvals/admin-requests/', views.admin_request_approvals, name='admin_request_approvals'),
    
    # Actions
    path('approve/user/<int:profile_id>/', views.approve_user, name='approve_user'),
    path('reject/user/<int:profile_id>/', views.reject_user, name='reject_user'),
    path('approve/application/<int:app_id>/', views.approve_application, name='approve_application'),
    path('reject/application/<int:app_id>/', views.reject_application, name='reject_application'),
    
    path('request/approve/<int:request_id>/', views.approve_admin_request, name='approve_admin_request'),
    path('request/reject/<int:request_id>/', views.reject_admin_request, name='reject_admin_request'),

    # Analytics
    path('analytics/', views.analytics, name='analytics'),
]
