from . import views
from django.urls import path
app_name = 'coreadmin'
urlpatterns = [
    path ('', views.coreadmin_dashboard, name='base'),
]
