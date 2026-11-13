from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('booking/<int:booking_id>/', views.chat_view, name='chat'),
]
