from django.urls import path
from . import views

app_name = 'tenders'
urlpatterns = [
    path('tenderCreator/', views.tenderCreator, name='tenderCreator'),
    path('updateProfile/', views.updateProfile, name='updateProfile'),
    path('dashboard/', views.deshboard, name='dashboard'),
    path('mytenders/', views.mytenders, name='mytenders'),
    path('tender_delete/<int:tender_id>/', views.tender_delete, name='tender_delete'),
    path('tender_edit/<int:tender_id>/', views.tender_edit, name='tender_edit'),
    path('tenderDetails/<int:tender_id>/', views.tenderDetails, name='tenderDetails'),
    path('bidsinfo/<int:tender_id>/', views.bidsinfo, name='bidsinfo'),
    path("tender/<int:tender_id>/bids/", views.view_tender_bids, name="view_tender_bids"),
    path("bid/<int:bid_id>/update/",views.update_bid_status,name="update_bid_status"),
    path("myBiddsApplications/", views.myBiddsApplications, name="myBiddsApplications")
]

