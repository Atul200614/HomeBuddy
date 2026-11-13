from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.services_list, name='list'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('view/<slug:slug>/', views.service_detail, name='detail'),
]
