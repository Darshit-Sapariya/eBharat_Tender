from . import views
from django.urls import path
app_name = 'bids'
urlpatterns = [
    path('applybid/<int:tender_id>/',views.applybid,name='applybid'),
    path("tender/<int:tender_id>/apply/", views.applybid, name="apply_tender"),
    path("tender/<int:tender_id>/applications/", views.tender_applications, name="tender_applications"),
    path('bidsdeshboard', views.bidsdeshboard, name='bidsdeshboard'),
    path('mybids', views.mybids, name='mybids'),
    path("bid/<int:bid_id>/", views.bid_detail, name="bid_detail"),
    path("download-bid/<int:bid_id>/", views.download_bid_pdf, name="download_bid_pdf"),
    path("download-bid/<int:bid_id>/", views.download_bid_pdf, name="download_bid_pdf"),
    
    
]
