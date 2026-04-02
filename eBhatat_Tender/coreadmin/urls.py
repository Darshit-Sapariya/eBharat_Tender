from . import views
from django.urls import path

app_name = 'coreadmin'

urlpatterns = [
    path('', views.coreadmin_deshbord, name='deshbord'), # Main dashboard
    path('base/', views.coreadmin_dashboard, name='base'), # Base layout view
    
    # User Management
    path('users/', views.user_list, name='user_list'),
    
    # Tender Management
    path('tender_list/', views.tender_list, name='tender_list'),
    path('tender/<int:tender_id>/bidders/', views.tender_bidders, name='tender_bidders'),
    
    # Funding Management
    path('funding/', views.funding_list, name='funding_list'),
    path('funding/create/', views.create_funding, name='create_funding'),
    
    # Approvals
    path('approvals/users/', views.user_approvals, name='user_approvals'),
    path('approvals/applications/', views.application_approvals, name='application_approvals'),
    path('approvals/admin-requests/', views.admin_request_approvals, name='admin_request_approvals'),
    path('approvals/funding/', views.funding_approvals, name='funding_approvals'),
    
    # Actions
    path('approve/user/<int:profile_id>/', views.approve_user, name='approve_user'),
    path('reject/user/<int:profile_id>/', views.reject_user, name='reject_user'),
    path('approve/application/<int:app_id>/', views.approve_application, name='approve_application'),
    path('reject/application/<int:app_id>/', views.reject_application, name='reject_application'),
    
    path('approve/funding/<int:app_id>/', views.approve_funding_app, name='approve_funding_app'),
    path('reject/funding/<int:app_id>/', views.reject_funding_app, name='reject_funding_app'),
    
    path('request/approve/<int:request_id>/', views.approve_admin_request, name='approve_admin_request'),
    path('request/reject/<int:request_id>/', views.reject_admin_request, name='reject_admin_request'),

    # Analytics
    path('emd-escrow/', views.emd_escrow_list, name='emd_escrow_list'),
    # History & Roles
    path('history/', views.action_history, name='action_history'),
    path('allocate/user/<int:profile_id>/', views.allocate_user_role, name='allocate_user_role'),

    # Notice Management
    path('notices/', views.notice_list, name='notice_list'),
    path('notices/create/', views.create_notice, name='create_notice'),
    path('notices/edit/<int:notice_id>/', views.edit_notice, name='edit_notice'),
    path('notices/delete/<int:notice_id>/', views.delete_notice, name='delete_notice'),

    path('profile/', views.admin_profile, name='admin_profile'),

    path('reports/', views.system_reports, name='reports'),
    path('reports/pdf/', views.download_report_pdf, name='download_report_pdf'),
    path('logout/', views.logout_view, name='logout'),
]
