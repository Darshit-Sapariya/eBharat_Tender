from django.urls import path
from . import views

app_name = 'funding'

urlpatterns = [
    path('apply/<int:funding_id>/<int:tender_id>/', views.apply_funding, name='apply_funding'),
    path('my-requests/', views.my_funding_requests, name='my_funding_requests'),
]
