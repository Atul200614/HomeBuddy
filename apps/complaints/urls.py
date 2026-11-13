from django.urls import path
from . import views

app_name = 'complaints'

urlpatterns = [
    path('', views.my_complaints, name='list'),
    path('create/<int:booking_id>/', views.create_complaint, name='create'),
    path('<int:complaint_id>/', views.complaint_detail, name='detail'),
]
