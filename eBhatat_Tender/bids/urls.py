from . import views
from django.urls import path
app_name = 'bids'
urlpatterns = [
    path('applybid/<int:tender_id>/',views.applybid,name='applybid'),
    path("tender/<int:tender_id>/apply/", views.applybid, name="apply_tender"),
    path("tender/<int:tender_id>/applications/", views.tender_applications, name="tender_applications"),
    path('bids_dashboard', views.bids_dashboard, name='bids_dashboard'),
    path('mybids', views.mybids, name='mybids'),
    path("bid/<int:bid_id>/", views.bid_detail, name="bid_detail"),
    path("download-bid/<int:bid_id>/", views.download_bid_pdf, name="download_bid_pdf"),
    path("bid/<int:bid_id>/withdraw/", views.withdraw_bid, name="withdraw_bid"),
    path("tender/<int:tender_id>/watchlist/", views.toggle_watchlist, name="toggle_watchlist"),
    path("watchlist/", views.my_watchlist, name="my_watchlist"),
    path("profile/", views.vendor_profile_update, name="vendor_profile_update"),
]
