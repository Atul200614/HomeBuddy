from django.urls import path
from . import api_views

urlpatterns = [
    path('my/', api_views.APIMyBookingsView.as_view(), name='api_my_bookings'),
]
