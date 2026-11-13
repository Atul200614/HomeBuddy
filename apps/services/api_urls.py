from django.urls import path
from . import api_views

urlpatterns = [
    path('categories/', api_views.APICategoriesView.as_view(), name='api_categories'),
    path('', api_views.APIServicesView.as_view(), name='api_services'),
]
