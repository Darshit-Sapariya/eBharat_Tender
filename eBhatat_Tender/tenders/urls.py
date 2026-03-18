from django.urls import path
from . import views

app_name = 'tenders'
urlpatterns = [
    path('tenderCreator/', views.tenderCreator, name='tenderCreator'),
    path('updateProfile/', views.updateProfile, name='updateProfile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('mytenders/', views.mytenders, name='mytenders'),
    path('tender_delete/<int:tender_id>/', views.tender_delete, name='tender_delete'),
    path('tender_edit/<int:tender_id>/', views.tender_edit, name='tender_edit'),
    path('tenderDetails/<int:tender_id>/', views.tenderDetails, name='tenderDetails'),
    path('viewbids/<int:tender_id>/', views.viewbids, name='viewbids'),
    path("tender/<int:tender_id>/bids/", views.view_tender_bids, name="view_tender_bids"),
    path("bid/<int:bid_id>/update/",views.update_bid_status,name="update_bid_status"),
    path("myBiddsApplications/", views.myBiddsApplications, name="myBiddsApplications"),
    path("request_admin/", views.request_admin, name="request_admin"),
    path("admin_requests/", views.admin_view_requests, name="admin_view_requests"),
]

