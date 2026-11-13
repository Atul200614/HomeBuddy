from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('addresses/', views.addresses_view, name='addresses'),
    path('addresses/<int:address_id>/delete/', views.delete_address, name='delete_address'),
    path('bookings/', views.booking_history, name='bookings'),
]
