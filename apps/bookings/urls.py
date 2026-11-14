from django.urls import path

from . import views

app_name = 'bookings'

urlpatterns = [
    path('emergency/', views.emergency_booking_view, name='emergency'),
    path('create/<slug:service_slug>/', views.create_booking, name='create'),
    path('<int:booking_id>/', views.booking_detail, name='detail'),
    path('<int:booking_id>/confirm/', views.confirm_completion, name='confirm_completion'),
    path('<int:booking_id>/cancel/', views.cancel_booking, name='cancel'),
    path('<int:booking_id>/rebook/', views.rebook, name='rebook'),
    path('<int:booking_id>/location/update/', views.update_location, name='update_location'),
    path('<int:booking_id>/location/', views.get_live_location, name='get_live_location'),
]
