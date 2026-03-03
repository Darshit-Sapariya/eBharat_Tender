from django.urls import path

from . import views

app_name = 'public'
urlpatterns = [
    path('', views.index, name='home'),
    path('tenders/', views.tenders, name='tenders'),
    path('funding/', views.funding, name='funding'),
    path('workflow/', views.workflow, name='workflow'),
    path('guidelines/', views.guidelines, name='guidelines'),
    path('tenderDetails/<int:tender_id>/', views.tenderDetails, name='tenderDetails'),
   

]