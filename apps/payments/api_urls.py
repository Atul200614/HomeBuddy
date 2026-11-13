from django.urls import path

from . import api_views

app_name = 'payments_api'

urlpatterns = [
    path('my/', api_views.APIMyPaymentsView.as_view(), name='api_my_payments'),
    path('booking/<int:booking_id>/', api_views.APIPaymentDetailView.as_view(), name='api_payment_detail'),
]
